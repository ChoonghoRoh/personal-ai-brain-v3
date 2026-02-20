"""관계 추천 API (Phase 18-4: cross-document 관계 추천)"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.models.database import get_db
from backend.models.models import KnowledgeRelation, KnowledgeChunk, Document
from backend.services.search.search_service import get_search_service
from backend.config import COLLECTION_NAME

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/relations", tags=["Relations"])


def classify_relation_type(
    source_chunk: "KnowledgeChunk",
    target_chunk: "KnowledgeChunk",
    similarity: float,
) -> str:
    """관계 타입 자동 분류.

    - similar: similarity >= 0.85 + 다른 document
    - prerequisite: 같은 document + chunk_index 순서 (source < target)
    - extends: 다른 document + 부모-자식 라벨 관계 (간이 판별)
    - 기본값: "similar"
    """
    same_doc = source_chunk.document_id == target_chunk.document_id

    # prerequisite: 같은 document 내에서 chunk_index 순서가 있는 경우
    if same_doc:
        src_idx = source_chunk.chunk_index or 0
        tgt_idx = target_chunk.chunk_index or 0
        if src_idx < tgt_idx:
            return "prerequisite"

    # similar: 높은 유사도 + 다른 document
    if not same_doc and similarity >= 0.85:
        return "similar"

    # extends: 다른 document (유사도가 중간 범위)
    if not same_doc and similarity >= 0.7:
        return "extends"

    return "similar"


@router.get("/recommendations")
async def get_recommendations(
    chunk_id: int = Query(..., description="소스 청크 ID"),
    top_k: int = Query(5, ge=1, le=20, description="추천 개수"),
    cross_document_only: bool = Query(
        False, description="다른 document의 청크만 추천"
    ),
    db: Session = Depends(get_db),
):
    """cross-document 관계 추천 API.

    chunk_id로 해당 청크의 Qdrant 벡터를 조회 후 유사 청크를 검색합니다.
    cross_document_only=true면 같은 document_id를 가진 청크를 제외합니다.
    이미 관계가 있는 쌍은 already_related=true로 표시합니다.
    """
    # 1. 소스 청크 조회
    source_chunk = (
        db.query(KnowledgeChunk)
        .filter(KnowledgeChunk.id == chunk_id)
        .first()
    )
    if not source_chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")
    if not source_chunk.qdrant_point_id:
        raise HTTPException(
            status_code=400, detail="이 청크는 Qdrant에 인덱싱되지 않았습니다"
        )

    # 2. Qdrant에서 유사 벡터 검색
    search_service = get_search_service()
    if not search_service.client:
        raise HTTPException(status_code=503, detail="검색 서비스를 사용할 수 없습니다")

    try:
        # Qdrant point에서 벡터 조회
        points = search_service.client.retrieve(
            collection_name=COLLECTION_NAME,
            ids=[source_chunk.qdrant_point_id],
            with_vectors=True,
        )
        if not points:
            raise HTTPException(
                status_code=404, detail="Qdrant에서 벡터를 찾을 수 없습니다"
            )

        source_vector = points[0].vector
        # 자기 자신 제외를 위해 더 많이 검색
        search_limit = top_k + 10
        similar_results = search_service.client.query_points(
            collection_name=COLLECTION_NAME,
            query=source_vector,
            limit=search_limit,
        )
    except Exception as e:
        logger.error("Qdrant 유사 검색 실패: %s", e)
        raise HTTPException(status_code=500, detail="유사도 검색 실패")

    # 3. 소스 청크의 document_id 확인
    source_document_id = source_chunk.document_id

    # 4. 기존 관계 조회 (양방향)
    existing_relations = (
        db.query(KnowledgeRelation)
        .filter(
            (KnowledgeRelation.source_chunk_id == chunk_id)
            | (KnowledgeRelation.target_chunk_id == chunk_id)
        )
        .all()
    )
    related_chunk_ids = set()
    for rel in existing_relations:
        if rel.source_chunk_id == chunk_id:
            related_chunk_ids.add(rel.target_chunk_id)
        else:
            related_chunk_ids.add(rel.source_chunk_id)

    # 5. 결과 구성
    recommendations = []
    for point in similar_results.points:
        qdrant_point_id = str(point.id)
        # 자기 자신 제외
        if qdrant_point_id == source_chunk.qdrant_point_id:
            continue

        # DB에서 청크 조회
        target_chunk = (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.qdrant_point_id == qdrant_point_id)
            .first()
        )
        if not target_chunk:
            continue

        # cross_document_only 필터
        if cross_document_only and target_chunk.document_id == source_document_id:
            continue

        # document 이름 조회
        doc = (
            db.query(Document)
            .filter(Document.id == target_chunk.document_id)
            .first()
        )
        document_name = doc.file_name if doc else ""

        # snippet (앞 200자)
        snippet = (target_chunk.content or "")[:200]
        if len(target_chunk.content or "") > 200:
            snippet += "..."

        already_related = target_chunk.id in related_chunk_ids
        sim = float(point.score)
        suggested_type = classify_relation_type(source_chunk, target_chunk, sim)

        recommendations.append({
            "chunk_id": target_chunk.id,
            "document_id": target_chunk.document_id,
            "document_name": document_name,
            "content_snippet": snippet,
            "similarity": sim,
            "chunk_index": target_chunk.chunk_index,
            "status": target_chunk.status,
            "already_related": already_related,
            "cross_document": target_chunk.document_id != source_document_id,
            "suggested_type": suggested_type,
        })

        if len(recommendations) >= top_k:
            break

    return {
        "source_chunk_id": chunk_id,
        "source_document_id": source_document_id,
        "recommendations": recommendations,
        "total": len(recommendations),
    }
