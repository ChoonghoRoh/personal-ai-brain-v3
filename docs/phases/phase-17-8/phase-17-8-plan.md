# Phase 17-8: 트리 구조 + AI 추천 연결

## 목표

키워드 그룹↔키워드 관계를 플랫 1단계에서 다단계 트리 구조로 확장하고,
LLM 기반 부모 노드 자동 추천 기능을 추가한다.

## 현재 상태 (AS-IS)

- `Label.parent_label_id` FK 정의됨 (self-referential)
- 1단계 계층만 활용 (keyword_group → keyword)
- 다단계 재귀 조회, 순환 참조 방지 미구현
- 트리뷰 UI 없음 (플랫 리스트만)

## 변경 계획 (TO-BE)

### Backend (3 tasks)

| Task | 내용 | 변경 파일 |
|------|------|-----------|
| 17-8-1 | 재귀 트리 조회 API + 깊이 제한 | `labels.py`, `labels_handlers.py` |
| 17-8-2 | 노드 이동 API + Breadcrumb API + 순환 방지 | `labels.py`, `labels_handlers.py` |
| 17-8-3 | AI 부모 노드 추천 (트리 분석→LLM) | `labels.py`, `labels_handlers.py`, `group_keyword_recommender.py` |

### Frontend (2 tasks)

| Task | 내용 | 변경 파일 |
|------|------|-----------|
| 17-8-4 | 트리뷰 컴포넌트 (접기/펼치기 + D&D) | `keyword-group-treeview.js`(신규), `groups.html`, `admin-groups.css` |
| 17-8-5 | Breadcrumb + 검색 시 트리 하이라이트 | `keyword-group-treeview.js`, `keyword-group-search.js`, `admin-groups.css` |

## API 엔드포인트 (신규)

```
GET  /api/labels/tree?max_depth=5              — 전체 트리 조회
GET  /api/labels/groups/{id}/tree?max_depth=5  — 그룹 하위 트리 조회
PATCH /api/labels/{id}/move                     — 노드 이동 (순환 검증)
GET  /api/labels/{id}/breadcrumb               — 경로 조회 (루트→현재)
POST /api/labels/suggest-parent                 — AI 부모 노드 추천
```

## 의존 관계

17-8-1 → (17-8-2, 17-8-3, 17-8-4 병렬) → 17-8-5
