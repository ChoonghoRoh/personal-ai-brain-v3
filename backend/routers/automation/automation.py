"""자동화 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.services.automation.automation_service import get_automation_service

router = APIRouter(prefix="/api/automation", tags=["Automation"])


class AutoLabelRequest(BaseModel):
    chunk_ids: Optional[List[int]] = None
    min_confidence: float = 0.7


class BatchAutoLabelRequest(BaseModel):
    batch_size: int = 100
    min_confidence: float = 0.7


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
