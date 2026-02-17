# Task 15-8-1: D3.js Force-Directed Graph 지식 노드 관계 시각화

**우선순위**: 15-8 내 1순위
**의존성**: 없음
**담당 팀원**: frontend-dev (API: backend-dev)
**상태**: DONE

---

## §1. 개요

D3.js Force-Directed Graph를 활용하여 지식 노드(documents, chunks, labels) 간 관계를 시각화하는 페이지를 구현한다. 백엔드에서 그래프 데이터를 제공하는 API를 추가하고, 프론트엔드에서 인터랙티브 그래프를 렌더링한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/knowledge/graph.py` | 신규 | 그래프 데이터 API (`GET /api/knowledge/graph`) |
| `web/src/pages/knowledge/knowledge-graph.html` | 신규 | 그래프 시각화 HTML 페이지 |
| `web/public/css/knowledge-graph.css` | 신규 | 그래프 전용 스타일시트 |
| `web/public/js/knowledge/knowledge-graph.js` | 신규 | D3.js force-directed 시뮬레이션 모듈 |
| `web/public/js/vendor/d3.v7.min.js` | 신규 | D3.js v7 로컬 번들 |
| `web/public/js/components/header-component.js` | 수정 | LNB 지식관리 그룹에 "지식 그래프" 메뉴 추가 |
| `backend/main.py` | 수정 | _HTML_ROUTES에 knowledge-graph 라우트 추가 |

## §3. 작업 체크리스트 (Done Definition)

### Backend API
- [x] `GET /api/knowledge/graph` -- 그래프 데이터 반환
  - 노드: documents (type: document), knowledge_chunks (type: chunk), labels (type: label)
  - 엣지: document-chunk (has_chunk), chunk-label (labeled_with), document-label (categorized_as)
  - 응답: `{ nodes: [{id, type, label, metadata}], edges: [{source, target, relation}] }`
  - 선택 필터: project_id, label_id, category
- [x] Redis 캐시 적용 (REDIS_GRAPH_CACHE_TTL)
- [x] `Depends(require_admin_knowledge)` 권한 적용

### Frontend 시각화
- [x] D3.js v7 force-directed simulation
  - 노드 색상: document(파랑), chunk(초록), label(주황)
  - 노드 크기: 연결 수(degree) 기반
  - 엣지 스타일: 관계 유형별 선 스타일
- [x] 인터랙션
  - 노드 드래그 (d3.drag)
  - 줌/팬 (d3.zoom)
  - 노드 호버 시 정보 패널 (제목, 타입, 연결 수)
  - 노드 클릭 시 연관 문서/청크 상세
- [x] 반응형 레이아웃 (SVG viewBox)
- [x] 성능: P95 1초 이내 렌더링 (100+ 노드), P99 2초 이내

### LNB/라우트
- [x] LNB 지식관리 그룹에 "지식 그래프" 메뉴 항목 추가
- [x] `_HTML_ROUTES`에 `("/knowledge/knowledge-graph", "knowledge/knowledge-graph.html", "지식 그래프")` 추가

### 통합
- [x] 페이지 로드 시 콘솔 에러 없음
- [x] 기존 LNB/레이아웃 스타일과 일관성
- [x] innerHTML 사용 시 esc() 적용

## §4. 참조

- `docs/phases/phase-15-master-plan.md` -- SS2.3.5 D3.js 지식 그래프 시각화 전략
- `backend/routers/knowledge/` -- 기존 knowledge 라우터 구조
- `web/public/js/components/header-component.js` -- LNB 메뉴 구조
- `backend/main.py` -- _HTML_ROUTES 라우트 등록
