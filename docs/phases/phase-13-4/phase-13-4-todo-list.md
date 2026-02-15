# Phase 13-4 Todo List — DB·운영 (선택)

**Phase**: 13-4
**작성일**: 2026-02-16

---

## Task 13-4-1 [DB] (선택) 메뉴/페이지 접근 로그 테이블 도입

- [ ] `page_access_log` 테이블 스키마 설계:
  - [ ] id (PK)
  - [ ] path (VARCHAR) — 접근 경로
  - [ ] user_agent (TEXT) — 선택
  - [ ] ip_address (VARCHAR) — 선택
  - [ ] accessed_at (TIMESTAMP)
- [ ] SQLAlchemy 모델 정의 (models.py)
- [ ] Alembic 마이그레이션 생성·적용
- [ ] 미들웨어 또는 라우터에서 접근 로그 기록 로직 구현
- [ ] 로그 기록 동작 확인
- [ ] 운영 데이터 조회 API 또는 Admin 페이지 연동 (선택)
