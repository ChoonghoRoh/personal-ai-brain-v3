# Phase 13-3 Plan — E2E·검증 확대

**작성일**: 2026-02-16
**Phase**: 13-3 (3순위)
**목표**: 사용자 메뉴 6개·Admin 지식 6개 E2E, 메뉴 간 이동·404 E2E, 36개 시나리오↔E2E 매핑
**기준 문서**: [phase-13-master-plan.md](../phase-13-master-plan.md)

---

## 목표

메뉴 개편 검증용 E2E 테스트 확대 4건:
1. 사용자 메뉴 6개(dashboard, search, knowledge, reason, ask, logs) 진입·헤더 활성 E2E
2. Admin 지식 6개(groups, labels, chunk-create, approval, chunk-labels, statistics) 진입 E2E
3. 메뉴 간 이동(사용자→Admin→설정→사용자)·404(/admin/unknown 등) E2E
4. 36개 시나리오와 E2E 테스트 케이스 ID 매핑 문서 갱신

## Task 구성

| Task | 도메인 | 목표 | 산출물 | 예상 |
|------|--------|------|--------|------|
| 13-3-1 | [E2E] | 사용자 메뉴 6개 진입·헤더 활성 E2E | phase-13-menu-user.spec.js | 1일 |
| 13-3-2 | [E2E] | Admin 지식 6개 진입 E2E | phase-13-menu-admin-knowledge.spec.js | 1일 |
| 13-3-3 | [E2E] | 메뉴 간 이동·404 시나리오 E2E | phase-13-menu-cross.spec.js | 0.5일 |
| 13-3-4 | [DOC] | 36개 시나리오↔E2E 매핑 문서 갱신 | scenarios 문서 §7 갱신 | 0.5일 |

## 구현 순서

- 13-3-1, 13-3-2: 병렬 가능
- 13-3-3: 13-3-1, 13-3-2 이후 권장
- 13-3-4: 최종 (전체 E2E 결과 반영)

## 의존성

- Phase 13-1·13-2 완료 후 권장 (메뉴·라우트 안정화 후 E2E)

## 검증 방법

- E2E 스펙 전체 통과 (playwright 또는 MCP 기반)
- 36개 시나리오 중 E2E 커버 시나리오 수 확인
