"""Reasoning 추천 서비스 — 관련 청크/라벨/샘플 질문/탐색 제안 (Phase 9-3-1)"""
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
from backend.services.search.hybrid_search import get_hybrid_search_service

logger = logging.getLogger(__name__)


class RecommendationService:
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
        label_ids = [lid for lid, _ in sorted_labels]
        labels = {l.id: l for l in self.db.query(Label).filter(Label.id.in_(label_ids)).all()}
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
        # 마크다운/특수문자 제거 후 공백·줄바꿈으로 분리
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

    def recommend_labels_with_llm(
        self,
        content: str,
        existing_label_ids: Optional[List[int]] = None,
        limit: int = 10,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """LLM(Ollama)으로 청크 내용에서 키워드 추출 후,
        (1) 기존 키워드 추천: DB 라벨과 매칭된 항목,
        (2) 새로운 키워드 추천: DB에 없는 LLM 추출 키워드(신설).

        Returns:
            {
                "suggestions": [{"label_id", "name", "label_type", "confidence", "source": "llm"}, ...],
                "new_keywords": ["키워드1", "키워드2", ...]  # DB에 없는 새 키워드
            }
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
        prompt = f"""다음 텍스트를 요약하는 키워드 또는 짧은 구문을 10개 이내로 한 줄에 하나씩만 나열하세요.
키워드는 영어 소문자나 한글 단어/구로 짧게 작성하세요. 번호나 불릿 없이 키워드만 한 줄에 하나씩 작성하세요.

텍스트:
{text_slice}

키워드 목록:"""

        try:
            raw = ollama_generate(prompt, max_tokens=300, temperature=0.3, model=model)
            if not raw:
                return _fallback_with_extract()
            lines = [
                ln.strip().lstrip("-*0123456789.) ")
                for ln in raw.strip().split("\n")
                if ln.strip() and len(ln.strip()) >= 2
            ]
            if not lines:
                # 쉼표/세미콜론으로도 분리 시도
                for sep in (",", ";", "、"):
                    if sep in raw:
                        lines = [x.strip() for x in raw.split(sep) if x.strip() and len(x.strip()) >= 2]
                        break
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
        # LLM이 키워드를 줬는데 매칭/필터 후 둘 다 비면, 추출 키워드로 새 키워드 채우기
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
            raw = ollama_generate(prompt, max_tokens=300, temperature=0.7, model=model)
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
                import json
                try:
                    data = json.loads(res.context_chunks) if isinstance(res.context_chunks, str) else res.context_chunks
                    if isinstance(data, list):
                        for c in data:
                            if isinstance(c, dict) and c.get("id"):
                                chunk_ids.append(c["id"])
                except Exception:
                    pass

        if not chunk_ids:
            # 전체 프로젝트/라벨에서 인기 항목
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


def get_recommendation_service(db: Session) -> RecommendationService:
    """RecommendationService 인스턴스 반환."""
    return RecommendationService(db=db)
