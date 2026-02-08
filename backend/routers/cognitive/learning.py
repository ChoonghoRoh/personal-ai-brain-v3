"""학습 및 적응 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.cognitive.learning_service import get_learning_service

router = APIRouter(prefix="/api/learning", tags=["learning"])


class FeedbackRequest(BaseModel):
    feedback_type: str  # label, relation, answer, etc.
    item_id: int
    rating: float  # 0.0 - 1.0
    comment: Optional[str] = None


@router.get("/patterns")
async def get_user_patterns(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """사용자 패턴 조회"""
    service = get_learning_service()
    patterns = service.learn_user_patterns(db, days=days)
    return patterns


@router.post("/feedback")
async def record_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """피드백 기록"""
    service = get_learning_service()
    feedback = service.record_feedback(
        feedback_type=request.feedback_type,
        item_id=request.item_id,
        rating=request.rating,
        comment=request.comment
    )
    return feedback


@router.get("/feedback/stats")
async def get_feedback_stats():
    """피드백 통계 조회"""
    service = get_learning_service()
    stats = service.get_feedback_stats()
    return stats


@router.post("/improve")
async def improve_based_on_feedback(
    db: Session = Depends(get_db)
):
    """피드백 기반 개선"""
    service = get_learning_service()
    improvements = service.improve_based_on_feedback(db)
    return improvements
