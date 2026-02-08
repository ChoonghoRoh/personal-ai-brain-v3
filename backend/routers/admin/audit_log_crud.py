"""
Admin Audit Log CRUD API (Phase 11-3)

Audit Log 조회 전용 API - 생성/수정/삭제 불가
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.admin_models import AdminAuditLog
from .schemas_pydantic import AuditLogResponse, ListResponse
from .deps import get_or_404, log_crud_action

router = APIRouter()


@router.get("", response_model=ListResponse[AuditLogResponse])
def list_audit_logs(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    record_id: Optional[str] = Query(None, description="Filter by record ID"),
    action: Optional[str] = Query(None, description="Filter by action (create, update, delete, publish, rollback)"),
    changed_by: Optional[str] = Query(None, description="Filter by changed_by"),
    from_date: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
):
    """
    Audit Log 목록 조회 (필터, 페이징)

    - **limit**: 한 페이지당 항목 수 (기본 50, 최대 100)
    - **offset**: 건너뛸 항목 수
    - **table_name**: 테이블 이름으로 필터
    - **record_id**: 레코드 ID로 필터
    - **action**: 액션으로 필터 (create, update, delete, publish, rollback)
    - **changed_by**: 변경자로 필터
    - **from_date**: 시작 날짜로 필터
    - **to_date**: 종료 날짜로 필터
    """
    query = db.query(AdminAuditLog)

    # Apply filters
    if table_name:
        query = query.filter(AdminAuditLog.table_name == table_name)

    if record_id:
        try:
            record_uuid = UUID(record_id)
            query = query.filter(AdminAuditLog.record_id == record_uuid)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid record_id format")

    if action:
        query = query.filter(AdminAuditLog.action == action)

    if changed_by:
        query = query.filter(AdminAuditLog.changed_by.ilike(f"%{changed_by}%"))

    if from_date:
        try:
            from_dt = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(AdminAuditLog.created_at >= from_dt)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid from_date format. Use YYYY-MM-DD")

    if to_date:
        try:
            to_dt = datetime.strptime(to_date, "%Y-%m-%d")
            # Add 1 day to include the entire end date
            to_dt = to_dt.replace(hour=23, minute=59, second=59)
            query = query.filter(AdminAuditLog.created_at <= to_dt)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid to_date format. Use YYYY-MM-DD")

    # Get total count
    total = query.count()

    # Apply ordering and pagination
    items = query.order_by(desc(AdminAuditLog.created_at)).offset(offset).limit(limit).all()

    log_crud_action("list", "AuditLog", extra={"total": total, "filters": {
        "table_name": table_name, "action": action, "changed_by": changed_by
    }})

    return ListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{log_id}", response_model=AuditLogResponse)
def get_audit_log(log_id: UUID, db: Session = Depends(get_db)):
    """
    Audit Log 단건 조회
    """
    log_entry = get_or_404(db, AdminAuditLog, log_id)
    log_crud_action("get", "AuditLog", log_id)
    return log_entry
