"""Multi-hop RAG — 관계 추적 기반 다단계 검색 (Phase 9-3-3)"""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.config import MULTIHOP_MAX_DEPTH
from backend.models.models import KnowledgeChunk, KnowledgeRelation
from backend.services.search.hybrid_search import get_hybrid_search_service
from backend.services.search.search_service import get_search_service

logger = logging.getLogger(__name__)


class MultiHopRAG:
    """다단계 RAG: 초기 검색 → 관계 추적 → (선택) 추가 검색."""

    def __init__(self, max_hops: int = MULTIHOP_MAX_DEPTH):
        self.max_hops = max(1, min(max_hops, 5))

    def _initial_search(
        self,
        question: str,
        top_k: int = 5,
        db: Optional[Session] = None,
        use_hybrid: bool = True,
    ) -> List[Dict[str, Any]]:
        """Hop 1: 초기 검색 (의미 또는 Hybrid)."""
        if use_hybrid and db:
            svc = get_hybrid_search_service()
            return svc.search_hybrid(db=db, query=question, top_k=top_k)
        search_svc = get_search_service()
        result = search_svc.search(query=question, top_k=top_k, offset=0)
        rows = []
        for r in result.get("results", []):
            rows.append({
                "document_id": r.get("document_id", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0.0),
                "file": r.get("file", ""),
                "snippet": r.get("snippet", ""),
                "chunk_index": r.get("chunk_index", 0),
            })
        return rows

    def _follow_relations(
        self,
        db: Session,
        chunk_ids: List[int],
        visited: set,
        max_related: int = 10,
    ) -> List[int]:
        """관계로 연결된 청크 ID 추가 (중복·방문 제외)."""
        if not chunk_ids:
            return []
        new_ids = []
        for cid in chunk_ids:
            if cid in visited:
                continue
            rels = (
                db.query(KnowledgeRelation)
                .filter(
                    (KnowledgeRelation.source_chunk_id == cid)
                    | (KnowledgeRelation.target_chunk_id == cid)
                )
                .limit(max_related)
                .all()
            )
            for rel in rels:
                other = (
                    rel.target_chunk_id
                    if rel.source_chunk_id == cid
                    else rel.source_chunk_id
                )
                if other not in visited:
                    visited.add(other)
                    new_ids.append(other)
        return new_ids

    def _chunk_ids_from_results(
        self,
        db: Session,
        results: List[Dict[str, Any]],
    ) -> List[int]:
        """검색 결과의 document_id(Qdrant point id) → KnowledgeChunk.id 목록."""
        ids = []
        for r in results:
            doc_id = r.get("document_id")
            if not doc_id:
                continue
            chunk = (
                db.query(KnowledgeChunk)
                .filter(KnowledgeChunk.qdrant_point_id == str(doc_id))
                .first()
            )
            if chunk:
                ids.append(chunk.id)
        return ids

    def _chunks_to_results(
        self,
        db: Session,
        chunk_ids: List[int],
    ) -> List[Dict[str, Any]]:
        """청크 ID 목록 → 검색 결과 형식 (content, score, document_id, ...)."""
        if not chunk_ids:
            return []
        chunks = (
            db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.id.in_(chunk_ids))
            .all()
        )
        by_id = {c.id: c for c in chunks}
        out = []
        for cid in chunk_ids:
            c = by_id.get(cid)
            if not c:
                continue
            out.append({
                "document_id": c.qdrant_point_id or str(c.id),
                "content": c.content or "",
                "score": 0.8,
                "file": "",
                "snippet": (c.content or "")[:200] + ("..." if len(c.content or "") > 200 else ""),
                "chunk_index": c.chunk_index or 0,
                "chunk_id": c.id,
            })
        return out

    def search(
        self,
        db: Session,
        question: str,
        max_hops: Optional[int] = None,
        initial_top_k: int = 5,
        project_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Multi-hop 검색 실행.

        Returns:
            {
                "chunks": [검색 결과 형식],
                "hop_trace": [{"hop_number", "action", "chunk_ids_found", "query_used", "relation_type_followed"}],
                "total_hops_executed": int,
            }
        """
        depth = max_hops if max_hops is not None else self.max_hops
        depth = max(1, min(depth, 5))
        all_chunks: List[Dict[str, Any]] = []
        seen_doc_ids: set = set()
        hop_trace: List[Dict[str, Any]] = []
        visited_chunk_ids: set = set()

        # Hop 1: 초기 검색
        initial = self._initial_search(
            question, top_k=initial_top_k, db=db, use_hybrid=True
        )
        chunk_ids_1 = self._chunk_ids_from_results(db, initial)
        for r in initial:
            doc_id = r.get("document_id")
            if doc_id and doc_id not in seen_doc_ids:
                seen_doc_ids.add(doc_id)
                all_chunks.append(r)
        for cid in chunk_ids_1:
            visited_chunk_ids.add(cid)
        hop_trace.append({
            "hop_number": 1,
            "action": "search",
            "chunk_ids_found": chunk_ids_1,
            "query_used": question,
            "relation_type_followed": None,
        })

        if depth < 2:
            return {
                "chunks": all_chunks,
                "hop_trace": hop_trace,
                "total_hops_executed": 1,
            }

        # Hop 2: 관계 추적
        related_ids = self._follow_relations(
            db, chunk_ids_1, visited_chunk_ids, max_related=10
        )
        related_chunks = self._chunks_to_results(db, related_ids)
        for r in related_chunks:
            doc_id = r.get("document_id")
            if doc_id and doc_id not in seen_doc_ids:
                seen_doc_ids.add(doc_id)
                all_chunks.append(r)
        hop_trace.append({
            "hop_number": 2,
            "action": "follow_relation",
            "chunk_ids_found": related_ids,
            "query_used": None,
            "relation_type_followed": "knowledge_relation",
        })

        return {
            "chunks": all_chunks,
            "hop_trace": hop_trace,
            "total_hops_executed": 2,
        }


def get_multi_hop_rag(max_hops: Optional[int] = None) -> MultiHopRAG:
    """MultiHopRAG 인스턴스 반환."""
    return MultiHopRAG(max_hops=max_hops or MULTIHOP_MAX_DEPTH)
