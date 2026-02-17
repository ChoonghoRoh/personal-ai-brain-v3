"""AI 자동화 워크플로우 상태 관리 서비스 (Phase 15-2-1)

태스크 상태를 메모리에 저장하고 SSE 이벤트 포맷을 제공합니다.
reason_stream.py의 active_tasks 패턴을 참조합니다.
"""
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# 진행 중인 태스크 메모리 저장소 (서버 재시작 시 초기화됨)
active_tasks: Dict[str, "TaskState"] = {}


class TaskState:
    """AI 워크플로우 태스크 상태"""

    def __init__(
        self,
        task_id: str,
        document_ids: List[int],
        auto_approve: bool = False,
    ):
        self.task_id = task_id
        self.document_ids = document_ids
        self.auto_approve = auto_approve

        # 상태
        self.status = "running"  # running, completed, failed, cancelled
        self.progress_pct = 0
        self.current_stage = ""
        self.stages: List[Dict[str, Any]] = []

        # 시간
        self.created_at = datetime.utcnow()
        self.started_at = time.time()
        self.completed_at: Optional[datetime] = None

        # 취소 플래그
        self.cancelled = False

        # 세부 진행률 (Phase 16-1-1)
        self.detail: Optional[Dict[str, Any]] = None
        self.eta_seconds: Optional[float] = None

        # 문서별 완료 결과 (Phase 16-3-1: doc_result SSE)
        self.doc_results: List[Dict[str, Any]] = []
        self.last_doc_result_index = 0  # SSE 전송 추적용

        # 결과
        self.results: Dict[str, Any] = {}
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            "task_id": self.task_id,
            "document_ids": self.document_ids,
            "auto_approve": self.auto_approve,
            "status": self.status,
            "progress_pct": self.progress_pct,
            "current_stage": self.current_stage,
            "stages": self.stages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "elapsed_time": round(time.time() - self.started_at, 1),
            "cancelled": self.cancelled,
            "detail": self.detail,
            "eta_seconds": self.eta_seconds,
            "doc_results": self.doc_results,
            "results": self.results,
            "error": self.error,
        }


def create_task(document_ids: List[int], auto_approve: bool = False) -> str:
    """새 태스크 생성

    Args:
        document_ids: 처리할 문서 ID 목록
        auto_approve: 자동 승인 여부

    Returns:
        생성된 태스크 ID
    """
    task_id = str(uuid.uuid4())
    task_state = TaskState(
        task_id=task_id,
        document_ids=document_ids,
        auto_approve=auto_approve,
    )
    active_tasks[task_id] = task_state
    logger.info(
        "AI 워크플로우 태스크 생성: task_id=%s document_ids=%s auto_approve=%s",
        task_id,
        document_ids,
        auto_approve,
    )
    return task_id


def update_progress(
    task_id: str,
    stage_name: str,
    progress_pct: int,
    message: Optional[str] = None,
    detail: Optional[Dict[str, Any]] = None,
    eta_seconds: Optional[float] = None,
) -> None:
    """태스크 진행 상황 업데이트

    Args:
        task_id: 태스크 ID
        stage_name: 현재 단계 이름
        progress_pct: 진행률 (0-100)
        message: 추가 메시지
        detail: 세부 진행률 (current, total, item_name 등)
        eta_seconds: 예상 잔여 시간 (초)
    """
    if task_id not in active_tasks:
        logger.warning("존재하지 않는 태스크: %s", task_id)
        return

    task = active_tasks[task_id]
    task.current_stage = stage_name
    task.progress_pct = progress_pct
    task.detail = detail
    task.eta_seconds = eta_seconds

    # 단계 기록 추가
    stage_record: Dict[str, Any] = {
        "name": stage_name,
        "progress": progress_pct,
        "message": message or stage_name,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if detail is not None:
        stage_record["detail"] = detail
    if eta_seconds is not None:
        stage_record["eta_seconds"] = eta_seconds
    task.stages.append(stage_record)

    logger.debug(
        "태스크 진행 업데이트: task_id=%s stage=%s progress=%d%%",
        task_id,
        stage_name,
        progress_pct,
    )


def add_doc_result(
    task_id: str,
    document_ids: List[int],
    batch_index: int,
    batch_stats: Dict[str, Any],
) -> None:
    """배치 완료 시 문서별 결과 기록 (Phase 16-3-1)

    Args:
        task_id: 태스크 ID
        document_ids: 완료된 문서 ID 목록
        batch_index: 배치 번호 (0-based)
        batch_stats: 배치 통계 (chunks_created, keywords 등)
    """
    if task_id not in active_tasks:
        return

    task = active_tasks[task_id]
    task.doc_results.append({
        "document_ids": document_ids,
        "batch_index": batch_index,
        "stats": batch_stats,
        "timestamp": datetime.utcnow().isoformat(),
    })

    logger.debug(
        "doc_result 추가: task_id=%s batch=%d docs=%d",
        task_id, batch_index, len(document_ids),
    )


def complete_task(
    task_id: str,
    results: Dict[str, Any],
) -> None:
    """태스크 완료 처리

    Args:
        task_id: 태스크 ID
        results: 실행 결과
    """
    if task_id not in active_tasks:
        logger.warning("존재하지 않는 태스크: %s", task_id)
        return

    task = active_tasks[task_id]
    task.status = "completed"
    task.progress_pct = 100
    task.completed_at = datetime.utcnow()
    task.results = results

    logger.info(
        "태스크 완료: task_id=%s elapsed=%.1fs",
        task_id,
        time.time() - task.started_at,
    )


def fail_task(
    task_id: str,
    error: str,
    failed_stage: Optional[str] = None,
) -> None:
    """태스크 실패 처리

    Args:
        task_id: 태스크 ID
        error: 에러 메시지
        failed_stage: 실패한 단계 이름
    """
    if task_id not in active_tasks:
        logger.warning("존재하지 않는 태스크: %s", task_id)
        return

    task = active_tasks[task_id]
    task.status = "failed"
    task.error = error
    task.completed_at = datetime.utcnow()

    if failed_stage:
        task.current_stage = f"{failed_stage} (실패)"

    logger.error(
        "태스크 실패: task_id=%s stage=%s error=%s",
        task_id,
        failed_stage,
        error,
    )


def cancel_task(task_id: str) -> bool:
    """태스크 취소 플래그 설정

    Args:
        task_id: 태스크 ID

    Returns:
        취소 성공 여부
    """
    if task_id not in active_tasks:
        logger.warning("존재하지 않는 태스크: %s", task_id)
        return False

    task = active_tasks[task_id]

    if task.status != "running":
        logger.warning("실행 중이 아닌 태스크는 취소할 수 없음: %s (status=%s)", task_id, task.status)
        return False

    task.cancelled = True
    task.status = "cancelled"
    task.completed_at = datetime.utcnow()

    logger.info("태스크 취소 요청: task_id=%s", task_id)
    return True


def is_cancelled(task_id: str) -> bool:
    """태스크 취소 여부 확인

    Args:
        task_id: 태스크 ID

    Returns:
        취소 여부
    """
    if task_id not in active_tasks:
        return False

    return active_tasks[task_id].cancelled


def get_task(task_id: str) -> Optional[TaskState]:
    """태스크 상태 조회

    Args:
        task_id: 태스크 ID

    Returns:
        TaskState 또는 None
    """
    return active_tasks.get(task_id)


def list_tasks(limit: int = 50) -> List[Dict[str, Any]]:
    """태스크 목록 조회 (최근 생성 순)

    Args:
        limit: 최대 개수

    Returns:
        태스크 목록
    """
    tasks = sorted(
        active_tasks.values(),
        key=lambda t: t.created_at,
        reverse=True,
    )
    return [task.to_dict() for task in tasks[:limit]]


def cleanup_old_tasks(max_age_seconds: int = 3600) -> int:
    """오래된 완료/실패 태스크 정리

    Args:
        max_age_seconds: 최대 보관 시간 (초)

    Returns:
        정리된 태스크 수
    """
    now = time.time()
    to_remove = []

    for task_id, task in active_tasks.items():
        if task.status in ("completed", "failed", "cancelled"):
            age = now - task.started_at
            if age > max_age_seconds:
                to_remove.append(task_id)

    for task_id in to_remove:
        del active_tasks[task_id]

    if to_remove:
        logger.info("오래된 태스크 %d개 정리됨", len(to_remove))

    return len(to_remove)


def format_sse_event(event_type: str, data: dict) -> str:
    """SSE 형식으로 이벤트 포맷팅

    Args:
        event_type: 이벤트 타입 (progress, result, error, done, cancelled)
        data: 이벤트 데이터

    Returns:
        SSE 형식 문자열
    """
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
