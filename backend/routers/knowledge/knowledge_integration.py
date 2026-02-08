"""지식 통합 및 세계관 구성 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.knowledge.knowledge_integration_service import get_knowledge_integration_service

router = APIRouter(prefix="/api/knowledge-integration", tags=["knowledge-integration"])


class KnowledgeIntegrationRequest(BaseModel):
    chunk_ids: List[int]
    strategy: str = "merge"  # merge, prioritize, resolve


class ContradictionResolutionRequest(BaseModel):
    resolution_strategy: str = "prioritize_new"  # prioritize_new, prioritize_old, merge


class ContradictionDetectionRequest(BaseModel):
    chunk_ids: List[int]


@router.post("/integrate")
async def integrate_knowledge(
    request: KnowledgeIntegrationRequest,
    db: Session = Depends(get_db)
):
    """지식 통합"""
    service = get_knowledge_integration_service()
    result = service.integrate_knowledge(
        db=db,
        chunk_ids=request.chunk_ids,
        strategy=request.strategy
    )
    return result


@router.post("/contradictions/detect")
async def detect_contradictions(
    request: ContradictionDetectionRequest,
    db: Session = Depends(get_db)
):
    """모순 감지"""
    service = get_knowledge_integration_service()
    contradictions = service.detect_contradictions(db, request.chunk_ids)
    return {
        "contradictions": contradictions,
        "count": len(contradictions)
    }


@router.post("/contradictions/resolve")
async def resolve_contradictions(
    contradictions: List[Dict],
    request: ContradictionResolutionRequest,
    db: Session = Depends(get_db)
):
    """모순 해결"""
    service = get_knowledge_integration_service()
    result = service.resolve_contradictions(
        contradictions=contradictions,
        resolution_strategy=request.resolution_strategy
    )
    return result


@router.get("/worldview")
async def build_worldview(
    project_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db)
):
    """세계관 구성"""
    service = get_knowledge_integration_service()
    worldview = service.build_worldview(db, project_ids)
    return worldview
