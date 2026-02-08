#!/usr/bin/env python3
"""
Phase 8-2-7: Task Plan 실행 스크립트 (n8n CMD_RunTaskExecution 호출용)

사용: python scripts/n8n/run_task_execution.py --task-id <id>
- workflow_tasks에서 해당 task 조회 → status 갱신만 수행 (Claude API 사용 삭제됨)
- 실제 Task 실행은 Backend POST /api/workflow/run-task (Claude Code CLI) 사용 권장
"""
import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import get_db


def get_task(db, task_id: int):
    """workflow_tasks에서 task_id 조회"""
    r = db.execute(
        text("SELECT id, phase_id, task_name, status, plan_doc, test_plan_doc FROM workflow_tasks WHERE id = :id"),
        {"id": task_id},
    )
    return r.fetchone()


def update_status(db, task_id: int, status: str):
    """workflow_tasks.status 갱신"""
    db.execute(
        text("UPDATE workflow_tasks SET status = :status, completed_at = NOW() WHERE id = :id"),
        {"status": status, "id": task_id},
    )
    db.commit()


def main():
    parser = argparse.ArgumentParser(description="Run task execution for workflow_tasks (status only)")
    parser.add_argument("--task-id", type=int, required=True, help="workflow_tasks.id")
    parser.add_argument("--workspace-root", type=str, default=None, help="Unused (kept for compat)")
    args = parser.parse_args()

    task_id = args.task_id

    db = next(get_db())
    try:
        row = get_task(db, task_id)
        if not row:
            print(f"Task id={task_id} not found", file=sys.stderr)
            sys.exit(1)

        task_name = row[2]

        update_status(db, task_id, "in_progress")
        update_status(db, task_id, "completed")
        print(f"Task {task_id} ({task_name[:50]}...) status updated to completed (run-task via Backend for CLI execution).")
        sys.exit(0)

    except Exception as e:
        try:
            update_status(db, task_id, "failed")
            db.commit()
        except Exception:
            pass
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
