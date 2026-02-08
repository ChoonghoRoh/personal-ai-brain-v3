# Task 7: 회귀 테스트 (Phase 10-1·10-2)

**순서**: 7/7  
**기준 문서**: [reason-lab-refactoring-design.md](../../reason-lab-refactoring-design.md)  
**목적**: 리팩터링 후 동작이 기존과 동일함을 검증한다.

---

## 1. 목표

Reasoning Lab 리팩터링 완료 후 **Phase 10-1(UX/UI)** 및 **Phase 10-2(모드별 시각화)** 기능이 그대로 동작하는지 E2E·MCP webtest로 확인한다.

---

## 2. 테스트 범위

| 구분           | 내용                                                                             | 참고                                                                            |
| -------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **Phase 10-1** | 진행 상태 5단계, 취소 버튼, 예상 소요 시간, 결과·추천 영역                       | e2e/phase-10-1.spec.js                                                          |
| **Phase 10-2** | 모드별 시각화 영역 DOM, design_explain/risk_review/next_steps/history_trace 패널 | e2e/phase-10-2.spec.js                                                          |
| **수동/MCP**   | Reasoning 실행 → 결과·시각화·추천 표시, 취소 동작                                | docs/webtest/phase-10-1-mcp-webtest-result.md, phase-10-2-mcp-webtest-result.md |

---

## 3. 작업 체크리스트

- [ ] E2E Phase 10-1: `npm run webtest:start -- 10-1` 실행 → 6 passed
- [ ] E2E Phase 10-2: `npm run webtest:start -- 10-2` 실행 → 6 passed
- [ ] (선택) MCP Cursor webtest: Reasoning 실행 → 진행 상태·취소·ETA·결과·모드별 시각화 확인
- [ ] (선택) design_explain 모드에서 Mermaid 다이어그램 또는 fallback 문구 표시 확인
- [ ] 실패 시 해당 task(1~6) 또는 설계서와 대조하여 원인 파악·수정 후 재테스트

---

## 4. 전제 조건

- Task 1~6 완료: 모든 JS 파일 분리 및 reason.html 스크립트 반영 완료.

---

## 5. 완료 기준

- Phase 10-1 E2E 6항목 통과.
- Phase 10-2 E2E 6항목 통과.
- (선택) MCP webtest에서 실행·취소·결과·시각화 동작 확인.
- 리팩터링으로 인한 기능 퇴행이 없음.
