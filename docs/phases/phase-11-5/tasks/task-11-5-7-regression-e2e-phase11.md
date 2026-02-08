# Task 11-5-7: 회귀·E2E·Phase 11 연동 (§2.5)

**우선순위**: 11-5 내 7순위
**예상 작업량**: 1일
**의존성**: Phase 11-2·11-3 일부 완료(Reasoning 연동) 또는 11-4 통합 테스트 시
**상태**: ✅ 완료

**기반 문서**: [phase-11-5-0-todo-list.md](../phase-11-5-0-todo-list.md)
**Plan**: [phase-11-5-0-plan.md](../phase-11-5-0-plan.md)
**고도화 검토 상세**: [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) **§2.5**
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**phase-10-improvement-plan §2.5** 표에 따른 **회귀·E2E·Phase 11 연동**을 수행한다. Phase 10 E2E 범위 확장·Phase 11 연동 후 회귀·devtest 연계를 정의·문서화한다.

### 1.2 §2.5 표 항목 (phase-10-improvement-plan)

| 항목                      | 현황                             | 고도화 방향                                                                                 | 우선순위 |
| ------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------- | -------- |
| **Phase 10 E2E 범위**     | 10-1~10-4 E2E 통과               | 시나리오 추가(에러 경로·취소·공유 만료), 회귀 시나리오 문서화                               | 상       |
| **Phase 11 연동 후 회귀** | Phase 11 Admin 설정 도입 예정    | Admin 설정(템플릿·프리셋·RAG) 변경 시 Reasoning 동작 검증, 회귀 테스트 범위에 Phase 10 포함 | 상       |
| **devtest·통합 테스트**   | Phase 11-4에서 docs/devtest 도입 | Phase 10 Reasoning Lab 시나리오를 devtest 또는 webtest와 연계                               | 중       |

---

## 2. 작업 범위 (파일 변경 계획)

### 2.1 신규 생성·보완

| 파일 경로                                      | 용도                                                       |
| ---------------------------------------------- | ---------------------------------------------------------- |
| `docs/phases/phase-11-5/` 또는 `docs/devtest/` | Phase 10 E2E·Phase 11 연동 후 회귀 시나리오·검증 범위 문서 |
| `docs/devtest/` (기존)                         | Phase 10 Reasoning Lab 시나리오·회귀 시나리오 추가         |

### 2.2 수정

| 파일 경로                                   | 용도                                                    |
| ------------------------------------------- | ------------------------------------------------------- |
| `docs/devtest/integration-test-guide.md` 등 | Phase 10 회귀 범위·Phase 11 연동 시나리오 참조(필요 시) |

---

## 3. 작업 체크리스트 (Done Definition)

- [x] **Phase 10 E2E 범위**: 시나리오 추가(에러 경로·취소·공유 만료), 회귀 시나리오 문서화 → [regression-e2e-phase11-scenarios.md](../regression-e2e-phase11-scenarios.md) §1
- [x] **Phase 11 연동 후 회귀**: Admin 설정(템플릿·프리셋·RAG) 변경 시 Reasoning 동작 검증, 회귀 테스트 범위에 Phase 10 포함 → 동일 문서 §2
- [x] **devtest·통합 테스트**: Phase 10 Reasoning Lab 시나리오를 devtest 또는 webtest와 연계 → [integration-test-guide.md](../../../devtest/integration-test-guide.md) §7, [phase-10-regression-scenarios.md](../../../devtest/scenarios/phase-10-regression-scenarios.md)
- [x] 산출물: `phase-11-5/regression-e2e-phase11-scenarios.md`, `docs/devtest/scenarios/phase-10-regression-scenarios.md`, integration-test-guide §7 보완

---

## 4. 참조·비고

- 수행 시점: Phase 11-2·11-3에서 Reasoning 연동 일부 완료 후, 또는 Phase 11-4 통합 테스트 시 수행 권장.
- [phase-11-4-0-plan.md](../../phase-11-4/phase-11-4-0-plan.md) — devtest 연계
- [phase-10-improvement-plan.md](../phase-10-improvement-plan.md) §2.5
