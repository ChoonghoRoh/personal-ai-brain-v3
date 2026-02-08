"""Phase 11-2 Task 11-2-2: RAG Profile (AdminRagProfile) CRUD API

엔드포인트:
- GET    /api/admin/rag-profiles         목록 조회 (필터·페이징)
- GET    /api/admin/rag-profiles/{id}    단건 조회
- POST   /api/admin/rag-profiles         생성
- PUT    /api/admin/rag-profiles/{id}    수정
- DELETE /api/admin/rag-profiles/{id}    삭제
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import get_db
from backend.models.admin_models import AdminRagProfile

from .deps import get_or_404, handle_integrity_error, log_crud_action
from .schemas_pydantic import (
    RagProfileCreate, RagProfileUpdate, RagProfileResponse,
    ListResponse, MessageResponse,
)

router = APIRouter()


@router.get("", response_model=ListResponse[RagProfileResponse])
async def list_rag_profiles(
    status: Optional[str] = Query(None, description="상태 필터 (draft/published)"),
    q: Optional[str] = Query(None, description="검색어 (name, description)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """RAG Profile 목록 조회 (필터·페이징)"""
    query = db.query(AdminRagProfile)

    # 필터
    if status:
        query = query.filter(AdminRagProfile.status == status)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (AdminRagProfile.name.ilike(search_term)) |
            (AdminRagProfile.description.ilike(search_term))
        )

    # 전체 개수
    total = query.count()

    # 정렬·페이징
    items = query.order_by(AdminRagProfile.name).offset(offset).limit(limit).all()

    log_crud_action("list", "rag_profiles", extra={"total": total, "limit": limit, "offset": offset})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{profile_id}", response_model=RagProfileResponse)
async def get_rag_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
):
    """RAG Profile 단건 조회"""
    record = get_or_404(db, AdminRagProfile, profile_id)
    log_crud_action("read", "rag_profiles", profile_id)
    return record


@router.post("", response_model=RagProfileResponse, status_code=201)
async def create_rag_profile(
    data: RagProfileCreate,
    db: Session = Depends(get_db),
):
    """RAG Profile 생성"""
    record = AdminRagProfile(**data.model_dump())
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "RagProfile")

    log_crud_action("create", "rag_profiles", record.id)
    return record


@router.put("/{profile_id}", response_model=RagProfileResponse)
async def update_rag_profile(
    profile_id: UUID,
    data: RagProfileUpdate,
    db: Session = Depends(get_db),
):
    """RAG Profile 수정 (부분 업데이트)"""
    record = get_or_404(db, AdminRagProfile, profile_id)

    # None이 아닌 필드만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "RagProfile")

    log_crud_action("update", "rag_profiles", profile_id, extra={"updated_fields": list(update_data.keys())})
    return record


@router.delete("/{profile_id}", response_model=MessageResponse)
async def delete_rag_profile(
    profile_id: UUID,
    db: Session = Depends(get_db),
):
    """RAG Profile 삭제"""
    record = get_or_404(db, AdminRagProfile, profile_id)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "RagProfile")

    log_crud_action("delete", "rag_profiles", profile_id)
    return MessageResponse(message="RAG Profile deleted successfully", id=profile_id)
