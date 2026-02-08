"""pytest 설정 및 픽스처"""
import pytest
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal, init_db, Base, engine

# db_session 픽스처는 반드시 테스트 전용 DB만 사용 (개발 DB drop_all 방지)
# 테스트 전용 엔진: 메모리 SQLite. 개발/운영 PostgreSQL과 분리됨.
TEST_DATABASE_URL = "sqlite:///:memory:"


def _get_test_engine():
    """테스트 전용 엔진 (모든 모델이 Base에 등록된 뒤 호출)."""
    import backend.models.models  # noqa: F401  # Base.metadata에 테이블 등록
    return create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="function")
def db_session():
    """테스트용 데이터베이스 세션. 테스트 전용 DB(SQLite 메모리)만 사용하여 drop_all이 개발 DB에 적용되지 않도록 함."""
    test_engine = _get_test_engine()
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)
