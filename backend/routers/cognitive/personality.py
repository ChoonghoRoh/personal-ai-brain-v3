"""인격 유지 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.cognitive.personality_service import get_personality_service

router = APIRouter(prefix="/api/personality", tags=["personality"])


class PersonalityProfileRequest(BaseModel):
    principles: List[str]
    values: List[str]
    preferences: Optional[Dict] = None  # Dict로 변경 (List에서 Dict로)
    communication_style: str = "professional"


class ContradictionDetectionRequest(BaseModel):
    content: str


class ContradictionResolutionRequest(BaseModel):
    resolution: str
    priority: str = "new"  # new, existing


@router.post("/profile")
async def define_personality_profile(
    request: PersonalityProfileRequest,
    db: Session = Depends(get_db)
):
    """인격 프로필 정의"""
    service = get_personality_service()
    profile = service.define_personality_profile(
        principles=request.principles,
        values=request.values,
        preferences=request.preferences,
        communication_style=request.communication_style
    )
    return profile


@router.get("/profile")
async def get_personality_profile():
    """인격 프로필 조회"""
    service = get_personality_service()
    profile = service.get_personality_profile()
    return profile


@router.post("/contradictions/detect")
async def detect_contradictions(
    request: ContradictionDetectionRequest,
    db: Session = Depends(get_db)
):
    """모순 감지"""
    service = get_personality_service()
    contradictions = service.detect_contradictions(db, request.content)
    return {
        "contradictions": contradictions,
        "count": len(contradictions)
    }


@router.post("/contradictions/{contradiction_id}/resolve")
async def resolve_contradiction(
    contradiction_id: int,
    request: ContradictionResolutionRequest,
    db: Session = Depends(get_db)
):
    """모순 해결"""
    service = get_personality_service()
    result = service.resolve_contradiction(
        contradiction_id=contradiction_id,
        resolution=request.resolution,
        priority=request.priority
    )
    return result
