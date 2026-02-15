# Phase 12-1 Todo List — P0 즉시 조치

**Phase**: 12-1
**작성일**: 2026-02-15

---

## Task 12-1-1 [FE] CDN 로컬화

- [ ] `web/public/libs/` 디렉토리 생성
- [ ] 5개 라이브러리 다운로드 및 배치:
  - [ ] marked.js (현재 CDN 버전 확인)
  - [ ] mermaid.js (v10.x)
  - [ ] chart.js (v4.x)
  - [ ] html2canvas.js (v1.4.1)
  - [ ] jspdf (v2.5.1 UMD)
- [ ] HTML 파일 CDN→로컬 경로 수정:
  - [ ] `web/src/pages/reason.html` (4개 CDN 참조)
  - [ ] `web/src/pages/admin/statistics.html` (chart.js)
  - [ ] `web/src/pages/logs.html` (marked.js)
  - [ ] `web/src/pages/document.html` (marked.js)
- [ ] Grep 검증: `cdn.jsdelivr.net` 0건
- [ ] 페이지 로드 확인

## Task 12-1-2 [FS] Base URL 8001 통일

- [ ] `backend/main.py` FastAPI servers URL 8000→8001 수정
- [ ] `backend/config.py` EXTERNAL_PORT 환경변수 추가
- [ ] `.env.example` 포트 설정 문서화
- [ ] `docs/` 내 localhost:8001 → localhost:8001 일괄 치환
- [ ] Grep 검증: 코드 파일에서 `localhost:8001` 0건

## Task 12-1-3 [INFRA] HTTPS/HSTS 활성화

- [ ] `backend/config.py` HSTS 환경변수 추가 (HSTS_ENABLED, HSTS_MAX_AGE 등)
- [ ] `backend/middleware/security.py` HSTS 조건부 활성화 구현
- [ ] `.env.example` HSTS 설정 문서화
- [ ] 개발 환경 HSTS 비활성화 확인
- [ ] 프로덕션 환경 HSTS 헤더 포함 확인
