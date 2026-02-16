"""대화 기록 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.models.database import get_db
from backend.models.models import Conversation

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


class ConversationCreate(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Dict]] = None
    model_used: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict] = None


class ConversationResponse(BaseModel):
    id: int
    question: str
    answer: str
    sources: Optional[List[Dict]] = None
    model_used: Optional[str] = None
    session_id: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """대화 기록 저장"""
    import json
    
    # sources와 metadata를 JSON 문자열로 변환
    sources_str = json.dumps(conversation.sources) if conversation.sources else None
    metadata_str = json.dumps(conversation.metadata) if conversation.metadata else None
    
    db_conversation = Conversation(
        question=conversation.question,
        answer=conversation.answer,
        sources=sources_str,
        model_used=conversation.model_used,
        session_id=conversation.session_id,
        meta_data=metadata_str
    )
    
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    
    # sources 파싱
    sources = json.loads(db_conversation.sources) if db_conversation.sources else None
    
    return ConversationResponse(
        id=db_conversation.id,
        question=db_conversation.question,
        answer=db_conversation.answer,
        sources=sources,
        model_used=db_conversation.model_used,
        session_id=db_conversation.session_id,
        created_at=db_conversation.created_at.isoformat()
    )


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    session_id: Optional[str] = Query(None, description="세션 ID 필터"),
    limit: int = Query(50, ge=1, le=1000, description="최대 결과 수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: Session = Depends(get_db)
):
    """대화 기록 목록 조회"""
    import json
    
    query = db.query(Conversation)
    
    if session_id:
        query = query.filter(Conversation.session_id == session_id)
    
    conversations = query.order_by(Conversation.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for conv in conversations:
        sources = json.loads(conv.sources) if conv.sources else None
        result.append(ConversationResponse(
            id=conv.id,
            question=conv.question,
            answer=conv.answer,
            sources=sources,
            model_used=conv.model_used,
            session_id=conv.session_id,
            created_at=conv.created_at.isoformat()
        ))
    
    return result


@router.get("/search")
async def search_conversations(
    q: str = Query(..., description="검색어"),
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    db: Session = Depends(get_db)
):
    """대화 기록 검색"""
    import json
    
    query = db.query(Conversation).filter(
        (Conversation.question.ilike(f"%{q}%")) |
        (Conversation.answer.ilike(f"%{q}%"))
    )
    
    total_count = query.count()
    conversations = query.order_by(Conversation.created_at.desc()).offset(offset).limit(limit).all()
    
    result = []
    for conv in conversations:
        sources = json.loads(conv.sources) if conv.sources else None
        result.append(ConversationResponse(
            id=conv.id,
            question=conv.question,
            answer=conv.answer,
            sources=sources,
            model_used=conv.model_used,
            session_id=conv.session_id,
            created_at=conv.created_at.isoformat()
        ))
    
    return {
        "results": result,
        "total_count": total_count,
        "offset": offset,
        "limit": limit
    }


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """대화 기록 조회"""
    import json
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="대화 기록을 찾을 수 없습니다")
    
    sources = json.loads(conversation.sources) if conversation.sources else None
    
    return ConversationResponse(
        id=conversation.id,
        question=conversation.question,
        answer=conversation.answer,
        sources=sources,
        model_used=conversation.model_used,
        session_id=conversation.session_id,
        created_at=conversation.created_at.isoformat()
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """대화 기록 삭제"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="대화 기록을 찾을 수 없습니다")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "대화 기록이 삭제되었습니다"}
