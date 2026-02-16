"""Phase 14-5-3: 사용자(User) CRUD API

엔드포인트:
- GET    /api/admin/users              목록 조회 (필터·페이징)
- GET    /api/admin/users/{id}         단건 조회
- POST   /api/admin/users              생성
- PUT    /api/admin/users/{id}         수정
- DELETE /api/admin/users/{id}         비활성화 (soft delete)
- POST   /api/admin/users/{id}/reset-password  비밀번호 초기화

권한: admin_system (admin/__init__.py에서 일괄 적용)
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.models.database import get_db
from backend.models.user_models import User

logger = logging.getLogger(__name__)
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

VALID_ROLES = ["user", "admin_knowledge", "admin_system"]


# ============================================
# Pydantic 스키마
# ============================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100, description="사용자명 (unique)")
    password: str = Field(..., min_length=8, max_length=72, description="비밀번호 (8자 이상)")
    display_name: Optional[str] = Field(None, max_length=200, description="표시 이름")
    email: Optional[str] = Field(None, max_length=255, description="이메일")
    role: str = Field(default="user", description="역할 (user|admin_knowledge|admin_system)")


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, description="역할 변경")
    is_active: Optional[bool] = Field(None, description="활성 상태")


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=72, description="새 비밀번호")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    role: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ============================================
# CRUD 엔드포인트
# ============================================

@router.get("", response_model=UserListResponse)
async def list_users(
    q: Optional[str] = Query(None, description="검색어 (username, display_name)"),
    role: Optional[str] = Query(None, description="역할 필터"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
):
    """사용자 목록 조회 (필터·페이징)"""
    query = db.query(User)

    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter(
            (User.username.ilike(term)) | (User.display_name.ilike(term))
        )
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    items = query.order_by(User.id).offset(offset).limit(limit).all()

    logger.info(f"Admin CRUD: LIST users total={total} limit={limit} offset={offset}")
    return UserListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 단건 조회"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """사용자 생성"""
    if data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid role: {data.role}. Must be one of {VALID_ROLES}",
        )

    user = User(
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
        display_name=data.display_name,
        email=data.email,
        role=data.role,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username already exists")

    logger.info(f"Admin CRUD: CREATE user id={user.id} username={user.username} role={user.role}")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    """사용자 수정 (역할 변경, 비활성화 등)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.role is not None:
        if data.role not in VALID_ROLES:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid role: {data.role}. Must be one of {VALID_ROLES}",
            )
        user.role = data.role
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.email is not None:
        user.email = data.email
    if data.is_active is not None:
        user.is_active = data.is_active

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    logger.info(f"Admin CRUD: UPDATE user id={user.id} username={user.username}")
    return user


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """사용자 비활성화 (soft delete)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"Admin CRUD: DEACTIVATE user id={user.id} username={user.username}")
    return MessageResponse(message=f"User '{user.username}' deactivated")


@router.post("/{user_id}/reset-password", response_model=MessageResponse)
async def reset_password(
    user_id: int,
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    """비밀번호 초기화 (admin_system 전용)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = pwd_context.hash(data.new_password)
    user.updated_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(f"Admin CRUD: RESET-PASSWORD user id={user.id} username={user.username}")
    return MessageResponse(message=f"Password reset for user '{user.username}'")
