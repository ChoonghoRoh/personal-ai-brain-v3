# Phase 10-2-0 Plan — 모드별 분석 고도화

**Phase ID**: 10-2  
**Phase 명**: 모드별 분석 고도화  
**Z**: 0 (초기 설계)  
**기준 문서**: [phase-10-master-plan.md](../phase-10-master-plan.md)  
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/ai-rule-phase-naming.md)

---

## 1. Phase Goal

Reasoning 4개 모드(design_explain, risk_review, next_steps, history_trace)의 **분석 결과를 시각화**하여 핵심 가치를 제공한다.

---

## 2. Scope

### 2.1 In Scope

| Task ID | 모드           | 시각화                           | 라이브러리           | 예상 |
| ------- | -------------- | -------------------------------- | -------------------- | ---- |
| 10-2-1  | design_explain | 아키텍처·의존성 다이어그램       | Mermaid.js           | 2일  |
| 10-2-2  | risk_review    | 5x5 리스크 매트릭스, 영향 그래프 | Chart.js             | 2일  |
| 10-2-3  | next_steps     | Phase별 로드맵, 간트·칸반        | Gantt.js 또는 Custom | 2일  |
| 10-2-4  | history_trace  | 수직 타임라인, Before/After      | Timeline.js          | 2일  |

### 2.2 Out of Scope

- PDF 내보내기·다크모드·접근성(Phase 10-3), 스트리밍·공유(Phase 10-4)는 본 Phase 제외.

---

## 3. Task 개요

| Task ID | Task 명                         | 예상 작업량 | 의존성                  |
| ------- | ------------------------------- | ----------- | ----------------------- |
| 10-2-1  | design_explain 시각화 (Mermaid) | 2일         | Phase 10-1 완료 후 권장 |
| 10-2-2  | risk_review 매트릭스            | 2일         | Phase 10-1 완료 후 권장 |
| 10-2-3  | next_steps 로드맵               | 2일         | Phase 10-1 완료 후 권장 |
| 10-2-4  | history_trace 타임라인          | 2일         | Phase 10-1 완료 후 권장 |

**진행**: 10-2-1 ~ 10-2-4 병렬 진행 가능.

---

## 4. Validation / Exit Criteria

- [x] design_explain 결과가 Mermaid 다이어그램으로 표시됨.
- [x] risk_review 결과가 5x5 매트릭스(또는 동등)로 표시됨. + 영향 그래프(Mermaid)
- [x] next_steps 결과가 로드맵/간트 형태로 표시됨.
- [x] history_trace 결과가 타임라인으로 표시됨. + Before/After 비교
- [x] Phase 9 회귀 테스트 유지.

---

## 5. 참고 문서

| 문서                                                   | 용도                           |
| ------------------------------------------------------ | ------------------------------ |
| [phase-10-master-plan.md](../phase-10-master-plan.md)  | Phase 10 전체 계획             |
| [phase-10-2-0-todo-list.md](phase-10-2-0-todo-list.md) | 본 Phase 할 일 목록            |
| `backend/routers/reasoning/reason.py`                  | Reasoning API (응답 구조 활용) |
