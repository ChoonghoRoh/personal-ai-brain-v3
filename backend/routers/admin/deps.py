"""Phase 11-2: Admin CRUD 공통 의존성·유틸

공통 CRUD 모듈:
1. DB 세션 의존성
2. 예외 변환 (404/409/422)
3. 로깅 유틸
"""
import logging
from typing import TypeVar, Type, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.database import Base

logger = logging.getLogger(__name__)

# 제네릭 타입 변수 (ORM 모델용)
ModelT = TypeVar("ModelT", bound=Base)


def get_or_404(db: Session, model: Type[ModelT], record_id: UUID) -> ModelT:
    """ID로 레코드 조회, 없으면 404 발생

    Args:
        db: DB 세션
        model: ORM 모델 클래스
        record_id: 조회할 레코드 UUID

    Returns:
        조회된 레코드

    Raises:
        HTTPException: 404 Not Found
    """
    record = db.query(model).filter(model.id == record_id).first()
    if not record:
        logger.warning(f"{model.__tablename__} not found: {record_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__tablename__} not found: {record_id}"
        )
    return record


def handle_integrity_error(e: IntegrityError, model_name: str) -> None:
    """IntegrityError를 적절한 HTTP 예외로 변환

    Args:
        e: SQLAlchemy IntegrityError
        model_name: 모델명 (에러 메시지용)

    Raises:
        HTTPException: 409 Conflict (중복) 또는 422 Unprocessable Entity (제약 위반)
    """
    error_msg = str(e.orig) if e.orig else str(e)
    logger.warning(f"{model_name} integrity error: {error_msg}")

    # unique 제약 위반 (중복)
    if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{model_name} already exists (unique constraint violation)"
        )

    # FK 제약 위반
    if "foreign key" in error_msg.lower():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid reference in {model_name} (foreign key constraint)"
        )

    # 기타 제약 위반
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"{model_name} constraint violation: {error_msg}"
    )


def log_crud_action(action: str, model_name: str, record_id: Optional[UUID] = None, extra: Optional[dict] = None) -> None:
    """CRUD 작업 로깅

    Args:
        action: CRUD 작업 (create/read/update/delete)
        model_name: 모델명
        record_id: 레코드 ID (선택)
        extra: 추가 정보 (선택)
    """
    msg_parts = [f"Admin CRUD: {action.upper()} {model_name}"]
    if record_id:
        msg_parts.append(f"id={record_id}")
    if extra:
        msg_parts.append(f"extra={extra}")
    logger.info(" ".join(msg_parts))
