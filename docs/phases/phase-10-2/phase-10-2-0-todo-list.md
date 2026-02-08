# Phase 10-2: 모드별 분석 고도화 — Todo List

**상태**: ✅ 완료 (Completed)
**우선순위**: Phase 10 내 2순위
**예상 작업량**: 8일
**시작일**: 2026-02-04
**완료일**: 2026-02-05

**기준 문서**: [phase-10-master-plan.md](../phase-10-master-plan.md)  
**Plan**: [phase-10-2-0-plan.md](phase-10-2-0-plan.md)

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 10-2
- **Phase 명**: 모드별 분석 고도화
- **핵심 목표**: design_explain, risk_review, next_steps, history_trace 4개 모드 시각화

### 이전 Phase

- **Prev Phase ID**: 10-1
- **Prev Phase 명**: UX/UI 개선
- **전환 조건**: 10-1 전체 Task 완료

### 다음 Phase

- **Next Phase ID**: 10-3
- **Next Phase 명**: 결과물 형식 개선
- **전환 조건**: 10-2 전체 Task 완료

### Phase 10 내 우선순위

| 순위  | Phase ID | Phase 명               | 상태    |
| ----- | -------- | ---------------------- | ------- |
| 1     | 10-1     | UX/UI 개선             | ✅ 완료 |
| **2** | **10-2** | **모드별 분석 고도화** | ✅ 완료 |
| 3     | 10-3     | 결과물 형식 개선       | ⏳ 대기 |
| 4     | 10-4     | 고급 기능 (선택)       | ⏳ 대기 |

---

## Task 목록

### 10-2-1: design_explain 시각화 (Mermaid) ✅

**우선순위**: 10-2 내 1순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장

- [x] Mermaid.js 도입 및 Reasoning 결과 영역에 연동
- [x] 설계 분석 결과 → Mermaid 문법 변환 로직 (응답 내 \`\`\`mermaid ... \`\`\` 블록 파싱)
- [x] 아키텍처 다이어그램, 의존성 그래프 등 차트 타입 지원 (Mermaid 렌더링)
- [x] `reason.html`(또는 해당 뷰)에 design_explain 결과 시각화 영역 추가

---

### 10-2-2: risk_review 매트릭스 ✅

**우선순위**: 10-2 내 2순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장

- [x] Chart.js(또는 동등) 도입 — 5x5 HTML 테이블 매트릭스로 구현
- [x] risk_review 결과 → 심각도/가능성 매트릭스 데이터 변환 (reasoning_steps 기반)
- [x] 5x5 리스크 매트릭스 시각화
- [x] 영향 그래프(선택) 구현 — Mermaid.js 기반 관계 그래프 (`renderRiskImpactGraph`), relations 데이터 있을 때 표시
- [x] Reasoning 페이지에 risk_review 시각화 영역 추가

---

### 10-2-3: next_steps 로드맵 ✅

**우선순위**: 10-2 내 3순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장

- [x] Gantt.js 또는 Custom 컴포넌트로 Phase별 로드맵 구현 — Custom 로드맵(카드) 사용
- [x] next_steps 결과 → 일정/단계 데이터 변환 (reasoning_steps 기반)
- [x] 간트 차트 또는 칸반 보드 형태 표시 (Phase 번호 + 내용 카드)
- [x] Reasoning 페이지에 next_steps 시각화 영역 추가

---

### 10-2-4: history_trace 타임라인 ✅

**우선순위**: 10-2 내 4순위  
**예상 작업량**: 2일  
**의존성**: Phase 10-1 완료 후 권장

- [x] Timeline.js(또는 동등) 도입 — Custom 수직 타임라인 사용
- [x] history_trace 결과 → 타임라인 이벤트 데이터 변환 (reasoning_steps/answer 기반)
- [x] 수직 타임라인 표시
- [x] Before/After 비교(선택) 구현 — 이전/이후 패턴 파싱 + 폴백 분할 (`renderBeforeAfterComparison`)
- [x] Reasoning 페이지에 history_trace 시각화 영역 추가

---

## 완료 기준

- [x] 10-2-1 ~ 10-2-4 모두 완료
- [x] 4개 모드 각각 시각화 적용 (2026-02-05 SSE 스트리밍 + 시각화 동작 검증 완료)
- [x] Phase 9 회귀 테스트 유지 (2026-02-05 `POST /api/reason` 정상 동작 확인)

---

## 참고 문서

- [phase-10-master-plan.md](../phase-10-master-plan.md)
- [phase-10-2-0-plan.md](phase-10-2-0-plan.md)
- 부록 A. 필요 라이브러리: Mermaid.js, Chart.js, Gantt.js/Custom, Timeline.js
