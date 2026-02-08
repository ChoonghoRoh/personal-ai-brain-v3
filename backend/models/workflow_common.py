"""
workflow 관련 테이블(phases, plans, tasks, test_results) 공통 컬럼명·상태값 정의.
DDL·raw SQL·향후 ORM에서 공통으로 사용.
"""
from enum import Enum
from typing import Final

# ---------------------------------------------------------------------------
# 공통 컬럼명 (DDL·SQL 문자열에서 재사용)
# ---------------------------------------------------------------------------
COL_ID: Final[str] = "id"
COL_STATUS: Final[str] = "status"
COL_CREATED_AT: Final[str] = "created_at"
COL_COMPLETED_AT: Final[str] = "completed_at"
COL_PHASE_ID: Final[str] = "phase_id"
COL_TASK_ID: Final[str] = "task_id"

# 테이블명
TABLE_PHASES: Final[str] = "workflow_phases"
TABLE_PLANS: Final[str] = "workflow_plans"
TABLE_TASKS: Final[str] = "workflow_tasks"
TABLE_TEST_RESULTS: Final[str] = "workflow_test_results"
TABLE_APPROVALS: Final[str] = "workflow_approvals"


# ---------------------------------------------------------------------------
# Phase 상태
# ---------------------------------------------------------------------------
class PhaseStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ---------------------------------------------------------------------------
# Plan 상태
# ---------------------------------------------------------------------------
class PlanStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


# ---------------------------------------------------------------------------
# Task 상태 (Task Execution 8-2-7에서 사용)
# ---------------------------------------------------------------------------
class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Test Result 상태
# ---------------------------------------------------------------------------
class TestResultStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# 공통 DDL 조각 (신규 workflow 테이블 생성 시 참고용, 실행용 아님)
# ---------------------------------------------------------------------------
COMMON_COLUMNS_DDL = """
-- 공통 패턴 (테이블별로 컬럼명·default 조정)
id          SERIAL PRIMARY KEY,
status      VARCHAR(20) DEFAULT 'pending',
created_at  TIMESTAMP DEFAULT NOW(),
completed_at TIMESTAMP
"""


def task_status_completed_or_failed(status: str) -> bool:
    """Task가 완료(completed) 또는 실패(failed) 상태인지 여부."""
    return status in (TaskStatus.COMPLETED.value, TaskStatus.FAILED.value)
