"""Database connection and session management"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

# Create engine with connection pool optimization
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,  # 연결 풀 크기
    max_overflow=20,  # 최대 오버플로우 연결 수
    pool_pre_ping=True,  # 연결 유효성 사전 확인
    pool_recycle=3600,  # 1시간마다 연결 재활용
    connect_args={
        "connect_timeout": 10,  # 연결 타임아웃
        "application_name": "personal_ai_brain"  # 애플리케이션 이름
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

