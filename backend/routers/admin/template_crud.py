"""Phase 11-2 Task 11-2-1: Template (AdminTemplate) CRUD API

엔드포인트:
- GET    /api/admin/templates         목록 조회 (필터·페이징)
- GET    /api/admin/templates/{id}    단건 조회
- POST   /api/admin/templates         생성
- PUT    /api/admin/templates/{id}    수정
- DELETE /api/admin/templates/{id}    삭제
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import get_db
from backend.models.admin_models import AdminTemplate

from .deps import get_or_404, handle_integrity_error, log_crud_action
from .schemas_pydantic import (
    TemplateCreate, TemplateUpdate, TemplateResponse,
    ListResponse, MessageResponse,
)

router = APIRouter()


@router.get("", response_model=ListResponse[TemplateResponse])
async def list_templates(
    template_type: Optional[str] = Query(None, description="템플릿 타입 필터"),
    status: Optional[str] = Query(None, description="상태 필터 (draft/published)"),
    q: Optional[str] = Query(None, description="검색어 (name, description)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """Template 목록 조회 (필터·페이징)"""
    query = db.query(AdminTemplate)

    # 필터
    if template_type:
        query = query.filter(AdminTemplate.template_type == template_type)
    if status:
        query = query.filter(AdminTemplate.status == status)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (AdminTemplate.name.ilike(search_term)) |
            (AdminTemplate.description.ilike(search_term))
        )

    # 전체 개수
    total = query.count()

    # 정렬·페이징
    items = query.order_by(AdminTemplate.name).offset(offset).limit(limit).all()

    log_crud_action("list", "templates", extra={"total": total, "limit": limit, "offset": offset})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """Template 단건 조회"""
    record = get_or_404(db, AdminTemplate, template_id)
    log_crud_action("read", "templates", template_id)
    return record


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
):
    """Template 생성"""
    record = AdminTemplate(**data.model_dump())
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Template")

    log_crud_action("create", "templates", record.id)
    return record


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
):
    """Template 수정 (부분 업데이트)"""
    record = get_or_404(db, AdminTemplate, template_id)

    # None이 아닌 필드만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Template")

    log_crud_action("update", "templates", template_id, extra={"updated_fields": list(update_data.keys())})
    return record


@router.delete("/{template_id}", response_model=MessageResponse)
async def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
):
    """Template 삭제"""
    record = get_or_404(db, AdminTemplate, template_id)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Template")

    log_crud_action("delete", "templates", template_id)
    return MessageResponse(message="Template deleted successfully", id=template_id)
