"""Phase 8-2-7: Task 실행 로직 (n8n HTTP 호출 및 CLI 공용)"""
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.config import PROJECT_ROOT
from backend.models.workflow_common import (
    COL_COMPLETED_AT,
    COL_ID,
    COL_STATUS,
    TABLE_TASKS,
    TaskStatus,
)

# 로컬 Claude Code CLI (Docker에서 호스트 마운트 시). bin/claude shebang 이 env 에서 실패할 수 있어 node + cli.js 사용
DEFAULT_CLAUDE_CLI_PATH = "/host-npm-global/bin/claude"
DEFAULT_CLAUDE_CLI_JS = "/host-npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js"

# plan_md_path 사용 시 CLI에 전달하는 프롬프트 지시문
PROMPT_BY_PLAN_PATH = (
    "Workspace root: {workspace_root}\n\n"
    "Task plan file (relative to workspace): {plan_md_path}\n\n"
    "Read this .md file and execute the task described in it. "
    "You may read, create, modify, or delete files under the project folder as needed. "
    "Reply with a short summary of what you did."
)


def get_task(db: Session, task_id: int):
    """workflow_tasks에서 task_id 조회. plan_md_path 있으면 경로 기반 실행, 없으면 plan_doc 사용."""
    try:
        r = db.execute(
            text(
                f"SELECT id, phase_id, task_name, {COL_STATUS}, plan_doc, test_plan_doc, plan_md_path "
                f"FROM {TABLE_TASKS} WHERE {COL_ID} = :id"
            ),
            {"id": task_id},
        )
        return r.fetchone()
    except Exception as _e:
        # plan_md_path 컬럼이 없을 때: 기존 6컬럼만 조회 (마이그레이션 전)
        r = db.execute(
            text(
                f"SELECT id, phase_id, task_name, {COL_STATUS}, plan_doc, test_plan_doc "
                f"FROM {TABLE_TASKS} WHERE {COL_ID} = :id"
            ),
            {"id": task_id},
        )
        row = r.fetchone()
        if row is None:
            return None
        # 7번째 요소 plan_md_path = None 으로 튜플 확장
        return (*row, None)


def update_status(db: Session, task_id: int, status: str) -> None:
    """workflow_tasks.status·completed_at 갱신 (공통 컬럼)."""
    db.execute(
        text(
            f"UPDATE {TABLE_TASKS} SET {COL_STATUS} = :status, {COL_COMPLETED_AT} = NOW() WHERE {COL_ID} = :id"
        ),
        {"status": status, "id": task_id},
    )
    db.commit()


def _resolve_claude_cli_js() -> Optional[str]:
    """cli.js 경로 반환. 기본 경로 없으면 bin/claude 심볼릭 링크를 따라감."""
    default_js = os.environ.get("CLAUDE_CLI_JS", DEFAULT_CLAUDE_CLI_JS)
    if Path(default_js).exists():
        return default_js
    bin_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)
    p = Path(bin_path)
    if p.exists() and p.is_symlink():
        resolved = p.resolve()
        if resolved.suffix == ".js":
            return str(resolved)
        # bin/claude -> ../lib/node_modules/.../cli.js 이면 resolve 시 절대경로
        return str(resolved) if resolved.exists() else None
    return None


def can_claude_access_workspace(workspace_root: str) -> Tuple[bool, str]:
    """
    Claude Code CLI가 프로젝트 폴더에 접근 가능한지 검사.
    (1) CLI 실행 파일 존재 (2) workspace 디렉터리 존재·읽기·쓰기 가능 (3) 선택적으로 CLI로 짧은 명령 실행.
    Returns: (성공 여부, 실패 시 사유 메시지)
    """
    workspace_path = Path(workspace_root)
    if not workspace_path.exists():
        return False, f"워크스페이스 경로가 없음: {workspace_root}"
    if not workspace_path.is_dir():
        return False, f"워크스페이스가 디렉터리가 아님: {workspace_root}"
    if not os.access(workspace_root, os.R_OK):
        return False, f"워크스페이스 읽기 불가: {workspace_root}"
    if not os.access(workspace_root, os.W_OK):
        return False, f"워크스페이스 쓰기 불가 (Task 실행 시 파일 수정 필요): {workspace_root}"

    cli_js = _resolve_claude_cli_js()
    claude_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)
    if not cli_js and (not claude_path or not Path(claude_path).exists()):
        return False, "Claude CLI 없음: cli.js 또는 bin/claude 경로 확인 (호스트 마운트)"

    # 선택: CLI가 해당 cwd에서 실제로 실행되는지 짧게 프로브 (타임아웃 15초)
    probe_prompt = "Reply with only: OK"
    env = os.environ.copy()
    env["HOME"] = "/root"
    try:
        if cli_js:
            cmd = ["node", cli_js, "-p", probe_prompt]
        else:
            cmd = [claude_path, "-p", probe_prompt]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            cwd=workspace_root,
            env=env,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "").strip()[:200]
            return False, f"Claude CLI가 워크스페이스에서 실행되지 않음 (exit {result.returncode}): {err}"
    except subprocess.TimeoutExpired:
        return False, "Claude CLI 프로브 타임아웃 (15s)"
    except Exception as e:
        return False, f"Claude CLI 프로브 실패: {e}"

    return True, ""


def run_with_claude_cli(
    workspace_root: str,
    plan_doc: Optional[str] = None,
    plan_md_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """로컬 Claude Code CLI로 실행. plan_md_path 있으면 해당 .md 파일을 읽어 실행하라고 전달, 없으면 plan_doc 텍스트 전달."""
    cli_js = _resolve_claude_cli_js()
    if plan_md_path:
        prompt = PROMPT_BY_PLAN_PATH.format(
            workspace_root=workspace_root,
            plan_md_path=plan_md_path.strip(),
        )
    else:
        prompt = (
            f"Workspace root: {workspace_root}\n\nTask Plan:\n{plan_doc or ''}\n\n"
            "Summarize the steps to execute this plan (short summary)."
        )
    if cli_js:
        cmd = ["node", cli_js, "-p", prompt]
    else:
        claude_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)
        if not claude_path or not Path(claude_path).exists():
            return False, "Claude CLI 없음: cli.js 및 bin/claude 경로 확인 (호스트 마운트)"
        cmd = [claude_path, "-p", prompt]

    # CLI는 ~/.claude 에서 인증 읽음. Docker에서는 /root/.claude 로 마운트해 두면 동일 인증 사용
    env = os.environ.copy()
    env["HOME"] = "/root"  # 컨테이너 내 root 홈에서 .claude 찾도록
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=workspace_root if os.path.isdir(workspace_root) else None,
            env=env,
        )
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()[:500]
            stdout = (result.stdout or "").strip()[:500]
            detail = stderr or stdout or "no stderr/stdout"
            return False, f"Claude Code CLI 실패 (exit {result.returncode}): {detail}"
        summary = (result.stdout or "").strip()[:500]
        if not summary:
            return False, "Claude Code CLI 응답 없음: stdout이 비어 있습니다. 인증( claude login ), 네트워크, 타임아웃을 확인하세요."
        return True, summary
    except subprocess.TimeoutExpired:
        return False, "Claude Code CLI 타임아웃 (300초). 응답이 없습니다."
    except Exception as e:
        return False, f"Claude Code CLI 오류: {str(e)[:500]}"


def run_with_claude(
    workspace_root: str,
    plan_doc: Optional[str] = None,
    plan_md_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """로컬 Claude Code CLI만 사용. API fallback 없음."""
    if not _resolve_claude_cli_js() and not Path(os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)).exists():
        return False, "Claude CLI 없음: cli.js 또는 bin/claude 경로 확인 (호스트 마운트)"
    return run_with_claude_cli(workspace_root, plan_doc=plan_doc, plan_md_path=plan_md_path)


def run_task(db: Session, task_id: int, workspace_root: str = None) -> Tuple[bool, str]:
    """
    Task 1건 실행: Claude 접근 검사 → 조회 → in_progress → (Claude 시도) → completed/failed
    plan_md_path 있으면 해당 .md 파일 경로만 CLI에 전달, 없으면 plan_doc 텍스트 전달.
    Returns: (success, message)
    """
    workspace_root = workspace_root or str(PROJECT_ROOT)

    ok, err = can_claude_access_workspace(workspace_root)
    if not ok:
        return False, f"Claude CLI가 프로젝트 폴더에 접근할 수 없음: {err}"

    row = get_task(db, task_id)
    if not row:
        return False, f"Task id={task_id} not found"

    task_name = row[2]
    plan_doc = (row[4] or "").strip() if row[4] else ""
    # row[6] = plan_md_path (SELECT에 plan_md_path 추가됨; 컬럼 없으면 마이그레이션 필요)
    plan_md_path = (row[6] or "").strip() if len(row) > 6 and row[6] else None

    try:
        update_status(db, task_id, TaskStatus.IN_PROGRESS.value)
        ok, summary = run_with_claude(
            workspace_root,
            plan_doc=plan_doc if not plan_md_path else None,
            plan_md_path=plan_md_path or None,
        )
        if not ok:
            update_status(db, task_id, TaskStatus.FAILED.value)
            return False, summary or "Claude 실행 실패"
        update_status(db, task_id, TaskStatus.COMPLETED.value)
        return True, summary or f"Task {task_id} ({task_name[:50]}...) completed."
    except Exception as e:
        try:
            update_status(db, task_id, TaskStatus.FAILED.value)
            db.commit()
        except Exception:
            pass
        return False, str(e)
