# Phase 18-2 Todo List

## Task 18-2-1: Document 폴더 계층 API [BE]
- [ ] GET /api/knowledge/folder-tree?project_id={id} API 생성
- [ ] file_path 파싱하여 가상 폴더 구조 구성
- [ ] 응답: 트리 형태 (폴더 노드 + 문서 노드)

## Task 18-2-2: 폴더 트리뷰 UI [FE]
- [ ] 트리뷰 컴포넌트 생성 (접기/펼치기)
- [ ] 폴더 아이콘 + 문서 아이콘 구분
- [ ] 문서 클릭 시 document 페이지 이동

## Task 18-2-3: 통합 지식 트리 API [BE]
- [ ] GET /api/knowledge/tree?project_id={id} API 생성
- [ ] Project→폴더→Document→Chunk 계층 구성
- [ ] 청크에 라벨 정보 포함 (선택적)

## Task 18-2-4: 통합 트리뷰 페이지 UI [FE]
- [ ] knowledge-tree.html 신규 페이지 또는 기존 페이지 내 사이드 패널
- [ ] 통합 트리 렌더링 (Project→폴더→문서→청크)
- [ ] 노드 클릭 시 상세 정보 표시

## Task 18-2-5: Breadcrumb 전역 네비게이션 [FE]
- [ ] 문서 관련 페이지에 Breadcrumb 컴포넌트 추가
- [ ] Project > 폴더 > 문서 > 청크 경로 표시
- [ ] 각 경로 항목 클릭 가능
