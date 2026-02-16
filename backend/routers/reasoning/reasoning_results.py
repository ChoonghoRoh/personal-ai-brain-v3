"""Reasoning 결과 저장/공유 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from backend.models.database import get_db
from backend.models.models import ReasoningResult

router = APIRouter(prefix="/api/reasoning-results", tags=["Reasoning Results"])


class ReasoningResultCreate(BaseModel):
    question: str
    answer: str
    reasoning_steps: Optional[List[str]] = None
    context_chunks: Optional[List[Dict]] = None
    relations: Optional[List[Dict]] = None
    mode: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict] = None


class ReasoningResultResponse(BaseModel):
    id: int
    question: str
    answer: str
    reasoning_steps: Optional[List[str]] = None
    context_chunks: Optional[List[Dict]] = None
    relations: Optional[List[Dict]] = None
    mode: Optional[str] = None
    session_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=ReasoningResultResponse)
async def create_reasoning_result(
    result: ReasoningResultCreate,
    db: Session = Depends(get_db)
):
    """Reasoning 결과 저장"""
    # JSON 문자열로 변환
    reasoning_steps_str = json.dumps(result.reasoning_steps) if result.reasoning_steps else None
    context_chunks_str = json.dumps(result.context_chunks) if result.context_chunks else None
    relations_str = json.dumps(result.relations) if result.relations else None
    metadata_str = json.dumps(result.metadata) if result.metadata else None
    
    db_result = ReasoningResult(
        question=result.question,
        answer=result.answer,
        reasoning_steps=reasoning_steps_str,
        context_chunks=context_chunks_str,
        relations=relations_str,
        mode=result.mode,
        session_id=result.session_id,
        meta_data=metadata_str
    )
    
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    # JSON 파싱
    reasoning_steps = json.loads(db_result.reasoning_steps) if db_result.reasoning_steps else None
    context_chunks = json.loads(db_result.context_chunks) if db_result.context_chunks else None
    relations = json.loads(db_result.relations) if db_result.relations else None
    
    return ReasoningResultResponse(
        id=db_result.id,
        question=db_result.question,
        answer=db_result.answer,
        reasoning_steps=reasoning_steps,
        context_chunks=context_chunks,
        relations=relations,
        mode=db_result.mode,
        session_id=db_result.session_id,
        created_at=db_result.created_at.isoformat()
    )


@router.get("", response_model=List[ReasoningResultResponse])
async def list_reasoning_results(
    session_id: Optional[str] = Query(None, description="세션 ID 필터"),
    limit: int = Query(50, ge=1, le=1000, description="최대 결과 수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: Session = Depends(get_db)
):
    """Reasoning 결과 목록 조회"""
    query = db.query(ReasoningResult)
    
    if session_id:
        query = query.filter(ReasoningResult.session_id == session_id)
    
    results = query.order_by(ReasoningResult.created_at.desc()).offset(offset).limit(limit).all()
    
    response_list = []
    for result in results:
        reasoning_steps = json.loads(result.reasoning_steps) if result.reasoning_steps else None
        context_chunks = json.loads(result.context_chunks) if result.context_chunks else None
        relations = json.loads(result.relations) if result.relations else None
        
        response_list.append(ReasoningResultResponse(
            id=result.id,
            question=result.question,
            answer=result.answer,
            reasoning_steps=reasoning_steps,
            context_chunks=context_chunks,
            relations=relations,
            mode=result.mode,
            session_id=result.session_id,
            created_at=result.created_at.isoformat()
        ))
    
    return response_list


@router.get("/{result_id}", response_model=ReasoningResultResponse)
async def get_reasoning_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Reasoning 결과 조회"""
    result = db.query(ReasoningResult).filter(ReasoningResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Reasoning 결과를 찾을 수 없습니다")
    
    reasoning_steps = json.loads(result.reasoning_steps) if result.reasoning_steps else None
    context_chunks = json.loads(result.context_chunks) if result.context_chunks else None
    relations = json.loads(result.relations) if result.relations else None
    
    return ReasoningResultResponse(
        id=result.id,
        question=result.question,
        answer=result.answer,
        reasoning_steps=reasoning_steps,
        context_chunks=context_chunks,
        relations=relations,
        mode=result.mode,
        session_id=result.session_id,
        created_at=result.created_at.isoformat()
    )


@router.delete("/{result_id}")
async def delete_reasoning_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Reasoning 결과 삭제"""
    result = db.query(ReasoningResult).filter(ReasoningResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Reasoning 결과를 찾을 수 없습니다")
    
    db.delete(result)
    db.commit()
    
    return {"message": "Reasoning 결과가 삭제되었습니다"}
