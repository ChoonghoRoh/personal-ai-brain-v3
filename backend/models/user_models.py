"""사용자 관리 테이블 모델 (Phase 14-5-2)

- users: 사용자 인증·역할 관리
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from .database import Base


class User(Base):
    """사용자 모델 (users 테이블)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(200), nullable=True)
    email = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default="user", index=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=text("true"))
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
