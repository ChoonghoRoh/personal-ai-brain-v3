# Task 17-5-3: [BE] 통계 API 필터링 파라미터 추가

**우선순위**: 17-5 내 1순위 (FE 의존)
**예상 작업량**: 중간
**의존성**: 없음
**상태**: 대기

---

## §1. 개요

통계 대시보드 하단 목록에 사용할 리스트 API를 추가한다. 문서/청크/라벨/추론기록 각각에 대해 페이지네이션+필터를 지원하는 엔드포인트를 추가한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/system/statistics.py` | 4개 리스트 엔드포인트 추가 |
| 수정 | `backend/services/system/statistics_service.py` | 4개 리스트 메서드 추가 |

## §3. 엔드포인트

1. `GET /api/system/statistics/documents/list` — page, size, type, q, sort_by, sort_order
2. `GET /api/system/statistics/chunks/list` — page, size, status, q, sort_by, sort_order
3. `GET /api/system/statistics/labels/list` — page, size, label_type, q, sort_by, sort_order
4. `GET /api/system/statistics/usage/list` — page, size, mode, from_date, to_date, sort_by, sort_order

## §4. 응답 형식 (공통)

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "total_pages": 5
}
```
