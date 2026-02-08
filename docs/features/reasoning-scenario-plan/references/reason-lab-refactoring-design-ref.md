**Reference copy — original:** [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md) (do not edit original).

# Reasoning Lab (reason.js) 리팩터링 설계 문서

**대상**: `web/public/js/reason/reason.js`
**목표**: 기능·역할·공통·컨트롤·model 분리, 파일당 500줄 이하, 확장성·유지보수성 확보
**버전**: 1.0
**작성일**: 2026-02-04
**Task 목록**: [reason-lab-refactoring/tasks/README.md](reason-lab-refactoring/tasks/README.md) (단계별 task 문서)

---

## 1. 현황 분석

### 1.1 현재 구조

| 구분             | 내용                                                                                                                                                                    | 예상 라인 수 |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 전역 상태        | reasoningElapsedTimerId, currentTaskId, currentEventSource, reasoningStartTime                                                                                          | ~10          |
| 상수·설정        | modeDescriptions, urlParams, seedChunkId                                                                                                                                | ~15          |
| 초기화·이벤트    | DOMContentLoaded, 모드 설명 바인딩                                                                                                                                      | ~35          |
| 공통·데이터 로드 | showLoading, loadReasoningOptions, loadSeedChunk                                                                                                                        | ~70          |
| 진행·취소·ETA    | updateProgressStage, 타이머, cancelReasoning, showCancelledState, loadAndDisplayETA                                                                                     | ~130         |
| UI 관리          | clearReasoningResults, clearModeViz, resetProgressStages, initializeReasoningUI, restoreReasoningUI                                                                     | ~150         |
| 요청·SSE         | prepareReasoningRequest, runReasoning, handleSSEEvent, processReasoningResult, showReasoningError                                                                       | ~180         |
| 결과 렌더        | switchContextTab, renderSummary, renderConclusion, renderContext\*, renderSteps, displayResults                                                                         | ~120         |
| 모드별 시각화    | renderModeViz, renderDesignExplainViz, renderRiskReviewViz, renderNextStepsViz, renderHistoryTraceViz                                                                   | ~150         |
| 추천             | hideRecommendationsSection, displayRecommendations, displayRelatedChunks, displaySuggestedLabels, displaySampleQuestions, handleSampleQuestionClick, displayExploreMore | ~140         |
| **합계**         |                                                                                                                                                                         | **~1,210**   |

### 1.2 문제점

- 단일 파일 1,200줄 이상으로 가독성·검색·병렬 수정이 불리함.
- 역할이 섞여 있어(상태·UI·API·렌더·이벤트) 변경 시 영향 범위 파악이 어렵음.
- 모드별 시각화·추천 UI 추가 시 reason.js만 비대해짐.
- 전역 변수·함수에만 의존해 단위 테스트·교체가 어렵음.

---

## 2. 목표 아키텍처

### 2.1 레이어 구분

| 레이어           | 한글 명    | 역할                                          | 의존 방향                        |
| ---------------- | ---------- | --------------------------------------------- | -------------------------------- |
| **model**        | 모델       | 상수, 상태, 요청/응답 형태(데이터 구조)       | ← 없음 (최하위)                  |
| **common**       | 공통       | 데이터 로드, 페이지 공통 유틸, 옵션/시드      | ← model, utils                   |
| **render**       | 역할(렌더) | 결과·시각화·추천 등 화면 그리기               | ← model, common(필요 시)         |
| **control**      | 컨트롤     | 사용자 액션, SSE, UI 상태 전환, 진행/취소/ETA | ← model, common, render          |
| **기능(진입점)** | 기능       | 초기화, 이벤트 바인딩, 진입점                 | ← model, common, control, render |

- **기능**: "Reasoning Lab 페이지가 무엇을 하는가" — 초기화·바인딩만 담당.
- **역할(render)**: "결과를 어떻게 보여주는가" — 렌더링 전담.
- **공통(common)**: "페이지 공통 데이터·유틸" — 옵션 로드, 시드 청크 등.
- **컨트롤(control)**: "사용자 입력·API·진행 상태를 어떻게 다루는가" — 플로우·상태 제어.
- **model**: "어떤 값과 구조를 쓰는가" — 상수·상태·형태 정의.

### 2.2 의존성 원칙

- **model** → 외부만 사용 (utils 등 프로젝트 공통).
- **common** → model (및 utils).
- **render** → model (필요 시 common).
- **control** → model, common, render (render는 콜백/함수 주입으로 역참조 최소화).
- **진입점(reason.js)** → 위 모듈을 조합하고, 전역 노출이 필요한 것만 `window` 또는 한 곳에 모음.

---

## 3. 파일 분리 계획

### 3.1 디렉터리·파일 구성

```
web/public/js/reason/
├── reason.js              # 진입점·기능 (초기화, 바인딩) — 500줄 이하
├── reason-model.js        # model: 상수, 상태, 형태
├── reason-common.js       # common: 옵션/시드 로드, 공통 유틸
├── reason-control.js      # control: 실행·취소·SSE·UI 상태
├── reason-render.js       # 역할(render): 결과·시각화·추천 렌더
└── reason-mode-viz.js     # (선택) 모드별 시각화만 분리 시 — 500줄 초과 시 사용
```

### 3.2 파일별 역할·예상 라인 수

| 파일                  | 레이어  | 담당 내용                                                                                                                                                                                                                                                                                                                | 예상 라인 |
| --------------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| **reason-model.js**   | model   | MODE_DESCRIPTIONS, REASONING_STATE(또는 state 객체), 요청/응답 필드 주석·상수                                                                                                                                                                                                                                            | ~80       |
| **reason-common.js**  | common  | loadReasoningOptions, loadSeedChunk, showLoading(또는 reason 전용 로딩), URL 파라미터·시드 처리                                                                                                                                                                                                                          | ~120      |
| **reason-render.js**  | render  | renderSummary, renderConclusion, renderContext*, renderSteps, renderModeViz, render*Viz 4종, displayRecommendations, displayRelatedChunks, displaySuggestedLabels, displaySampleQuestions, displayExploreMore, hideRecommendationsSection, switchContextTab, displayResults                                              | ~480      |
| **reason-control.js** | control | prepareReasoningRequest, runReasoning, handleSSEEvent, processReasoningResult, cancelReasoning, showCancelledState, initializeReasoningUI, restoreReasoningUI, clearReasoningResults, clearModeViz, resetProgressStages, updateProgressStage, startElapsedTimer, stopElapsedTimer, loadAndDisplayETA, showReasoningError | ~380      |
| **reason.js**         | 기능    | DOMContentLoaded, 모드 설명 바인딩, cancel 버튼 바인딩, runReasoning 폼 연결, initLayout/header/ollama/options 호출, 스크립트 로드 순서 주석                                                                                                                                                                             | ~180      |

- 모드별 시각화가 커지면 `reason-mode-viz.js`로 분리(render에서 호출만 유지)하여 **reason-render.js**를 500줄 이하로 유지.

### 3.3 스크립트 로드 순서 (HTML)

```html
<script src="/static/js/components/utils.js"></script>
<!-- ... layout, header, ollama ... -->
<script src="/static/js/reason/reason-model.js"></script>
<script src="/static/js/reason/reason-common.js"></script>
<script src="/static/js/reason/reason-render.js"></script>
<script src="/static/js/reason/reason-control.js"></script>
<script src="/static/js/reason/reason.js"></script>
```

- model → common → render → control → 진입점 순서 유지.

---

## 4. 모듈 상세 설계

### 4.1 reason-model.js (model)

**역할**: Reasoning Lab에서 쓰는 상수·전역 상태·데이터 형태 정의.

**내용**:

- `MODE_DESCRIPTIONS`: 모드 ID → 설명 문구.
- `REASONING_STATE`:
  `{ taskId, elapsedTimerId, eventSource, startTime }` 또는 개별 전역 변수 유지 시 이들을 한 객체로 참조하는 접근 경로 명시.
- (선택) `REASONING_REQUEST_SHAPE`, `REASONING_RESPONSE_SHAPE` 주석으로 요청/응답 필드 문서화.

**공개(전역)**:

- `window.ReasonModel` 또는 네임스페이스 하나로 상수·상태 접근자만 노출하면, 테스트·교체 시 유리.

**의존성**: 없음 (또는 `escapeHtml` 등 utils만 사용).

---

### 4.2 reason-common.js (common)

**역할**: 프로젝트/라벨 옵션 로드, 시드 청크 로드, 페이지 공통 유틸.

**내용**:

- `loadReasoningOptions()`: /api/knowledge/projects, /api/labels 호출 후 select 채우기.
- `loadSeedChunk(chunkId)`: /api/knowledge/chunks/:id 호출 후 질문 필드 설정.
- URL 파라미터에서 seed_chunk 읽어서 loadSeedChunk 호출하는 초기화 로직.
- (선택) `showLoading(elementId, message, style)` — reason 전용일 경우만 common에 두고, 아니면 utils로.

**공개**:

- `loadReasoningOptions`, `loadSeedChunk` — control·진입점에서 호출.

**의존성**: reason-model(필요 시), utils(escapeHtml 등).

---

### 4.3 reason-render.js (역할·렌더)

**역할**: API 결과를 받아 DOM을 갱신하는 모든 렌더링.

**내용**:

- **결과 요약·결론·컨텍스트**: renderSummary, renderConclusion, renderContextChunks, renderContextDocuments, renderContext, renderSteps.
- **탭**: switchContextTab.
- **메인 진입**: displayResults(result) — summary → modeViz → conclusion → context → steps → recommendations 순서 호출.
- **모드별 시각화**: renderModeViz, renderDesignExplainViz, renderRiskReviewViz, renderNextStepsViz, renderHistoryTraceViz.
- **추천**: displayRecommendations, displayRelatedChunks, displaySuggestedLabels, displaySampleQuestions, displayExploreMore, hideRecommendationsSection, handleSampleQuestionClick.

**공개**:

- `displayResults(result)`, `switchContextTab(tab)` — control·HTML에서 호출.
- (선택) `clearModeViz`, `clearReasoningResults` 중 “화면만 비우는” 부분을 render로 모아도 됨(control은 “상태 초기화 + clear 호출”만 담당).

**의존성**: reason-model(상수·형태), utils(escapeHtml).

- Mermaid 등 외부 라이브러리는 전역 사용.

---

### 4.4 reason-control.js (컨트롤)

**역할**: 사용자 액션·SSE·UI 상태 전환·진행/취소/ETA.

**내용**:

- **요청 준비**: prepareReasoningRequest() — 폼 값 수집, mode/question/projects/labels/model 반환.
- **실행·SSE**: runReasoning(event), handleSSEEvent(eventType, data), processReasoningResult(result).
- **취소**: cancelReasoning(), showCancelledState().
- **UI 상태**: initializeReasoningUI(), restoreReasoningUI(), clearReasoningResults(), clearModeViz(), resetProgressStages().
- **진행·타이머·ETA**: updateProgressStage(stage, message, percent), startElapsedTimer(), stopElapsedTimer(), loadAndDisplayETA().
- **에러**: showReasoningError(error).

**공개**:

- `runReasoning(event)`, `cancelReasoning()` — HTML/진입점에서 바인딩.
- processReasoningResult 내부에서 render.displayResults(result) 호출하도록, render 모듈을 참조하거나 콜백으로 주입.

**의존성**: reason-model(상태·상수), reason-common(옵션·시드), reason-render(displayResults 등).

- 전역 상태는 model에서 읽고 씀.

---

### 4.5 reason.js (기능·진입점)

**역할**: 페이지 로드 시 한 번 실행되는 초기화와 이벤트 바인딩.

**내용**:

- DOMContentLoaded:
  - initLayout(), renderHeader(…), loadOllamaModelOptions("reason-model"), loadReasoningOptions().
  - 모드 설명: mode select change → mode-description 갱신.
  - 취소 버튼: click → cancelReasoning.
  - 폼 submit: runReasoning(event); return false.
- URL에서 seed_chunk 있으면 loadSeedChunk(seedChunkId) 호출(또는 common에서 처리).

**공개**:

- 전역 함수로 노출할 필요 있는 것만: runReasoning, cancelReasoning, switchContextTab(HTML onclick용).

**의존성**: model, common, control, render(초기화·바인딩만 사용).

---

## 5. 확장성·유지보수성 설계

### 5.1 새 모드 시각화 추가

- **model**: MODE_VIZ_TITLES 등에 새 모드 ID·제목 추가.
- **render**: renderModeViz 분기 한 곳에 case 추가, `reason-render.js` 내에 renderXxxViz 함수 추가 (또는 `reason-mode-viz.js`에 추가 후 render에서 호출).
- control·common·진입점은 수정 최소화.

### 5.2 새 API 필드·추천 타입 추가

- **model**: 주석 또는 상수로 응답 형태 갱신.
- **render**: displayRecommendations 내부 또는 displayXxx 함수만 추가/수정.
- 나머지 레이어는 터치하지 않음.

### 5.3 테스트·목업

- model: 상수·상태만 있으므로 단위 테스트·목 데이터 삽입이 쉬움.
- control: runReasoning를 목 fetch/목 reader로 교체해 SSE 시나리오 테스트 가능.
- render: displayResults(목 result)로 DOM 스냅샷/요소 존재 검증 가능.

### 5.4 공통 규칙

- **파일당 500줄 이하**: 초과 시 해당 레이어 내에서만 파일 추가(예: reason-mode-viz.js).
- **전역 변수 최소화**: 상태는 reason-model.js에만 두고, 나머지는 함수 인자·반환으로 전달.
- **DOM ID 상수화(선택)**: getElementById("submit-btn") 등을 model 또는 common에 ID 상수로 두면 테스트·리팩터 시 유리.

---

## 6. 마이그레이션 순서 제안

1. **reason-model.js** 작성: 상수·상태 이동, 기존 reason.js에서 해당 변수 제거 후 model 참조로 교체.
2. **reason-common.js** 작성: loadReasoningOptions, loadSeedChunk, 시드 파라미터 처리 이동.
3. **reason-render.js** 작성: 모든 render* / display* 이동, displayResults에서 control이 호출할 수 있도록 전역 또는 네임스페이스로 노출.
4. **reason-control.js** 작성: runReasoning, SSE, 취소, UI 상태, 진행/ETA 이동; processReasoningResult에서 render.displayResults 호출.
5. **reason.js** 축소: DOMContentLoaded·바인딩만 남기고, 스크립트 태그 순서 반영.
6. **HTML(reason.html)** 수정: script 태그 5개 추가 순서로 반영.
7. **회귀 테스트**: Phase 10-1·10-2 E2E 및 MCP webtest로 동작 검증.

---

## 7. 요약

| 구분    | 파일              | 라인 목표 | 역할                      |
| ------- | ----------------- | --------- | ------------------------- |
| model   | reason-model.js   | ~80       | 상수, 상태, 데이터 형태   |
| common  | reason-common.js  | ~120      | 옵션/시드 로드, 공통 유틸 |
| render  | reason-render.js  | ~480      | 결과·시각화·추천 렌더     |
| control | reason-control.js | ~380      | 실행·취소·SSE·UI 상태     |
| 기능    | reason.js         | ~180      | 초기화·이벤트 바인딩      |

- **의존 방향**: model ← common ← render ← control ← reason.js.
- **확장**: 새 모드/새 추천 타입은 해당 레이어(주로 model·render)만 수정.
- **유지보수**: 역할별로 파일이 나뉘어 변경 범위가 명확함.
