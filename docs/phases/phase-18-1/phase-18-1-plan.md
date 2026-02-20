# Phase 18-1: 키워드 그룹 트리 구조 UI

## 목표

키워드 그룹 관리 페이지에 트리 구조 연결 탭을 추가하고, LLM 추천 복구, 연관 키워드 기능, 하단 액션바 통합을 수행한다.

## 현재 상태 (AS-IS)

- 3단 레이아웃: 그룹 목록(목록/트리 토글) | 그룹 상세 | 키워드 목록
- 트리뷰 컴포넌트 존재 (`keyword-group-treeview.js`, 414줄)
- LLM 키워드 추천: `keyword-group-suggestion.js` (339줄) — 그룹 생성 시에만 동작
- 연관 키워드 기능 없음
- 하단 바: matching-summary-bar (선택 연결/해제만)

## 변경 계획 (TO-BE)

### Part A: 트리 구조 연결 탭 (18-1-1, 18-1-2)
- 1단 컬럼의 목록/트리 토글 → 별도 탭 UI 전환
- 트리 연결 탭에서 D&D 계층 편집 + Breadcrumb

### Part B: 키워드 추천 복구 + 연관 키워드 (18-1-3, 18-1-4, 18-1-5)
- 키워드 목록 상단에 LLM 추천 버튼 복구
- 연관 키워드 API: ILIKE + Qdrant 유사도 결합
- 연관 키워드 섹션 UI: 유사도 % 표시 + 조회/추가

### Part C: 하단 액션바 + CSS 정리 (18-1-6, 18-1-7)
- 수정/삭제/저장 버튼 일원화
- admin-groups.css (613줄) 정리/모니터링

## Task 구조

| Task | 내용 | 도메인 | 담당 |
|------|------|--------|------|
| 18-1-1 | 그룹 관리 페이지 탭 UI (목록 탭 / 트리 연결 탭) | [FE] | frontend-dev |
| 18-1-2 | 트리 연결 탭: D&D 계층 편집 UI 강화 | [FE] | frontend-dev |
| 18-1-3 | 키워드 목록 상단에 LLM 추천 버튼 복구 | [FE] | frontend-dev |
| 18-1-4 | 연관 키워드 섹션 UI (유사도 % + 조회/추가) | [FS] | frontend-dev + backend-dev |
| 18-1-5 | 연관 키워드 API (ILIKE + Qdrant 유사도 결합) | [BE] | backend-dev |
| 18-1-6 | 하단 액션바 통합 (수정/삭제/저장 일원화) | [FE] | frontend-dev |
| 18-1-7 | 키워드 그룹 CSS 정리 | [FE] | frontend-dev |

## 의존 관계

```
18-1-5 (연관 키워드 API) ──→ 18-1-4 (연관 키워드 UI)
18-1-1 (탭 UI) ──→ 18-1-2 (트리 연결 탭 강화)
나머지는 독립
```

## 병렬 실행 가능 그룹

- **BE**: 18-1-5 (연관 키워드 API)
- **FE 선행**: 18-1-1, 18-1-3, 18-1-6 (병렬 가능)
- **FE 후행**: 18-1-2 (18-1-1 후), 18-1-4 (18-1-5 후), 18-1-7 (마지막)

## 주요 파일

### Backend
- `backend/routers/knowledge/labels.py` — 라우터
- `backend/routers/knowledge/labels_crud.py` — CRUD 핸들러
- `backend/routers/knowledge/labels_suggest.py` — AI 추천
- 신규: 연관 키워드 API 핸들러

### Frontend
- `web/src/pages/admin/groups.html` — 그룹 관리 HTML
- `web/public/js/admin/keyword-group-*.js` — 7개 JS 모듈
- `web/public/js/admin/admin-groups.js` — 초기화
- `web/public/css/admin/admin-groups.css` — 스타일 (613줄, 모니터링 대상)
