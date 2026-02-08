"""Phase 11-2 Task 11-2-1: Schema (AdminSchema) CRUD API

엔드포인트:
- GET    /api/admin/schemas         목록 조회 (필터·페이징)
- GET    /api/admin/schemas/{id}    단건 조회
- POST   /api/admin/schemas         생성
- PUT    /api/admin/schemas/{id}    수정
- DELETE /api/admin/schemas/{id}    삭제
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import get_db
from backend.models.admin_models import AdminSchema

from .deps import get_or_404, handle_integrity_error, log_crud_action
from .schemas_pydantic import (
    SchemaCreate, SchemaUpdate, SchemaResponse,
    ListResponse, MessageResponse,
)

router = APIRouter()


@router.get("", response_model=ListResponse[SchemaResponse])
async def list_schemas(
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    q: Optional[str] = Query(None, description="검색어 (role_key, display_name)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """Schema 목록 조회 (필터·페이징)"""
    query = db.query(AdminSchema)

    # 필터
    if is_active is not None:
        query = query.filter(AdminSchema.is_active == is_active)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (AdminSchema.role_key.ilike(search_term)) |
            (AdminSchema.display_name.ilike(search_term))
        )

    # 전체 개수
    total = query.count()

    # 정렬·페이징
    items = query.order_by(AdminSchema.display_order, AdminSchema.role_key).offset(offset).limit(limit).all()

    log_crud_action("list", "schemas", extra={"total": total, "limit": limit, "offset": offset})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{schema_id}", response_model=SchemaResponse)
async def get_schema(
    schema_id: UUID,
    db: Session = Depends(get_db),
):
    """Schema 단건 조회"""
    record = get_or_404(db, AdminSchema, schema_id)
    log_crud_action("read", "schemas", schema_id)
    return record


@router.post("", response_model=SchemaResponse, status_code=201)
async def create_schema(
    data: SchemaCreate,
    db: Session = Depends(get_db),
):
    """Schema 생성"""
    record = AdminSchema(**data.model_dump())
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Schema")

    log_crud_action("create", "schemas", record.id)
    return record


@router.put("/{schema_id}", response_model=SchemaResponse)
async def update_schema(
    schema_id: UUID,
    data: SchemaUpdate,
    db: Session = Depends(get_db),
):
    """Schema 수정 (부분 업데이트)"""
    record = get_or_404(db, AdminSchema, schema_id)

    # None이 아닌 필드만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Schema")

    log_crud_action("update", "schemas", schema_id, extra={"updated_fields": list(update_data.keys())})
    return record


@router.delete("/{schema_id}", response_model=MessageResponse)
async def delete_schema(
    schema_id: UUID,
    db: Session = Depends(get_db),
):
    """Schema 삭제"""
    record = get_or_404(db, AdminSchema, schema_id)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "Schema")

    log_crud_action("delete", "schemas", schema_id)
    return MessageResponse(message="Schema deleted successfully", id=schema_id)
