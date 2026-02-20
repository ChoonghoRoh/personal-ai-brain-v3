# Phase 18-0: 선행 리팩토링 (Lv1) — labels_handlers.py 분리

## 목표

`labels_handlers.py`(748줄, Lv1)를 기능 단위로 3개 파일로 분리하여 유지보수성을 확보한다.
Phase 18-1에서 해당 파일을 수정하므로 필수 선행 작업이다.

## 근거

- 리팩토링 레지스트리 #1: `labels_handlers.py` 748줄 / Lv1 / 조사 대기
- REFACTOR-2: Master Plan 작성 시 700줄 초과 → 리팩토링 편성

## 현재 구조 (AS-IS)

```
backend/routers/knowledge/labels_handlers.py (748줄)
  ├── CRUD 핸들러 (create/read/update/delete label)   ~250줄
  ├── 트리 API 핸들러 (tree/move/breadcrumb)           ~280줄
  └── 추천 핸들러 (suggest-parent, suggest-keywords)    ~180줄
```

## 목표 구조 (TO-BE)

```
backend/routers/knowledge/
  ├── labels_crud.py       (~250줄) — Label CRUD 핸들러
  ├── labels_tree.py       (~280줄) — 트리 조회/이동/Breadcrumb
  └── labels_suggest.py    (~180줄) — AI 추천 핸들러
```

## Task 구조

| Task | 내용 | 도메인 | 의존성 |
|------|------|--------|--------|
| 18-0-1 | `labels_crud.py` 분리 — Label CRUD 핸들러 추출 | [BE] | 없음 |
| 18-0-2 | `labels_tree.py` 분리 — 트리 조회/이동/Breadcrumb 추출 | [BE] | 18-0-1 |
| 18-0-3 | `labels_suggest.py` 분리 — AI 추천 핸들러 추출 + import 정리 + 테스트 통과 검증 | [BE] | 18-0-2 |

## 완료 기준

- [ ] 원본 `labels_handlers.py` 삭제
- [ ] 3개 파일로 완전 분리
- [ ] `labels.py` 라우터의 import 경로 수정
- [ ] 기존 테스트 전체 통과 (pytest)
- [ ] 리팩토링 레지스트리 해소 이력 기재

## 리스크

- 다른 파일에서 `labels_handlers` import → Grep으로 전수 조사 필요
- 순환 참조 발생 가능 → 공통 의존성 분리 또는 인터페이스 추출
