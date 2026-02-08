#!/usr/bin/env python3
"""Phase 8-2-6 테스트용: workflow_phases 1건 + workflow_tasks 2건 INSERT"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.models.database import get_db

PHASE_NAME = "Phase-8-Test"
TASKS = [
    {
        "task_name": "테스트 Task 1: README.md 존재 확인",
        "plan_doc": """# Task Plan: 테스트 Task 1: README.md 존재 확인

## 목표
README.md 존재 여부를 확인한다.

## 단계
1. 프로젝트 루트에서 README.md 파일 확인
2. 없으면 생성, 있으면 통과
3. 완료 기준 충족 확인

## 완료 기준
- README.md 파일이 존재함
""",
        "test_plan_doc": """# Test Plan: 테스트 Task 1

## 테스트 시나리오
- README.md 파일 존재 여부 확인

## 예상 결과
- README.md가 프로젝트 루트에 존재함
""",
    },
    {
        "task_name": "테스트 Task 2: docs/phases/tasks 폴더 생성",
        "plan_doc": """# Task Plan: 테스트 Task 2: docs/phases/tasks 폴더 생성

## 목표
docs/phases/tasks 폴더를 생성한다.

## 단계
1. docs/phases/tasks 경로 확인
2. 없으면 mkdir -p로 생성
3. 완료 기준 충족 확인

## 완료 기준
- docs/phases/tasks 디렉토리가 존재함
""",
        "test_plan_doc": """# Test Plan: 테스트 Task 2

## 테스트 시나리오
- docs/phases/tasks 디렉토리 존재 여부 확인

## 예상 결과
- docs/phases/tasks 폴더가 생성됨
""",
    },
]


def insert_test_tasks():
    """테스트용 phase 1건 + task 2건 INSERT"""
    db = next(get_db())
    try:
        # phase 조회 또는 생성
        phase_result = db.execute(
            text("SELECT id FROM workflow_phases WHERE phase_name = :name"),
            {"name": PHASE_NAME},
        )
        phase_row = phase_result.fetchone()
        if phase_row:
            phase_id = phase_row[0]
            print(f"✅ 기존 Phase 사용: {PHASE_NAME} (id={phase_id})")
        else:
            result = db.execute(
                text("""
                    INSERT INTO workflow_phases (phase_name, status, created_at)
                    VALUES (:name, 'draft', NOW())
                    RETURNING id
                """),
                {"name": PHASE_NAME},
            )
            phase_id = result.fetchone()[0]
            print(f"✅ Phase 생성: {PHASE_NAME} (id={phase_id})")

        # task 2건 INSERT
        for i, t in enumerate(TASKS, 1):
            db.execute(
                text("""
                    INSERT INTO workflow_tasks
                    (phase_id, task_name, status, plan_doc, test_plan_doc, created_at)
                    VALUES (:phase_id, :task_name, 'pending', :plan_doc, :test_plan_doc, NOW())
                """),
                {
                    "phase_id": phase_id,
                    "task_name": t["task_name"],
                    "plan_doc": t["plan_doc"],
                    "test_plan_doc": t["test_plan_doc"],
                },
            )
            print(f"✅ Task {i} INSERT: {t['task_name'][:50]}...")

        db.commit()
        print("✅ PostgreSQL 저장 완료. SELECT * FROM workflow_tasks 로 확인하세요.")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = insert_test_tasks()
    sys.exit(0 if success else 1)
