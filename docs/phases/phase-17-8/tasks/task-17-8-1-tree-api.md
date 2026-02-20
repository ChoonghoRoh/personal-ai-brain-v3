# Task 17-8-1: [BE] 재귀 트리 조회 API + 깊이 제한

**우선순위**: 17-8 내 1순위 (다른 Task의 기반)
**예상 작업량**: 중간
**의존성**: 없음
**상태**: 완료

---

## §1. 개요

키워드 그룹↔키워드 관계를 다단계 트리 구조로 조회하는 API를 구현한다.
CTE(Common Table Expression) 재귀 쿼리를 사용하여 전체/부분 트리를 조회한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/knowledge/labels.py` | 트리 조회 엔드포인트 추가 |
| 수정 | `backend/services/knowledge/labels_handlers.py` | CTE 재귀 쿼리 구현 |

## §3. API 엔드포인트

- `GET /api/labels/tree?max_depth=5` — 전체 트리 조회
- `GET /api/labels/groups/{id}/tree?max_depth=5` — 그룹 하위 트리 조회

## §4. 작업 체크리스트

- [x] CTE 재귀 쿼리로 전체 트리 조회 구현
- [x] max_depth 파라미터로 깊이 제한
- [x] children 재귀 구조 응답 (id, name, label_type, children)
- [x] 그룹별 하위 트리 조회 구현
