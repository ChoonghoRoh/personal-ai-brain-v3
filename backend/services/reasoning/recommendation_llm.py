"""Reasoning 추천 서비스 — LLM 기반 추천/질문/탐색 Mixin (Phase 16-4-1)

recommendation_service.py에서 LLM 의존 메서드를 분리합니다.
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional, Set

from sqlalchemy.orm import Session

from backend.models.models import (
    KnowledgeChunk,
    KnowledgeRelation,
    KnowledgeLabel,
    Label,
    Document,
    Project,
    ReasoningResult,
)

logger = logging.getLogger(__name__)


class RecommendationLLMMixin:
    """LLM 기반 추천/질문/탐색 메서드 Mixin

    RecommendationService에 합성됩니다.
    self.db, self.hybrid_search, self.recommend_labels 접근 필요.
    """

    def _extract_keywords_from_content(
        self,
        content: str,
        existing_label_names_lower: Optional[Set[str]] = None,
        limit: int = 10,
    ) -> List[str]:
        """청크 텍스트에서 2글자 이상 단어/구를 추출해, 기존 라벨명에 없는 것만 반환 (fallback용)."""
        if not content or not content.strip():
            return []
        existing = existing_label_names_lower or set()
        text = re.sub(r"[#*_`|\[\]()]", " ", content)
        tokens = re.findall(r"[가-힣a-zA-Z0-9]{2,}", text)
        seen: Set[str] = set()
        out: List[str] = []
        for t in tokens:
            low = t.lower()
            if low in seen:
                continue
            if any(low in ln or ln in low for ln in existing):
                continue
            seen.add(low)
            out.append(t.strip())
            if len(out) >= limit:
                break
        return out

    def _gather_keyword_context(self, content: str, chunk_id: Optional[int] = None) -> str:
        """추천 키워드 추론용 컨텍스트 수집: 유사 청크 라벨, 관계 청크 라벨, 기존 라벨 샘플."""
        parts: List[str] = []
        try:
            # 1) 유사 청크의 라벨 수집
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

            # 2) 관계 청크의 라벨 수집 (chunk_id가 있는 경우)
            if chunk_id:
                relations = (
                    self.db.query(KnowledgeRelation)
                    .filter(
                        (
                            KnowledgeRelation.source_chunk_id == chunk_id
                        ) | (
                            KnowledgeRelation.target_chunk_id == chunk_id
                        ),
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

            # 3) DB 전체 라벨 샘플
            all_labels = self.db.query(Label.name).distinct().limit(30).all()
            sample_names = [lb[0] for lb in all_labels]
            if sample_names:
                parts.append(f"참고 - 시스템 내 기존 키워드 (일부): {', '.join(sample_names)}")
        except Exception as e:
            logger.debug("_gather_keyword_context failed: %s", e)

        return "\n".join(parts)

    def recommend_labels_with_llm(
        self,
        content: str,
        existing_label_ids: Optional[List[int]] = None,
        limit: int = 10,
        model: Optional[str] = None,
        chunk_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """LLM(Ollama)으로 청크 내용에서 키워드 추출 후,
        (1) 기존 키워드 추천: DB 라벨과 매칭된 항목,
        (2) 새로운 키워드 추천: DB에 없는 LLM 추출 키워드(신설).
        """
        empty_result = {"suggestions": [], "new_keywords": []}
        if not content or not content.strip() or limit <= 0:
            return empty_result
        limit = min(limit, 15)
        existing = set(existing_label_ids or [])
        all_label_names_lower = {lb.name.lower() for lb in self.db.query(Label.name).distinct().all()}

        def _fallback_with_extract():
            fallback = self.recommend_labels(content, existing_label_ids=existing_label_ids, limit=limit)
            new_kw = self._extract_keywords_from_content(content, all_label_names_lower, limit=10)
            return {"suggestions": fallback, "new_keywords": new_kw}

        try:
            from backend.services.ai.ollama_client import ollama_generate, ollama_available
            if not ollama_available():
                return _fallback_with_extract()
        except Exception:
            return _fallback_with_extract()

        text_slice = (content or "").strip()[:2000]
        context_info = self._gather_keyword_context(content, chunk_id)
        if context_info:
            context_info = "\n\n" + context_info
        prompt = f"""다음 텍스트를 분석하여 핵심 키워드를 10개 이내로 추출하세요.
텍스트에 직접 언급되지 않더라도, 참고 정보를 바탕으로 관련성이 높은 키워드를 추론하여 포함하세요.

반드시 한국어 또는 영어 소문자 전문 용어로만 작성하세요.
중국어(中文), 일본어로 답변하지 마세요.
번호나 불릿 없이 키워드만 한 줄에 하나씩 작성하세요.

텍스트:
{text_slice}
{context_info}
키워드 목록:"""

        try:
            from backend.config import OLLAMA_MODEL_LIGHT
            use_model = model or OLLAMA_MODEL_LIGHT
            raw = ollama_generate(prompt, max_tokens=300, temperature=0.3, model=use_model)
            if not raw:
                return _fallback_with_extract()
            from backend.utils.korean_utils import postprocess_korean_keywords
            lines = postprocess_korean_keywords(raw)
            if not lines:
                return _fallback_with_extract()
        except Exception as e:
            logger.debug("recommend_labels_with_llm generate failed: %s", e)
            return _fallback_with_extract()

        scored: Dict[int, tuple] = {}
        matched_keywords: set = set()
        for i, keyword in enumerate(lines[:15]):
            if not keyword or len(keyword) < 2:
                continue
            kw_clean = keyword.strip().lower()
            labels = (
                self.db.query(Label)
                .filter(Label.name.ilike(f"%{kw_clean}%"))
                .limit(5)
                .all()
            )
            conf = 0.9 - (i * 0.03)
            conf = max(0.5, min(conf, 0.9))
            if labels:
                matched_keywords.add(kw_clean)
                for lb in labels:
                    if lb.id not in existing and (lb.id not in scored or scored[lb.id][0] < conf):
                        scored[lb.id] = (conf, "llm")

        all_label_names = all_label_names_lower
        new_keywords = []
        for keyword in lines[:15]:
            if not keyword or len(keyword) < 2:
                continue
            kw_clean = keyword.strip().lower()
            if kw_clean in matched_keywords:
                continue
            if any(kw_clean in ln or ln in kw_clean for ln in all_label_names):
                continue
            if kw_clean not in [k.lower() for k in new_keywords]:
                new_keywords.append(keyword.strip())

        sorted_labels = sorted(scored.items(), key=lambda x: -x[1][0])[:limit]
        label_ids = [lid for lid, _ in sorted_labels]
        labels_map = {l.id: l for l in self.db.query(Label).filter(Label.id.in_(label_ids)).all()}
        out = []
        for lid, (conf, src) in sorted_labels:
            lb = labels_map.get(lid)
            if not lb:
                continue
            out.append({
                "label_id": lb.id,
                "name": lb.name,
                "label_type": lb.label_type or "keyword",
                "confidence": round(conf, 2),
                "source": src,
            })
        if not out and not new_keywords and lines:
            new_keywords = [
                ln for ln in lines[:10]
                if ln.strip() and ln.strip().lower() not in all_label_names
            ][:10]
        if not out and not new_keywords:
            new_keywords = self._extract_keywords_from_content(content, all_label_names, limit=10)
        return {"suggestions": out, "new_keywords": new_keywords[:10]}

    def generate_sample_questions(
        self,
        project_id: Optional[int] = None,
        label_ids: Optional[List[int]] = None,
        limit: int = 3,
        model: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """샘플 질문 생성: 청크 컨텍스트 기반 LLM 호출 (Ollama). 실패 시 빈 목록."""
        limit = min(limit, 10)
        chunks = (
            self.db.query(KnowledgeChunk)
            .filter(KnowledgeChunk.status == "approved")
            .limit(30)
            .all()
        )
        if project_id is not None:
            chunks = [
                c
                for c in chunks
                if c.document_id
                and self.db.query(Document)
                .filter(Document.id == c.document_id, Document.project_id == project_id)
                .first()
            ]
        if label_ids:
            chunk_ids_with_label = (
                self.db.query(KnowledgeLabel.chunk_id)
                .filter(
                    KnowledgeLabel.label_id.in_(label_ids),
                    KnowledgeLabel.status == "confirmed",
                )
                .distinct()
                .all()
            )
            cid_set = {r[0] for r in chunk_ids_with_label}
            chunks = [c for c in chunks if c.id in cid_set]
        if not chunks:
            return []

        context_parts = [(c.content or "")[:200] for c in chunks[:10]]
        context_text = "\n\n".join(context_parts)
        if len(context_text) > 2000:
            context_text = context_text[:2000] + "..."

        try:
            from backend.services.ai.ollama_client import ollama_generate, ollama_available
            if not ollama_available():
                return []
            prompt = f"""다음 지식을 바탕으로 사용자가 물어볼 수 있는 질문 {limit}개를 한 줄씩만 생성하세요.
반드시 한국어로만 작성하세요. 중국어(中文)로 작성하지 마세요.
지식:
{context_text}

질문 목록 (번호 없이 한 줄에 하나씩):"""
            from backend.config import OLLAMA_MODEL_LIGHT
            use_model = model or OLLAMA_MODEL_LIGHT
            raw = ollama_generate(prompt, max_tokens=300, temperature=0.7, model=use_model)
            if not raw:
                return []
            from backend.utils.korean_utils import postprocess_korean_text
            raw = postprocess_korean_text(raw)
            if not raw:
                return []
            lines = [ln.strip() for ln in raw.strip().split("\n") if ln.strip() and not ln.strip().startswith("#")]
            questions = []
            for i, q in enumerate(lines[:limit]):
                if len(q) > 10:
                    questions.append({
                        "question": q,
                        "suggested_mode": "design_explain" if i % 3 == 0 else "risk_review" if i % 3 == 1 else "next_steps",
                        "related_chunk_ids": [c.id for c in chunks[:3]],
                        "topic": "general",
                    })
            return questions
        except Exception as e:
            logger.warning("generate_sample_questions LLM failed: %s", e)
            return []

    def suggest_exploration(
        self,
        context_chunk_ids: Optional[List[int]] = None,
        reasoning_result_id: Optional[int] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """추가 탐색 제안: 컨텍스트 청크 기반 관련 프로젝트/라벨/질문 제안."""
        if limit <= 0:
            return []
        limit = min(limit, 10)
        out: List[Dict[str, Any]] = []

        chunk_ids = list(context_chunk_ids or [])
        if reasoning_result_id is not None:
            res = self.db.query(ReasoningResult).filter(ReasoningResult.id == reasoning_result_id).first()
            if res and res.context_chunks:
                try:
                    data = json.loads(res.context_chunks) if isinstance(res.context_chunks, str) else res.context_chunks
                    if isinstance(data, list):
                        for c in data:
                            if isinstance(c, dict) and c.get("id"):
                                chunk_ids.append(c["id"])
                except Exception:
                    pass

        if not chunk_ids:
            projects = self.db.query(Project).limit(3).all()
            for p in projects:
                out.append({
                    "type": "project",
                    "id": p.id,
                    "name": p.name,
                    "description": (p.description or "")[:100],
                    "relevance": 0.5,
                })
            return out[:limit]

        # 관련 프로젝트
        doc_ids = (
            self.db.query(KnowledgeChunk.document_id)
            .filter(KnowledgeChunk.id.in_(chunk_ids))
            .distinct()
            .all()
        )
        doc_id_set = {d[0] for d in doc_ids if d[0]}
        if doc_id_set:
            projects = (
                self.db.query(Project)
                .join(Document, Document.project_id == Project.id)
                .filter(Document.id.in_(doc_id_set))
                .distinct()
                .limit(3)
                .all()
            )
            for p in projects:
                out.append({
                    "type": "project",
                    "id": p.id,
                    "name": p.name,
                    "description": (p.description or "")[:100] or "관련 프로젝트",
                    "relevance": 0.75,
                })

        # 관련 라벨
        label_ids = (
            self.db.query(KnowledgeLabel.label_id)
            .filter(KnowledgeLabel.chunk_id.in_(chunk_ids), KnowledgeLabel.status == "confirmed")
            .distinct()
            .limit(5)
            .all()
        )
        lid_set = [r[0] for r in label_ids]
        if lid_set:
            labels = self.db.query(Label).filter(Label.id.in_(lid_set)).all()
            for lb in labels:
                out.append({
                    "type": "label",
                    "id": lb.id,
                    "name": lb.name,
                    "description": (lb.description or "")[:100] or f"라벨: {lb.name}",
                    "relevance": 0.68,
                })

        return out[:limit]
