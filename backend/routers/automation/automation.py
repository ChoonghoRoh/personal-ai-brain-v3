"""자동화 API 라우터 (Phase 15-2-1 확장)"""
import asyncio
import logging
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Any, List, Dict, Optional, AsyncGenerator
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.automation.automation_service import get_automation_service
from backend.services.automation import ai_workflow_state
from backend.services.automation.ai_workflow_service import get_ai_workflow_service
from backend.middleware.auth import require_admin_knowledge, UserInfo

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/automation", tags=["Automation"])


class AutoLabelRequest(BaseModel):
    chunk_ids: Optional[List[int]] = None
    min_confidence: float = 0.7


class BatchAutoLabelRequest(BaseModel):
    batch_size: int = 100
    min_confidence: float = 0.7


# ============================================
# Phase 15-2-1: AI 워크플로우 API
# ============================================


class RunFullWorkflowRequest(BaseModel):
    """전체 워크플로우 실행 요청"""
    document_ids: List[int]
    auto_approve: bool = False


class RunFullWorkflowResponse(BaseModel):
    """전체 워크플로우 실행 응답"""
    task_id: str
    message: str


class ApprovePendingRequest(BaseModel):
    """대기 항목 승인 요청"""
    task_id: Optional[str] = None
    chunk_ids: Optional[List[int]] = None


class ApprovePendingResponse(BaseModel):
    """대기 항목 승인 응답"""
    approved_chunks: int
    approved_labels: int
    message: str


@router.post("/labels/auto")
async def auto_label(
    request: AutoLabelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """청크 자동 라벨링"""
    service = get_automation_service()
    
    result = service.auto_label_chunks(
        db=db,
        chunk_ids=request.chunk_ids,
        min_confidence=request.min_confidence
    )
    
    return {
        "message": f"{result['labeled_count']}개의 라벨이 추가되었습니다.",
        "labeled_count": result["labeled_count"],
        "processed_chunks": result["processed_chunks"]
    }


@router.post("/labels/batch-auto")
async def batch_auto_label(
    request: BatchAutoLabelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """배치 자동 라벨링"""
    service = get_automation_service()
    
    result = service.batch_auto_label(
        db=db,
        batch_size=request.batch_size,
        min_confidence=request.min_confidence
    )
    
    return {
        "message": f"{result['labeled']}개의 라벨이 추가되었습니다.",
        "processed": result["processed"],
        "labeled": result["labeled"]
    }


@router.get("/relations/auto-suggest/{chunk_id}")
async def auto_suggest_relations(
    chunk_id: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """자동 관계 추론"""
    service = get_automation_service()

    suggestions = service.auto_suggest_relations(
        db=db,
        chunk_id=chunk_id,
        limit=limit
    )

    return {
        "chunk_id": chunk_id,
        "suggestions": suggestions
    }


# ============================================
# Phase 15-2-1: AI 워크플로우 엔드포인트
# ============================================


def _execute_workflow_background(task_id: str) -> None:
    """백그라운드에서 워크플로우 실행

    Args:
        task_id: 태스크 ID
    """
    from backend.models.database import SessionLocal

    db = SessionLocal()
    try:
        workflow_service = get_ai_workflow_service()
        workflow_service.execute_workflow(task_id, db)
    except Exception as e:
        logger.exception("워크플로우 백그라운드 실행 실패: task_id=%s", task_id)
        ai_workflow_state.fail_task(
            task_id=task_id,
            error=str(e),
            failed_stage="백그라운드 실행",
        )
    finally:
        db.close()


@router.post("/run-full", response_model=RunFullWorkflowResponse)
async def run_full_workflow(
    request: RunFullWorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge),
):
    """전체 AI 워크플로우 실행 (Phase 15-2-1)

    문서 선택부터 임베딩까지 6단계 자동화 파이프라인을 실행합니다.

    Args:
        request: 실행 요청 (document_ids, auto_approve)
        background_tasks: FastAPI BackgroundTasks
        db: DB 세션
        user: 인증된 사용자 (admin_knowledge 권한 필요)

    Returns:
        task_id와 메시지
    """
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="document_ids가 비어 있습니다.")

    # 태스크 생성
    task_id = ai_workflow_state.create_task(
        document_ids=request.document_ids,
        auto_approve=request.auto_approve,
    )

    # 백그라운드에서 워크플로우 실행
    background_tasks.add_task(_execute_workflow_background, task_id)

    logger.info(
        "AI 워크플로우 실행 요청: task_id=%s documents=%d auto_approve=%s user=%s",
        task_id,
        len(request.document_ids),
        request.auto_approve,
        user.username,
    )

    return RunFullWorkflowResponse(
        task_id=task_id,
        message=f"AI 워크플로우가 시작되었습니다. (문서 {len(request.document_ids)}개)",
    )


async def stream_progress(task_id: str) -> AsyncGenerator[str, None]:
    """SSE 진행 상황 스트리밍 (Phase 15-2-1)

    Args:
        task_id: 태스크 ID

    Yields:
        SSE 형식 이벤트
    """
    task = ai_workflow_state.get_task(task_id)
    if not task:
        yield ai_workflow_state.format_sse_event("error", {"message": "태스크를 찾을 수 없습니다."})
        return

    last_stage_count = 0
    heartbeat_counter = 0

    while True:
        task = ai_workflow_state.get_task(task_id)
        if not task:
            yield ai_workflow_state.format_sse_event("error", {"message": "태스크가 삭제되었습니다."})
            return

        # 새로운 단계 업데이트가 있으면 전송
        if len(task.stages) > last_stage_count:
            for stage in task.stages[last_stage_count:]:
                event_data: Dict[str, Any] = {
                    "task_id": task_id,
                    "stage_name": stage["name"],
                    "progress_pct": stage["progress"],
                    "message": stage["message"],
                    "status": task.status,
                    "detail": stage.get("detail"),
                    "eta_seconds": stage.get("eta_seconds"),
                }
                yield ai_workflow_state.format_sse_event("progress", event_data)
            last_stage_count = len(task.stages)

        # doc_result 이벤트 전송 (Phase 16-3-1: 배치 완료 시 문서별 결과)
        if len(task.doc_results) > task.last_doc_result_index:
            for dr in task.doc_results[task.last_doc_result_index:]:
                yield ai_workflow_state.format_sse_event("doc_result", {
                    "task_id": task_id,
                    "document_ids": dr["document_ids"],
                    "batch_index": dr["batch_index"],
                    "stats": dr["stats"],
                })
            task.last_doc_result_index = len(task.doc_results)

        # 완료/실패/취소 시 종료
        if task.status == "completed":
            yield ai_workflow_state.format_sse_event("result", {
                "task_id": task_id,
                "status": "completed",
                "results": task.results,
                "elapsed_time": round(time.time() - task.started_at, 1),
            })
            yield ai_workflow_state.format_sse_event("done", {"task_id": task_id})
            return

        if task.status == "failed":
            yield ai_workflow_state.format_sse_event("error", {
                "task_id": task_id,
                "message": task.error or "알 수 없는 오류",
                "status": "failed",
            })
            yield ai_workflow_state.format_sse_event("done", {"task_id": task_id})
            return

        if task.status == "cancelled":
            yield ai_workflow_state.format_sse_event("cancelled", {
                "task_id": task_id,
                "message": "사용자에 의해 취소됨",
            })
            yield ai_workflow_state.format_sse_event("done", {"task_id": task_id})
            return

        # Heartbeat 발행 (매 10회 폴링 ≈ 5초 간격)
        heartbeat_counter += 1
        if heartbeat_counter >= 10:
            heartbeat_counter = 0
            yield ai_workflow_state.format_sse_event("heartbeat", {
                "type": "heartbeat",
                "timestamp": time.time(),
            })

        # 0.5초 대기 후 다음 체크
        await asyncio.sleep(0.5)


@router.get("/progress/{task_id}")
async def get_progress(
    task_id: str,
):
    """SSE 진행 상황 스트리밍 (Phase 15-2-1)

    EventSource는 커스텀 HTTP 헤더를 지원하지 않으므로 인증 제외.
    기존 reason_stream.py SSE 패턴과 동일.

    Args:
        task_id: 태스크 ID

    Returns:
        StreamingResponse (SSE)
    """
    task = ai_workflow_state.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")

    return StreamingResponse(
        stream_progress(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Task-ID": task_id,
        },
    )


@router.post("/cancel/{task_id}")
async def cancel_workflow(
    task_id: str,
    user: UserInfo = Depends(require_admin_knowledge),
):
    """AI 워크플로우 취소 (Phase 15-2-1)

    Args:
        task_id: 취소할 태스크 ID
        user: 인증된 사용자 (admin_knowledge 권한 필요)

    Returns:
        취소 결과
    """
    success = ai_workflow_state.cancel_task(task_id)

    if not success:
        task = ai_workflow_state.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")

        return {
            "message": f"취소할 수 없습니다. 현재 상태: {task.status}",
            "task_id": task_id,
            "status": task.status,
        }

    logger.info("AI 워크플로우 취소: task_id=%s user=%s", task_id, user.username)

    return {
        "message": "취소 요청됨",
        "task_id": task_id,
        "status": "cancelled",
    }


@router.get("/tasks")
async def list_tasks(
    limit: int = 50,
    user: UserInfo = Depends(require_admin_knowledge),
):
    """태스크 목록 조회 (Phase 15-2-1)

    Args:
        limit: 최대 개수
        user: 인증된 사용자 (admin_knowledge 권한 필요)

    Returns:
        태스크 목록
    """
    tasks = ai_workflow_state.list_tasks(limit=limit)

    return {
        "tasks": tasks,
        "count": len(tasks),
    }


@router.post("/approve-pending", response_model=ApprovePendingResponse)
async def approve_pending(
    request: ApprovePendingRequest,
    db: Session = Depends(get_db),
    user: UserInfo = Depends(require_admin_knowledge),
):
    """대기 항목 승인 (Phase 15-2-1)

    task_id 또는 chunk_ids로 draft 청크와 suggested 라벨을 일괄 승인합니다.

    Args:
        request: 승인 요청 (task_id 또는 chunk_ids)
        db: DB 세션
        user: 인증된 사용자 (admin_knowledge 권한 필요)

    Returns:
        승인된 청크 및 라벨 수
    """
    from backend.models.models import KnowledgeChunk, KnowledgeLabel
    from datetime import datetime

    chunk_ids_to_approve = []

    # task_id로 청크 수집
    if request.task_id:
        task = ai_workflow_state.get_task(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")

        # 해당 태스크에서 생성된 draft 청크 찾기 (results에서 chunk_ids 가져오기)
        if "chunk_ids" in task.results:
            chunk_ids_to_approve = task.results["chunk_ids"]
        else:
            # 폴백: task의 document_ids로 draft 청크 조회
            chunks = (
                db.query(KnowledgeChunk)
                .filter(
                    KnowledgeChunk.document_id.in_(task.document_ids),
                    KnowledgeChunk.status == "draft",
                )
                .all()
            )
            chunk_ids_to_approve = [c.id for c in chunks]

    # chunk_ids로 직접 지정
    elif request.chunk_ids:
        chunk_ids_to_approve = request.chunk_ids
    else:
        raise HTTPException(status_code=400, detail="task_id 또는 chunk_ids 중 하나를 제공해야 합니다.")

    if not chunk_ids_to_approve:
        return ApprovePendingResponse(
            approved_chunks=0,
            approved_labels=0,
            message="승인할 항목이 없습니다.",
        )

    # 청크 승인
    chunks = (
        db.query(KnowledgeChunk)
        .filter(
            KnowledgeChunk.id.in_(chunk_ids_to_approve),
            KnowledgeChunk.status == "draft",
        )
        .all()
    )

    approved_chunks = 0
    for chunk in chunks:
        chunk.status = "approved"
        chunk.approved_at = datetime.utcnow()
        chunk.approved_by = user.username
        approved_chunks += 1

    # 라벨 승인
    labels = (
        db.query(KnowledgeLabel)
        .filter(
            KnowledgeLabel.chunk_id.in_(chunk_ids_to_approve),
            KnowledgeLabel.status == "suggested",
        )
        .all()
    )

    approved_labels = 0
    for label in labels:
        label.status = "confirmed"
        approved_labels += 1

    db.commit()

    logger.info(
        "대기 항목 승인: chunks=%d labels=%d user=%s",
        approved_chunks,
        approved_labels,
        user.username,
    )

    return ApprovePendingResponse(
        approved_chunks=approved_chunks,
        approved_labels=approved_labels,
        message=f"청크 {approved_chunks}개, 라벨 {approved_labels}개 승인됨",
    )
