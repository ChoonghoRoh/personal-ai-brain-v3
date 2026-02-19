"""라벨 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, field_serializer

from backend.models.database import get_db

# --- 핸들러 import (labels_handlers.py) ---
from backend.routers.knowledge.labels_handlers import (
    handle_create_label,
    handle_list_labels,
    handle_get_label,
    handle_get_label_impact,
    handle_delete_label,
    handle_list_keyword_groups,
    handle_get_keyword_group,
    handle_create_keyword_group,
    handle_suggest_keywords,
    handle_update_keyword_group,
    handle_get_group_impact,
    handle_delete_keyword_group,
    handle_list_group_keywords,
    handle_add_keywords_to_group,
    handle_remove_keyword_from_group,
    handle_add_label_to_chunk,
    handle_remove_label_from_chunk,
    handle_get_chunk_labels,
    # Phase 17-8: 트리 + 이동 + AI 추천
    handle_get_label_tree,
    handle_get_group_tree,
    handle_move_label,
    handle_get_breadcrumb,
    handle_suggest_parent,
)

router = APIRouter(prefix="/api/labels", tags=["Labels"])


# --- Pydantic 모델 ---

class LabelCreate(BaseModel):
    name: str
    label_type: str
    description: str = None
    parent_label_id: int = None
    color: str = None


class LabelResponse(BaseModel):
    id: int
    name: str
    label_type: str
    description: Optional[str] = None
    parent_label_id: Optional[int] = None
    color: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        if dt is None:
            return None
        return dt.isoformat()

    class Config:
        from_attributes = True


class KeywordGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class KeywordGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class GroupKeywordsAdd(BaseModel):
    keyword_ids: List[int] = None
    keyword_names: List[str] = None


class SuggestKeywordsRequest(BaseModel):
    description: str = ""
    model: Optional[str] = None
    group_id: Optional[int] = None


class MoveRequest(BaseModel):
    new_parent_id: Optional[int] = None


class SuggestParentRequest(BaseModel):
    keyword_name: str
    model: Optional[str] = None


# --- 엔드포인트 ---

@router.post("", response_model=LabelResponse)
async def create_label(label: LabelCreate, db: Session = Depends(get_db)):
    """라벨 생성"""
    return await handle_create_label(label, db)


@router.get("")
async def list_labels(
    label_type: Optional[str] = None,
    q: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """라벨 목록 조회."""
    return await handle_list_labels(label_type, q, limit, offset, db)


# ========== Phase 17-8: 트리 조회 + AI 추천 (/{label_id} 라우트보다 먼저 정의) ==========

@router.get("/tree")
async def get_label_tree(
    max_depth: int = 5,
    db: Session = Depends(get_db),
):
    """전체 트리 조회 (keyword_group 루트 + 재귀 하위 노드)"""
    return await handle_get_label_tree(max_depth, db)


@router.post("/suggest-parent")
async def suggest_parent(
    body: SuggestParentRequest,
    db: Session = Depends(get_db),
):
    """AI 부모 노드 추천 (LLM 기반 트리 분석)"""
    return await handle_suggest_parent(body, db)


# ========== Phase 7.7: 키워드 그룹 관리 API (/{label_id} 라우트보다 먼저 정의) ==========

@router.get("/groups")
async def list_keyword_groups(
    q: Optional[str] = None,
    page: Optional[int] = None,
    size: int = 20,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """키워드 그룹 목록 조회 (page/size 페이지네이션 또는 limit/offset)"""
    return await handle_list_keyword_groups(q, limit, offset, db, page=page, size=size)


@router.get("/groups/{group_id}/tree")
async def get_group_tree(
    group_id: int,
    max_depth: int = 5,
    db: Session = Depends(get_db),
):
    """특정 그룹의 하위 트리 조회"""
    return await handle_get_group_tree(group_id, max_depth, db)


@router.get("/groups/{group_id}", response_model=LabelResponse)
async def get_keyword_group(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 조회"""
    return await handle_get_keyword_group(group_id, db)


@router.post("/groups", response_model=LabelResponse)
async def create_keyword_group(group: KeywordGroupCreate, db: Session = Depends(get_db)):
    """키워드 그룹 생성"""
    return await handle_create_keyword_group(group, db)


@router.post("/groups/suggest-keywords")
async def suggest_keywords_from_description(
    body: SuggestKeywordsRequest,
    db: Session = Depends(get_db),
):
    """그룹 설명 기반 LLM 키워드 추천 + 기존 키워드 유사도 매칭 (Phase 7.7)"""
    return await handle_suggest_keywords(body, db)


@router.patch("/groups/{group_id}", response_model=LabelResponse)
async def update_keyword_group(
    group_id: int,
    group_update: KeywordGroupUpdate,
    db: Session = Depends(get_db),
):
    """키워드 그룹 수정"""
    return await handle_update_keyword_group(group_id, group_update, db)


@router.get("/groups/{group_id}/impact")
async def get_group_impact(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 삭제 전 영향도 조회"""
    return await handle_get_group_impact(group_id, db)


@router.delete("/groups/{group_id}")
async def delete_keyword_group(group_id: int, db: Session = Depends(get_db)):
    """키워드 그룹 삭제"""
    return await handle_delete_keyword_group(group_id, db)


@router.get("/groups/{group_id}/keywords", response_model=List[LabelResponse])
async def list_group_keywords(group_id: int, db: Session = Depends(get_db)):
    """그룹 내 키워드 목록 조회"""
    return await handle_list_group_keywords(group_id, db)


@router.post("/groups/{group_id}/keywords")
async def add_keywords_to_group(
    group_id: int,
    request: GroupKeywordsAdd,
    db: Session = Depends(get_db),
):
    """그룹에 키워드 추가"""
    return await handle_add_keywords_to_group(group_id, request, db)


@router.delete("/groups/{group_id}/keywords/{keyword_id}")
async def remove_keyword_from_group(
    group_id: int,
    keyword_id: int,
    db: Session = Depends(get_db),
):
    """그룹에서 키워드 제거"""
    return await handle_remove_keyword_from_group(group_id, keyword_id, db)


# ========== Phase 17-8: 노드 이동 + Breadcrumb (/{label_id} GET/DELETE 보다 먼저 정의) ==========

@router.patch("/{label_id}/move")
async def move_label(
    label_id: int,
    body: MoveRequest,
    db: Session = Depends(get_db),
):
    """노드 이동 (parent_label_id 변경)"""
    return await handle_move_label(label_id, body.new_parent_id, db)


@router.get("/{label_id}/breadcrumb")
async def get_breadcrumb(
    label_id: int,
    db: Session = Depends(get_db),
):
    """루트→현재 경로(breadcrumb) 조회"""
    return await handle_get_breadcrumb(label_id, db)


@router.get("/{label_id}", response_model=LabelResponse)
async def get_label(label_id: int, db: Session = Depends(get_db)):
    """라벨 조회"""
    return await handle_get_label(label_id, db)


@router.get("/{label_id}/impact")
async def get_label_impact(label_id: int, db: Session = Depends(get_db)):
    """라벨 삭제 전 영향도 조회"""
    return await handle_get_label_impact(label_id, db)


@router.delete("/{label_id}")
async def delete_label(label_id: int, db: Session = Depends(get_db)):
    """라벨 삭제"""
    return await handle_delete_label(label_id, db)


@router.post("/chunks/{chunk_id}/labels/{label_id}")
async def add_label_to_chunk(chunk_id: int, label_id: int, confidence: float = 1.0, db: Session = Depends(get_db)):
    """청크에 라벨 추가"""
    return await handle_add_label_to_chunk(chunk_id, label_id, confidence, db)


@router.delete("/chunks/{chunk_id}/labels/{label_id}")
async def remove_label_from_chunk(chunk_id: int, label_id: int, db: Session = Depends(get_db)):
    """청크에서 라벨 제거"""
    return await handle_remove_label_from_chunk(chunk_id, label_id, db)


@router.get("/chunks/{chunk_id}/labels")
async def get_chunk_labels(chunk_id: int, db: Session = Depends(get_db)):
    """청크의 라벨 목록 조회"""
    return await handle_get_chunk_labels(chunk_id, db)
