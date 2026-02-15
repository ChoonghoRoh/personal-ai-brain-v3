# Task 13-3-1: [E2E] 사용자 메뉴 6개 진입·헤더 활성 E2E

**우선순위**: 13-3 내 1순위
**예상 작업량**: 중 (1일)
**의존성**: Phase 13-1·13-2 완료 후
**상태**: TODO

---

## 1. 목표

사용자 메뉴 6개(dashboard, search, knowledge, reason, ask, logs)의 진입 및 헤더 활성 메뉴 하이라이트 E2E 테스트.

## 2. 테스트 대상

| 경로 | 페이지 | 검증 항목 |
|------|--------|----------|
| / | Dashboard | 200 OK, 헤더 active |
| /search | 검색 | 200 OK, 헤더 active |
| /knowledge | 지식 탐색 | 200 OK, 헤더 active |
| /reason | Reasoning Lab | 200 OK, 헤더 active |
| /ask | AI 질문 | 200 OK, 헤더 active |
| /logs | 로그 | 200 OK, 헤더 active |

## 3. 참조

- Phase 13 Master Plan §E-1
- 사용자 메뉴 진입 시나리오 (8개)
