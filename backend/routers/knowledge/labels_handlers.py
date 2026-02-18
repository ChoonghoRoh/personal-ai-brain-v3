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

async def handle_list_keyword_groups(
    q: Optional[str], limit: int, offset: int, db: Session,
    page: Optional[int] = None, size: int = 20,
):
    """키워드 그룹 목록 조회 (page/size 페이지네이션 지원)"""
    query = db.query(Label).filter(Label.label_type == "keyword_group")

    if q:
        query = query.filter(Label.name.ilike(f"%{q}%"))

    # page 파라미터가 있으면 페이지네이션 모드
    if page is not None:
        total = query.count()
        page_offset = (max(page, 1) - 1) * size
        items = query.order_by(Label.name).offset(page_offset).limit(size).all()
        return {"items": items, "total": total, "page": max(page, 1), "size": size}

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
    from backend.models.models import Label
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
