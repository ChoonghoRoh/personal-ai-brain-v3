# 작업 로그 - 2026-02-03

**날짜**: 2026-02-03  
**작업**: Reasoning Lab 개선 및 질문 기반 동작 고도화

---

## Reasoning Lab 개선 (reason.html / reason.js / reason.py)

**상태**: ✅ 완료  
**유형**: feature, fix, refactor

### 1. UI/UX

- **질문 우선 배치**: 질문/지시사항을 폼 최상단으로 이동, 보조 조회(프로젝트·라벨)는 하단 섹션으로 분리
- **프로젝트/라벨 조회·선택**: 쉼표 입력 대신 `GET /api/knowledge/projects`, `GET /api/labels`로 다중 선택(select multiple) + 직접 입력 병합
- **실행 중 표시**: 버튼 비활성화, "⏳ Reasoning 중" 문구, `aria-busy` 처리
- **경과 시간 표시**: 로딩 시 "고민 중... N초" 1초마다 갱신 (`#results-loading` / `#reasoning-elapsed-text`), 결과 영역 DOM 유지로 응답 후 정상 표시
- **결과 초기화**: 실행 시마다 `clearReasoningResults()`로 이전 결과 비우기, 동일 결과 반복 표시 방지
- **폼 제출 방지**: `onsubmit="runReasoning(event); return false;"` 추가
- **DOM null 방지**: `renderSummary`, 모드 설명, 버튼, `renderSteps` 등에 요소 존재 시에만 `textContent`/속성 설정
- **컨텍스트 표시**: 청크에 `project_id`, `labels` 보조 표기

### 2. 백엔드 동작 (질문 기반 고도화)

- **질문 우선 수집**: 질문이 있으면 `collect_chunks_by_question(..., use_cache=False)`로 의미 검색 우선, 프로젝트/라벨은 보조 병합
- **0건 시 전체 폴백 제거**: 질문에 대한 관련 지식이 0건이면 전체 청크로 대체하지 않음. `reasoning_steps`에 "질문과 관련된 지식이 수집되지 않았습니다" 기록 후, 빈 컨텍스트로 LLM 호출
- **질문 없을 때만 프로젝트/라벨 수집**: `if not chunks and not question:` 일 때만 `collect_knowledge_chunks` 호출
- **검색 캐시 미사용**: Reasoning용 `collect_chunks_by_question`에서 `use_cache=False`, `search_simple(..., use_cache=True)`에 `use_cache` 인자 추가
- **context_chunks 메타**: `build_context_chunks`에서 각 청크에 `project_id`, `labels`(확정 라벨 이름 목록) 포함

### 3. LLM 프롬프트 (dynamic_reasoning_service.py)

- **NO_CONTEXT_PROMPT**: 컨텍스트가 비어 있을 때 "해당 주제에 대한 지식이 수집되어 있지 않습니다" + 질문 인용 안내 생성
- **MODE_PROMPTS**: 모드별 "반드시 주어진 질문에 직접 답변하세요" 문구 추가
- **빈 컨텍스트 시에도 LLM 호출**: `context_text`가 비어 있으면 `None` 반환하지 않고 `NO_CONTEXT_PROMPT`로 질문별 안내 생성

### 4. 수정/추가된 주요 파일

- `backend/routers/reasoning/reason.py` — 질문 우선 수집, 0건 폴백 제거, `use_cache=False`, `project_id`/`labels` in context
- `backend/services/reasoning/dynamic_reasoning_service.py` — NO_CONTEXT_PROMPT, 모드별 질문 직접 답변 지시
- `backend/services/search/search_service.py` — `search_simple(..., use_cache=True)` 인자 추가
- `web/src/pages/reason.html` — 질문 우선 배치, 보조 조회 섹션, `#results-loading` / `#results-content` 분리, 폼 return false
- `web/public/js/reason/reason.js` — `loadReasoningOptions`, `clearReasoningResults`, 경과 시간 타이머, null 체크, 요청에 `Cache-Control`/`cache: no-store`
- `web/public/css/reason.css` — 보조 섹션, 로딩/경과 스타일

### 관련

- Reasoning 모드(design_explain, risk_review, next_steps, history_trace)는 LLM 프롬프트·템플릿 폴백·프론트 설명만 모드별로 다르고, 지식 수집/검색 로직은 동일
