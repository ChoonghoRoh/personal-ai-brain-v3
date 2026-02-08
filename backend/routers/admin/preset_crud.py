"""Phase 11-2 Task 11-2-1: PromptPreset (AdminPromptPreset) CRUD API

엔드포인트:
- GET    /api/admin/presets         목록 조회 (필터·페이징)
- GET    /api/admin/presets/{id}    단건 조회
- POST   /api/admin/presets         생성
- PUT    /api/admin/presets/{id}    수정
- DELETE /api/admin/presets/{id}    삭제
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import get_db
from backend.models.admin_models import AdminPromptPreset

from .deps import get_or_404, handle_integrity_error, log_crud_action
from .schemas_pydantic import (
    PresetCreate, PresetUpdate, PresetResponse,
    ListResponse, MessageResponse,
)

router = APIRouter()


@router.get("", response_model=ListResponse[PresetResponse])
async def list_presets(
    task_type: Optional[str] = Query(None, description="작업 타입 필터"),
    status: Optional[str] = Query(None, description="상태 필터 (draft/published)"),
    q: Optional[str] = Query(None, description="검색어 (name)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """PromptPreset 목록 조회 (필터·페이징)"""
    query = db.query(AdminPromptPreset)

    # 필터
    if task_type:
        query = query.filter(AdminPromptPreset.task_type == task_type)
    if status:
        query = query.filter(AdminPromptPreset.status == status)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(AdminPromptPreset.name.ilike(search_term))

    # 전체 개수
    total = query.count()

    # 정렬·페이징
    items = query.order_by(AdminPromptPreset.name).offset(offset).limit(limit).all()

    log_crud_action("list", "presets", extra={"total": total, "limit": limit, "offset": offset})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset(
    preset_id: UUID,
    db: Session = Depends(get_db),
):
    """PromptPreset 단건 조회"""
    record = get_or_404(db, AdminPromptPreset, preset_id)
    log_crud_action("read", "presets", preset_id)
    return record


@router.post("", response_model=PresetResponse, status_code=201)
async def create_preset(
    data: PresetCreate,
    db: Session = Depends(get_db),
):
    """PromptPreset 생성"""
    record = AdminPromptPreset(**data.model_dump())
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PromptPreset")

    log_crud_action("create", "presets", record.id)
    return record


@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(
    preset_id: UUID,
    data: PresetUpdate,
    db: Session = Depends(get_db),
):
    """PromptPreset 수정 (부분 업데이트)"""
    record = get_or_404(db, AdminPromptPreset, preset_id)

    # None이 아닌 필드만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PromptPreset")

    log_crud_action("update", "presets", preset_id, extra={"updated_fields": list(update_data.keys())})
    return record


@router.delete("/{preset_id}", response_model=MessageResponse)
async def delete_preset(
    preset_id: UUID,
    db: Session = Depends(get_db),
):
    """PromptPreset 삭제"""
    record = get_or_404(db, AdminPromptPreset, preset_id)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PromptPreset")

    log_crud_action("delete", "presets", preset_id)
    return MessageResponse(message="PromptPreset deleted successfully", id=preset_id)
