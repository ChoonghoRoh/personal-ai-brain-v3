# 테스트

## pytest와 개발 DB 분리

**과거 이슈**: `db_session` 픽스처가 앱과 **동일한 PostgreSQL**(`DATABASE_URL`)을 사용하고, 테스트 후 `Base.metadata.drop_all(bind=engine)`를 실행했습니다.  
`pytest tests/test_models.py` 등 `db_session`을 쓰는 테스트를 실행하면 **개발 DB의 모든 테이블(labels, knowledge_chunks, documents 등)이 삭제**되는 문제가 있었습니다.

**현재**: `conftest.py`의 `db_session`은 **테스트 전용 DB(SQLite 메모리)**만 사용합니다.  
`drop_all`은 해당 인메모리 DB에만 적용되므로, pytest 실행으로 개발/운영 PostgreSQL 데이터가 삭제되지 않습니다.

- 테스트 전용 DB: `sqlite:///:memory:` (픽스처별로 새 엔진 생성)
- 개발/운영 DB: `DATABASE_URL`(PostgreSQL) — pytest에서 사용하지 않음

## 실행

```bash
python -m pytest tests/ -v
# 또는
python -m pytest tests/test_models.py tests/test_structure_matching.py -v
```
