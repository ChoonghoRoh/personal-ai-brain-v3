# Task 13-3-2: [E2E] Admin 지식 6개 진입 E2E

**우선순위**: 13-3 내 2순위 (13-3-1과 병렬 가능)
**예상 작업량**: 중 (1일)
**의존성**: Phase 13-1·13-2 완료 후
**상태**: TODO

---

## 1. 목표

Admin 지식 메뉴 6개(groups, labels, chunk-create, approval, chunk-labels, statistics)의 진입 및 공통 shell 로드 E2E 테스트.

## 2. 테스트 대상

| 경로 | 페이지 | 검증 항목 |
|------|--------|----------|
| /admin/groups | 키워드 그룹 | 200 OK, Admin shell |
| /admin/labels | 라벨 관리 | 200 OK, Admin shell |
| /admin/chunk-create | 청크 생성 | 200 OK, Admin shell |
| /admin/approval | 승인 관리 | 200 OK, Admin shell |
| /admin/chunk-labels | 청크 라벨 | 200 OK, Admin shell |
| /admin/statistics | 통계 | 200 OK, Admin shell |

## 3. 참조

- Phase 13 Master Plan §E-2
- Admin 지식 메뉴 진입 시나리오 (8개)
