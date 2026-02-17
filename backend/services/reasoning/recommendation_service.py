"""Reasoning 추천 서비스 — 관련 청크/라벨 추천 (Phase 9-3-1, Phase 16-4-1 리팩토링)

LLM 기반 메서드는 recommendation_llm.py Mixin에 분리되어 있습니다:
  - recommend_labels_with_llm, generate_sample_questions, suggest_exploration 등
"""
import logging
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from backend.models.models import (
    KnowledgeChunk,
    KnowledgeRelation,
    KnowledgeLabel,
    Label,
    Document,
)
from backend.services.search.hybrid_search import get_hybrid_search_service
from backend.services.reasoning.recommendation_llm import RecommendationLLMMixin

logger = logging.getLogger(__name__)


class RecommendationService(RecommendationLLMMixin):
    """관련 청크, 라벨, 샘플 질문, 탐색 제안을 생성하는 서비스."""

    def __init__(self, db: Session):
        self.db = db
        self.hybrid_search = get_hybrid_search_service()

    def recommend_related_chunks(
        self,
        chunk_ids: List[int],
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """관련 청크 추천: 관계·의미 검색·동일 라벨 기반.

        Returns:
            [{"chunk_id", "title", "content_preview", "similarity_score", "source", "document_name"}, ...]
        """
        if not chunk_ids or limit <= 0:
            return []
        limit = min(limit, 20)
        seen: set = set(chunk_ids)
        scored: List[tuple] = []  # (score, source, chunk_id, ...)

        # 1) 관계 기반
        relations = (
            self.db.query(KnowledgeRelation)
            .filter(
                (
                    KnowledgeRelation.source_chunk_id.in_(chunk_ids)
                    | KnowledgeRelation.target_chunk_id.in_(chunk_ids)
                ),
                KnowledgeRelation.confirmed == "true",
            )
            .limit(limit * 2)
            .all()
        )
        for rel in relations:
            other = (
                rel.target_chunk_id
                if rel.source_chunk_id in chunk_ids
                else rel.source_chunk_id
            )
            if other not in seen:
                seen.add(other)
                scored.append((0.9, "relation", other))

        # 2) Hybrid 검색: 첫 청크 내용으로 유사 검색
        first_chunk = (
            self.db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.id == chunk_ids[0], KnowledgeChunk.status == "approved")
            .first()
        )
        if first_chunk and first_chunk.content:
            try:
                hybrid_results = self.hybrid_search.search_hybrid(
                    db=self.db,
                    query=(first_chunk.content or "")[:300],
                    top_k=limit + len(chunk_ids),
                )
                for r in hybrid_results:
                    doc_id = r.get("document_id")
                    c = (
                        self.db.query(KnowledgeChunk)
                        .filter(
                            KnowledgeChunk.qdrant_point_id == str(doc_id),
                            KnowledgeChunk.status == "approved",
                        )
                        .first()
                    )
                    if c and c.id not in seen:
                        seen.add(c.id)
                        scored.append((float(r.get("score", 0.8)), "semantic", c.id))
            except Exception as e:
                logger.debug("recommend_related_chunks hybrid search: %s", e)

        # 3) 동일 라벨 청크
        label_ids = (
            self.db.query(KnowledgeLabel.label_id)
            .filter(KnowledgeLabel.chunk_id.in_(chunk_ids), KnowledgeLabel.status == "confirmed")
            .distinct()
            .all()
        )
        label_id_set = {lid[0] for lid in label_ids}
        if label_id_set:
            same_label_chunk_ids = (
                self.db.query(KnowledgeLabel.chunk_id)
                .filter(
                    KnowledgeLabel.label_id.in_(label_id_set),
                    KnowledgeLabel.status == "confirmed",
                    ~KnowledgeLabel.chunk_id.in_(chunk_ids),
                )
                .distinct()
                .limit(limit)
                .all()
            )
            for (cid,) in same_label_chunk_ids:
                if cid not in seen:
                    seen.add(cid)
                    scored.append((0.7, "label", cid))

        # 상위 limit개 조회해 문서/제목 매핑
        scored.sort(key=lambda x: (-x[0], x[2]))
        top_ids = [s[2] for s in scored[:limit]]
        if not top_ids:
            return []

        chunks = (
            self.db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.id.in_(top_ids), KnowledgeChunk.status == "approved")
            .all()
        )
        doc_ids = list({c.document_id for c in chunks})
        docs = {
            d.id: d
            for d in self.db.query(Document).filter(Document.id.in_(doc_ids)).all()
        }
        by_id = {c.id: c for c in chunks}
        score_map = {s[2]: (s[0], s[1]) for s in scored[:limit]}

        out = []
        for cid in top_ids:
            c = by_id.get(cid)
            if not c:
                continue
            sc, src = score_map.get(cid, (0.8, "semantic"))
            doc = docs.get(c.document_id)
            out.append({
                "chunk_id": c.id,
                "title": (c.title or (c.content or "")[:50] or "").strip(),
                "content_preview": (c.content or "")[:100],
                "similarity_score": round(sc, 2),
                "source": src,
                "document_name": doc.file_name if doc else (doc.file_path if doc else ""),
            })
        return out

    def recommend_labels(
        self,
        content: str,
        existing_label_ids: Optional[List[int]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """라벨 추천: content 키워드·유사 청크 라벨 기반.

        Returns:
            [{"label_id", "name", "label_type", "confidence", "source"}, ...]
        """
        if not content or not content.strip() or limit <= 0:
            return []
        limit = min(limit, 15)
        existing = set(existing_label_ids or [])
        scored: Dict[int, tuple] = {}  # label_id -> (confidence, source)

        # 1) content 단어로 Label 이름 매칭
        words = [w.strip().lower() for w in content.split() if len(w.strip()) >= 2]
        for w in words[:20]:
            labels = (
                self.db.query(Label)
                .filter(Label.name.ilike(f"%{w}%"))
                .limit(5)
                .all()
            )
            for lb in labels:
                if lb.id not in existing and lb.id not in scored:
                    scored[lb.id] = (0.85, "keyword")

        # 2) 유사 청크의 라벨
        try:
            hybrid_results = self.hybrid_search.search_hybrid(
                db=self.db,
                query=content[:400],
                top_k=5,
            )
            for r in hybrid_results:
                doc_id = r.get("document_id")
                chunk = (
                    self.db.query(KnowledgeChunk)
                    .filter(
                        KnowledgeChunk.qdrant_point_id == str(doc_id),
                        KnowledgeChunk.status == "approved",
                    )
                    .first()
                )
                if not chunk:
                    continue
                kl_list = (
                    self.db.query(KnowledgeLabel)
                    .filter(
                        KnowledgeLabel.chunk_id == chunk.id,
                        KnowledgeLabel.status == "confirmed",
                    )
                    .all()
                )
                for kl in kl_list:
                    if kl.label_id not in existing:
                        if kl.label_id not in scored:
                            scored[kl.label_id] = (float(r.get("score", 0.7)), "similar_chunk")
                        else:
                            old_c, _ = scored[kl.label_id]
                            scored[kl.label_id] = (max(old_c, float(r.get("score", 0.7))), "similar_chunk")
        except Exception as e:
            logger.debug("recommend_labels hybrid: %s", e)

        # 상위 limit개, 라벨 정보 조회
        sorted_labels = sorted(scored.items(), key=lambda x: -x[1][0])[:limit]
        label_ids_result = [lid for lid, _ in sorted_labels]
        labels = {l.id: l for l in self.db.query(Label).filter(Label.id.in_(label_ids_result)).all()}
        out = []
        for lid, (conf, src) in sorted_labels:
            lb = labels.get(lid)
            if not lb:
                continue
            out.append({
                "label_id": lb.id,
                "name": lb.name,
                "label_type": lb.label_type or "keyword",
                "confidence": round(conf, 2),
                "source": src,
            })
        return out


def get_recommendation_service(db: Session) -> RecommendationService:
    """RecommendationService 인스턴스 반환."""
    return RecommendationService(db=db)
