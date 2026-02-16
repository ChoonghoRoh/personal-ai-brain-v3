"""추론 체인 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.reasoning.reasoning_chain_service import get_reasoning_chain_service

router = APIRouter(prefix="/api/reasoning-chain", tags=["Reasoning Chain"])


class ReasoningChainRequest(BaseModel):
    question: str
    max_depth: int = 3
    max_steps: int = 10


@router.post("/build")
async def build_reasoning_chain(
    request: ReasoningChainRequest,
    db: Session = Depends(get_db)
):
    """다단계 추론 체인 구축"""
    service = get_reasoning_chain_service()
    chain = service.build_reasoning_chain(
        db=db,
        question=request.question,
        max_depth=request.max_depth,
        max_steps=request.max_steps
    )
    return chain


class VisualizationRequest(BaseModel):
    question: str
    steps: List[Dict]


@router.post("/visualize")
async def visualize_reasoning_chain(
    request: VisualizationRequest,
    db: Session = Depends(get_db)
):
    """추론 체인 시각화"""
    service = get_reasoning_chain_service()
    chain = {
        "question": request.question,
        "steps": request.steps
    }
    visualization = service.visualize_reasoning_chain(chain)
    return visualization
