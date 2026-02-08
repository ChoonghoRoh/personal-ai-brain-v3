# Phase 10-1-0 Plan — UX/UI 개선

**Phase ID**: 10-1  
**Phase 명**: UX/UI 개선  
**Z**: 0 (초기 설계)  
**기준 문서**: [phase-10-master-plan.md](../../../phases/phase-10-master-plan.md)  
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/references/ai-rule-phase-naming.md)

---

## 1. Phase Goal

Reasoning 페이지에서 **로딩·취소·예상 시간** 등 사용자 체감을 즉시 개선한다.

---

## 2. Scope

### 2.1 In Scope

| 항목                  | 내용                                                |
| --------------------- | --------------------------------------------------- |
| 진행 상태 실시간 표시 | 분석 진행 중 5단계 상태를 실시간 표시 (Task 10-1-1) |
| 분석 작업 취소 기능   | 진행 중인 분석을 사용자가 취소 (Task 10-1-2)        |
| 예상 소요 시간 표시   | 분석 시작 시 예상 소요 시간 안내 (Task 10-1-3)      |

### 2.2 Out of Scope

- 모드별 시각화(Phase 10-2), PDF/다크모드(Phase 10-3), 스트리밍(Phase 10-4)은 본 Phase 제외.

---

## 3. Task 개요

| Task ID | Task 명               | 예상 작업량 | 의존성      |
| ------- | --------------------- | ----------- | ----------- |
| 10-1-1  | 진행 상태 실시간 표시 | 1.5일       | 없음        |
| 10-1-2  | 분석 작업 취소 기능   | 1일         | 10-1-1 권장 |
| 10-1-3  | 예상 소요 시간 표시   | 0.5일       | 없음        |

**진행 순서**: 10-1-1 → 10-1-2, 10-1-3 (10-1-2·10-1-3은 10-1-1 이후 병렬 가능)

---

## 4. Validation / Exit Criteria

- [ ] 5단계 진행 상태가 Reasoning 실행 시 실시간 표시됨.
- [ ] 취소 버튼 클릭 시 진행 중인 분석이 중단됨.
- [ ] 분석 시작 시 예상 소요 시간이 UI에 표시됨.
- [ ] Phase 9 회귀 테스트 유지 (Reasoning API·E2E).

---

## 5. 참고 문서

| 문서                                                   | 용도                     |
| ------------------------------------------------------ | ------------------------ |
| [phase-10-master-plan.md](../../../phases/phase-10-master-plan.md)  | Phase 10 전체 계획       |
| [phase-10-1-0-todo-list.md](../../../phases/phase-10-1/phase-10-1-0-todo-list.md) | 본 Phase 할 일 목록      |
| `web/src/pages/reason.html`                            | Reasoning UI (수정 대상) |
