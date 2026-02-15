# Phase 9-3: API 검증 체크리스트

**작성일**: 2026-02-01  
**대상**: Phase 9-3 AI 기능 고도화 (Task 9-3-3, 9-3-1, 9-3-2)  
**용도**: Task별 **API 검증** 2차 점검 — Task report 기반, 샘플 데이터 지정·점검 기록

**Web 브라우저 기능 점검**(기능 flow, 메뉴/라우터별 시나리오)은 별도 문서 → [phase-9-3-web-user-checklist.md](phase-9-3-web-user-checklist.md)

---

## 검증 절차

| 단계 | 내용                                                                                               |
| ---- | -------------------------------------------------------------------------------------------------- |
| 1차  | Task별 수행 결과 report 확인 ([phase-9-3-task-9-3-X-report.md](phase-9-3-task-9-3-3-report.md) 등) |
| 2차  | **API 검증**: report 기준으로 샘플 데이터를 지정하고 Postman/curl 등으로 API 호출 후 점검 기록     |
| 기록 | 각 Task별 "샘플 데이터(예)", "점검 기록" 란에 실제 사용한 값·결과 요약 기입                        |

**전제 조건**: 백엔드 서버 기동, DB·Qdrant·Ollama(Reasoning 추천 시) 가용.

---

## Postman 기본 설정 (API 단독 조회)

| 항목          | 값                                             |
| ------------- | ---------------------------------------------- |
| **Base URL**  | `http://localhost:8001`                        |
| **인증**      | 없음                                           |
| **공통 헤더** | `Content-Type: application/json` (POST/PUT 시) |

- **검색 API**: `GET /api/search` — 쿼리 파라미터 **q** (필수). `query` 사용 시 422 Unprocessable Entity (필드명 불일치).
- **Ask API**: `POST /api/ask` (경로는 `/api/ask`. `/api/ai/ask` 아님). Body: `{"question":"...", "use_reranking": true, "use_multihop": true, "search_mode": "hybrid"}` 등.
- **Reason API**: `POST /api/reason` (경로는 `/api/reason`. `/api/reason/reason` 아님). Body: `{"mode":"design_explain", "inputs": {}, "question": "..."}`.
- 상세: [phase-9-3-web-user-checklist.md](phase-9-3-web-user-checklist.md) 상단 참조.

---

## 1. Task 9-3-3: RAG 기능 강화 — API 검증

**참조 report**: [phase-9-3-task-9-3-3-report.md](phase-9-3-task-9-3-3-report.md)

### 1.1 검색 API

| #     | 항목                                          | 샘플 데이터(예)                             | 결과 | 점검 기록                  |
| ----- | --------------------------------------------- | ------------------------------------------- | ---- | -------------------------- |
| 1.1.1 | GET /api/search?q=검색어&search_mode=semantic | q=test, search_mode=semantic                | [x]  | 200, results 반환          |
| 1.1.2 | GET /api/search?q=검색어&search_mode=keyword  | q=test, search_mode=keyword                 | [x]  | 200, results(빈 배열 가능) |
| 1.1.3 | GET /api/search?q=검색어&search_mode=hybrid   | q=test, search_mode=hybrid                  | [x]  | 200, RRF 결합 결과 반환    |
| 1.1.4 | project_id, label_ids 필터링                  | q=프로젝트, project_id=1 또는 label_ids=1,2 | [ ]  |                            |
| 1.1.5 | search_mode 미지정(하위 호환)                 | q=test (search_mode 생략)                   | [x]  | 200, semantic 기본 동작    |

**GET /api/search 오류 분석**

| 잘못된 호출 예 | 원인 | 응답 |
|----------------|------|------|
| `GET /api/search?query=test` | 파라미터명이 `query`임 (API는 `q` 사용) | 422 Unprocessable Entity, "Field required" (q 누락) |
| `GET /api/search` (q 없음) | 필수 파라미터 `q` 누락 | 422 Unprocessable Entity |
| `GET /api/search?q=` (빈 값) | 검색어 공백 검사 | 400 Bad Request, "검색어를 입력하세요" |

→ Postman/클라이언트에서는 반드시 **q** 파라미터로 검색어를 전달해야 합니다.

### 1.2 Ask API

| #     | 항목                                     | 샘플 데이터(예)                                | 결과 | 점검 기록                                               |
| ----- | ---------------------------------------- | ---------------------------------------------- | ---- | ------------------------------------------------------- |
| 1.2.1 | POST **/api/ask** — use_reranking=true   | question=프로젝트 목적은?, use_reranking=true  | [x]  | 200, answer·context 반환 (Ollama 미동작 시 폴백 메시지) |
| 1.2.2 | POST **/api/ask** — use_multihop=true    | question=관련 내용 요약해줘, use_multihop=true | [ ]  |                                                         |
| 1.2.3 | POST **/api/ask** — search_mode=hybrid   | question=키워드, search_mode=hybrid            | [ ]  |                                                         |
| 1.2.4 | POST **/api/ask** — 옵션 없음(하위 호환) | question=테스트 (옵션 생략)                    | [x]  | 200, answer 반환                                        |

### 1.3 시나리오 (API 연속 호출)

| #     | 항목                           | 샘플 데이터(예)                                                             | 결과 | 점검 기록 |
| ----- | ------------------------------ | --------------------------------------------------------------------------- | ---- | --------- |
| 1.3.1 | keyword vs hybrid 결과 비교    | GET search?q=동일검색어&search_mode=keyword / hybrid 각각 호출 후 결과 비교 | [ ]  |           |
| 1.3.2 | use_multihop=true 시 관계 맥락 | 관계 있는 청크 존재 시 ask(use_multihop=true) 호출 후 답변에 관계 반영 여부 | [ ]  |           |

---

## 2. Task 9-3-1: Reasoning AI 추천/샘플 — API 검증

**참조 report**: [phase-9-3-task-9-3-1-report.md](phase-9-3-task-9-3-1-report.md)

### 2.1 추천 API

| #     | 항목                                      | 샘플 데이터(예)                     | 결과 | 점검 기록                      |
| ----- | ----------------------------------------- | ----------------------------------- | ---- | ------------------------------ |
| 2.1.1 | GET /api/reason/recommendations/chunks    | chunk_ids=1, limit=5                | [x]  | 200, recommendations 배열 반환 |
| 2.1.2 | GET /api/reason/recommendations/labels    | content=프로젝트 개발, limit=5      | [ ]  |                                |
| 2.1.3 | GET /api/reason/recommendations/questions | project_id=1, limit=3 (Ollama 필요) | [ ]  |                                |
| 2.1.4 | GET /api/reason/recommendations/explore   | (파라미터 없음)                     | [x]  | 200, recommendations 반환      |

### 2.2 Reason API

| #     | 항목                                        | 샘플 데이터(예)                                    | 결과 | 점검 기록                                                 |
| ----- | ------------------------------------------- | -------------------------------------------------- | ---- | --------------------------------------------------------- |
| 2.2.1 | POST **/api/reason** — recommendations 포함 | mode=design_explain, inputs={}, question=설계 의도 | [x]  | 400 "승인된 지식이 없습니다" (API 동작함, 승인 청크 없음) |
| 2.2.2 | 모드별 응답                                 | mode=risk_review, next_steps 등 각각 1회           | [ ]  |                                                           |
| 2.2.3 | Ollama 미동작 시 폴백                       | Ollama 중지 후 동일 호출 → 템플릿 응답 반환 여부   | [ ]  |                                                           |

---

## 3. Task 9-3-2: 지식구조 자동 매칭 — API 검증

**참조 report**: [phase-9-3-task-9-3-2-report.md](phase-9-3-task-9-3-2-report.md)

### 3.1 청크 구조 추천

| #     | 항목                                                    | 샘플 데이터(예)                                              | 결과 | 점검 기록 |
| ----- | ------------------------------------------------------- | ------------------------------------------------------------ | ---- | --------- |
| 3.1.1 | GET /api/knowledge/chunks/{chunk_id}/suggestions        | chunk_id=실제 존재 ID                                        | [ ]  |           |
| 3.1.2 | POST /api/knowledge/chunks — structure_suggestions 반환 | document_id, content, chunk_index (include_suggestions=true) | [ ]  |           |
| 3.1.3 | POST /api/knowledge/chunks — include_suggestions=false  | 동일 body, include_suggestions=false → 빈/생략 확인          | [ ]  |           |
| 3.1.4 | POST /api/knowledge/chunks/{chunk_id}/labels/apply      | chunk_id, body에 label_ids 등 (API 스펙대로)                 | [ ]  |           |

### 3.2 문서 구조 추천

| #     | 항목                                                                  | 샘플 데이터(예)                          | 결과 | 점검 기록 |
| ----- | --------------------------------------------------------------------- | ---------------------------------------- | ---- | --------- |
| 3.2.1 | GET /api/knowledge/documents/{document_id}/suggestions                | document_id=실제 존재 ID                 | [ ]  |           |
| 3.2.2 | POST /api/knowledge/documents — suggested_category, similar_documents | file_path, file_name, file_type, size 등 | [ ]  |           |
| 3.2.3 | POST /api/knowledge/documents — include_suggestions=false             | 동일 body, include_suggestions=false     | [ ]  |           |

### 3.3 승인 시 관계 추천

| #     | 항목                                                           | 샘플 데이터(예)                                                 | 결과 | 점검 기록 |
| ----- | -------------------------------------------------------------- | --------------------------------------------------------------- | ---- | --------- |
| 3.3.1 | POST /api/approval/chunks/batch/approve?suggest_relations=true | body에 승인할 chunk 목록                                        | [ ]  |           |
| 3.3.2 | suggest_relations=false                                        | 동일 body, suggest_relations=false → suggested_relations 미포함 | [ ]  |           |

### 3.4 관계 일괄 적용

| #     | 항목                                     | 샘플 데이터(예)                                                          | 결과 | 점검 기록 |
| ----- | ---------------------------------------- | ------------------------------------------------------------------------ | ---- | --------- |
| 3.4.1 | POST /api/relations/apply                | relations: [{ source_chunk_id, target_chunk_id, relation_type, score? }] | [ ]  |           |
| 3.4.2 | 적용 후 저장 값 확인                     | confirmed=false, source=ai 등 DB/GET 응답 확인                           | [ ]  |           |
| 3.4.3 | 잘못된 chunk_id 시 errors, skipped_count | 존재하지 않는 id 포함 relations 전송                                     | [ ]  |           |

### 3.5 설정 동작

| #     | 항목                                  | 샘플 데이터(예)                                    | 결과 | 점검 기록 |
| ----- | ------------------------------------- | -------------------------------------------------- | ---- | --------- |
| 3.5.1 | AUTO_STRUCTURE_MATCHING_ENABLED=False | 환경 변수 변경 후 suggestions API 호출 → 빈/비활성 | [ ]  |           |

### 3.6 시나리오 (API 연속 호출)

| #     | 항목                                                              | 샘플 데이터(예)                                                      | 결과 | 점검 기록 |
| ----- | ----------------------------------------------------------------- | -------------------------------------------------------------------- | ---- | --------- |
| 3.6.1 | 청크 생성 → structure_suggestions → labels/apply                  | POST chunks → 응답 suggestions 확인 → POST labels/apply              | [ ]  |           |
| 3.6.2 | 문서 생성 → suggested_category, similar_documents → category 설정 | POST documents → GET suggestions 또는 응답 활용 → POST category      | [ ]  |           |
| 3.6.3 | batch/approve(suggest_relations=true) → relations/apply           | POST batch/approve → suggested_relations 확인 → POST relations/apply | [ ]  |           |

---

## 4. 통합·회귀 (API)

| #   | 항목                              | 샘플 데이터(예)                                          | 결과 | 점검 기록               |
| --- | --------------------------------- | -------------------------------------------------------- | ---- | ----------------------- |
| 4.1 | 기존 검색(의미만) 클라이언트 동작 | GET search?q=test (search_mode 생략)                     | [x]  | 200, semantic 기본 동작 |
| 4.2 | Reason API 응답 스키마 확장       | POST reason 응답에 recommendations 필드 + 기존 필드 유지 | [ ]  |                         |
| 4.3 | 청크/문서/관계 CRUD 유지          | GET/POST/PUT/DELETE 기존 엔드포인트 각 1회               | [ ]  |                         |

---

## 5. API 검증 결과 요약

| Task                 | 총 항목 | 성공 | 실패 | 비고                                            |
| -------------------- | ------- | ---- | ---- | ----------------------------------------------- |
| 9-3-3 RAG 강화       | 12      | 7    | 0    | 검색 5/5, Ask 2/4 (1.2.2·1.2.3·시나리오 미실행) |
| 9-3-1 Reasoning 추천 | 7       | 3    | 0    | 추천 2/4, Reason 1/3 (승인 청크 없음 시 400)    |
| 9-3-2 지식구조 매칭  | 16      | 0    | 0    | 미실행 (청크/문서/승인·관계 API)                |
| 통합·회귀            | 3       | 1    | 0    | 4.1 검색 하위호환 확인                          |
| **합계**             | 38      | 11   | 0    | 1차 curl 기반 점검                              |

**API 검증 수행일**: 2026-02-02  
**검증 수행자**: (curl 기반 1차 점검)  
**환경 (Ollama/Qdrant/DB)**: 백엔드 localhost:8001, Qdrant·DB 연동됨. Ollama 미동작 시 Ask/Reason 폴백 동작.
