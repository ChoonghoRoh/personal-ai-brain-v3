"""라벨 엔드포인트 핸들러 (labels.py에서 분리)

라벨 CRUD, 키워드 그룹 관리, 청크-라벨 연결 등의 비즈니스 로직.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from typing import List, Optional

from backend.models.models import Label, KnowledgeLabel, KnowledgeChunk


# ---------------------------------------------------------------------------
# 라벨 CRUD
# ---------------------------------------------------------------------------

async def handle_create_label(label, db: Session):
    """라벨 생성"""
    existing = db.query(Label).filter(
        Label.name == label.name,
        Label.label_type == label.label_type,
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"같은 이름과 타입의 라벨이 이미 존재합니다 (name: {label.name}, type: {label.label_type})",
        )

    db_label = Label(**label.dict())
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label


async def handle_list_labels(
    label_type: Optional[str],
    q: Optional[str],
    limit: Optional[int],
    offset: int,
    db: Session,
):
    """라벨 목록 조회."""
    try:
        query = db.query(Label)
        if label_type:
            query = query.filter(Label.label_type == label_type)
        if q and q.strip():
            query = query.filter(Label.name.ilike(f"%{q.strip()}%"))
        if limit is not None:
            total = query.count()
            items = query.order_by(Label.id).offset(offset).limit(limit).all()
            return {"items": items, "total": total}
        return query.order_by(Label.id).all()
    except ProgrammingError as e:
        if "does not exist" in str(e.orig) if hasattr(e, "orig") else "does not exist" in str(e):
            return [] if limit is None else {"items": [], "total": 0}
        raise


async def handle_get_label(label_id: int, db: Session):
    """라벨 조회"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    return label


async def handle_get_label_impact(label_id: int, db: Session):
    """라벨 삭제 전 영향도 조회"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    chunks_count = db.query(KnowledgeLabel).filter(KnowledgeLabel.label_id == label_id).count()

    parent_group = None
    if label.parent_label_id:
        parent_group = db.query(Label).filter(Label.id == label.parent_label_id).first()

    child_labels_count = 0
    if label.label_type == "keyword_group":
        child_labels_count = db.query(Label).filter(Label.parent_label_id == label_id).count()

    return {
        "label_id": label_id,
        "label_name": label.name,
        "label_type": label.label_type,
        "chunks_count": chunks_count,
        "child_labels_count": child_labels_count,
        "parent_group": {
            "id": parent_group.id,
            "name": parent_group.name,
        } if parent_group else None,
    }


async def handle_delete_label(label_id: int, db: Session):
    """라벨 삭제"""
    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")
    db.delete(label)
    db.commit()
    return {"message": "라벨이 삭제되었습니다"}


# ---------------------------------------------------------------------------
# 키워드 그룹 관리
# ---------------------------------------------------------------------------

async def handle_list_keyword_groups(q: Optional[str], limit: int, offset: int, db: Session):
    """키워드 그룹 목록 조회"""
    query = db.query(Label).filter(Label.label_type == "keyword_group")

    if q:
        query = query.filter(Label.name.ilike(f"%{q}%"))

    return query.offset(offset).limit(limit).all()


async def handle_get_keyword_group(group_id: int, db: Session):
    """키워드 그룹 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")
    return group


async def handle_create_keyword_group(group, db: Session):
    """키워드 그룹 생성"""
    existing = db.query(Label).filter(
        Label.name == group.name,
        Label.label_type == "keyword_group",
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 그룹 이름입니다")

    db_group = Label(
        name=group.name,
        label_type="keyword_group",
        description=group.description if group.description else None,
        color=group.color if group.color else None,
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


async def handle_suggest_keywords(body, db: Session):
    """그룹 설명 기반 LLM 키워드 추천 + 기존 키워드 유사도 매칭 (Phase 7.7)"""
    from scripts.backend.extract_keywords_and_labels import extract_keywords_with_gpt4all, extract_keywords_with_regex

    description = (body.description or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="설명을 입력해주세요")

    MAX_DESCRIPTION_LENGTH = 1000
    if len(description) > MAX_DESCRIPTION_LENGTH:
        description = description[:MAX_DESCRIPTION_LENGTH] + "..."

    llm_keywords = []
    extraction_method = "regex"

    prompt = f"""다음 그룹 설명을 분석하여 관련 키워드를 추출해주세요.

그룹 설명:
{description}

요구사항:
1. 설명과 관련된 의미 있는 키워드만 추출
2. 불용어(것, 수, 등, 때 등)는 제외
3. 전문 용어나 개념을 우선
4. 키워드는 한글로, 2글자 이상
5. 상위 10개만 추출
6. 중국어(中文)나 일본어로 작성하지 마세요

키워드를 쉼표로 구분하여 나열해주세요. 설명 없이 키워드만 출력하세요.
예시: 인프라, 벡터, 데이터베이스, API, 시스템"""

    try:
        from backend.config import OLLAMA_MODEL_LIGHT
        use_model = body.model or OLLAMA_MODEL_LIGHT
        llm_keywords = extract_keywords_with_gpt4all(prompt, top_n=10, model=use_model)
        from backend.utils.korean_utils import postprocess_korean_keywords
        llm_keywords = postprocess_korean_keywords("\n".join(llm_keywords)) if llm_keywords else []
        extraction_method = "ollama"
    except Exception as e:
        print(f"Ollama error: {e}, falling back to regex...")
        llm_keywords = extract_keywords_with_regex(description, top_n=10)
        extraction_method = "regex"

    try:
        existing_keywords = db.query(Label).filter(
            Label.label_type == "keyword"
        ).all()
    except ProgrammingError:
        existing_keywords = []

    similar_keywords = []
    similar_keywords_with_score = []

    def calculate_similarity(keyword_name: str, desc: str) -> float:
        """간단한 유사도 계산 (0.0 ~ 1.0)"""
        keyword_lower = keyword_name.lower()
        desc_lower = desc.lower()

        if keyword_lower == desc_lower:
            return 1.0
        if keyword_lower in desc_lower:
            return 0.9
        if desc_lower in keyword_lower:
            return 0.8

        keyword_words = set(word for word in keyword_lower.split() if len(word) >= 2)
        desc_words = set(word for word in desc_lower.split() if len(word) >= 2)
        if keyword_words and desc_words:
            common_words = keyword_words.intersection(desc_words)
            if common_words:
                return min(0.7, len(common_words) / max(len(keyword_words), len(desc_words)))

        if len(keyword_lower) >= 2 and keyword_lower in desc_lower:
            return 0.6

        keyword_chars = set(keyword_lower)
        desc_chars = set(desc_lower)
        if keyword_chars and desc_chars:
            intersection = keyword_chars.intersection(desc_chars)
            union = keyword_chars.union(desc_chars)
            if union:
                jaccard = len(intersection) / len(union)
                if jaccard > 0.3:
                    return jaccard * 0.5

        return 0.0

    for keyword in existing_keywords:
        similarity = calculate_similarity(keyword.name, description)
        if similarity >= 0.3:
            if keyword.name not in similar_keywords:
                similar_keywords.append(keyword.name)
                similar_keywords_with_score.append({
                    "keyword": keyword.name,
                    "score": similarity,
                })

    similar_keywords_with_score.sort(key=lambda x: x["score"], reverse=True)
    similar_keywords = [item["keyword"] for item in similar_keywords_with_score]

    all_keywords = list(dict.fromkeys(llm_keywords + similar_keywords))

    return {
        "keywords": all_keywords[:15],
        "count": len(all_keywords),
        "llm_keywords": llm_keywords,
        "similar_keywords": similar_keywords[:10],
        "similar_keywords_with_score": similar_keywords_with_score[:10],
        "extraction_method": extraction_method,
    }


async def handle_update_keyword_group(group_id: int, group_update, db: Session):
    """키워드 그룹 수정"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

    if group_update.name is not None:
        group.name = group_update.name
    if group_update.description is not None:
        group.description = group_update.description
    if group_update.color is not None:
        group.color = group_update.color

    db.commit()
    db.refresh(group)
    return group


async def handle_get_group_impact(group_id: int, db: Session):
    """키워드 그룹 삭제 전 영향도 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

    keywords_count = db.query(Label).filter(Label.parent_label_id == group_id).count()

    group_keywords = db.query(Label).filter(Label.parent_label_id == group_id).all()
    keyword_ids = [kw.id for kw in group_keywords]
    chunks_count = 0
    if keyword_ids:
        chunks_count = db.query(KnowledgeLabel).filter(
            KnowledgeLabel.label_id.in_(keyword_ids)
        ).distinct(KnowledgeLabel.chunk_id).count()

    return {
        "group_id": group_id,
        "group_name": group.name,
        "keywords_count": keywords_count,
        "chunks_count": chunks_count,
    }


async def handle_delete_keyword_group(group_id: int, db: Session):
    """키워드 그룹 삭제"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

    db.query(Label).filter(Label.parent_label_id == group_id).update(
        {"parent_label_id": None}
    )

    db.delete(group)
    db.commit()
    return {"message": "키워드 그룹이 삭제되었습니다"}


async def handle_list_group_keywords(group_id: int, db: Session):
    """그룹 내 키워드 목록 조회"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

    keywords = db.query(Label).filter(
        Label.label_type == "keyword",
        Label.parent_label_id == group_id,
    ).all()

    return keywords


async def handle_add_keywords_to_group(group_id: int, request, db: Session):
    """그룹에 키워드 추가"""
    group = db.query(Label).filter(
        Label.id == group_id,
        Label.label_type == "keyword_group",
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

    added_count = 0
    errors = []
    skipped_count = 0

    if request.keyword_ids:
        keywords = db.query(Label).filter(
            Label.id.in_(request.keyword_ids),
            Label.label_type == "keyword",
        ).all()
        for keyword in keywords:
            try:
                if keyword.parent_label_id != group_id:
                    keyword.parent_label_id = group_id
                    added_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                errors.append(f"키워드 ID {keyword.id} 처리 중 오류: {str(e)}")

    if request.keyword_names:
        for keyword_name in request.keyword_names:
            if not keyword_name or not keyword_name.strip():
                continue

            keyword_name = keyword_name.strip()

            try:
                existing = db.query(Label).filter(
                    Label.name == keyword_name,
                    Label.label_type == "keyword",
                ).first()

                if existing:
                    if existing.parent_label_id != group_id:
                        existing.parent_label_id = group_id
                        added_count += 1
                    else:
                        skipped_count += 1
                else:
                    new_keyword = Label(
                        name=keyword_name,
                        label_type="keyword",
                        parent_label_id=group_id,
                    )
                    db.add(new_keyword)
                    added_count += 1
            except Exception as e:
                error_msg = f"'{keyword_name}' 처리 중 오류: {str(e)}"
                errors.append(error_msg)
                print(f"Warning: {error_msg}")
                continue

    try:
        db.commit()
        result = {
            "message": f"{added_count}개의 키워드가 그룹에 추가되었습니다",
            "added_count": added_count,
            "skipped_count": skipped_count,
        }
        if errors:
            result["errors"] = errors
            result["error_count"] = len(errors)
        return result
    except Exception as e:
        db.rollback()
        error_detail = str(e)
        print(f"DB error during keyword add: {error_detail}")
        raise HTTPException(status_code=500, detail=f"키워드 추가 중 오류: {error_detail}")


async def handle_remove_keyword_from_group(group_id: int, keyword_id: int, db: Session):
    """그룹에서 키워드 제거"""
    keyword = db.query(Label).filter(
        Label.id == keyword_id,
        Label.label_type == "keyword",
        Label.parent_label_id == group_id,
    ).first()
    if not keyword:
        raise HTTPException(status_code=404, detail="키워드를 찾을 수 없거나 그룹에 속하지 않습니다")

    keyword.parent_label_id = None
    db.commit()
    return {"message": "키워드가 그룹에서 제거되었습니다"}


# ---------------------------------------------------------------------------
# 청크-라벨 연결 (labels 라우터 쪽)
# ---------------------------------------------------------------------------

async def handle_add_label_to_chunk(chunk_id: int, label_id: int, confidence: float, db: Session):
    """청크에 라벨 추가"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    label = db.query(Label).filter(Label.id == label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    existing = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id,
        KnowledgeLabel.label_id == label_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 라벨이 추가되어 있습니다")

    knowledge_label = KnowledgeLabel(chunk_id=chunk_id, label_id=label_id, confidence=confidence)
    db.add(knowledge_label)
    db.commit()
    return {"message": "라벨이 추가되었습니다"}


async def handle_remove_label_from_chunk(chunk_id: int, label_id: int, db: Session):
    """청크에서 라벨 제거"""
    knowledge_label = db.query(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id,
        KnowledgeLabel.label_id == label_id,
    ).first()
    if not knowledge_label:
        raise HTTPException(status_code=404, detail="라벨을 찾을 수 없습니다")

    db.delete(knowledge_label)
    db.commit()
    return {"message": "라벨이 제거되었습니다"}


async def handle_get_chunk_labels(chunk_id: int, db: Session):
    """청크의 라벨 목록 조회"""
    chunk = db.query(KnowledgeChunk).filter(KnowledgeChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="청크를 찾을 수 없습니다")

    labels = db.query(Label).join(KnowledgeLabel).filter(
        KnowledgeLabel.chunk_id == chunk_id
    ).all()

    return [{"id": label.id, "name": label.name, "label_type": label.label_type} for label in labels]
