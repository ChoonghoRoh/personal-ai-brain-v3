"""Claude Code CLI 기반 Task Plan 생성기 - 프로젝트 코드 분석 후 구체적인 Task Plan 작성"""
import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from backend.config import PROJECT_ROOT
from backend.services.automation.project_analyzer import (
    find_related_files,
    collect_file_context,
    extract_keywords_from_task,
    get_project_structure,
)

logger = logging.getLogger(__name__)

# Claude Code CLI 경로
DEFAULT_CLAUDE_CLI_PATH = "/host-npm-global/bin/claude"
DEFAULT_CLAUDE_CLI_JS = "/host-npm-global/lib/node_modules/@anthropic-ai/claude-code/cli.js"


# Task Plan 생성 프롬프트 템플릿
TASK_PLAN_PROMPT = """당신은 시니어 소프트웨어 개발자입니다. 아래 정보를 바탕으로 구체적인 Task Plan을 작성하세요.

## Task 정보
- Task 번호: {task_num}
- Task 제목: {task_title}
- Phase: {phase_slug}

## 프로젝트 구조
{project_structure}

## 관련 파일 컨텍스트
{file_context}

## 작성 지침
1. 실제 코드를 분석하여 구체적인 구현 계획을 작성하세요
2. 수정/생성해야 할 파일 경로를 명시하세요
3. 각 단계별 상세 구현 내용을 포함하세요
4. 기존 코드 패턴과 일관성을 유지하세요

## 출력 형식
아래 마크다운 형식으로 작성:

# Task Plan: {task_title}

## 목표
(이 Task가 달성해야 할 목표를 1-2문장으로 설명)

## 관련 파일
(분석한 파일 목록과 각 파일의 역할)

## 구현 단계
1. **단계 1**: (구체적인 작업 내용)
   - 파일: (수정할 파일 경로)
   - 작업: (상세 작업 내용)

2. **단계 2**: ...

## 완료 기준
- (체크리스트 형태로 작성)

## 주의사항
- (기존 코드와의 호환성, 테스트 필요 항목 등)
"""


def _resolve_claude_cli_js() -> Optional[str]:
    """Claude CLI cli.js 경로 반환. 없으면 None."""
    default_js = os.environ.get("CLAUDE_CLI_JS", DEFAULT_CLAUDE_CLI_JS)
    if Path(default_js).exists():
        return default_js
    bin_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)
    p = Path(bin_path)
    if p.exists() and p.is_symlink():
        resolved = p.resolve()
        if resolved.suffix == ".js":
            return str(resolved)
        return str(resolved) if resolved.exists() else None
    return None


def _check_claude_cli_available() -> Tuple[bool, str]:
    """
    Claude Code CLI 사용 가능 여부 확인.
    Returns: (사용 가능 여부, 오류 메시지)
    """
    cli_js = _resolve_claude_cli_js()
    claude_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)

    if not cli_js and (not claude_path or not Path(claude_path).exists()):
        return False, "Claude Code CLI가 설치되어 있지 않습니다. (cli.js 또는 bin/claude 경로 확인)"

    # CLI 실행 테스트 (토큰 확인)
    env = os.environ.copy()
    env["HOME"] = "/root"

    try:
        if cli_js:
            cmd = ["node", cli_js, "-p", "Reply with only: OK"]
        else:
            cmd = [claude_path, "-p", "Reply with only: OK"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
        )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            # 토큰/인증 관련 오류 체크
            if "auth" in stderr.lower() or "token" in stderr.lower() or "login" in stderr.lower() or "unauthorized" in stderr.lower():
                return False, "Claude Code 인증 토큰이 없습니다. 'claude login' 명령으로 인증해주세요."
            return False, f"Claude Code CLI 오류: {stderr[:200]}"

        return True, ""

    except subprocess.TimeoutExpired:
        return False, "Claude Code CLI 응답 타임아웃 (15초)"
    except FileNotFoundError:
        return False, "Claude Code CLI를 찾을 수 없습니다. Node.js가 설치되어 있는지 확인해주세요."
    except Exception as e:
        return False, f"Claude Code CLI 확인 실패: {str(e)}"


def _run_claude_cli(prompt: str, workspace_root: str, timeout: int = 300) -> Tuple[bool, str]:
    """
    Claude Code CLI로 프롬프트 실행.
    Returns: (성공 여부, 응답 텍스트 또는 오류 메시지)
    """
    cli_js = _resolve_claude_cli_js()
    claude_path = os.environ.get("CLAUDE_CLI_PATH", DEFAULT_CLAUDE_CLI_PATH)

    if cli_js:
        cmd = ["node", cli_js, "-p", prompt]
    else:
        cmd = [claude_path, "-p", prompt]

    env = os.environ.copy()
    env["HOME"] = "/root"

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=workspace_root if os.path.isdir(workspace_root) else None,
            env=env,
        )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()[:500]
            stdout = (result.stdout or "").strip()[:500]
            detail = stderr or stdout or "no output"
            return False, f"Claude Code CLI 실행 실패 (exit {result.returncode}): {detail}"

        output = (result.stdout or "").strip()
        if not output:
            return False, "Claude Code CLI 응답 없음: stdout이 비어 있습니다. 인증( claude login ), 네트워크, 타임아웃을 확인하세요."
        return True, output

    except subprocess.TimeoutExpired:
        return False, f"Claude Code CLI 타임아웃 ({timeout}초). 응답이 없습니다."
    except Exception as e:
        return False, f"Claude Code CLI 오류: {str(e)[:500]}"


def generate_task_plan(
    task_num: str,
    task_title: str,
    phase_slug: str,
    context_hint: Optional[str] = None,
    workspace_root: Optional[str] = None,
    max_related_files: int = 10,
) -> Dict:
    """
    프로젝트 코드를 분석하고 Claude Code CLI로 Task Plan 생성.

    Args:
        task_num: Task 번호 (예: "8-2-7")
        task_title: Task 제목
        phase_slug: Phase 식별자 (예: "phase-8-2")
        context_hint: 추가 컨텍스트 힌트
        workspace_root: 프로젝트 루트 경로
        max_related_files: 분석할 최대 파일 수

    Returns:
        {
            task_plan: str,
            analyzed_files: List[str],
            success: bool,
            error: Optional[str]
        }
    """
    workspace = workspace_root or str(PROJECT_ROOT)

    # 1. Claude Code CLI 사용 가능 여부 확인
    cli_available, cli_error = _check_claude_cli_available()
    if not cli_available:
        logger.warning(f"Claude Code CLI 사용 불가: {cli_error}")
        return {
            "task_plan": "",
            "analyzed_files": [],
            "success": False,
            "error": cli_error,
        }

    try:
        # 2. 키워드 추출
        keywords = extract_keywords_from_task(task_title, context_hint or "")
        logger.info(f"추출된 키워드: {keywords}")

        # 3. 관련 파일 찾기
        related_files = find_related_files(
            keywords=keywords,
            context_hint=context_hint,
            workspace_root=workspace,
            max_files=max_related_files * 2
        )
        logger.info(f"관련 파일 {len(related_files)}개 발견")

        # 4. 프로젝트 구조 수집
        structure = get_project_structure(workspace_root=workspace, max_depth=2)
        structure_text = _format_project_structure(structure)

        # 5. 파일 컨텍스트 수집 (상위 파일만)
        top_files = [f["path"] for f in related_files[:max_related_files]]
        context = collect_file_context(
            file_paths=top_files,
            workspace_root=workspace,
            max_content_per_file=3000,
            max_total_content=20000
        )
        context_text = _format_file_context(context)

        # 6. Task Plan 생성 프롬프트 구성
        task_plan_prompt = TASK_PLAN_PROMPT.format(
            task_num=task_num,
            task_title=task_title,
            phase_slug=phase_slug,
            project_structure=structure_text,
            file_context=context_text,
        )

        # 7. Claude Code CLI로 Task Plan 생성
        logger.info(f"Claude Code CLI로 Task Plan 생성 중: {task_num}")
        success, task_plan = _run_claude_cli(task_plan_prompt, workspace, timeout=300)

        if not success:
            logger.error(f"Task Plan 생성 실패: {task_plan}")
            return {
                "task_plan": "",
                "analyzed_files": top_files,
                "success": False,
                "error": task_plan,
            }

        return {
            "task_plan": task_plan.strip(),
            "analyzed_files": top_files,
            "success": True,
            "error": None,
        }

    except Exception as e:
        logger.exception(f"Task Plan 생성 실패: {e}")
        return {
            "task_plan": "",
            "analyzed_files": [],
            "success": False,
            "error": str(e),
        }


def _format_project_structure(structure: Dict) -> str:
    """프로젝트 구조를 텍스트로 포맷"""
    lines = ["### 디렉터리"]
    for d in structure.get("directories", [])[:20]:
        lines.append(f"- {d}")

    lines.append("\n### 주요 파일")
    for f in structure.get("key_files", []):
        lines.append(f"- {f}")

    return "\n".join(lines)


def _format_file_context(context: Dict) -> str:
    """파일 컨텍스트를 텍스트로 포맷"""
    lines = []
    for fc in context.get("files", []):
        path = fc["path"]
        content = fc["content"]
        truncated = " (일부)" if fc.get("truncated") else ""
        lines.append(f"### {path}{truncated}")
        lines.append("```")
        lines.append(content[:2000] if len(content) > 2000 else content)
        lines.append("```\n")

    if not lines:
        return "(관련 파일 없음)"

    return "\n".join(lines)


