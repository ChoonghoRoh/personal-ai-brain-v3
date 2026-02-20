"""라벨 AI 추천 핸들러

LLM 기반 부모 노드 추천, 키워드 추천 등의 AI 추천 로직.
labels_handlers.py에서 분리됨 (Phase 17-8).
"""
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from backend.models.models import Label

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# AI 부모 노드 추천 (Phase 17-8)
# ---------------------------------------------------------------------------


def _build_tree_text(db: Session) -> str:
    """전체 트리를 들여쓰기 텍스트로 변환한다 (LLM 프롬프트용)."""
    roots = (
        db.query(Label)
        .filter(
            Label.parent_label_id.is_(None),
            Label.label_type == "keyword_group",
        )
        .order_by(Label.name)
        .all()
    )
    lines: List[str] = []

    def walk(label: Label, indent: int = 0) -> None:
        prefix = "  " * indent
        desc = f" - {label.description}" if label.description else ""
        lines.append(f"{prefix}[{label.name}]{desc}")
        children = (
            db.query(Label)
            .filter(Label.parent_label_id == label.id)
            .order_by(Label.name)
            .all()
        )
        for child in children:
            walk(child, indent + 1)

    for root in roots:
        walk(root)
    return "\n".join(lines)


async def handle_suggest_parent(body: Any, db: Session) -> Dict[str, Any]:
    """LLM 기반으로 새 키워드의 적합한 부모 그룹을 추천한다."""
    keyword_name = body.keyword_name.strip()
    if not keyword_name:
        raise HTTPException(status_code=400, detail="키워드 이름을 입력해주세요")

    tree_text = _build_tree_text(db)
    if not tree_text:
        return {
            "suggested_parent": None,
            "reason": "트리 구조가 비어 있습니다",
            "source": "fallback",
        }

    # LLM 호출 시도
    try:
        from backend.services.reasoning.recommendation_llm import resolve_model
        from backend.services.ai.ollama_client import ollama_generate, ollama_available

        if not ollama_available():
            raise RuntimeError("Ollama 사용 불가")

        use_model = resolve_model(body.model)
        prompt = (
            f"다음은 키워드 트리 구조입니다:\n{tree_text}\n\n"
            f"새 키워드 '{keyword_name}'이(가) 가장 적합한 부모 그룹(또는 키워드)의 이름을 추천하세요.\n"
            f"적합한 위치가 없으면 \"없음\"이라고 작성하세요.\n"
            f"부모 이름만 한 줄로 작성하세요."
        )
        raw = ollama_generate(prompt, max_tokens=100, temperature=0.3, model=use_model)
        if raw:
            suggested_name = raw.strip().split("\n")[0].strip().strip("[]")
            if suggested_name and suggested_name != "없음":
                # DB에서 매칭되는 그룹 찾기
                matched = (
                    db.query(Label)
                    .filter(
                        Label.name == suggested_name,
                        Label.label_type == "keyword_group",
                    )
                    .first()
                )
                if not matched:
                    # 부분 매칭 시도
                    matched = (
                        db.query(Label)
                        .filter(
                            Label.name.ilike(f"%{suggested_name}%"),
                            Label.label_type == "keyword_group",
                        )
                        .first()
                    )
                if matched:
                    return {
                        "suggested_parent": {"id": matched.id, "name": matched.name},
                        "reason": f"LLM이 '{keyword_name}'에 적합한 그룹으로 '{matched.name}'을(를) 추천했습니다",
                        "source": "llm",
                    }
            return {
                "suggested_parent": None,
                "reason": f"LLM이 적합한 부모 그룹을 찾지 못했습니다",
                "source": "llm",
            }
    except Exception as e:
        logger.warning("suggest_parent LLM 호출 실패: %s", e)

    # Fallback: 텍스트 유사도 매칭
    groups = (
        db.query(Label)
        .filter(Label.label_type == "keyword_group")
        .all()
    )
    keyword_lower = keyword_name.lower()
    best_match: Optional[Label] = None
    best_score = 0

    for group in groups:
        group_name_lower = group.name.lower()
        # 포함 관계 확인
        if keyword_lower in group_name_lower or group_name_lower in keyword_lower:
            score = len(group_name_lower)
            if score > best_score:
                best_score = score
                best_match = group
        # 설명에 키워드가 포함되는지 확인
        if group.description and keyword_lower in group.description.lower():
            score = len(group_name_lower) + 1
            if score > best_score:
                best_score = score
                best_match = group

    if best_match:
        return {
            "suggested_parent": {"id": best_match.id, "name": best_match.name},
            "reason": f"텍스트 매칭으로 '{best_match.name}' 그룹을 추천합니다",
            "source": "fallback",
        }

    return {
        "suggested_parent": None,
        "reason": "적합한 부모 그룹을 찾지 못했습니다",
        "source": "fallback",
    }


async def handle_suggest_keywords(body, db: Session):
    """그룹 설명 기반 키워드 추천 — RecommendationService 통일 (청크 추천과 동일 로직)"""
    from backend.services.reasoning.group_keyword_recommender import GroupKeywordRecommender
    from backend.services.ai.ollama_client import ollama_connection_check

    description = (body.description or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="설명을 입력해주세요")

    import re
    meaningful_text = re.sub(r'[^\w가-힣]', '', description)
    MIN_DESCRIPTION_LENGTH = 2
    if len(meaningful_text) < MIN_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"키워드를 추출할 수 있도록 {MIN_DESCRIPTION_LENGTH}자 이상의 의미 있는 설명을 입력해주세요",
        )

    MAX_DESCRIPTION_LENGTH = 1000
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"설명은 {MAX_DESCRIPTION_LENGTH}자 이하로 입력해주세요 (현재 {len(description)}자)",
        )

    ollama_feedback = ollama_connection_check()

    # 사용자가 모델을 지정한 경우, 설치된 모델 목록에 있는지 검증
    if body.model and ollama_feedback["available"]:
        installed = [m["name"] for m in ollama_feedback.get("models", [])]
        if body.model not in installed:
            raise HTTPException(
                status_code=400,
                detail=f"모델 '{body.model}'을(를) 찾을 수 없습니다. 사용 가능한 모델: {', '.join(installed)}",
            )

    # 그룹에 이미 소속된 키워드 조회 (중복 추천 방지)
    existing_label_ids = []
    existing_keyword_names = []
    if body.group_id:
        group_keywords = (
            db.query(Label)
            .filter(Label.parent_label_id == body.group_id, Label.label_type == "keyword")
            .all()
        )
        existing_label_ids = [kw.id for kw in group_keywords]
        existing_keyword_names = [kw.name for kw in group_keywords]

    recommender = GroupKeywordRecommender(db)
    result = recommender.recommend(
        description=description,
        existing_label_ids=existing_label_ids,
        existing_keyword_names=existing_keyword_names,
        limit=15,
        model=body.model,
    )

    suggestions = result.get("suggestions", [])
    new_keywords = result.get("new_keywords", [])

    # 그룹 기존 키워드와 이름이 동일한 new_keywords도 제외
    if existing_keyword_names:
        existing_lower = {n.lower() for n in existing_keyword_names}
        new_keywords = [kw for kw in new_keywords if kw.lower() not in existing_lower]

    return {
        "suggestions": suggestions,
        "new_keywords": new_keywords,
        "source": "llm",
        "ollama_feedback": ollama_feedback,
    }
