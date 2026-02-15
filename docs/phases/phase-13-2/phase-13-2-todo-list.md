# Phase 13-2 Todo List — Backend 라우팅·에러 처리 보완

**Phase**: 13-2
**작성일**: 2026-02-16
**완료일**: 2026-02-16

---

## Task 13-2-1 [BE] HTML 라우트 목록 문서화·메뉴 path 1:1 대응 검증

- [x] main.py에서 HTML 라우트 전수 추출
- [x] 메뉴 path 17개 + 추가 라우트 6개 목록 작성
- [x] 라우트↔메뉴 1:1 대응 표 작성 (route-menu-mapping.md)
- [x] Base URL(8001) 일치 확인
- [x] curl 검증: 17개 path 모두 200 OK

## Task 13-2-2 [BE] HTML 404 전용 응답

- [x] FastAPI 예외 핸들러에서 Accept: text/html 판별
- [x] HTML 요청 시 404.html 템플릿 반환 로직 구현
- [x] API 요청(Accept: application/json) 시 기존 JSON 404 유지
- [x] /admin/nonexistent → 404 HTML, /api/nonexistent → 404 JSON 테스트 통과

## Task 13-2-3 [BE] 라우트 일괄 등록 리팩터링

- [x] 현재 main.py HTML 라우트 등록 패턴 분석 (22개 개별 핸들러)
- [x] _HTML_ROUTES 리스트 + _register_html_routes() 루프 패턴 설계
- [x] 리팩터링 적용 (/document/{id} 제외 — path parameter)
- [x] Docker 재시작 후 17개 라우트 + 추가 6개 모두 200 OK 회귀 확인
