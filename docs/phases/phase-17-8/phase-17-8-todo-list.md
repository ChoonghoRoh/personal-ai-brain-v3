# Phase 17-8 Todo List: 트리 구조 + AI 추천 연결

> **상태**: 완료 (소급 생성)
> **완료일**: 2026-02-20

## Task 17-8-1: [BE] 재귀 트리 조회 API + 깊이 제한

- [x] `GET /api/labels/tree?max_depth=5` 전체 트리 조회 (CTE 재귀 쿼리)
- [x] `GET /api/labels/groups/{id}/tree?max_depth=5` 그룹 하위 트리 조회
- [x] max_depth 파라미터로 깊이 제한
- [x] children 재귀 구조 응답 (id, name, label_type, children)

## Task 17-8-2: [BE] 노드 이동 API + Breadcrumb + 순환 방지

- [x] `PATCH /api/labels/{id}/move` 노드 이동 API
- [x] 순환 참조 방지 로직 (이동 전 조상 체인 검증)
- [x] `GET /api/labels/{id}/breadcrumb` 경로 조회 (루트→현재)

## Task 17-8-3: [BE] AI 부모 노드 추천

- [x] `POST /api/labels/suggest-parent` AI 부모 노드 추천 API
- [x] 기존 트리 구조 분석 → LLM 컨텍스트 주입
- [x] group_keyword_recommender.py 연동

## Task 17-8-4: [FE] 트리뷰 컴포넌트 (접기/펼치기 + D&D)

- [x] keyword-group-treeview.js 신규 생성
- [x] 트리 노드 접기/펼치기 UI
- [x] 드래그 앤 드롭으로 노드 이동
- [x] groups.html에 트리뷰 영역 추가
- [x] admin-groups.css 트리뷰 스타일

## Task 17-8-5: [FE] Breadcrumb + 검색 시 트리 하이라이트

- [x] Breadcrumb 컴포넌트 (루트→현재 경로 표시)
- [x] 검색 시 매칭 노드 하이라이트
- [x] 트리 자동 펼침 (검색 결과 노드까지)

## Gate 결과

| Gate | 결과 |
|------|------|
| G1 계획 리뷰 | PASS |
| G2 BE 코드 리뷰 | PASS |
| G2 FE 코드 리뷰 | PASS |
| G3 테스트 | PASS (import OK, 회귀 26/26) |
| G4 최종 | PASS |
