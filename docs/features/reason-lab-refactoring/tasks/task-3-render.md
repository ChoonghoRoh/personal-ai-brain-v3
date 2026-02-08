# Task 3: reason-render.js 작성 (render 레이어)

**순서**: 3/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/public/js/reason/reason-render.js`  
**예상 라인**: ~480줄 (500줄 이하)

---

## 1. 목표

**결과·시각화·추천** 등 화면을 그리는 모든 렌더링 로직을 한 파일로 분리한다.  
control은 processReasoningResult에서 displayResults(result)만 호출한다.

---

## 2. 담당 내용

| 구분                        | 함수/역할                                                                                                                                                               |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **결과 요약·결론·컨텍스트** | renderSummary, renderConclusion, renderContextChunks, renderContextDocuments, renderContext, renderSteps                                                                |
| **탭**                      | switchContextTab(tab)                                                                                                                                                   |
| **메인 진입**               | displayResults(result) — summary → modeViz → conclusion → context → steps → recommendations 순서                                                                        |
| **모드별 시각화**           | renderModeViz, renderDesignExplainViz, renderRiskReviewViz, renderNextStepsViz, renderHistoryTraceViz                                                                   |
| **추천**                    | displayRecommendations, displayRelatedChunks, displaySuggestedLabels, displaySampleQuestions, displayExploreMore, hideRecommendationsSection, handleSampleQuestionClick |
| **(선택) 화면 비우기**      | clearModeViz, clearReasoningResults 중 “DOM만 비우는” 부분을 render에 두고 control에서 호출                                                                             |

---

## 3. 작업 체크리스트

- [ ] `web/public/js/reason/reason-render.js` 파일 생성
- [ ] 위 함수들을 기존 reason.js에서 이관
- [ ] displayResults, switchContextTab을 control·HTML에서 호출 가능하도록 전역 또는 ReasonRender 네임스페이스로 공개
- [ ] Mermaid 등 외부 라이브러리는 전역 사용 유지
- [ ] 파일 라인 수 500줄 이하 확인; 초과 시 reason-mode-viz.js 분리 검토

---

## 4. 의존성

- **reason-model**: MODE_VIZ_TITLES 등 상수 (필요 시)
- **utils**: escapeHtml

---

## 5. 완료 기준

- reason-render.js가 설계서 4.3절 내용을 만족한다.
- control에서 displayResults(result) 호출 시 기존과 동일하게 결과·시각화·추천이 표시된다.
