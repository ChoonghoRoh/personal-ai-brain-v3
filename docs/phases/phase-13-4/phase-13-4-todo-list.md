# Phase 13-4 Todo List — DB·운영

**Phase**: 13-4
**작성일**: 2026-02-16

---

## Task 13-4-1 [DB] 메뉴/페이지 접근 로그 테이블 도입 ✅

- [x] `page_access_logs` 테이블 스키마 설계:
  - [x] id (PK, SERIAL)
  - [x] path (VARCHAR 255) — 접근 경로
  - [x] method (VARCHAR 10) — HTTP 메서드
  - [x] status_code (INTEGER) — HTTP 상태 코드
  - [x] response_time_ms (INTEGER) — 응답 시간(ms)
  - [x] user_agent (TEXT) — 선택
  - [x] ip_address (VARCHAR 45) — 선택
  - [x] accessed_at (TIMESTAMP)
- [x] SQLAlchemy 모델 정의 (admin_models.py — `PageAccessLog`)
- [x] SQL 마이그레이션 생성 (`002_create_page_access_log.sql`)
- [x] 마이그레이션 실행 (Docker 환경)
- [x] 미들웨어 구현 (`backend/middleware/page_access_log.py` — `PageAccessLogMiddleware`)
  - [x] HTML 페이지 요청만 기록 (API/정적 파일 제외)
  - [x] 응답 시간 측정
- [x] main.py에 미들웨어 등록
- [x] 조회 API 구현 (`backend/routers/admin/page_access_log_crud.py`):
  - [x] `GET /api/admin/page-access-logs` — 목록 조회 (필터, 페이징)
  - [x] `GET /api/admin/page-access-logs/stats` — 경로별 접근 통계
- [x] Admin 라우터에 등록 (`backend/routers/admin/__init__.py`)
- [x] 로그 기록 동작 확인 (7건 기록 확인, API 호출 비기록 확인)
- [x] migrations README 업데이트
