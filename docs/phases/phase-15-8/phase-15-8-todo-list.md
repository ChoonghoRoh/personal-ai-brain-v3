# Phase 15-8 Todo List: (선택) 지식 그래프 시각화 및 인프라 고도화

**Phase**: 15-8
**G1 판정**: PASS
**작성일**: 2026-02-17

---

- [x] Task 15-8-1: [FE] D3.js Force-Directed Graph 지식 노드 관계 시각화 (Owner: frontend-dev)
  - `GET /api/knowledge/graph` API 엔드포인트 (backend)
  - 노드: documents, labels, knowledge_chunks
  - 엣지: document-chunk, chunk-label, document-label 관계
  - D3.js v7 force-directed simulation
  - 노드 드래그, 줌/팬, 호버 정보 패널
  - `/knowledge/knowledge-graph` HTML 페이지 + LNB 메뉴
  - P95 1초 이내 렌더링 (100+ 노드)

- [x] Task 15-8-2: [BE] Redis 캐싱 확대, Qdrant 벡터 양자화 (Owner: backend-dev)
  - `REDIS_REASONING_CACHE_TTL` 설정 (기본 300초)
  - `REDIS_GRAPH_CACHE_TTL` 설정 (기본 600초)
  - `QDRANT_QUANTIZATION_ENABLED` / `QDRANT_QUANTIZATION_TYPE` 설정
  - config.py에 환경변수 통합
  - 캐시 히트 시 응답 시간 목표: Redis 10ms, Qdrant 검색 100ms

- [x] Task 15-8-3: [DOC] 4대 추론 모드 및 Re-ranking, 하이브리드 검색 정리 (Owner: backend-dev)
  - design_explain 모드 정리 (설계 설명, Mermaid 시각화)
  - risk_review 모드 정리 (리스크 검토 매트릭스)
  - next_steps 모드 정리 (후속 절차 로드맵)
  - history_trace 모드 정리 (이력 추적 타임라인)
  - Re-ranking (Cross-Encoder) 전략 정리
  - 하이브리드 검색 (Sparse + Dense) 전략 정리
  - 캐싱/양자화 정책 정리
