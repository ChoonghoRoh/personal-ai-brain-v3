"""키워드 그룹 추천 전용 Recommender (Phase 17-2)

키워드 그룹 설명의 의미를 해석하여 소속 키워드를 생성합니다.
"""
import logging
from typing import List, Dict, Any, Optional, Callable

from sqlalchemy.orm import Session

from backend.models.models import Label

logger = logging.getLogger(__name__)


class GroupKeywordRecommender:
    """키워드 그룹 설명 → 키워드 생성 전용 Recommender"""

    def __init__(self, db: Session, recommend_labels_fn: Optional[Callable] = None):
        self.db = db
        self._recommend_labels_fn = recommend_labels_fn

    def recommend(
        self,
        description: str,
        existing_label_ids: Optional[List[int]] = None,
        existing_keyword_names: Optional[List[str]] = None,
        limit: int = 10,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """그룹 설명의 의미를 해석하여 소속 키워드를 생성."""
        from backend.services.reasoning.recommendation_llm import (
            extract_keywords_from_content,
            resolve_model,
            generate_keywords_via_llm,
            match_and_score_labels,
            fallback_extract,
        )

        empty_result: Dict[str, Any] = {"suggestions": [], "new_keywords": []}
        if not description or not description.strip() or limit <= 0:
            return empty_result
        limit = min(limit, 15)
        existing = set(existing_label_ids or [])
        all_label_names_lower = {lb.name.lower() for lb in self.db.query(Label.name).distinct().all()}

        def _fallback() -> Dict[str, Any]:
            return fallback_extract(
                description, existing_label_ids, all_label_names_lower,
                recommend_labels_fn=self._recommend_labels_fn, limit=limit,
            )

        try:
            from backend.services.ai.ollama_client import ollama_available
            if not ollama_available():
                return _fallback()
        except Exception:
            return _fallback()

        text_slice = description.strip()[:2000]

        existing_kw_context = ""
        if existing_keyword_names:
            existing_kw_context = f"""
이미 등록된 키워드 (아래 키워드는 추천하지 마세요):
{', '.join(existing_keyword_names)}
"""

        prompt = f"""다음은 키워드 그룹의 설명입니다.
이 그룹에 포함될 구체적인 키워드를 10개 이내로 추천하세요.

중요: 설명 텍스트에 나오는 단어를 그대로 나열하지 말고,
설명의 의미를 해석하여 이 그룹에 실제로 소속될 구체적인 항목·용어·이름을 추천하세요.

예시:
- "고양이 품종 모음" → 페르시안, 샴, 러시안블루, 코리안숏헤어 등 실제 품종명
- "프로그래밍 언어" → python, java, javascript, go 등 실제 언어명
- "SI 프로젝트 역할" → PM, PL, 아키텍트, QA 등 실제 역할명

규칙:
- 반드시 한국어로 작성하세요 (영어 고유명사·전문 용어는 영어 허용)
- 중국어(中文), 일본어로 답변하지 마세요
- 번호나 불릿 없이 키워드만 한 줄에 하나씩 작성하세요
- 각 키워드는 1~3단어 이내로 작성하세요

그룹 설명:
{text_slice}
{existing_kw_context}
추천 키워드 목록:"""

        try:
            use_model = resolve_model(model)
            keywords = generate_keywords_via_llm(prompt, use_model)
            if not keywords:
                return _fallback()
        except Exception as e:
            logger.debug("GroupKeywordRecommender LLM failed: %s", e)
            return _fallback()

        result = match_and_score_labels(self.db, keywords, existing, all_label_names_lower, limit)
        if not result["suggestions"] and not result["new_keywords"]:
            result["new_keywords"] = extract_keywords_from_content(description, all_label_names_lower, limit=10)
        return result
