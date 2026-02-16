"""
페이지 접근 로그 조회 API (Phase 13-4)

접근 로그 조회 전용 — 생성은 미들웨어가 담당.
"""
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.admin_models import PageAccessLog

router = APIRouter()


class PageAccessLogItem(BaseModel):
    id: int
    path: str
    method: str
    status_code: int
    response_time_ms: Optional[int] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    accessed_at: datetime

    class Config:
        from_attributes = True


class PageAccessStats(BaseModel):
    path: str
    count: int
    avg_response_time_ms: Optional[float] = None


@router.get("", response_model=dict)
def list_page_access_logs(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    path: Optional[str] = Query(None, description="경로 필터 (완전 일치)"),
    from_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
):
    """페이지 접근 로그 목록 조회"""
    query = db.query(PageAccessLog)

    if path:
        query = query.filter(PageAccessLog.path == path)
    if from_date:
        query = query.filter(PageAccessLog.accessed_at >= datetime.strptime(from_date, "%Y-%m-%d"))
    if to_date:
        to_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(PageAccessLog.accessed_at <= to_dt)

    total = query.count()
    items = query.order_by(desc(PageAccessLog.accessed_at)).offset(offset).limit(limit).all()

    return {
        "items": [PageAccessLogItem.model_validate(i).model_dump() for i in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/stats", response_model=List[PageAccessStats])
def page_access_stats(
    db: Session = Depends(get_db),
    from_date: Optional[str] = Query(None, description="시작일 (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="종료일 (YYYY-MM-DD)"),
    limit: int = Query(30, ge=1, le=100),
):
    """경로별 접근 통계 (상위 N개)"""
    query = db.query(
        PageAccessLog.path,
        func.count(PageAccessLog.id).label("count"),
        func.avg(PageAccessLog.response_time_ms).label("avg_response_time_ms"),
    )

    if from_date:
        query = query.filter(PageAccessLog.accessed_at >= datetime.strptime(from_date, "%Y-%m-%d"))
    if to_date:
        to_dt = datetime.strptime(to_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(PageAccessLog.accessed_at <= to_dt)

    rows = (
        query
        .group_by(PageAccessLog.path)
        .order_by(func.count(PageAccessLog.id).desc())
        .limit(limit)
        .all()
    )

    return [
        PageAccessStats(
            path=row.path,
            count=row.count,
            avg_response_time_ms=round(float(row.avg_response_time_ms), 1) if row.avg_response_time_ms else None,
        )
        for row in rows
    ]
