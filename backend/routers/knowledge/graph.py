"""Phase 15-8-1: 지식 그래프 데이터 API

D3.js Force-Directed Graph에 필요한 노드·링크 데이터를 제공.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.models import KnowledgeChunk, KnowledgeRelation, Document

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/knowledge/graph", tags=["Knowledge Graph"])


class GraphNode(BaseModel):
    id: int
    label: str
    group: str  # document_id 기반 그룹
    document_id: Optional[int] = None
    document_name: Optional[str] = None


class GraphLink(BaseModel):
    source: int
    target: int
    relation_type: str
    confidence: float


class GraphData(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]
    total_nodes: int
    total_links: int


@router.get("", response_model=GraphData, summary="지식 그래프 데이터 조회")
async def get_graph_data(
    limit: int = Query(100, ge=1, le=500, description="최대 노드 수"),
    document_id: Optional[int] = Query(None, description="특정 문서 필터"),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0, description="최소 관계 신뢰도"),
    db: Session = Depends(get_db),
):
    """
    D3.js Force-Directed Graph용 노드·링크 데이터 반환 (Phase 15-8-1)

    - nodes: 청크 (id, label, group)
    - links: 관계 (source, target, relation_type, confidence)
    """
    # 관계가 있는 청크만 조회
    query = db.query(KnowledgeRelation)
    if min_confidence > 0:
        query = query.filter(KnowledgeRelation.confidence >= min_confidence)

    relations = query.all()

    # 관련 청크 ID 수집
    chunk_ids = set()
    for r in relations:
        chunk_ids.add(r.source_chunk_id)
        chunk_ids.add(r.target_chunk_id)

    # document_id 필터
    if document_id:
        doc_chunks = {
            c.id for c in db.query(KnowledgeChunk.id).filter(
                KnowledgeChunk.document_id == document_id
            ).all()
        }
        chunk_ids &= doc_chunks
        relations = [
            r for r in relations
            if r.source_chunk_id in chunk_ids or r.target_chunk_id in chunk_ids
        ]

    # limit 적용
    if len(chunk_ids) > limit:
        chunk_ids = set(list(chunk_ids)[:limit])
        relations = [
            r for r in relations
            if r.source_chunk_id in chunk_ids and r.target_chunk_id in chunk_ids
        ]

    # 청크 상세 정보 조회
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.id.in_(chunk_ids)).all()
    chunk_map = {c.id: c for c in chunks}

    # 문서 정보 조회
    doc_ids = {c.document_id for c in chunks if c.document_id}
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all()
    doc_map = {d.id: d for d in docs}

    # 노드 생성
    nodes = []
    for cid in chunk_ids:
        chunk = chunk_map.get(cid)
        if not chunk:
            continue
        doc = doc_map.get(chunk.document_id)
        label = chunk.title or f"Chunk #{chunk.id}"
        nodes.append(GraphNode(
            id=chunk.id,
            label=label[:50],
            group=str(chunk.document_id or 0),
            document_id=chunk.document_id,
            document_name=doc.file_name if doc else None,
        ))

    # 링크 생성
    links = []
    for r in relations:
        if r.source_chunk_id in chunk_ids and r.target_chunk_id in chunk_ids:
            links.append(GraphLink(
                source=r.source_chunk_id,
                target=r.target_chunk_id,
                relation_type=r.relation_type,
                confidence=r.confidence or 0.5,
            ))

    return GraphData(
        nodes=nodes,
        links=links,
        total_nodes=len(nodes),
        total_links=len(links),
    )
