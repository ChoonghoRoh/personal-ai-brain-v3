"""라벨 CRUD 핸들러

라벨 기본 CRUD, 키워드 그룹 관리, 청크-라벨 연결 등의 비즈니스 로직.
labels_handlers.py에서 분리됨.
"""
import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError
from typing import Any, Dict, List, Optional

from backend.models.models import Label, KnowledgeLabel, KnowledgeChunk

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Qdrant 유사도 검색 헬퍼 (graceful fallback)
# ---------------------------------------------------------------------------

def _try_qdrant_similarity_search(query: str, exclude_ids: List[int], limit: int) -> List[Dict[str, Any]]:
    """Qdrant 유사도 검색 시도 (실패 시 빈 리스트 반환)

    Args:
        query: 검색어
        exclude_ids: 제외할 Label ID 목록
        limit: 최대 결과 수

    Returns:
        [{"id": int, "name": str, "similarity_score": float, "source": "qdrant"}, ...]
    """
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchAny
        from sentence_transformers import SentenceTransformer
        from backend.config import QDRANT_HOST, QDRANT_PORT, EMBEDDING_MODEL

        # Qdrant 컬렉션 이름 (라벨용, 실제 프로젝트에 맞게 조정 필요)
        LABEL_COLLECTION = "labels"  # 라벨 임베딩 컬렉션이 있다면

        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        model = SentenceTransformer(EMBEDDING_MODEL)

        # 쿼리 임베딩 생성
        query_vector = model.encode(query).tolist()

        # Qdrant 검색 (exclude_ids 제외)
        search_filter = None
        if exclude_ids:
            search_filter = Filter(
                must_not=[
                    FieldCondition(
                        key="label_id",
                        match=MatchAny(any=exclude_ids)
                    )
                ]
            )

        results = client.search(
            collection_name=LABEL_COLLECTION,
            query_vector=query_vector,
            limit=limit,
            query_filter=search_filter,
        )

        return [
            {
                "id": hit.payload.get("label_id"),
                "name": hit.payload.get("name"),
                "similarity_score": hit.score,
                "source": "qdrant"
            }
            for hit in results
            if hit.payload.get("label_id") is not None
        ]

    except Exception as e:
        logger.info(f"Qdrant 유사도 검색 실패 (fallback to text search): {e}")
        return []


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


# ---------------------------------------------------------------------------
# Phase 18-1: 연관 키워드 조회 (ILIKE + Qdrant 유사도)
# ---------------------------------------------------------------------------

async def handle_get_related_keywords(
    group_id: int,
    q: Optional[str],
    limit: int,
    db: Session,
) -> Dict[str, Any]:
    """그룹 연관 키워드 조회 (ILIKE + Qdrant 유사도)

    Args:
        group_id: 키워드 그룹 ID
        q: 검색어 (ILIKE 사용, 없으면 전체 키워드)
        limit: 최대 결과 수
        db: 데이터베이스 세션

    Returns:
        {
            "items": [
                {"id": int, "name": str, "similarity_score": float, "source": "text"|"qdrant"},
                ...
            ],
            "total": int
        }
    """
    try:
        # 1. 그룹 존재 확인
        group = db.query(Label).filter(
            Label.id == group_id,
            Label.label_type == "keyword_group",
        ).first()
        if not group:
            raise HTTPException(status_code=404, detail="키워드 그룹을 찾을 수 없습니다")

        # 2. 그룹 소속 키워드 ID 목록 조회 → 제외 목록
        group_keyword_ids = [
            row[0] for row in db.query(Label.id).filter(
                Label.label_type == "keyword",
                Label.parent_label_id == group_id,
            ).all()
        ]

        # 3. ILIKE 텍스트 검색
        text_query = db.query(Label).filter(
            Label.label_type == "keyword",
            Label.id.notin_(group_keyword_ids) if group_keyword_ids else True,
        )

        if q and q.strip():
            text_query = text_query.filter(Label.name.ilike(f"%{q.strip()}%"))

        text_results = text_query.limit(limit * 2).all()  # Qdrant와 병합 위해 여유있게 조회

        # ILIKE 결과를 딕셔너리로 변환
        text_items = [
            {
                "id": label.id,
                "name": label.name,
                "similarity_score": 0.5,  # 기본 점수
                "source": "text"
            }
            for label in text_results
        ]

        # 4. Qdrant 유사도 검색 (q가 있을 때만 시도)
        qdrant_items: List[Dict[str, Any]] = []
        if q and q.strip():
            qdrant_items = _try_qdrant_similarity_search(
                query=q.strip(),
                exclude_ids=group_keyword_ids,
                limit=limit * 2,
            )

        # 5. 두 결과 병합, 중복 제거 (id 기준)
        merged_dict: Dict[int, Dict[str, Any]] = {}

        # ILIKE 결과 먼저 추가
        for item in text_items:
            merged_dict[item["id"]] = item

        # Qdrant 결과 병합 (높은 점수로 덮어쓰기)
        for item in qdrant_items:
            label_id = item["id"]
            if label_id in merged_dict:
                # 기존 항목보다 점수가 높으면 덮어쓰기
                if item["similarity_score"] > merged_dict[label_id]["similarity_score"]:
                    merged_dict[label_id] = item
            else:
                merged_dict[label_id] = item

        # 6. similarity_score 기준 정렬
        sorted_items = sorted(
            merged_dict.values(),
            key=lambda x: x["similarity_score"],
            reverse=True
        )

        # 7. 상위 limit개 반환
        final_items = sorted_items[:limit]

        return {
            "items": final_items,
            "total": len(final_items),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"연관 키워드 조회 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"연관 키워드 조회 중 오류: {str(e)}")
