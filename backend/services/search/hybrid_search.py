"""Hybrid Search 서비스 — 키워드 + 의미 검색, RRF 결합 (Phase 9-3-3)"""
import logging
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.config import (
    HYBRID_SEARCH_SEMANTIC_WEIGHT,
    HYBRID_SEARCH_KEYWORD_WEIGHT,
)
from backend.models.models import KnowledgeChunk, Document, KnowledgeLabel
from backend.services.search.search_service import get_search_service

logger = logging.getLogger(__name__)

# RRF 상수 (k=60 일반적)
RRF_K = 60


class HybridSearchService:
    """키워드 검색과 의미 검색을 결합한 Hybrid Search 서비스."""

    def __init__(
        self,
        semantic_weight: float = HYBRID_SEARCH_SEMANTIC_WEIGHT,
        keyword_weight: float = HYBRID_SEARCH_KEYWORD_WEIGHT,
    ):
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    def semantic_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """의미 검색 (기존 Qdrant 검색 래핑).

        Args:
            query: 검색 쿼리
            top_k: 반환할 결과 수
            filters: Qdrant 필터 (file_path, chunk_index 등)

        Returns:
            [{"document_id", "content", "score", "chunk_id", "file", "snippet", "chunk_index"}, ...]
        """
        try:
            search_service = get_search_service()
            result = search_service.search(
                query=query,
                top_k=top_k,
                offset=0,
                filters=filters,
                use_cache=True,
            )
            documents = []
            for doc in result.get("results", []):
                # document_id는 Qdrant point id (문자열)
                documents.append({
                    "document_id": str(doc.get("document_id", "")),
                    "content": doc.get("content", ""),
                    "score": float(doc.get("score", 0.0)),
                    "file": doc.get("file", ""),
                    "snippet": doc.get("snippet", ""),
                    "chunk_index": doc.get("chunk_index", 0),
                    "source": "semantic",
                })
            return documents
        except Exception as e:
            logger.warning("semantic_search failed: %s", e)
            return []

    def keyword_search(
        self,
        db: Session,
        query: str,
        top_k: int = 10,
        project_id: Optional[int] = None,
        label_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """키워드 검색 (PostgreSQL ILIKE 기반).

        Args:
            db: DB 세션
            query: 검색 쿼리 (공백으로 분리해 OR 조건)
            top_k: 반환할 결과 수
            project_id: 프로젝트 필터 (선택)
            label_ids: 라벨 필터 (선택)

        Returns:
            [{"document_id", "content", "score", "chunk_id", "file", "source": "keyword"}, ...]
            document_id는 qdrant_point_id가 있으면 사용, 없으면 "chunk_{id}"
        """
        if not query or not query.strip():
            return []
        try:
            terms = [t.strip() for t in query.strip().split() if t.strip()]
            if not terms:
                terms = [query.strip()]

            q = (
                db.query(KnowledgeChunk)
                .join(Document, KnowledgeChunk.document_id == Document.id)
                .filter(KnowledgeChunk.status == "approved")
                .filter(KnowledgeChunk.content.isnot(None))
            )
            # ILIKE OR 조건 (content + file_path)
            if terms:
                content_filters = [KnowledgeChunk.content.ilike(f"%{t}%") for t in terms]
                filepath_filters = [Document.file_path.ilike(f"%{t}%") for t in terms]
                ilike_filter = or_(*(content_filters + filepath_filters))
                q = q.filter(ilike_filter)

            if project_id is not None:
                q = q.filter(
                    Document.project_id == project_id
                )
            if label_ids:
                q = (
                    q.join(KnowledgeLabel, KnowledgeLabel.chunk_id == KnowledgeChunk.id)
                    .filter(KnowledgeLabel.label_id.in_(label_ids))
                    .distinct()
                )

            chunks = q.limit(top_k * 2).all()  # 중복 제거 전 더 가져옴

            # 간단한 점수: 매칭된 term 수 / 전체 term 수
            results = []
            seen_ids = set()
            for chunk in chunks:
                if chunk.id in seen_ids:
                    continue
                seen_ids.add(chunk.id)
                # document_id: Qdrant와 fusion 시 동일 키로 매칭되도록
                doc_id = chunk.qdrant_point_id if chunk.qdrant_point_id else f"chunk_{chunk.id}"
                chunk_file_path = ""
                if chunk.document_id:
                    doc_row = db.query(Document).filter(Document.id == chunk.document_id).first()
                    if doc_row:
                        chunk_file_path = doc_row.file_path or ""
                content_lower = (chunk.content or "").lower()
                filepath_lower = chunk_file_path.lower()
                match_count = sum(1 for t in terms if t.lower() in content_lower or t.lower() in filepath_lower)
                score = match_count / len(terms) if terms else 0.0
                results.append({
                    "document_id": str(doc_id),
                    "content": chunk.content or "",
                    "score": min(1.0, score * 1.2),  # 소폭 상한
                    "chunk_id": chunk.id,
                    "file": chunk_file_path,
                    "snippet": (chunk.content or "")[:200] + ("..." if len(chunk.content or "") > 200 else ""),
                    "chunk_index": chunk.chunk_index or 0,
                    "source": "keyword",
                })
                if len(results) >= top_k:
                    break
            return results
        except Exception as e:
            logger.warning("keyword_search failed: %s", e)
            return []

    def fuse_results(
        self,
        semantic: List[Dict[str, Any]],
        keyword: List[Dict[str, Any]],
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """RRF(Reciprocal Rank Fusion)로 두 결과 리스트 결합.

        Args:
            semantic: 의미 검색 결과 (document_id, content, score, ...)
            keyword: 키워드 검색 결과 (document_id, content, score, ...)
            semantic_weight: 의미 가중치 (기본값 self.semantic_weight)
            keyword_weight: 키워드 가중치 (기본값 self.keyword_weight)

        Returns:
            RRF 점수로 정렬된 결합 결과. score는 0~1 정규화, source="hybrid"
        """
        sw = semantic_weight if semantic_weight is not None else self.semantic_weight
        kw = keyword_weight if keyword_weight is not None else self.keyword_weight

        # rank -> document_id (1-based rank)
        def rank_by_position(items: List[Dict], key: str = "document_id") -> Dict[str, int]:
            out = {}
            for rank, item in enumerate(items, start=1):
                doc_id = item.get(key)
                if doc_id is not None:
                    out[str(doc_id)] = rank
            return out

        rank_s = rank_by_position(semantic)
        rank_k = rank_by_position(keyword)
        all_ids = set(rank_s.keys()) | set(rank_k.keys())

        # RRF: score(d) = sw/(k+rank_s) + kw/(k+rank_k)
        rrf_scores: Dict[str, float] = {}
        for doc_id in all_ids:
            rrf = 0.0
            if doc_id in rank_s:
                rrf += sw / (RRF_K + rank_s[doc_id])
            if doc_id in rank_k:
                rrf += kw / (RRF_K + rank_k[doc_id])
            rrf_scores[doc_id] = rrf

        # document_id -> 풀 레코드 (semantic 우선, 없으면 keyword)
        by_id: Dict[str, Dict] = {}
        for item in semantic:
            doc_id = str(item.get("document_id", ""))
            if doc_id and doc_id not in by_id:
                by_id[doc_id] = dict(item)
        for item in keyword:
            doc_id = str(item.get("document_id", ""))
            if doc_id and doc_id not in by_id:
                by_id[doc_id] = dict(item)

        # RRF 점수로 정렬, 점수 0~1 정규화
        sorted_ids = sorted(all_ids, key=lambda x: rrf_scores[x], reverse=True)
        max_rrf = max(rrf_scores.values()) if rrf_scores else 1.0
        results = []
        for doc_id in sorted_ids:
            rec = by_id.get(doc_id)
            if not rec:
                continue
            rec = dict(rec)
            rec["score"] = rrf_scores[doc_id] / max_rrf if max_rrf > 0 else 0.0
            rec["source"] = "hybrid"
            results.append(rec)
        return results

    def search_hybrid(
        self,
        db: Session,
        query: str,
        top_k: int = 10,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None,
        project_id: Optional[int] = None,
        label_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Hybrid 검색: 의미 + 키워드 후 RRF 결합.

        Args:
            db: DB 세션
            query: 검색 쿼리
            top_k: 반환 개수
            semantic_weight: 의미 가중치
            keyword_weight: 키워드 가중치
            filters: Qdrant 필터 (semantic 검색에만 적용)
            project_id: 프로젝트 필터 (keyword 검색에 적용)
            label_ids: 라벨 필터 (keyword 검색에 적용)

        Returns:
            RRF로 결합된 결과 리스트 (score 0~1, source="hybrid")
        """
        sem = self.semantic_search(query, top_k=top_k, filters=filters)
        kw = self.keyword_search(db, query, top_k=top_k, project_id=project_id, label_ids=label_ids)
        fused = self.fuse_results(sem, kw, semantic_weight, keyword_weight)
        return fused[:top_k]


def get_hybrid_search_service(
    semantic_weight: float = HYBRID_SEARCH_SEMANTIC_WEIGHT,
    keyword_weight: float = HYBRID_SEARCH_KEYWORD_WEIGHT,
) -> HybridSearchService:
    """HybridSearchService 인스턴스 반환."""
    return HybridSearchService(
        semantic_weight=semantic_weight,
        keyword_weight=keyword_weight,
    )
