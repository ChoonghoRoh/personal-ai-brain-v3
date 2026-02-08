"""메타 인지 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.cognitive.metacognition_service import get_metacognition_service

router = APIRouter(prefix="/api/metacognition", tags=["metacognition"])


@router.get("/confidence/{chunk_id}")
async def get_confidence_score(
    chunk_id: int,
    db: Session = Depends(get_db)
):
    """신뢰도 점수 조회"""
    service = get_metacognition_service()
    confidence = service.calculate_confidence_score(db, chunk_id)
    return {
        "chunk_id": chunk_id,
        "confidence_score": confidence
    }


@router.get("/uncertainty/{chunk_id}")
async def get_uncertainty(
    chunk_id: int,
    threshold: float = 0.5,
    db: Session = Depends(get_db)
):
    """지식 불확실성 표시"""
    service = get_metacognition_service()
    uncertainty = service.indicate_uncertainty(db, chunk_id, threshold)
    return uncertainty


class UncertaintyMapRequest(BaseModel):
    chunk_ids: Optional[List[int]] = None


@router.post("/uncertainty/map")
async def get_uncertainty_map(
    request: UncertaintyMapRequest,
    db: Session = Depends(get_db)
):
    """지식 불확실성 맵"""
    service = get_metacognition_service()
    uncertainty_map = service.get_knowledge_uncertainty_map(db, request.chunk_ids)
    return uncertainty_map
