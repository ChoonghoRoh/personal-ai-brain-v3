# Phase 13-3 Todo List — E2E·검증 확대

**Phase**: 13-3
**작성일**: 2026-02-16

---

## Task 13-3-1 [E2E] 사용자 메뉴 6개 진입·헤더 활성 E2E

- [ ] E2E 스펙 파일 생성 (phase-13-menu-user.spec.js)
- [ ] 각 메뉴 진입 테스트:
  - [ ] / (Dashboard)
  - [ ] /search (검색)
  - [ ] /knowledge (지식 탐색)
  - [ ] /reason (Reasoning Lab)
  - [ ] /ask (AI 질문)
  - [ ] /logs (로그)
- [ ] 각 페이지 진입 시 헤더 메뉴 활성 하이라이트 검증
- [ ] 페이지 로드 200 OK 확인

## Task 13-3-2 [E2E] Admin 지식 6개 진입 E2E

- [ ] E2E 스펙 파일 생성 (phase-13-menu-admin-knowledge.spec.js)
- [ ] 각 메뉴 진입 테스트:
  - [ ] /admin/groups (키워드 그룹)
  - [ ] /admin/labels (라벨 관리)
  - [ ] /admin/chunk-create (청크 생성)
  - [ ] /admin/approval (승인 관리)
  - [ ] /admin/chunk-labels (청크 라벨)
  - [ ] /admin/statistics (통계)
- [ ] Admin 공통 shell 로드 확인
- [ ] 헤더 활성 메뉴 검증

## Task 13-3-3 [E2E] 메뉴 간 이동·404 시나리오 E2E

- [ ] 메뉴 간 이동 E2E:
  - [ ] 사용자 메뉴 → Admin 지식 메뉴
  - [ ] Admin 지식 메뉴 → Admin 설정 메뉴
  - [ ] Admin 설정 메뉴 → 사용자 메뉴
  - [ ] 사용자 → Admin 지식 → Admin 설정 → 사용자 전체 순회
- [ ] 404 시나리오 E2E:
  - [ ] /admin/unknown → 404 응답
  - [ ] /admin/settings/unknown → 404 응답
  - [ ] /dashbord (오타) → 404 응답

## Task 13-3-4 [DOC] 36개 시나리오↔E2E 매핑 문서 갱신

- [ ] 36개 시나리오 ID 전수 목록 작성
- [ ] 각 시나리오에 대응하는 E2E 스펙·테스트 케이스 ID 매핑
- [ ] 미커버 시나리오 식별·수동/MCP 테스트 계획
- [ ] web-service-menu-restructuring-scenarios.md §7 갱신
