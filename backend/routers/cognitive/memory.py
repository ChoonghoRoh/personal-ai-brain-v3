"""기억 시스템 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from backend.models.database import get_db
from backend.models.models import Memory
from backend.services.cognitive.memory_service import get_memory_service

router = APIRouter(prefix="/api/memory", tags=["memory"])


class MemoryCreate(BaseModel):
    memory_type: str  # long_term, short_term, working
    content: str
    importance_score: float = 0.5
    category: Optional[str] = None
    related_chunk_id: Optional[int] = None
    metadata: Optional[Dict] = None  # 클라이언트에서는 metadata로 받지만 내부적으로는 meta_data로 변환
    expires_in_hours: Optional[int] = None


class MemoryResponse(BaseModel):
    id: int
    memory_type: str
    content: str
    importance_score: float
    category: Optional[str] = None
    related_chunk_id: Optional[int] = None
    access_count: int
    last_accessed_at: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=MemoryResponse)
async def create_memory(
    memory: MemoryCreate,
    db: Session = Depends(get_db)
):
    """기억 생성"""
    service = get_memory_service()
    
    try:
        created_memory = service.create_memory(
            db=db,
            memory_type=memory.memory_type,
            content=memory.content,
            importance_score=memory.importance_score,
            category=memory.category,
            related_chunk_id=memory.related_chunk_id,
            metadata=memory.metadata,  # JSON 문자열로 변환하여 meta_data에 저장
            expires_in_hours=memory.expires_in_hours
        )
        
        return MemoryResponse(
            id=created_memory.id,
            memory_type=created_memory.memory_type,
            content=created_memory.content,
            importance_score=created_memory.importance_score,
            category=created_memory.category,
            related_chunk_id=created_memory.related_chunk_id,
            access_count=created_memory.access_count,
            last_accessed_at=created_memory.last_accessed_at.isoformat() if created_memory.last_accessed_at else None,
            expires_at=created_memory.expires_at.isoformat() if created_memory.expires_at else None,
            created_at=created_memory.created_at.isoformat(),
            updated_at=created_memory.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[MemoryResponse])
async def list_memories(
    memory_type: Optional[str] = Query(None, description="기억 타입 필터 (long_term, short_term, working)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """기억 목록 조회"""
    service = get_memory_service()
    
    if memory_type == "long_term":
        memories = service.get_long_term_memories(db=db, category=category, limit=limit)
    elif memory_type == "short_term":
        memories = service.get_short_term_memories(db=db, limit=limit)
    elif memory_type == "working":
        memories = service.get_working_memories(db=db, limit=limit)
    else:
        # 모든 타입 조회
        memories = db.query(Memory).order_by(Memory.created_at.desc()).limit(limit).all()
        if category:
            memories = [m for m in memories if m.category == category]
    
    return [
        MemoryResponse(
            id=m.id,
            memory_type=m.memory_type,
            content=m.content,
            importance_score=m.importance_score,
            category=m.category,
            related_chunk_id=m.related_chunk_id,
            access_count=m.access_count,
            last_accessed_at=m.last_accessed_at.isoformat() if m.last_accessed_at else None,
            expires_at=m.expires_at.isoformat() if m.expires_at else None,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat()
        )
        for m in memories
    ]


@router.get("/long-term", response_model=List[MemoryResponse])
async def get_long_term_memories(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """장기 기억 조회"""
    service = get_memory_service()
    memories = service.get_long_term_memories(db=db, category=category, limit=limit)
    
    return [
        MemoryResponse(
            id=m.id,
            memory_type=m.memory_type,
            content=m.content,
            importance_score=m.importance_score,
            category=m.category,
            related_chunk_id=m.related_chunk_id,
            access_count=m.access_count,
            last_accessed_at=m.last_accessed_at.isoformat() if m.last_accessed_at else None,
            expires_at=m.expires_at.isoformat() if m.expires_at else None,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat()
        )
        for m in memories
    ]


@router.get("/short-term", response_model=List[MemoryResponse])
async def get_short_term_memories(
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """단기 기억 조회"""
    service = get_memory_service()
    memories = service.get_short_term_memories(db=db, limit=limit)
    
    return [
        MemoryResponse(
            id=m.id,
            memory_type=m.memory_type,
            content=m.content,
            importance_score=m.importance_score,
            category=m.category,
            related_chunk_id=m.related_chunk_id,
            access_count=m.access_count,
            last_accessed_at=m.last_accessed_at.isoformat() if m.last_accessed_at else None,
            expires_at=m.expires_at.isoformat() if m.expires_at else None,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat()
        )
        for m in memories
    ]


@router.get("/working", response_model=List[MemoryResponse])
async def get_working_memories(
    limit: int = Query(10, ge=1, le=50, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """작업 기억 조회"""
    service = get_memory_service()
    memories = service.get_working_memories(db=db, limit=limit)
    
    return [
        MemoryResponse(
            id=m.id,
            memory_type=m.memory_type,
            content=m.content,
            importance_score=m.importance_score,
            category=m.category,
            related_chunk_id=m.related_chunk_id,
            access_count=m.access_count,
            last_accessed_at=m.last_accessed_at.isoformat() if m.last_accessed_at else None,
            expires_at=m.expires_at.isoformat() if m.expires_at else None,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat()
        )
        for m in memories
    ]


@router.get("/search")
async def search_memories(
    q: str = Query(..., description="검색어"),
    memory_types: Optional[str] = Query(None, description="기억 타입 (쉼표로 구분)"),
    limit: int = Query(20, ge=1, le=100, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """기억 검색"""
    service = get_memory_service()
    
    types_list = None
    if memory_types:
        types_list = [t.strip() for t in memory_types.split(',')]
    
    memories = service.search_memories(
        db=db,
        query=q,
        memory_types=types_list,
        limit=limit
    )
    
    return [
        MemoryResponse(
            id=m.id,
            memory_type=m.memory_type,
            content=m.content,
            importance_score=m.importance_score,
            category=m.category,
            related_chunk_id=m.related_chunk_id,
            access_count=m.access_count,
            last_accessed_at=m.last_accessed_at.isoformat() if m.last_accessed_at else None,
            expires_at=m.expires_at.isoformat() if m.expires_at else None,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat()
        )
        for m in memories
    ]


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """기억 상세 조회"""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="기억을 찾을 수 없습니다")
    
    return MemoryResponse(
        id=memory.id,
        memory_type=memory.memory_type,
        content=memory.content,
        importance_score=memory.importance_score,
        category=memory.category,
        related_chunk_id=memory.related_chunk_id,
        access_count=memory.access_count,
        last_accessed_at=memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
        expires_at=memory.expires_at.isoformat() if memory.expires_at else None,
        created_at=memory.created_at.isoformat(),
        updated_at=memory.updated_at.isoformat()
    )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    db: Session = Depends(get_db)
):
    """기억 삭제"""
    memory = db.query(Memory).filter(Memory.id == memory_id).first()
    if not memory:
        raise HTTPException(status_code=404, detail="기억을 찾을 수 없습니다")
    
    db.delete(memory)
    db.commit()
    return {"message": "기억이 삭제되었습니다.", "id": memory_id}


class ImportanceUpdate(BaseModel):
    importance_score: float = Field(..., ge=0.0, le=1.0, description="중요도 점수")


@router.put("/{memory_id}/importance")
async def update_importance(
    memory_id: int,
    update: ImportanceUpdate,
    db: Session = Depends(get_db)
):
    """기억 중요도 업데이트"""
    service = get_memory_service()
    
    try:
        memory = service.update_importance(
            db=db,
            memory_id=memory_id,
            importance_score=update.importance_score
        )
        
        return MemoryResponse(
            id=memory.id,
            memory_type=memory.memory_type,
            content=memory.content,
            importance_score=memory.importance_score,
            category=memory.category,
            related_chunk_id=memory.related_chunk_id,
            access_count=memory.access_count,
            last_accessed_at=memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
            expires_at=memory.expires_at.isoformat() if memory.expires_at else None,
            created_at=memory.created_at.isoformat(),
            updated_at=memory.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{memory_id}/promote")
async def promote_to_long_term(
    memory_id: int,
    importance_score: float = Query(0.7, ge=0.0, le=1.0, description="중요도 점수"),
    db: Session = Depends(get_db)
):
    """단기 기억을 장기 기억으로 승격"""
    service = get_memory_service()
    
    try:
        memory = service.promote_to_long_term(
            db=db,
            memory_id=memory_id,
            importance_score=importance_score
        )
        
        return MemoryResponse(
            id=memory.id,
            memory_type=memory.memory_type,
            content=memory.content,
            importance_score=memory.importance_score,
            category=memory.category,
            related_chunk_id=memory.related_chunk_id,
            access_count=memory.access_count,
            last_accessed_at=memory.last_accessed_at.isoformat() if memory.last_accessed_at else None,
            expires_at=memory.expires_at.isoformat() if memory.expires_at else None,
            created_at=memory.created_at.isoformat(),
            updated_at=memory.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/expired")
async def delete_expired_memories(
    db: Session = Depends(get_db)
):
    """만료된 단기 기억 삭제"""
    service = get_memory_service()
    count = service.delete_expired_memories(db=db)
    
    return {"message": f"{count}개의 만료된 기억이 삭제되었습니다."}
