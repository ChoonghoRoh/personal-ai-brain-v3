# Phase 16 Master Plan — AI 자동화 고도화 및 대형 파일 리팩토링

**작성일**: 2026-02-17  
**역할**: PM(Project Manager) 마스터 플랜  
**선행 조건**: Phase 15 완료 (지식관리·AI 자동화·Reasoning·회원·보안·안정화).  
**기준 문서**:

- [260217-1600-AI자동화기능-리스크분석.md](../planning/260217-1600-AI자동화기능-리스크분석.md) — 80+ 파일 처리 시 리스크·개선 방안·우선순위 로드맵
- [260217-1400-500lines-over-index-and-refactor-guide.md](../planning/260217-1400-500lines-over-index-and-refactor-guide.md) — 500줄 초과 파일 인덱스·영향도·리팩토링 가이드

---

## 1. 목표 및 범위

### 1.1 Phase 16 목표 (1문장)

**AI 자동화 파이프라인이 80개 이상 파일 처리 시에도 안정·성능·UX를 만족하도록 백엔드·프론트엔드 개선을 적용하고, 동시에 backend/web 내 500줄 초과 대형 파일을 영향도 기반으로 단계적 리팩토링하여 유지보수성과 품질 게이트를 강화한다.**

### 1.2 범위 요약

| 블록 | 내용 |
|------|------|
| **AI 자동화 고도화 (16-1~16-3)** | 리스크 분석 문서의 Phase 1(즉시)·Phase 2(중기)·Phase 3(장기) 개선안 적용: UI(사전 검증·세부 진행률·Virtual Scroll·SSE Heartbeat), 백엔드(Qdrant 배치·LLM 묶음·DB 트랜잭션 분할·배치 분할·라벨 역인덱스·Streaming Results·Celery 옵션). |
| **Backend 리팩토링 (16-4)** | 500줄 초과 백엔드 파일 9개: 서비스 계층 → 라우터 계층 → main.py 순으로 라우터+핸들러·서비스 서브 모듈·라우터 레지스트리 분리. |
| **Web JS 리팩토링 (16-5)** | 500줄 초과 프론트엔드 JS 9개(백업 제외): Admin(knowledge-files, label-manager, ai-automation, chunk-approval-manager, statistics) → Knowledge·Dashboard·Reason, 기능별 모듈 분리·공통 유틸 추출·reason_backup 정리. |
| **Web CSS 리팩토링 (16-6)** | 500줄 초과 CSS 6개: reason·knowledge·admin 페이지/기능 단위 분할, 공통 변수·중복 제거 (선택·병렬 가능). |
| **검증·문서 (16-7)** | E2E·단위 테스트 회귀, 500줄 인덱스·영향도 문서 갱신, 리팩토링·자동화 고도화 운영 가이드. |

---

## 2. 기준 문서 반영 요약

### 2.1 AI 자동화 리스크 분석 (260217-1600) 반영

| 구분 | 방안 ID | 내용 | Phase 16 대응 |
|------|---------|------|---------------|
| **Phase 1 (즉시)** | C | 사전 검증 UI (선택 문서 수·예상 청크·예상 소요 시간) | 16-1-2 |
| | B | 단계별 세부 진행률 + 청크 카운터 + ETA | 16-1-1 |
| | H | DB 트랜잭션 분할 (단계별 세션) | 16-1-3 |
| | D | SSE 재연결 + Heartbeat | 16-1-4 |
| **Phase 2 (중기)** | E | Qdrant 배치 임베딩 (50건 단위) | 16-2-1 |
| | F-1 | LLM 키워드 묶음 호출 (5~10청크/1회) | 16-2-2 |
| | I | 자동 배치 분할 실행 (20문서/배치) | 16-2-3 |
| | G | 라벨 역인덱스 매칭 | 16-2-4 |
| **Phase 3 (장기)** | K | 파일별 완료 즉시 반영 (Streaming Results) | 16-3-1 |
| | A | Virtual Scroll 문서 리스트 | 16-3-2 |
| | J | Celery/큐 기반 비동기 (옵션) | 16-3-3 |

### 2.2 500줄 초과 리팩토링 가이드 (260217-1400) 반영

| 구분 | 가이드 내용 | Phase 16 대응 |
|------|-------------|---------------|
| **Backend** | 서비스 → 라우터 → main 순, 라우터+핸들러·서비스 서브 모듈 | 16-4 |
| **Web JS** | 백업 제거 → Admin 대형 → Knowledge/Dashboard/Reason, 기능별 모듈·공통 유틸 | 16-5 |
| **Web CSS** | 페이지/기능 단위 분할, 공통 변수·중복 제거 | 16-6 |
| **영향도** | 직접 의존·역의존·API 계약·테스트·우선순위 채운 뒤 작업 | 16-4·16-5·16-6 각 Task 전 필수 |
| **실행 절차** | 영향도 작성 → 테스트 통과 확인 → 분할 계획 → 작업 → 문서 갱신 | 16-7 검증 절차에 통합 |

---

## 3. Phase 16 구조

```
Phase 16

16-1   AI 자동화 Phase 1 (즉시 적용 — 코드 변경 최소)
       ├── 16-1-1   [BE] 단계별 세부 진행률·청크 카운터·ETA SSE 이벤트 (progress 이벤트 detail/eta_seconds)
       ├── 16-1-2   [FE] 파일 선택 시 사전 검증 UI (선택 수·예상 청크·예상 소요·50개 초과 시 경고)
       ├── 16-1-3   [BE] DB 트랜잭션 분할 (단계별 Session 분리·커밋)
       └── 16-1-4   [BE+FE] SSE Heartbeat·재연결 (backend 0.5s heartbeat, FE 30s 타임아웃·재연결)

16-2   AI 자동화 Phase 2 (중기 — 성능 핵심)
       ├── 16-2-1   [BE] Qdrant 배치 임베딩 (50건 단위 batch upsert, SentenceTransformer encode 배치)
       ├── 16-2-2   [BE] LLM 키워드 추출 묶음 호출 (5~10 청크/1회, 결과 파싱 후 청크별 할당)
       ├── 16-2-3   [BE] 자동 배치 분할 실행 (20문서/배치, 배치 간 GC·진행률 0~25%/25~50%/…)
       └── 16-2-4   [BE] 라벨 매칭 역인덱스 (keyword→[label_id], O(N*M)→O(N*K))

16-3   AI 자동화 Phase 3 (장기 — UX·인프라)
       ├── 16-3-1   [BE+FE] 파일별 완료 즉시 반영 (doc_result 이벤트, 결과 패널·문서 완료 표시)
       ├── 16-3-2   [FE] Virtual Scroll 문서 리스트 (가시 영역 ~22개 노드, 500개 대비 96% DOM 절감)
       └── 16-3-3   [BE+INFRA] (선택) Celery/Redis 큐 기반 비동기·workflow_tasks 테이블

16-4   Backend 500줄 초과 리팩토링
       ├── 16-4-1   [BE] 서비스 계층: recommendation_service, ai_workflow_service, statistics_service
       ├── 16-4-2   [BE] 라우터 계층: knowledge.py, labels.py, reason.py, reason_stream.py, ai.py
       └── 16-4-3   [BE] main.py 축소 (라우터 레지스트리/미들웨어 정리)

16-5   Web JS 500줄 초과 리팩토링
       ├── 16-5-1   [FE] reason_backup.js 참조 제거·삭제 검토
       ├── 16-5-2   [FE] Admin: knowledge-files.js, label-manager.js, ai-automation.js, chunk-approval-manager.js, statistics.js
       ├── 16-5-3   [FE] Knowledge·Dashboard·Reason: knowledge-detail.js, dashboard.js, reason-render.js, knowledge-relation-matching.js
       └── 16-5-4   [FE] 공통 유틸 추출 (admin-common·API·에러 처리)

16-6   Web CSS 리팩토링 (선택·병렬)
       ├── 16-6-1   [FE] reason.css, knowledge-detail.css, knowledge-admin.css 분할
       └── 16-6-2   [FE] admin-knowledge-files.css, settings-common.css, admin-ai-automation.css 분할·공통 변수

16-7   검증·문서화
       ├── 16-7-1   [QA] E2E·단위 테스트 회귀 (자동화·지식·Admin·Reason)
       ├── 16-7-2   [DOC] 500줄 인덱스·영향도·리팩토링 가이드 갱신
       └── 16-7-3   [DOC] AI 자동화 고도화 운영 가이드 (배치 크기·Rate Limit·모니터링)
```

---

## 4. 16-1 AI 자동화 Phase 1 (즉시 적용)

### 4.1 목표

리스크 분석 Phase 1: 사용자 인지·연결 안정성·DB 커넥션 안정성. 기능 동작 변경 없이 안정성·UX만 개선.

### 4.2 Task 상세

#### 16-1-1 [BE] 단계별 세부 진행률·청크 카운터·ETA

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.1 방안 B |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py`, (진행률 발행 로직), `backend/routers/automation/` SSE 응답 |
| **구현 요약** | `progress` SSE 이벤트에 `detail: { current, total, item_name }`, `eta_seconds`(선택) 포함. 단계 내 청크/문서 인덱스로 세부 진행률 계산. |
| **완료 기준** | SSE 클라이언트에서 `d.detail.current/total`, `d.eta_seconds` 수신 가능. 기존 `progress_pct` 호환 유지. |
| **테스트** | `tests/test_automation*.py` 또는 수동 SSE 구독으로 payload 검증. |

#### 16-1-2 [FE] 파일 선택 시 사전 검증 UI

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.1 방안 C |
| **변경 파일** | `web/public/js/admin/ai-automation.js`, (선택) `web/public/css/admin/admin-ai-automation.css` |
| **구현 요약** | 선택 문서 수 변경 시: `예상 청크 ≈ selected.length * 12`, `예상 소요 ≈ ceil(예상 청크/10)` 분. 50개 초과 시 "대량 처리 - 배치 분할 권장" 경고 표시. |
| **완료 기준** | 체크박스 선택/해제 시 요약 영역에 "선택: N개 \| 예상 청크: ~M \| 예상 소요: ~K분" 갱신. 50개 초과 시 warn 스타일 적용. |
| **테스트** | E2E 또는 수동: 선택 10/50/80 시 UI 텍스트·스타일 확인. |

#### 16-1-3 [BE] DB 트랜잭션 분할

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.2 방안 H |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py` |
| **구현 요약** | `execute_workflow`(또는 run-full 진입점) 내 단계별로 `SessionLocal()` 컨텍스트 분리. 텍스트 추출 → commit; 청크 생성 → commit; 키워드 추출 → commit; … 중간 실패 시 해당 단계 이전 커밋은 유지. |
| **완료 기준** | 단계 경계마다 세션 종료·신규 세션. 기존 6단계 동작 결과와 일치. |
| **테스트** | 기존 자동화 테스트·수동 run-full 후 DB 상태 검증. |

#### 16-1-4 [BE+FE] SSE Heartbeat·재연결

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.1 방안 D |
| **변경 파일** | Backend: `ai_workflow_service.py` 또는 progress 스트리밍 라우터. Frontend: `ai-automation.js` (EventSource 래핑). |
| **구현 요약** | Backend: progress 스트림에서 0.5s(또는 5s) 간격으로 `event: heartbeat` 발행. Frontend: `heartbeat` 수신 시 `lastEventTime` 갱신; 30초 미수신 시 연결 종료 후 `reconnectSSE(taskId)` (3초 후 재연결). 재연결 시 기존 task_id로 progress 재구독. |
| **완료 기준** | 장시간 실행 중 proxy/브라우저 타임아웃 시에도 재연결 후 진행률 재개. |
| **테스트** | 수동: progress 중 네트워크 차단 후 복구 시나리오. |

### 4.3 의존성

- 16-1은 Phase 15-2(AI 자동화 run-full·SSE) 완료 전제. 16-1-1과 16-1-2는 병렬 가능; 16-1-3·16-1-4는 16-1-1과 순서 조율(동일 서비스 파일).

---

## 5. 16-2 AI 자동화 Phase 2 (중기 — 성능)

### 5.1 목표

80파일 기준 총 소요 100분+ → 약 15분 수준으로 단축. 메모리 피크·DB 커넥션·중간 실패 보존 개선.

### 5.2 Task 상세

#### 16-2-1 [BE] Qdrant 배치 임베딩

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.2 방안 E |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py`, (선택) `backend/services/search/` 임베딩 유틸 |
| **구현 요약** | `sync_chunk_to_qdrant()` 단건 루프 대신, approved 청크를 50건 단위로 묶어 `embedding_model.encode(texts, batch_size=50)` 후 `qdrant_client.upsert(points=[])` 한 번에 전송. 배치마다 progress 갱신. |
| **완료 기준** | 960청크 시 Qdrant 호출 약 20회 이하. 기존 단건과 동일한 벡터/메타데이터. |
| **테스트** | 자동화 E2E 또는 20+ 문서 run-full 후 검색 품질·Qdrant 문서 수 비교. |

#### 16-2-2 [BE] LLM 키워드 추출 묶음 호출

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.2 방안 F-1 |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py` (키워드 추출 루프) |
| **구현 요약** | 청크당 1회 호출 대신, 5~10개 청크 텍스트를 `[문서 1]\n...\n---\n[문서 2]\n...` 형태로 묶어 1회 프롬프트. 응답 파싱 후 청크별 키워드 할당. 배치 크기는 설정/환경변수로 조정 가능하게. |
| **완료 기준** | 960청크 시 LLM 호출 약 96~192회. 기존 단건 추출과 동일한 스키마(키워드 리스트) 유지. |
| **테스트** | 소량 문서로 키워드 결과 비교; 80문서 수준에서 소요 시간 측정. |

#### 16-2-3 [BE] 자동 배치 분할 실행

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.3 방안 I |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py` |
| **구현 요약** | `document_ids`를 20개 단위 배치로 분할. 배치마다 6단계 전체 실행 후 결과 누적; 배치 간 `gc.collect()`. 진행률: 배치 1/4 → 0~25%, 2/4 → 25~50% 등. 단일 task_id로 상위 진행률 노출. |
| **완료 기준** | 80문서 선택 시 4배치로 순차 처리. 중간 배치 실패 시 이전 배치 결과는 DB에 유지. |
| **테스트** | 40·80문서 run-full, 메모리 프로파일·완료 결과 일치 검증. |

#### 16-2-4 [BE] 라벨 매칭 역인덱스

| 항목 | 내용 |
|------|------|
| **참조** | 리스크 분석 §3.2 방안 G |
| **변경 파일** | `backend/services/automation/ai_workflow_service.py` (라벨 매칭 단계) 또는 지식 서비스 |
| **구현 요약** | `label_index: token → [label_id]` 구축 후, 청크별로 `chunk.content.lower().split()` 토큰에 대해 `label_index` 조회해 후보 라벨만 확정 매칭. |
| **완료 기준** | 960청크 x 수백 라벨 환경에서 매칭 시간 단축. 결과 집합은 기존 브루트포스와 동일(또는 검증 가능). |
| **테스트** | 기존 라벨 매칭 테스트·소량 데이터로 결과 동일성 확인. |

### 5.3 의존성

- 16-2-1·16-2-2·16-2-4는 서로 독립; 16-2-3(배치 분할)은 16-2-1·16-2-2와 통합된 워크플로우 내에서 적용. 권장 순서: 16-2-4 → 16-2-1 → 16-2-2 → 16-2-3.

---

## 6. 16-3 AI 자동화 Phase 3 (장기)

### 6.1 Task 요약

| Task | 내용 | 우선순위 |
|------|------|:--------:|
| 16-3-1 | 파일별 완료 즉시 반영: `doc_result` 이벤트, FE 결과 패널·문서 완료 체크 | 높음 |
| 16-3-2 | Virtual Scroll: 문서 리스트 가시 영역만 렌더 (예: 22노드), 스크롤 시 갱신 | 중간 |
| 16-3-3 | (선택) Celery/Redis 큐·workflow_tasks 테이블·멀티 워커 | 낮음 |

16-3-1·16-3-2는 16-2 완료 후 적용. 16-3-3은 인프라 확장 시 별도 Phase로 분리 가능.

---

## 7. 16-4 Backend 500줄 초과 리팩토링

### 7.1 대상 파일 (500줄 초과 인덱스 기준)

| 순위 | 파일 | 줄 수 | 리팩토링 방향 |
|:----:|------|:-----:|---------------|
| 1 | `backend/routers/knowledge/knowledge.py` | 792 | 라우터 + knowledge_handlers.py 분리 |
| 2 | `backend/services/reasoning/recommendation_service.py` | 646 | 도메인별 recommendation_*.py 또는 내부 모듈 분리 |
| 3 | `backend/routers/reasoning/reason_stream.py` | 642 | 라우터 + reason_stream_handlers.py |
| 4 | `backend/routers/reasoning/reason.py` | 626 | 라우터 + reason_handlers.py |
| 5 | `backend/routers/knowledge/labels.py` | 613 | 라우터 + labels_handlers.py |
| 6 | `backend/main.py` | 558 | 라우터 레지스트리·미들웨어 모듈 위임 |
| 7 | `backend/routers/ai/ai.py` | 543 | 라우터 + ai_handlers.py |
| 8 | `backend/services/automation/ai_workflow_service.py` | 570 | 단계별 서브 모듈 (16-1·16-2 작업과 조율) |
| 9 | `backend/services/system/statistics_service.py` | 503 | 쿼리/집계/포맷 등 서브 모듈 분리 |

### 7.2 Task 상세

#### 16-4-1 [BE] 서비스 계층 리팩토링

| 항목 | 내용 |
|------|------|
| **대상** | recommendation_service, ai_workflow_service, statistics_service |
| **방법** | 260217-1400 §4.2: 서비스 → 도메인별 서브 모듈·내부 클래스 그룹. 공개 API(함수/클래스) 시그니처 유지. |
| **영향도** | 260217-1400 §3.2 테이블대로 직접 의존·역의존·테스트 채운 뒤 작업. |
| **완료 기준** | 파일당 500줄 이하 또는 명확한 책임 분리. 기존 테스트·호출부 동작 유지. |

#### 16-4-2 [BE] 라우터 계층 리팩토링

| 항목 | 내용 |
|------|------|
| **대상** | knowledge.py, labels.py, reason.py, reason_stream.py, ai.py |
| **방법** | 엔드포인트 함수를 `*_handlers.py`로 이동, 라우터는 `include_router`·경로·의존성 주입만 유지. |
| **영향도** | main.py·테스트 경로 확인 후 분할. API 경로·요청/응답 스키마 불변. |
| **완료 기준** | 라우터 파일 300줄 이하 권장, 핸들러 모듈로 로직 이전. E2E·API 테스트 통과. |

#### 16-4-3 [BE] main.py 축소

| 항목 | 내용 |
|------|------|
| **대상** | backend/main.py |
| **방법** | 라우터 등록을 `routers/__init__.py` 또는 `routers/registry.py`에서 일괄 등록; 미들웨어 체인은 config 또는 전용 모듈로. |
| **완료 기준** | main.py는 앱 생성·미들웨어·라우터 등록 호출만 남기고 500줄 이하. 기존 라우트 목록·동작 동일. |

### 7.3 실행 순서

1) 16-4-1 (서비스) → 2) 16-4-2 (라우터) → 3) 16-4-3 (main). 각 파일별로 영향도 작성 → 테스트 통과 확인 → 분할 계획 → 작업 → 260217-1400 문서 갱신.

---

## 8. 16-5 Web JS 500줄 초과 리팩토링

### 8.1 대상 파일

| 순위 | 파일 | 줄 수 | 리팩토링 방향 |
|:----:|------|:-----:|---------------|
| — | reason_backup.js | 1216 | 참조 제거 후 삭제 검토 (16-5-1) |
| 1 | admin/knowledge-files.js | 922 | 기능별: knowledge-files-api.js, knowledge-files-ui.js 등 |
| 2 | admin/label-manager.js | 913 | 동일 패턴 |
| 3 | dashboard/dashboard.js | 749 | dashboard-api.js, dashboard-ui.js 등 |
| 4 | knowledge/knowledge-detail.js | 691 | knowledge-detail-api.js, knowledge-detail-ui.js |
| 5 | admin/ai-automation.js | 668 | ai-automation-api.js, ai-automation-ui.js (16-1·16-2·16-3 FE와 조율) |
| 6 | reason/reason-render.js | 652 | 렌더/이벤트 분리 |
| 7 | knowledge/knowledge-relation-matching.js | 587 | API·UI 분리 |
| 8 | admin/chunk-approval-manager.js | 572 | API·UI 분리 |
| 9 | admin/statistics.js | 519 | API·UI 분리 |

### 8.2 Task 상세

#### 16-5-1 [FE] reason_backup.js 정리

| 항목 | 내용 |
|------|------|
| **작업** | 프로젝트 전역에서 `reason_backup.js` 참조 검색 후 제거. 참조 없으면 파일 삭제 또는 `docs/planning/260217-1400` 제외 목록 유지. |
| **완료 기준** | HTML/JS에서 reason_backup 로드 없음. |

#### 16-5-2 [FE] Admin 대형 JS 분할

| 항목 | 내용 |
|------|------|
| **대상** | knowledge-files.js, label-manager.js, ai-automation.js, chunk-approval-manager.js, statistics.js |
| **방법** | 260217-1400 §4.3: fetch·API 호출 → *-api.js; DOM·이벤트·테이블 렌더 → *-ui.js. 메인 JS는 import 후 조합만. |
| **완료 기준** | 각 파일 500줄 이하. 기존 페이지 동작·E2E 동일. |

#### 16-5-3 [FE] Knowledge·Dashboard·Reason 분할

| 항목 | 내용 |
|------|------|
| **대상** | knowledge-detail.js, dashboard.js, reason-render.js, knowledge-relation-matching.js |
| **방법** | 동일하게 API/UI 또는 렌더/이벤트 분리. |
| **완료 기준** | 파일당 500줄 이하. E2E·회귀 통과. |

#### 16-5-4 [FE] 공통 유틸 추출

| 항목 | 내용 |
|------|------|
| **방법** | Admin 공통: API 호출 래퍼·에러 메시지·테이블 렌더 패턴을 `admin-common.js` 또는 `utils/` 로 이동. |
| **완료 기준** | 중복 코드 감소, 기존 Admin 페이지 동작 유지. |

### 8.3 실행 순서

16-5-1 → 16-5-2 (Admin) → 16-5-4 (공통) → 16-5-3. 각 파일 작업 전 260217-1400 §3.3 영향도 채우고 E2E 확인.

---

## 9. 16-6 Web CSS 리팩토링 (선택·병렬)

### 9.1 대상

reason.css(1586), knowledge-detail.css(746), admin-knowledge-files.css(704), knowledge-admin.css(603), settings-common.css(534), admin-ai-automation.css(512).

### 9.2 방법

260217-1400 §4.4: 페이지/기능 단위 분할(reason-control.css, reason-render.css 등), 공통 변수(admin-variables.css), 중복 클래스 정리. HTML에서 다중 `<link>` 또는 메인 CSS에서 `@import`.

### 9.3 완료 기준

파일당 500줄 이하 또는 명확한 블록 분리. 시각·레이아웃 회귀 없음.

---

## 10. 16-7 검증·문서화

### 10.1 16-7-1 [QA] E2E·단위 테스트 회귀

| 항목 | 내용 |
|------|------|
| **범위** | AI 자동화(run-full·progress·취소), 지식(파일 목록·업로드), Admin(라벨·청크·통계), Reason, 메뉴·라우트. |
| **실행** | `pytest tests/`, `npx playwright test e2e/smoke.spec.js e2e/phase-*.spec.js` 및 Phase 16 추가 시나리오. |
| **완료 기준** | 기존 E2E·단위 전부 통과. 16-1~16-3·16-4·16-5 변경 영역에 대한 시나리오 추가 권장. |

### 10.2 16-7-2 [DOC] 500줄 인덱스·영향도·가이드 갱신

| 항목 | 내용 |
|------|------|
| **문서** | docs/planning/260217-1400-500lines-over-index-and-refactor-guide.md |
| **갱신** | 리팩토링 완료 파일의 줄 수·제거된 파일 반영. §3.2·§3.3 영향도 셀 업데이트. |
| **완료 기준** | 인덱스가 현재 코드베이스와 일치. |

### 10.3 16-7-3 [DOC] AI 자동화 고도화 운영 가이드

| 항목 | 내용 |
|------|------|
| **내용** | 배치 크기(문서 20·임베딩 50)·LLM 묶음 크기(5~10)·Rate Limit 대응·SSE Heartbeat·재연결·모니터링 포인트. 80+ 파일 시 예상 소요·메모리. |
| **위치** | docs/planning/ 또는 docs/operations/ (프로젝트 규칙에 따름). |
| **완료 기준** | 운영자가 자동화 고도화 옵션·한계를 문서만으로 파악 가능. |

---

## 11. 의존성 및 순서

| 선행 | 후속 | 비고 |
|------|------|------|
| Phase 15 완료 | 16-1 전체 | AI 자동화 run-full·SSE 존재 전제 |
| 16-1 | 16-2 | Phase 1 안정화 후 Phase 2 성능 |
| 16-2 | 16-3 | Phase 2 후 Phase 3 UX·인프라 |
| — | 16-4 | Backend 리팩토링은 16-1·16-2와 병렬 가능(동일 파일 시 순서 조율) |
| — | 16-5 | FE 리팩토링은 16-1~16-3 FE와 병렬 가능(ai-automation.js 등 조율) |
| 16-4·16-5·16-6 | 16-7 | 리팩토링 후 검증·문서 갱신 |

**권장 마일스톤**

- M1: 16-1 완료 (안정성·UX 즉시 개선)
- M2: 16-2 완료 (80파일 약 15분 목표 달성)
- M3: 16-4-1·16-4-2 완료 (서비스·라우터 리팩토링)
- M4: 16-5-1·16-5-2 완료 (백업 제거·Admin JS 분할)
- M5: 16-3-1·16-3-2·16-7 완료 (Streaming Results·Virtual Scroll·검증·문서)

---

## 12. 성공 기준 (체크리스트)

### 12.1 AI 자동화 고도화

- [ ] **16-1** 세부 진행률·사전 검증 UI·DB 트랜잭션 분할·SSE Heartbeat·재연결 동작.
- [ ] **16-2** Qdrant 배치 임베딩·LLM 묶음 호출·20문서 배치 분할·라벨 역인덱스 적용; 80파일 기준 소요·메모리 개선 검증.
- [ ] **16-3** (목표) 파일별 doc_result·Virtual Scroll·(선택) Celery 큐 적용.

### 12.2 리팩토링

- [ ] **16-4** Backend 9개 500줄 초과 파일이 500줄 이하 또는 명확히 분리됨. 테스트·E2E 통과.
- [ ] **16-5** Web JS 9개(백업 제외) 파일 분할·공통 유틸 추출. reason_backup 참조 제거.
- [ ] **16-6** (선택) Web CSS 6개 분할·공통 변수 반영.

### 12.3 검증·문서

- [ ] **16-7** E2E·단위 회귀 통과; 500줄 인덱스·영향도·리팩토링 가이드 갱신; AI 자동화 고도화 운영 가이드 작성.

---

## 13. 참고 문서

| 문서 | 용도 |
|------|------|
| [260217-1600-AI자동화기능-리스크분석.md](../planning/260217-1600-AI자동화기능-리스크분석.md) | 80+ 파일 리스크·Phase 1/2/3 방안·코드 예시 |
| [260217-1400-500lines-over-index-and-refactor-guide.md](../planning/260217-1400-500lines-over-index-and-refactor-guide.md) | 500줄 인덱스·영향도 템플릿·리팩토링 패턴·실행 절차 |
| [phase-15-master-plan.md](phase-15-master-plan.md) | 선행 Phase 15 범위·15-2 AI 자동화 |
| [docs/SSOT/claude/2-architecture-ssot.md](../SSOT/claude/2-architecture-ssot.md) | 코드 구조·검증 기준 |
| [docs/SSOT/claude/3-workflow-ssot.md](../SSOT/claude/3-workflow-ssot.md) | Phase 워크플로우·상태·검증 |

---

**문서 상태**: Phase 16 마스터 플랜. AI 자동화 고도화(16-1~16-3)와 500줄 초과 리팩토링(16-4~16-6)·검증·문서(16-7)를 기준 문서 두 편에 맞춰 상세 반영.  
**다음 단계**: 16-1 Task 세분화(plan·todo-list)·착수. 16-2는 16-1 완료 후; 16-4·16-5는 영향도 작성 후 파일 단위로 진행.
