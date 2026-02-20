# Phase 18-4 TODO List

## Task 18-4-1: Qdrant status 필터
- [ ] hybrid_search.py semantic_search에 status 필터 추가
- [ ] search API에 status 파라미터 추가
- [ ] Qdrant payload에 status 확인/업데이트

## Task 18-4-2: 검색 결과 UI 차별화
- [ ] 모드별 배지 (semantic/keyword/hybrid)
- [ ] 점수 의미 표시 (높음/중간/낮음)
- [ ] search.js 결과 렌더링 개선

## Task 18-4-3: snippet 하이라이트
- [ ] BE: 검색 결과에 하이라이트된 snippet 반환
- [ ] FE: snippet 표시 + 컨텍스트 확장 토글

## Task 18-4-4: cross-document 관계 추천
- [ ] Qdrant point ID 기반 유사 청크 검색
- [ ] cross-document 관계 추천 API

## Task 18-4-5: 관계 타입 자동 분류
- [ ] similar/prerequisite/extends 자동 분류 로직
- [ ] 추천 UI 리디자인
