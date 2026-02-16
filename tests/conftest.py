"""pytest 설정 및 픽스처"""
import pytest
import sys
import sqlite3
import datetime
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.database import SessionLocal, init_db, Base, engine

# db_session 픽스처는 반드시 테스트 전용 DB만 사용 (개발 DB drop_all 방지)
# 테스트 전용 엔진: 메모리 SQLite. 개발/운영 PostgreSQL과 분리됨.
TEST_DATABASE_URL = "sqlite:///:memory:"


def _register_pg_functions(dbapi_conn, connection_record):
    """SQLite에 PostgreSQL 호환 함수 등록 (NOW, gen_random_uuid 등)."""
    dbapi_conn.create_function("NOW", 0, lambda: datetime.datetime.now().isoformat())
    dbapi_conn.create_function("gen_random_uuid", 0, lambda: str(__import__("uuid").uuid4()))


def _get_test_engine():
    """테스트 전용 엔진 (모든 모델이 Base에 등록된 뒤 호출)."""
    import backend.models.models  # noqa: F401  # Base.metadata에 테이블 등록
    import backend.models.admin_models  # noqa: F401  # Phase 15-1: system_settings 테이블 등록
    eng = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    event.listen(eng, "connect", _register_pg_functions)
    return eng


def _is_sqlite_compatible(table):
    """테이블이 SQLite와 호환되는지 검사 (ARRAY, JSONB 등 PG 전용 타입 감지)."""
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB
    for col in table.columns:
        if isinstance(col.type, (ARRAY, JSONB)):
            return False
    return True


def _sqlite_safe_tables():
    """SQLite와 호환되는 테이블만 반환."""
    return [t for t in Base.metadata.sorted_tables if _is_sqlite_compatible(t)]


@pytest.fixture(scope="function")
def db(db_session):
    """db_session의 별칭 (테스트 호환성)."""
    yield db_session


@pytest.fixture(scope="function")
def db_session():
    """테스트용 데이터베이스 세션. 테스트 전용 DB(SQLite 메모리)만 사용하여 drop_all이 개발 DB에 적용되지 않도록 함."""
    test_engine = _get_test_engine()
    safe_tables = _sqlite_safe_tables()
    Base.metadata.create_all(bind=test_engine, tables=safe_tables)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine, tables=safe_tables)
