"""Reasoning 추천 서비스 — LLM 기반 추천/질문/탐색 Mixin (Phase 16-4-1, Phase 17-2 리팩토링)

recommendation_service.py에서 LLM 의존 메서드를 분리합니다.

Phase 17-2: 공통 유틸 함수 추출 + recommend_labels_with_llm 래퍼 전환.
  - 청크 추천 → ChunkLabelRecommender (chunk_label_recommender.py)
  - 그룹 추천 → GroupKeywordRecommender (group_keyword_recommender.py)
"""
import json
import logging
import re
from typing import List, Dict, Any, Optional, Set, Callable

from sqlalchemy.orm import Session

from backend.models.models import (
    KnowledgeChunk,
    KnowledgeLabel,
    Label,
    Document,
    Project,
    ReasoningResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 공통 유틸 함수 (Phase 17-2: 두 Recommender 에서 공유)
# ---------------------------------------------------------------------------


def extract_keywords_from_content(
    content: str,
    existing_label_names_lower: Optional[Set[str]] = None,
    limit: int = 10,
) -> List[str]:
    """텍스트에서 2글자 이상 단어/구를 추출해, 기존 라벨명에 없는 것만 반환 (fallback용)."""
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


def resolve_model(model: Optional[str] = None) -> str:
    """사용할 Ollama 모델 결정 (LIGHT → OLLAMA_MODEL 폴백)."""
    from backend.config import OLLAMA_MODEL_LIGHT, OLLAMA_MODEL
    from backend.services.ai.ollama_client import ollama_list_models

    use_model = model or OLLAMA_MODEL_LIGHT
    if not model:
        installed = [m["name"] for m in ollama_list_models()]
        if use_model not in installed and OLLAMA_MODEL in installed:
            use_model = OLLAMA_MODEL
            logger.info(
                "OLLAMA_MODEL_LIGHT(%s) 미설치, OLLAMA_MODEL(%s) 사용",
                OLLAMA_MODEL_LIGHT, OLLAMA_MODEL,
            )
    return use_model


def _is_single_concept_word(word: str) -> bool:
    """단일 개념어 판별 (공백 분리 허용 조건).

    - 한글만 2자 이상: "화성", "우주", "프로젝트"
    - 영어만 2자 이상: "AI", "backend", "design"
    """
    if not word or len(word) < 2:
        return False
    # 한글만
    if re.match(r"^[가-힣]{2,}$", word):
        return True
    # 영어만
    if re.match(r"^[a-zA-Z]{2,}$", word):
        return True
    return False


def generate_keywords_via_llm(prompt: str, model: str) -> Optional[List[str]]:
    """LLM 호출 → postprocess_korean_keywords → 조건부 공백 분리.

    분리 우선순위:
    1순위: 쉼표(,) / 세미콜론(;) 분리
    2순위: 개행(\n) 분리
    3순위: 공백 분리 (각 토큰이 단일 개념어인 경우만)
    """
    from backend.services.ai.ollama_client import ollama_generate
    from backend.utils.korean_utils import postprocess_korean_keywords

    raw = ollama_generate(prompt, max_tokens=300, temperature=0.3, model=model)
    if not raw:
        return None
    lines = postprocess_korean_keywords(raw)

    # 단일 라인인 경우 추가 분리 시도
    if len(lines) == 1 and lines[0]:
        single_line = lines[0]

        # 1순위: 쉼표/세미콜론 분리
        if "," in single_line or ";" in single_line:
            # postprocess_korean_keywords에서 이미 처리됨 (L104-107)
            pass
        # 2순위: 개행 분리
        elif "\n" in single_line:
            # postprocess_korean_keywords에서 이미 처리됨 (L100)
            pass
        # 3순위: 공백 분리 (단일 개념어만)
        elif " " in single_line and len(single_line.split()) >= 2:
            words = [w.strip() for w in single_line.split() if len(w.strip()) >= 2]
            # 모든 토큰이 단일 개념어인 경우에만 분리
            if words and all(_is_single_concept_word(w) for w in words):
                lines = words

    return lines if lines else None


def match_and_score_labels(
    db: Session,
    keywords: List[str],
    existing_ids: Set[int],
    all_label_names_lower: Set[str],
    limit: int,
) -> Dict[str, Any]:
    """LLM 추출 키워드를 DB 라벨과 3단계 계층 매칭하여 suggestions + new_keywords 생성.

    Tier 1: 정확 매칭 (모든 키워드) - base_conf
    Tier 2: 접두사 매칭 (3자 이상) - base_conf × 0.85
    Tier 3: 부분 매칭 (4자 이상) - base_conf × 0.7
    """
    from sqlalchemy import func

    scored: Dict[int, tuple] = {}
    matched_keywords: set = set()

    for i, keyword in enumerate(keywords[:15]):
        if not keyword or len(keyword) < 2:
            continue

        kw_clean = keyword.strip().lower()
        kw_len = len(kw_clean)
        base_conf = 0.9 - (i * 0.03)
        base_conf = max(0.5, min(base_conf, 0.9))

        matched_in_tier = False

        # Tier 1: 정확 매칭 (모든 키워드)
        tier1_labels = (
            db.query(Label)
            .filter(func.lower(Label.name) == kw_clean)
            .limit(5)
            .all()
        )
        if tier1_labels:
            matched_keywords.add(kw_clean)
            matched_in_tier = True
            for lb in tier1_labels:
                if lb.id not in existing_ids:
                    if lb.id not in scored or scored[lb.id][0] < base_conf:
                        scored[lb.id] = (base_conf, "llm")

        # Tier 2: 접두사 매칭 (3자 이상만)
        if not matched_in_tier and kw_len >= 3:
            tier2_labels = (
                db.query(Label)
                .filter(Label.name.ilike(f"{kw_clean}%"))
                .limit(5)
                .all()
            )
            # Tier 1 정확 매칭 제외
            tier2_labels = [lb for lb in tier2_labels if lb.name.lower() != kw_clean]
            if tier2_labels:
                matched_keywords.add(kw_clean)
                matched_in_tier = True
                tier2_conf = base_conf * 0.85
                for lb in tier2_labels:
                    if lb.id not in existing_ids:
                        if lb.id not in scored or scored[lb.id][0] < tier2_conf:
                            scored[lb.id] = (tier2_conf, "llm")

        # Tier 3: 부분 매칭 (4자 이상만)
        if not matched_in_tier and kw_len >= 4:
            tier3_labels = (
                db.query(Label)
                .filter(Label.name.ilike(f"%{kw_clean}%"))
                .limit(5)
                .all()
            )
            # Tier 1, 2 제외
            tier3_labels = [
                lb for lb in tier3_labels
                if lb.name.lower() != kw_clean and not lb.name.lower().startswith(kw_clean)
            ]
            if tier3_labels:
                matched_keywords.add(kw_clean)
                tier3_conf = base_conf * 0.7
                for lb in tier3_labels:
                    if lb.id not in existing_ids:
                        if lb.id not in scored or scored[lb.id][0] < tier3_conf:
                            scored[lb.id] = (tier3_conf, "llm")

    # new_keywords: Tier 1~3 모두 실패한 키워드만 분류
    new_keywords: List[str] = []
    for keyword in keywords[:15]:
        if not keyword or len(keyword) < 2:
            continue
        kw_clean = keyword.strip().lower()
        if kw_clean in matched_keywords:
            continue
        # exact match 체크 (all_label_names_lower는 정확 매칭용)
        if kw_clean in all_label_names_lower:
            continue
        if kw_clean not in [k.lower() for k in new_keywords]:
            new_keywords.append(keyword.strip())

    sorted_labels = sorted(scored.items(), key=lambda x: -x[1][0])[:limit]
    label_ids = [lid for lid, _ in sorted_labels]
    labels_map = {lb.id: lb for lb in db.query(Label).filter(Label.id.in_(label_ids)).all()}
    out: List[Dict[str, Any]] = []
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
    if not out and not new_keywords and keywords:
        new_keywords = [
            ln for ln in keywords[:10]
            if ln.strip() and ln.strip().lower() not in all_label_names_lower
        ][:10]
    return {"suggestions": out, "new_keywords": new_keywords[:10]}


def fallback_extract(
    content: str,
    existing_label_ids: Optional[List[int]],
    all_label_names_lower: Set[str],
    recommend_labels_fn: Optional[Callable] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    """LLM 실패 시 텍스트 기반 fallback."""
    suggestions: List[Dict[str, Any]] = []
    if recommend_labels_fn:
        suggestions = recommend_labels_fn(content, existing_label_ids=existing_label_ids, limit=limit)
    new_kw = extract_keywords_from_content(content, all_label_names_lower, limit=10)
    return {"suggestions": suggestions, "new_keywords": new_kw}


# ---------------------------------------------------------------------------
# Mixin 클래스
# ---------------------------------------------------------------------------


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
        """공통 함수 위임."""
        return extract_keywords_from_content(content, existing_label_names_lower, limit)

    def recommend_labels_with_llm(
        self,
        content: str,
        existing_label_ids: Optional[List[int]] = None,
        limit: int = 10,
        model: Optional[str] = None,
        chunk_id: Optional[int] = None,
        existing_keyword_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """[래퍼] 새 코드는 ChunkLabelRecommender / GroupKeywordRecommender 직접 사용 권장.

        기존 시그니처를 유지하며, chunk_id 여부에 따라 전용 Recommender로 위임합니다.
        """
        if chunk_id:
            from backend.services.reasoning.chunk_label_recommender import ChunkLabelRecommender

            recommender = ChunkLabelRecommender(
                self.db, self.hybrid_search,
                recommend_labels_fn=self.recommend_labels,
            )
            return recommender.recommend(
                chunk_id=chunk_id,
                content=content,
                existing_label_ids=existing_label_ids,
                limit=limit,
                model=model,
            )
        else:
            from backend.services.reasoning.group_keyword_recommender import GroupKeywordRecommender

            recommender = GroupKeywordRecommender(
                self.db,
                recommend_labels_fn=self.recommend_labels,
            )
            return recommender.recommend(
                description=content,
                existing_label_ids=existing_label_ids,
                existing_keyword_names=existing_keyword_names,
                limit=limit,
                model=model,
            )

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
