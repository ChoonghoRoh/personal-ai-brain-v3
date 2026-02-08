"""Phase 11-2 Task 11-2-2: Policy Set (AdminPolicySet) CRUD API

엔드포인트:
- GET    /api/admin/policy-sets         목록 조회 (필터·페이징)
- GET    /api/admin/policy-sets/{id}    단건 조회
- POST   /api/admin/policy-sets         생성
- PUT    /api/admin/policy-sets/{id}    수정
- DELETE /api/admin/policy-sets/{id}    삭제
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import get_db
from backend.models.admin_models import AdminPolicySet

from .deps import get_or_404, handle_integrity_error, log_crud_action
from .schemas_pydantic import (
    PolicySetCreate, PolicySetUpdate, PolicySetResponse,
    ListResponse, MessageResponse,
)

router = APIRouter()


@router.get("", response_model=ListResponse[PolicySetResponse])
async def list_policy_sets(
    project_id: Optional[int] = Query(None, description="프로젝트 ID 필터"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    q: Optional[str] = Query(None, description="검색어 (name, description)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """Policy Set 목록 조회 (필터·페이징)"""
    query = db.query(AdminPolicySet)

    # 필터
    if project_id is not None:
        query = query.filter(AdminPolicySet.project_id == project_id)
    if is_active is not None:
        query = query.filter(AdminPolicySet.is_active == is_active)
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        query = query.filter(
            (AdminPolicySet.name.ilike(search_term)) |
            (AdminPolicySet.description.ilike(search_term))
        )

    # 전체 개수
    total = query.count()

    # 정렬·페이징 (우선순위 → 이름)
    items = query.order_by(AdminPolicySet.priority.desc(), AdminPolicySet.name).offset(offset).limit(limit).all()

    log_crud_action("list", "policy_sets", extra={"total": total, "limit": limit, "offset": offset})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{policy_id}", response_model=PolicySetResponse)
async def get_policy_set(
    policy_id: UUID,
    db: Session = Depends(get_db),
):
    """Policy Set 단건 조회"""
    record = get_or_404(db, AdminPolicySet, policy_id)
    log_crud_action("read", "policy_sets", policy_id)
    return record


@router.post("", response_model=PolicySetResponse, status_code=201)
async def create_policy_set(
    data: PolicySetCreate,
    db: Session = Depends(get_db),
):
    """Policy Set 생성"""
    record = AdminPolicySet(**data.model_dump())
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PolicySet")

    log_crud_action("create", "policy_sets", record.id)
    return record


@router.put("/{policy_id}", response_model=PolicySetResponse)
async def update_policy_set(
    policy_id: UUID,
    data: PolicySetUpdate,
    db: Session = Depends(get_db),
):
    """Policy Set 수정 (부분 업데이트)"""
    record = get_or_404(db, AdminPolicySet, policy_id)

    # None이 아닌 필드만 업데이트
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PolicySet")

    log_crud_action("update", "policy_sets", policy_id, extra={"updated_fields": list(update_data.keys())})
    return record


@router.delete("/{policy_id}", response_model=MessageResponse)
async def delete_policy_set(
    policy_id: UUID,
    db: Session = Depends(get_db),
):
    """Policy Set 삭제"""
    record = get_or_404(db, AdminPolicySet, policy_id)

    try:
        db.delete(record)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        handle_integrity_error(e, "PolicySet")

    log_crud_action("delete", "policy_sets", policy_id)
    return MessageResponse(message="Policy Set deleted successfully", id=policy_id)
