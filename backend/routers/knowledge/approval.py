"""Chunk Approval API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.models.database import get_db
from backend.models.models import KnowledgeChunk, KnowledgeLabel, KnowledgeRelation
from backend.config import AUTO_STRUCTURE_MATCHING_ENABLED
from backend.services.knowledge.structure_matcher import get_structure_matcher

# prefix를 /api/approval/chunks로 변경하여 knowledge.router와의 경로 충돌 방지
router = APIRouter(prefix="/api/approval/chunks", tags=["Approval"])


class ApproveRequest(BaseModel):
    approved_by: Optional[str] = "admin"


class RejectRequest(BaseModel):
    reason: Optional[str] = None


class PendingChunkResponse(BaseModel):
    id: int
    content: str
    status: str
    source: Optional[str] = None
    document_id: int
    chunk_index: int
    created_at: Optional[str] = None


class PendingChunkListResponse(BaseModel):
    """페이징 정보를 포함한 승인 대기 청크 목록 응답"""
    items: List[PendingChunkResponse]
    total_count: int
    limit: int
    offset: int
    total_pages: int
    current_page: int


@router.get("/pending", response_model=PendingChunkListResponse)
async def get_pending_chunks(
    status: Optional[str] = Query(None, description="Filter by status: draft, approved, rejected"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, description="오프셋"),
    sort_by: str = Query("created_at", description="정렬 기준 (created_at, chunk_index)"),
    sort_order: str = Query("desc", description="정렬 방향 (asc, desc)"),
    db: Session = Depends(get_db)
):
    """승인 대기 중인 청크 목록 조회 (페이징 지원)"""
    query = db.query(KnowledgeChunk)
    
    if status:
        query = query.filter(KnowledgeChunk.status == status)
    else:
        # 기본값: draft 상태만
        query = query.filter(KnowledgeChunk.status == "draft")
    
    # 정렬 적용
    valid_sort_fields = ["created_at", "chunk_index"]
    if sort_by not in valid_sort_fields:
        sort_by = "created_at"
    
    sort_field = getattr(KnowledgeChunk, sort_by, KnowledgeChunk.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(sort_field.asc())
    else:
        query = query.order_by(sort_field.desc())
    
    # 총 개수 계산
    total_count = query.count()
    
    # 페이징 적용
    chunks = query.offset(offset).limit(limit).all()
    
    # 결과 생성
    items = [
        PendingChunkResponse(
            id=chunk.id,
            content=chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
            status=chunk.status,
            source=chunk.source,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            created_at=chunk.created_at.isoformat() if chunk.created_at else None,
        )
        for chunk in chunks
    ]
    
    # 페이징 메타데이터 계산
    total_pages = (total_count + limit - 1) // limit if limit > 0 else 0
    current_page = (offset // limit) + 1 if limit > 0 else 1
    
    return PendingChunkListResponse(
        items=items,
        total_count=total_count,
        limit=limit,
        offset=offset,
        total_pages=total_pages,
        current_page=current_page
    )


class BatchApproveRequest(BaseModel):
    chunk_ids: List[int]
    approved_by: Optional[str] = "admin"


class BatchRejectRequest(BaseModel):
    chunk_ids: List[int]
    reason: Optional[str] = None


@router.post("/batch/approve")
async def batch_approve_chunks(
    request: BatchApproveRequest,
    suggest_relations: bool = Query(True, description="관계 추천 포함 여부 (Phase 9-3-2)"),
    db: Session = Depends(get_db),
):
    """여러 청크 일괄 승인. suggest_relations=True 시 첫 승인 청크에 대한 관계 추천 반환 (Phase 9-3-2)."""
    if not request.chunk_ids:
        raise HTTPException(status_code=400, detail="청크 ID 목록이 필요합니다.")

    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(request.chunk_ids)).all()

    if len(chunks) != len(request.chunk_ids):
        raise HTTPException(status_code=404, detail="일부 청크를 찾을 수 없습니다.")

    approved_count = 0
    for chunk in chunks:
        chunk.status = "approved"
        chunk.approved_at = datetime.utcnow()
        chunk.approved_by = request.approved_by
        chunk.version += 1
        chunk.updated_at = datetime.utcnow()
        approved_count += 1

    db.commit()

    suggested_relations = []
    if suggest_relations and AUTO_STRUCTURE_MATCHING_ENABLED and chunks:
        try:
            matcher = get_structure_matcher(db)
            suggested_relations = matcher.suggest_relations_on_approve(chunks[0])
        except Exception:
            pass

    return {
        "message": f"{approved_count}개의 청크가 승인되었습니다.",
        "approved_count": approved_count,
        "chunk_ids": request.chunk_ids,
        "suggested_relations": suggested_relations,
    }


@router.post("/batch/reject")
async def batch_reject_chunks(request: BatchRejectRequest, db: Session = Depends(get_db)):
    """여러 청크 일괄 거절"""
    if not request.chunk_ids:
        raise HTTPException(status_code=400, detail="청크 ID 목록이 필요합니다.")
    
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(request.chunk_ids)).all()
    
    if len(chunks) != len(request.chunk_ids):
        raise HTTPException(status_code=404, detail="일부 청크를 찾을 수 없습니다.")
    
    rejected_count = 0
    for chunk in chunks:
        chunk.status = "rejected"
        chunk.updated_at = datetime.utcnow()
        rejected_count += 1
    
    db.commit()
    
    return {
        "message": f"{rejected_count}개의 청크가 거절되었습니다.",
        "rejected_count": rejected_count,
        "chunk_ids": request.chunk_ids
    }


@router.post("/{chunk_id:int}/approve")
async def approve_chunk(
    chunk_id: int,
    request: ApproveRequest = None,
    db: Session = Depends(get_db),
):
    """단일 청크 승인"""
    request = request or ApproveRequest()
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    chunk.status = "approved"
    chunk.approved_at = datetime.utcnow()
    chunk.approved_by = request.approved_by
    chunk.version = (chunk.version or 0) + 1
    chunk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chunk)
    return {
        "message": "청크가 승인되었습니다.",
        "chunk_id": chunk_id,
        "status": chunk.status,
    }


@router.post("/{chunk_id:int}/reject")
async def reject_chunk(
    chunk_id: int,
    request: RejectRequest = None,
    db: Session = Depends(get_db),
):
    """단일 청크 거절"""
    request = request or RejectRequest()
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다.")
    chunk.status = "rejected"
    chunk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(chunk)
    return {
        "message": "청크가 거절되었습니다.",
        "chunk_id": chunk_id,
        "status": chunk.status,
    }

