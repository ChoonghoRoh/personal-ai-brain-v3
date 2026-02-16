"""맥락 이해 및 연결 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from backend.models.database import get_db
from backend.models.models import KnowledgeChunk
from backend.services.cognitive.context_service import get_context_service

router = APIRouter(prefix="/api/context", tags=["Context"])


@router.get("/chunks/{chunk_id}/semantic-connections")
async def get_semantic_connections(
    chunk_id: int,
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="유사도 임계값"),
    limit: int = Query(10, ge=1, le=50, description="최대 결과 수"),
    db: Session = Depends(get_db)
):
    """의미적으로 연결된 청크 찾기"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    connections = context_service.find_semantic_connections(
        db=db,
        chunk=chunk,
        threshold=threshold,
        limit=limit
    )
    
    return {
        'chunk_id': chunk_id,
        'connections': connections
    }


@router.get("/chunks/{chunk_id}/temporal-context")
async def get_temporal_context(
    chunk_id: int,
    time_window_days: int = Query(30, ge=1, le=365, description="시간 창 (일)"),
    db: Session = Depends(get_db)
):
    """시간적 맥락 추적"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    temporal_context = context_service.track_temporal_context(
        db=db,
        chunk=chunk,
        time_window_days=time_window_days
    )
    
    return temporal_context


class ClusterRequest(BaseModel):
    chunk_ids: List[int]
    n_clusters: int = 5


@router.post("/chunks/cluster")
async def cluster_chunks(
    request: ClusterRequest,
    db: Session = Depends(get_db)
):
    """주제별 클러스터링"""
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.id.in_(request.chunk_ids)
    ).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    clusters = context_service.cluster_by_topic(
        db=db,
        chunks=chunks,
        n_clusters=request.n_clusters
    )
    
    return clusters


class HierarchyRequest(BaseModel):
    chunk_ids: List[int]


@router.post("/chunks/hierarchy")
async def infer_hierarchy(
    request: HierarchyRequest,
    db: Session = Depends(get_db)
):
    """문서 계층 구조 자동 추론"""
    chunks = db.query(KnowledgeChunk).filter(
        KnowledgeChunk.id.in_(request.chunk_ids)
    ).all()
    
    if not chunks:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    hierarchy = context_service.infer_hierarchy(
        db=db,
        chunks=chunks
    )
    
    return hierarchy


@router.get("/chunks/{chunk_id}/references")
async def get_references(
    chunk_id: int,
    db: Session = Depends(get_db)
):
    """참조 관계 자동 감지 및 추적"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    references = context_service.detect_references(
        db=db,
        chunk=chunk
    )
    
    return {
        'chunk_id': chunk_id,
        'references': references
    }


@router.get("/chunks/{chunk_id}/similarity")
async def calculate_similarity(
    chunk_id: int,
    target_chunk_id: int,
    db: Session = Depends(get_db)
):
    """두 청크 간 의미적 유사도 계산"""
    chunk1 = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    chunk2 = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == target_chunk_id).first()
    
    if not chunk1 or not chunk2:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    
    context_service = get_context_service()
    similarity = context_service.calculate_semantic_similarity(chunk1, chunk2)
    
    return {
        'chunk1_id': chunk_id,
        'chunk2_id': target_chunk_id,
        'similarity': similarity
    }
