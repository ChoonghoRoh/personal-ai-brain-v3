"""Reasoning 스트리밍 API 라우터 (Phase 10-1-1, 10-4-1 LLM 토큰 스트리밍)

SSE(Server-Sent Events)를 사용하여 Reasoning 진행 상태를 실시간으로 전송합니다.

5단계 진행 상태:
1. 질문 분석 중...
2. 관련 문서 검색 중...
3. 연관 지식 확장 중...
4. AI 추론 중... (토큰 단위 스트리밍)
5. 추천 정보 생성 중...
"""
import uuid
import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.models.database import get_db

# --- 실행 엔진 import (stream_executor.py) ---
from backend.routers.reasoning.stream_executor import (
    format_sse_event,
    execute_reasoning_with_progress,
    active_tasks,
    PROGRESS_STAGES,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reason", tags=["Reasoning Stream"])


# --- Pydantic 모델 ---

class ReasonFilters(BaseModel):  # Phase 15-3
    project_ids: Optional[List[int]] = None
    category_label_ids: Optional[List[int]] = None
    keyword_group_ids: Optional[List[int]] = None
    keyword_ids: Optional[List[int]] = None
    document_ids: Optional[List[int]] = None  # Phase 15-3


class ReasonStreamRequest(BaseModel):
    mode: str = "design_explain"
    inputs: Dict
    question: Optional[str] = None
    filters: Optional[ReasonFilters] = None
    model: Optional[str] = None


class ETAFeedbackBody(BaseModel):
    mode: Optional[str] = "design_explain"
    actual_seconds: int


# --- 엔드포인트 ---

@router.post("/stream")
async def reason_stream(request: ReasonStreamRequest, db: Session = Depends(get_db)):
    """
    Reasoning 스트리밍 실행 (SSE)

    진행 상태를 실시간으로 전송하며, 취소 기능을 지원합니다.

    이벤트 타입:
    - progress: 진행 상태 업데이트
    - result: 최종 결과
    - cancelled: 취소됨
    - error: 오류 발생
    - done: 완료
    """
    task_id = str(uuid.uuid4())

    return StreamingResponse(
        execute_reasoning_with_progress(task_id, request, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Task-ID": task_id,
        },
    )


@router.post("/{task_id}/cancel")
async def cancel_reasoning(task_id: str):
    """
    진행 중인 Reasoning 작업 취소 (Phase 10-1-2)

    Args:
        task_id: 취소할 태스크 ID

    Returns:
        취소 결과
    """
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")

    if active_tasks[task_id].get("cancelled"):
        return {"message": "이미 취소된 태스크입니다.", "task_id": task_id}

    active_tasks[task_id]["cancelled"] = True
    return {"message": "취소 요청됨", "task_id": task_id}


@router.get("/tasks")
async def list_active_tasks():
    """
    진행 중인 태스크 목록 조회

    Returns:
        활성 태스크 목록
    """
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": info.get("status"),
                "started_at": info.get("started_at"),
                "cancelled": info.get("cancelled", False),
            }
            for task_id, info in active_tasks.items()
        ],
        "count": len(active_tasks),
    }


@router.get("/eta")
async def get_estimated_time(mode: str = "design_explain"):
    """
    예상 소요 시간 조회 (Phase 10-1-3)
    """
    eta_map = {
        "design_explain": {"min": 20, "max": 45, "typical": 30},
        "risk_review": {"min": 25, "max": 50, "typical": 35},
        "next_steps": {"min": 20, "max": 40, "typical": 28},
        "history_trace": {"min": 25, "max": 55, "typical": 38},
    }

    eta = eta_map.get(mode, eta_map["design_explain"])

    return {
        "mode": mode,
        "estimated_seconds": eta,
        "display_text": f"약 {eta['min']}초 ~ {eta['max']}초",
        "typical_text": f"일반적으로 약 {eta['typical']}초",
    }


@router.post("/eta/feedback")
async def eta_feedback(body: ETAFeedbackBody):
    """
    11-5-3: 실제 소요 시간 피드백.
    향후 ETA 예측 보정에 활용할 수 있도록 로깅합니다.
    """
    logger.info(
        "ETA feedback: mode=%s actual_seconds=%s",
        body.mode or "design_explain",
        body.actual_seconds,
    )
    return {"ok": True, "mode": body.mode, "actual_seconds": body.actual_seconds}
