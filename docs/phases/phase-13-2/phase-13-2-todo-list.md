# Phase 13-2 Todo List — Backend 라우팅·에러 처리 보완

**Phase**: 13-2
**작성일**: 2026-02-16

---

## Task 13-2-1 [BE] HTML 라우트 목록 문서화·메뉴 path 1:1 대응 검증

- [ ] main.py에서 HTML 라우트 전수 추출
- [ ] 메뉴 path 17개 목록 작성:
  - [ ] USER_MENU: /, /dashboard, /search, /knowledge, /reason, /ask, /logs
  - [ ] ADMIN_MENU: /admin/groups, /admin/labels, /admin/chunk-create, /admin/approval, /admin/chunk-labels, /admin/statistics
  - [ ] SETTINGS_MENU: /admin/settings/templates, /admin/settings/presets, /admin/settings/rag-profiles, /admin/settings/policy-sets, /admin/settings/audit-logs
- [ ] 라우트↔메뉴 1:1 대응 표 작성 (route-menu-mapping.md)
- [ ] 누락 라우트 발견 시 main.py에 추가
- [ ] Base URL(8001) 일치 확인
- [ ] curl 검증: 17개 path 모두 200 OK

## Task 13-2-2 [BE] (선택) HTML 404 전용 응답

- [ ] FastAPI 예외 핸들러에서 Accept: text/html 판별
- [ ] HTML 요청 시 404.html 템플릿 반환 로직 구현
- [ ] API 요청(Accept: application/json) 시 기존 JSON 404 유지
- [ ] /admin/unknown, /admin/settings/unknown 테스트

## Task 13-2-3 [BE] (선택) 라우트 일괄 등록 리팩터링

- [ ] 현재 main.py HTML 라우트 등록 패턴 분석
- [ ] 라우트 리스트 + 루프 패턴 설계
- [ ] 리팩터링 적용
- [ ] 기존 17개 라우트 정상 동작 회귀 확인
