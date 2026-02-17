# Phase 15-8 Plan: (선택) 지식 그래프 시각화 및 인프라 고도화

**Phase**: 15-8
**작성일**: 2026-02-17
**상태**: DONE

---

## 1. 목표

지식 그래프 시각화와 인프라 고도화를 통해 엔터프라이즈 수준의 탐색 경험과 시스템 성능을 확보한다.
- D3.js Force-Directed Graph로 지식 노드 간 관계를 시각화 (P95 1초, P99 2초 목표)
- Redis 캐싱 확대 (중복 질의 캐시, Reasoning/Graph 캐시 TTL) 및 Qdrant 벡터 양자화
- 4대 추론 모드(design_explain, risk_review, next_steps, history_trace), Re-ranking, 하이브리드 검색 정리 문서

## 2. 범위

| 포함 | 제외 |
|------|------|
| D3.js Force-Directed Graph API + FE 시각화 | Mermaid.js 연동 (별도 확장) |
| Redis Reasoning/Graph 캐시 TTL 설정 | Redis Pub/Sub 워크플로우 동기화 |
| Qdrant 벡터 양자화 설정 (config.py) | Qdrant 클러스터링/샤딩 |
| 4대 추론 모드 정리 문서 | 신규 추론 모드 구현 (legal_compliance 등) |
| D3.js v7 로컬 번들 | CDN 의존 |

## 3. 설계 결정

| 결정 | 선택 | 근거 |
|------|------|------|
| 그래프 라이브러리 | D3.js v7 (로컬 번들) | CDN 미의존, 에어갭 환경 지원, Force-Directed 최적화 |
| 그래프 데이터 API | `GET /api/knowledge/graph` | 기존 knowledge 라우터 prefix 활용 |
| 노드 구성 | documents + labels + knowledge_chunks | 지식 엔티티 간 관계 시각화 |
| Redis 캐시 TTL | Reasoning 300s, Graph 600s | 중복 질의 응답 0.3초 이내 목표 |
| Qdrant 양자화 | Scalar (32bit->8bit) config.py 설정 | 메모리 75% 절감, 정확도 손실 최소 |
| 추론 모드 문서 | Markdown 정리 | 운영 참조용, 모드별 프롬프트/파이프라인 명세 |

## 4. 리스크

| 리스크 | 영향 | 대응 |
|--------|------|------|
| 100+ 노드 렌더링 성능 | 중 | D3.js tick 최적화, 노드 수 제한 옵션 |
| Redis 캐시 무효화 타이밍 | 저 | TTL 기반 자동 만료, 수동 flush API 제공 |
| Qdrant 양자화 정확도 저하 | 저 | Scalar 양자화로 손실 최소화, 벤치마크 수행 |
| D3.js 번들 용량 | 저 | minified 번들 사용 (d3.v7.min.js) |

## 5. 참조

- `docs/phases/phase-15-master-plan.md` -- Phase 15 전체 계획 (15-8 선택 섹션, SS2.3.5, SS2.3.6)
- `docs/phases/phase-15-8/reasoning-modes.md` -- 4대 추론 모드 정리 산출물
- `backend/routers/knowledge/graph.py` -- 그래프 데이터 API
- `web/public/js/knowledge/knowledge-graph.js` -- D3.js 시각화
- `backend/config.py` -- Redis/Qdrant 설정
