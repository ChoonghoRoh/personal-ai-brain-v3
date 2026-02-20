---
chain_name: "phase-18-refactor-ui-renewal"
phases: ["18-0", "18-1", "18-2", "18-3", "18-4"]
current_index: 5
status: "completed"
ssot_version: "6.0-renewal-4th"
created_at: "2026-02-21T09:00:00Z"
phase_summaries:
  "18-0": "선행 리팩토링 완료 — labels_handlers.py(748줄) → labels_crud.py(396) + labels_tree.py(151) + labels_suggest.py(227) 3파일 분리. 테스트 168 passed"
  "18-1": "키워드 그룹 트리 탭 UI + LLM 추천 복구 + 연관 키워드 API/UI + 하단 액션바 통합 완료. 테스트 168 passed. admin-groups.css 805줄 Lv2 확정"
  "18-2": "지식 구조 UI 완료 — 폴더 트리 API + 통합 트리 API (BE), 폴더 트리뷰 컴포넌트 + 통합 트리 페이지 + Breadcrumb (FE). 테스트 168 passed"
  "18-3": "Reasoning 리뉴얼 완료 — Step 1~4 순차 진행 UI + SSE 연동 + 모드 예시 + CSS 5파일 분리(607+597→base/form/steps/results/actions) + 중간 미리보기 + 세션 UI 개선. 테스트 168 passed"
  "18-4": "검색 품질 + 관계 추천 완료 — Qdrant status 필터 + 검색 UI 차별화(배지/점수) + snippet 하이라이트 + cross-document 관계 추천 API + 관계 타입 자동 분류. 테스트 168 passed"
---

# Phase Chain: 18-0 ~ 18-4

## 목표

선행 리팩토링 + 키워드 그룹 트리 UI + 지식 구조 UI + Reasoning 리뉴얼 + 검색 품질 고도화.

## 실행 대상

| Phase | 내용 | Task 수 | 의존성 |
|-------|------|:-------:|--------|
| 18-0 | 선행 리팩토링 (labels_handlers.py Lv1 분리) | 3 | 독립 (최우선) |
| 18-1 | 키워드 그룹 트리 구조 UI | 7 | 18-0 |
| 18-2 | 지식 구조 UI (폴더 트리 + 통합 트리) | 5 | 독립 |
| 18-3 | Reasoning 페이지 리뉴얼 | 6 | 독립 |
| 18-4 | 검색 품질 + 관계 추천 고도화 | 5 | 독립 |

## 마일스톤

- **M0**: 18-0 완료 (선행 리팩토링)
- **M1**: 18-1 완료 (키워드 그룹 트리 탭 + 추천 UX)
- **M2**: 18-2 완료 (지식 구조 통합 트리)
- **M3**: 18-3 완료 (Reasoning 리뉴얼)
- **M4**: 18-4 완료 (검색 + 관계 품질)

## 참조

- [Phase 18 Master Plan](phase-18-master-plan.md)
- [리팩토링 레지스트리](../refactoring/refactoring-registry.md)
- [SSOT Phase Chain Protocol](../SSOT/renewal/iterations/4th/3-workflow.md#8-phase-chain-자동-순차-실행)
