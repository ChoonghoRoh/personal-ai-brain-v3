# Task 4: reason-control.js 작성 (control 레이어)

**순서**: 4/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/public/js/reason/reason-control.js`  
**예상 라인**: ~380줄

---

## 1. 목표

**사용자 액션·SSE·UI 상태 전환·진행/취소/ETA**를 한 파일로 분리한다.  
runReasoning, cancelReasoning, UI 초기화/복원, 진행 단계·타이머·ETA를 담당한다.

---

## 2. 담당 내용

| 구분                | 함수/역할                                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------- |
| **요청 준비**       | prepareReasoningRequest() — mode, question, projects, labels, model 수집                                      |
| **실행·SSE**        | runReasoning(event), handleSSEEvent(eventType, data), processReasoningResult(result)                          |
| **취소**            | cancelReasoning(), showCancelledState()                                                                       |
| **UI 상태**         | initializeReasoningUI(), restoreReasoningUI(), clearReasoningResults(), clearModeViz(), resetProgressStages() |
| **진행·타이머·ETA** | updateProgressStage(stage, message, percent), startElapsedTimer(), stopElapsedTimer(), loadAndDisplayETA()    |
| **에러**            | showReasoningError(error)                                                                                     |

---

## 3. 작업 체크리스트

- [ ] `web/public/js/reason/reason-control.js` 파일 생성
- [ ] 위 함수들을 기존 reason.js에서 이관
- [ ] processReasoningResult 내부에서 render의 displayResults(result) 호출 — ReasonRender.displayResults 또는 전역 displayResults 참조
- [ ] 전역 상태( taskId, elapsedTimerId 등)는 reason-model(REASONING_STATE) 참조
- [ ] runReasoning, cancelReasoning을 HTML/진입점에서 호출 가능하도록 전역 또는 ReasonControl 네임스페이스로 공개

---

## 4. 의존성

- **reason-model**: REASONING_STATE, 상수
- **reason-common**: loadReasoningOptions, loadSeedChunk (필요 시)
- **reason-render**: displayResults, clearModeViz, clearReasoningResults(또는 render 쪽 clear 호출)

---

## 5. 완료 기준

- reason-control.js가 설계서 4.4절 내용을 만족한다.
- Reasoning 실행·취소·진행 표시·ETA·에러 표시가 기존과 동일하게 동작한다.
