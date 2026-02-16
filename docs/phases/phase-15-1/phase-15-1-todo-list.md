# Phase 15-1 Todo List: 지식관리 지정 폴더 & 파일 관리

**Phase**: 15-1
**G1 판정**: PASS
**작성일**: 2026-02-16

---

- [ ] Task 15-1-1: [DB+BE] 지정 폴더 경로 설정 API (Owner: backend-dev)
  - 환경변수 `KNOWLEDGE_FOLDER_PATH` 기본값 추가
  - GET/PUT `/api/knowledge/folder-config` 엔드포인트
  - DB 오버라이드 메커니즘 (system_settings 또는 policy_sets)
  - `require_admin_knowledge` 권한 적용

- [ ] Task 15-1-2: [BE] 폴더 내 파일 목록 API (Owner: backend-dev)
  - GET `/api/knowledge/folder-files` 엔드포인트
  - 폴더 재귀 스캔 + documents 테이블 매칭
  - 허용 확장자 필터링 (FileParserService 지원 형식)
  - 페이징 지원

- [ ] Task 15-1-3: [BE] 파일 업로드/동기화 API (Owner: backend-dev)
  - POST `/api/knowledge/upload` — 파일 업로드 + documents 등록 + 파싱
  - POST `/api/knowledge/sync` — 폴더 스캔 → DB 동기화
  - FileParserService 재사용
  - 중복 방지 (file_path upsert)

- [ ] Task 15-1-4: [FE] 파일관리 UI 페이지 (Owner: frontend-dev)
  - `web/src/pages/admin/knowledge-files.html` 신규
  - `web/public/js/admin/admin-knowledge-files.js` 신규
  - 폴더 경로 표시/변경, 파일 목록 테이블, 업로드, 동기화
  - LNB ADMIN_MENU에 "파일관리" 추가
  - `_HTML_ROUTES` 등록
