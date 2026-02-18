# Task 17-1-1: [BE] 그룹 목록 페이지네이션 API

**우선순위**: 17-1 내 1순위
**예상 작업량**: 소
**의존성**: 없음 (Phase 16 완료 전제)
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

키워드 그룹 목록 API에 페이지네이션 파라미터(page, size)를 추가하고, 응답에 total 카운트를 포함하여 FE 페이지네이션 UI를 지원한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/knowledge/labels.py` | page, size 쿼리 파라미터 추가 |
| 수정 | `backend/routers/knowledge/labels_handlers.py` | 페이지네이션 쿼리 + total 카운트 응답 |

## §3. 작업 체크리스트 (Done Definition)

- [x] GET /api/labels/groups?page=1&size=20 파라미터 수용
- [x] 응답 형식: { items: [...], total: int, page: int, size: int }
- [x] page 기본값 1, size 기본값 20
- [x] 기존 전체 목록 조회 API 하위 호환 유지

## §4. 참조

- [Phase 17 Master Plan §4](../../phase-17-master-plan.md)
- [Phase 17 개발 요구사항 §2](../../../planning/260218-0830-phase17-개발-요구사항.md)
