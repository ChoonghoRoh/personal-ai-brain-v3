# Task 1: reason-model.js 작성 (model 레이어)

**순서**: 1/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**산출물**: `web/public/js/reason/reason-model.js`  
**예상 라인**: ~80줄

---

## 1. 목표

Reasoning Lab에서 사용하는 **상수·전역 상태·데이터 형태**를 한 파일로 분리한다.  
다른 레이어(common, render, control)는 model에만 의존하도록 한다.

---

## 2. 담당 내용

| 항목                      | 내용                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------ |
| **MODE_DESCRIPTIONS**     | 모드 ID → 설명 문구 객체 (design_explain, risk_review, next_steps, history_trace)    |
| **MODE_VIZ_TITLES**       | 모드 ID → 시각화 섹션 제목 (선택, render에서 사용)                                   |
| **REASONING_STATE**       | taskId, elapsedTimerId, eventSource, startTime — 한 객체로 관리하거나 접근 경로 명시 |
| **(선택) 요청/응답 형태** | REASONING_REQUEST_SHAPE, REASONING_RESPONSE_SHAPE 주석으로 필드 문서화               |

---

## 3. 작업 체크리스트

- [ ] `web/public/js/reason/reason-model.js` 파일 생성
- [ ] MODE_DESCRIPTIONS 정의 (기존 modeDescriptions 이관)
- [ ] 전역 상태를 REASONING_STATE 객체 또는 getter/setter로 노출
- [ ] (선택) MODE_VIZ_TITLES, 요청/응답 필드 주석 추가
- [ ] `window.ReasonModel` 또는 네임스페이스로 공개 시 export 형태 문서화
- [ ] 기존 reason.js에서 해당 상수·변수 제거 후 model 참조로 교체하지 않음(다음 단계에서 제거)

---

## 4. 의존성

- **없음** (utils의 escapeHtml 등은 model에서 사용하지 않음)
- 다른 모듈이 model을 참조: common, render, control, reason.js

---

## 5. 완료 기준

- reason-model.js가 설계서 4.1절 내용을 만족한다.
- 다른 task에서 이 파일을 script로 로드해 상수·상태를 사용할 수 있다.
