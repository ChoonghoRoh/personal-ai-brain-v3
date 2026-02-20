# Task 17-8-2: [BE] 노드 이동 API + Breadcrumb + 순환 방지

**우선순위**: 17-8 내 2순위 (17-8-1 이후 병렬)
**예상 작업량**: 중간
**의존성**: 17-8-1
**상태**: 완료

---

## §1. 개요

트리 노드를 다른 부모로 이동하는 API와 경로(Breadcrumb) 조회 API를 구현한다.
순환 참조 방지 로직을 포함한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/knowledge/labels.py` | move, breadcrumb 엔드포인트 추가 |
| 수정 | `backend/services/knowledge/labels_handlers.py` | 순환 검증 + breadcrumb 로직 |

## §3. API 엔드포인트

- `PATCH /api/labels/{id}/move` — 노드 이동 (순환 검증)
- `GET /api/labels/{id}/breadcrumb` — 경로 조회 (루트→현재)

## §4. 작업 체크리스트

- [x] PATCH /api/labels/{id}/move 엔드포인트 구현
- [x] 이동 전 조상 체인 검증 (순환 참조 방지)
- [x] GET /api/labels/{id}/breadcrumb 엔드포인트 구현
- [x] 루트→현재 노드 경로 배열 응답
