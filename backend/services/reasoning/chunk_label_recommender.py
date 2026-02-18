"""청크 라벨 추천 전용 Recommender (Phase 17-2)

청크 텍스트에서 키워드를 추출하여 기존 라벨 매칭 + 새 키워드를 반환합니다.
"""
import logging
from typing import List, Dict, Any, Optional, Callable

from sqlalchemy.orm import Session

from backend.models.models import (
    KnowledgeChunk,
    KnowledgeRelation,
    KnowledgeLabel,
    Label,
)

logger = logging.getLogger(__name__)


class ChunkLabelRecommender:
    """청크 텍스트 → 키워드 추출 전용 Recommender"""

    def __init__(self, db: Session, hybrid_search, recommend_labels_fn: Optional[Callable] = None):
        self.db = db
        self.hybrid_search = hybrid_search
        self._recommend_labels_fn = recommend_labels_fn

    def _gather_keyword_context(self, content: str, chunk_id: int) -> str:
        """추천 키워드 추론용 컨텍스트 수집: 유사 청크 라벨, 관계 청크 라벨, 기존 라벨 샘플."""
        parts: List[str] = []
        try:
            hybrid_results = self.hybrid_search.search_hybrid(
                db=self.db,
                query=(content or "")[:400],
                top_k=5,
            )
            similar_label_names: List[str] = []
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
                    lb = self.db.query(Label).filter(Label.id == kl.label_id).first()
                    if lb and lb.name not in similar_label_names:
                        similar_label_names.append(lb.name)
                if len(similar_label_names) >= 20:
                    break
            if similar_label_names:
                parts.append(f"참고 - 유사한 문서의 키워드: {', '.join(similar_label_names[:20])}")

            relations = (
                self.db.query(KnowledgeRelation)
                .filter(
                    (KnowledgeRelation.source_chunk_id == chunk_id)
                    | (KnowledgeRelation.target_chunk_id == chunk_id),
                    KnowledgeRelation.confirmed == "true",
                )
                .limit(10)
                .all()
            )
            related_label_names: List[str] = []
            for rel in relations:
                other_id = rel.target_chunk_id if rel.source_chunk_id == chunk_id else rel.source_chunk_id
                kl_list = (
                    self.db.query(KnowledgeLabel)
                    .filter(
                        KnowledgeLabel.chunk_id == other_id,
                        KnowledgeLabel.status == "confirmed",
                    )
                    .all()
                )
                for kl in kl_list:
                    lb = self.db.query(Label).filter(Label.id == kl.label_id).first()
                    if lb and lb.name not in related_label_names and lb.name not in similar_label_names:
                        related_label_names.append(lb.name)
            if related_label_names:
                parts.append(f"참고 - 관련 문서의 키워드: {', '.join(related_label_names[:20])}")

            all_labels = self.db.query(Label.name).distinct().limit(30).all()
            sample_names = [lb[0] for lb in all_labels]
            if sample_names:
                parts.append(f"참고 - 시스템 내 기존 키워드 (일부): {', '.join(sample_names)}")
        except Exception as e:
            logger.debug("_gather_keyword_context failed: %s", e)

        return "\n".join(parts)

    def recommend(
        self,
        chunk_id: int,
        content: str,
        existing_label_ids: Optional[List[int]] = None,
        limit: int = 10,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """청크 콘텐츠에서 키워드를 추출하여 기존 라벨 매칭 + 새 키워드 반환."""
        from backend.services.reasoning.recommendation_llm import (
            extract_keywords_from_content,
            resolve_model,
            generate_keywords_via_llm,
            match_and_score_labels,
            fallback_extract,
        )

        empty_result: Dict[str, Any] = {"suggestions": [], "new_keywords": []}
        if not content or not content.strip() or limit <= 0:
            return empty_result
        limit = min(limit, 15)
        existing = set(existing_label_ids or [])
        all_label_names_lower = {lb.name.lower() for lb in self.db.query(Label.name).distinct().all()}

        def _fallback() -> Dict[str, Any]:
            return fallback_extract(
                content, existing_label_ids, all_label_names_lower,
                recommend_labels_fn=self._recommend_labels_fn, limit=limit,
            )

        try:
            from backend.services.ai.ollama_client import ollama_available
            if not ollama_available():
                return _fallback()
        except Exception:
            return _fallback()

        text_slice = content.strip()[:2000]
        context_info = self._gather_keyword_context(content, chunk_id)
        if context_info:
            context_info = "\n\n" + context_info
        else:
            context_info = ""

        prompt = f"""다음 텍스트의 주제와 직접 관련된 핵심 키워드를 10개 이내로 추출하세요.
텍스트의 의미를 분석하여, 해당 주제를 설명하는 구체적인 키워드를 추출하세요.

규칙:
- 반드시 한국어로 작성하세요 (영어 전문 용어는 영어 소문자 허용)
- 중국어(中文), 일본어로 답변하지 마세요
- 번호나 불릿 없이 키워드만 한 줄에 하나씩 작성하세요
- 각 키워드는 1~3단어 이내로 작성하세요

텍스트:
{text_slice}
{context_info}
키워드 목록:"""

        try:
            use_model = resolve_model(model)
            keywords = generate_keywords_via_llm(prompt, use_model)
            if not keywords:
                return _fallback()
        except Exception as e:
            logger.debug("ChunkLabelRecommender LLM failed: %s", e)
            return _fallback()

        result = match_and_score_labels(self.db, keywords, existing, all_label_names_lower, limit)
        if not result["suggestions"] and not result["new_keywords"]:
            result["new_keywords"] = extract_keywords_from_content(content, all_label_names_lower, limit=10)
        return result
