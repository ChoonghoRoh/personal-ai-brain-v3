# AI 실행 가이드: 개발 워크플로우 Ver 2.0 (Executable System)

**용도**: Rules 인덱스를 기반으로 AI가 실제 실행 시 따라야 하는 순서를 정의합니다.

**중요**: 본 문서는 "작동하는 시스템 코드" 수준의 실행 가이드입니다. 각 Agent의 System Prompt, 템플릿, 조건 분기 로직이 모두 포함됩니다.

**버전**: 2.0 (Executable System)
**최종 수정**: 2026-02-07

---

## 🚀 Quick Start: Bootloader Sequence

**Phase 시작 시 실행 순서**:

```bash
# 1. Status 파일 생성 (최초 1회)
echo "---
phase: \"X-Y\"
current_step: \"1. 계획 단계\"
last_action: \"Phase initiated\"
last_action_result: \"N/A\"
next_action: \"Plan 문서 작성\"
blockers: []
last_updated: \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
---" > docs/phases/phase-X-Y/phase-X-Y-status.md

# 2. Orchestrator Agent 활성화
# Load System Prompt: docs/rules/prompts/agent-system-prompts.md#1-orchestrator-agent

# 3. Orchestrator가 Planner Agent 활성화
# Load System Prompt: docs/rules/prompts/agent-system-prompts.md#2-planner-agent
```

---

## 목차

0. [Bootloader Sequence](#-quick-start-bootloader-sequence)
1. [시스템 아키텍처](#1-시스템-아키텍처)
   - [1.1 Agent System Prompts](#11-agent-system-prompts)
   - [1.2 템플릿 시스템](#12-템플릿-시스템)
   - [1.3 Phase 단계별 Agent 활성화 매트릭스](#13-phase-단계별-agent-활성화-매트릭스)
   - [1.4 상태 관리 메커니즘 (State Tracking)](#14-상태-관리-메커니즘-state-tracking)
2. [계획 단계 실행](#2-계획-단계-실행)
3. [Task 생성 및 개발 단계](#3-task-생성-및-개발-단계)
4. [검증 단계 실행 (Schema 강제)](#4-검증-단계-실행-schema-강제)
5. [통합 테스트 단계 실행](#5-통합-테스트-단계-실행)
6. [E2E Spec 워크플로우 실행](#6-e2e-spec-워크플로우-실행)
7. [웹 테스트 실행](#7-웹-테스트-실행)
8. [Phase 완료 처리](#8-phase-완료-처리)
9. [실행 원칙 (Ver 2.0)](#9-실행-원칙-ver-20)
   - [9.1 기본 실행 순서](#91-기본-실행-순서)
   - [9.2 Self-Correction (자가 수정) 원칙](#92-self-correction-자가-수정-원칙)
   - [9.3 Context 최소화 원칙](#93-context-최소화-원칙)
   - [9.4 SSOT (Single Source of Truth) 원칙](#94-ssot-single-source-of-truth-원칙)
   - [9.5 템플릿 강제 원칙](#95-템플릿-강제-원칙)

---

## 1. 시스템 아키텍처

### 1.1 Agent System Prompts

**위치**: [prompts/agent-system-prompts.md](./prompts/agent-system-prompts.md)

각 Agent는 시작 시 해당 System Prompt를 로드합니다. 이것이 Agent의 "뇌(Brain)"입니다.

| Agent            | System Prompt 위치 | 역할                                          |
| ---------------- | ------------------ | --------------------------------------------- |
| **Orchestrator** | §1                 | Phase 흐름 관리, Agent 활성화, Pass/Fail 판단 |
| **Planner**      | §2                 | Plan·Todo 생성, Task 분해                     |
| **Builder**      | §3                 | 코드 구현, Task 문서 작성                     |
| **Tester**       | §4                 | 검증 리포트 작성, 테스트 실행                 |

**사용 방법**:

```
1. Agent 활성화 시점에 해당 섹션 읽기
2. Identity, Responsibilities, Input Context 순서대로 처리
3. Output Format에 따라 산출물 생성
4. Constraints 준수
```

### 1.2 템플릿 시스템

**위치**: [templates/](./templates/)

| 템플릿                                    | 사용 시점            | 강제 여부 |
| ----------------------------------------- | -------------------- | --------- |
| **verification-report-template.md**       | 검증 단계 (Tester)   | ✅ 필수   |
| **task-template.md**                      | Task 생성 (Builder)  | ⚠️ 권장   |
| **integration-test-scenario-template.md** | 통합 테스트 (Tester) | ⚠️ 권장   |

**템플릿 사용 규칙**:

- Tester Agent는 **반드시** verification-report-template.md를 사용
- 템플릿의 모든 섹션을 빈칸 없이 작성
- "최종 판정" 필드는 `[PASS | FAIL | PARTIAL]` 중 하나만 사용 (자유 텍스트 금지)

### 1.3 Phase 단계별 Agent 활성화 매트릭스

**원칙**: 각 Phase 단계에서 활성화되는 Agent를 명시하여, 불필요한 Context 로드를 방지합니다.

| Phase 단계        | 활성 Agent(s)         | System Prompt 로드 | 주요 작업                                |
| ----------------- | --------------------- | ------------------ | ---------------------------------------- |
| **계획**          | Planner, Orchestrator | §2, §1             | Plan·Todo 문서 생성, 완료 기준 정의      |
| **개발**          | Builder               | §3                 | 코드 구현, DB migration, API 개발        |
| **검증**          | Tester, Orchestrator  | §4, §1             | Verification report 작성, Pass/Fail 판단 |
| **통합 테스트**   | Tester                | §4                 | 시나리오 작성·실행, 결함 문서화          |
| **E2E/웹 테스트** | Tester                | §4                 | E2E spec 실행, 웹 테스트 체크리스트 확인 |
| **Phase 완료**    | Orchestrator          | §1                 | 최종 Summary 작성, 다음 Phase 준비       |

**활성화 명령 예시**:

```
[ACTIVATE] Planner Agent
[LOAD_PROMPT] prompts/agent-system-prompts.md#2-planner-agent
[CONTEXT] phase-X-master-plan.md, phase-X-navigation.md
[GOAL] Generate phase-X-Y-plan.md and phase-X-Y-todo-list.md
```

### 1.4 상태 관리 메커니즘 (State Tracking)

**문제**: AI는 기본적으로 무상태(Stateless)이므로, 현재 Phase가 어느 단계인지 매번 추론해야 합니다.

**해결**: 각 Phase 폴더에 `phase-X-Y-status.md` 파일을 생성하여 현재 상태를 명시적으로 기록합니다.

#### Status 파일 구조

```yaml
---
phase: "10-1"
current_step: "4. 검증 단계"
last_action: "Verification Report 작성 완료"
last_action_result: "Pass"
next_action: "통합 테스트 시나리오 작성"
blockers: []
last_updated: "2026-02-07T10:30:00Z"
---
```

#### Status 파일 업데이트 규칙

- **누가**: Orchestrator Agent만 쓰기 가능 (다른 Agent는 읽기 전용)
- **언제**: 각 단계 완료 시점 (Plan 작성 완료, 개발 완료, 검증 완료, 테스트 완료)
- **어떻게**: 단계 전환 시 자동으로 `phase-X-Y-status.md` 업데이트

#### Status 파일 사용 방법

1. **Phase 진입 시**: Orchestrator가 `phase-X-Y-status.md` 파일을 먼저 읽습니다.
2. **현재 단계 확인**: `current_step` 필드를 확인하여 어디서부터 재개할지 판단합니다.
3. **Blocker 확인**: `blockers` 배열이 비어있지 않으면 해당 이슈부터 해결합니다.
4. **다음 단계 진행**: `next_action`에 명시된 작업을 수행합니다.

---

## 0. Rules Index 로딩

AI는 실행 시작 시 다음 Rules 인덱스를 기준으로 규칙을 로드합니다.

**참조 인덱스**:

- [rules-index.md](./rules-index.md) — 통합 Rules 인덱스
- [common/common-rules-index.md](./common/common-rules-index.md) — 공통 규약 인덱스
- [ai/ai-rules-index.md](../ai/ai-rules-index.md) — AI 룰 인덱스
- [backend/backend-rules-index.md](./backend/backend-rules-index.md) — Backend 룰 인덱스

**메인 규약 허브**:

- [rules-index.md](./rules-index.md) — 통합 Rules 인덱스 (유일한 진실 공급원)
- [README/04-rules-and-conventions.md](../README/04-rules-and-conventions.md) — 전체 룰·규약 요약 허브

---

## 1. Phase 개발 워크플로우 진입

**참조**: [rules-index.md](./rules-index.md#71-phase-개발-워크플로우)

### 기본 흐름

```
Phase 계획 → 개발 → 검증 → 통합 테스트 → 웹 테스트 → E2E 테스트 → 배포
```

### Phase 개발 워크플로우 전체 단계

| 단계            | 산출물                                                         | 비고                                                                                                         |
| --------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **계획**        | `phase-X-Y-0-plan.md`, `phase-X-Y-0-todo-list.md`              | AI rule 참조: [ai-rule-phase-plan-todo-generation.md](./ai/references/ai-rule-phase-plan-todo-generation.md) |
| **개발**        | Task 문서(`task-X-Y-Z.md`), 코드 구현                          | AI rule 참조: [ai-rule-task-creation.md](./ai/references/ai-rule-task-creation.md)                           |
| **검증**        | `phase-X-Y-verification-report.md`                             | 개발 완료 후 파일 존재, 기능 동작 확인                                                                       |
| **통합 테스트** | `docs/devtest/scenarios/`, `docs/devtest/reports/`             | DB, API, UI 연동 검증                                                                                        |
| **웹 테스트**   | `docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md` | 사용자 시나리오 기반 테스트                                                                                  |
| **E2E 테스트**  | `e2e/phase-X-Y.spec.js`, Playwright 자동화 테스트              | E2E spec 우선 생성, 없으면 대체 방법 사용                                                                    |

---

## 1.1 Agent Persona 정의 및 Context 할당

**원칙**: AI는 "조직"이 아닌 "역할(Persona)"로 작동합니다. 각 Agent는 명확한 Goal, Context, Output을 갖습니다.

### [Orchestrator] Agent

- **Primary Goal**: Phase 전체 흐름 관리, 단계 간 전환 판단, 이슈 집계
- **Required Context**:
  - `phase-X-Y-status.md` (현재 단계)
  - 모든 하위 Agent의 Output (Plan, Verification Report, Test Report)
- **Output**: Phase 진행 상태 요약, 차단 이슈(Blocker) 리스트
- **Decision Authority**: Phase 다음 단계 진입 여부, Rollback 판단

### [Planner] Agent

- **Primary Goal**: Phase 목표 분석, Task 분해, 완료 기준 정의
- **Required Context**:
  - `docs/phases/phase-X-master-plan.md`
  - `docs/phases/phase-X-navigation.md`
  - 이전 Phase summary report
- **Output**: `phase-X-Y-plan.md`, `phase-X-Y-todo-list.md`
- **Decision Authority**: Task 분해 기준, 완료 기준(Definition of Done)

### [Builder] Agent

- **Primary Goal**: 코드 구현, API/UI 개발, DB 스키마 작성
- **Required Context**:
  - `phase-X-Y-todo-list.md`
  - Frontend: `web/src/`, 관련 rules 문서
  - Backend: `backend/`, `requirements.txt`, API rules
  - DB: `backend/models/`, schema migration files
- **Output**: Task 문서(`task-X-Y-Z.md`), 구현 코드(Python/JS), DB migration SQL
- **Decision Authority**: 기술 스택 선택, 코드 구조 설계

### [Tester] Agent

- **Primary Goal**: 검증, 테스트 시나리오 작성·실행, 결함 문서화
- **Required Context**:
  - `phase-X-Y-verification-report.md`
  - `docs/devtest/scenarios/`, `docs/webtest/`
  - `e2e/*.spec.js` (E2E test files)
- **Output**:
  - Verification report
  - Integration test scenarios/reports
  - E2E test spec (Playwright)
  - Web test execution report
- **Decision Authority**: Pass/Fail 판단, Regression 여부, Blocker 등급 분류

---

## 1.2 Phase 단계별 Agent 활성화 매트릭스

**원칙**: 각 Phase 단계에서 활성화되는 Agent를 명시하여, 불필요한 Context 로드를 방지합니다.

| Phase 단계        | 활성 Agent(s)         | 주요 작업                                |
| ----------------- | --------------------- | ---------------------------------------- |
| **계획**          | Planner, Orchestrator | Plan·Todo 문서 생성, 완료 기준 정의      |
| **개발**          | Builder               | 코드 구현, DB migration, API 개발        |
| **검증**          | Tester, Orchestrator  | Verification report 작성, Pass/Fail 판단 |
| **통합 테스트**   | Tester                | 시나리오 작성·실행, 결함 문서화          |
| **E2E/웹 테스트** | Tester                | E2E spec 실행, 웹 테스트 체크리스트 확인 |
| **Phase 완료**    | Orchestrator          | 최종 Summary 작성, 다음 Phase 준비       |

**활성화 규칙**:

- 각 단계에서 지정된 Agent만 실행됩니다.
- Orchestrator는 모든 단계에서 상태 추적을 위해 Background로 활성화됩니다.
- Builder Agent는 개발 단계 이외에는 비활성화되어 Context를 소비하지 않습니다.

---

## 1.3 상태 관리 메커니즘 (State Tracking)

**문제**: AI는 기본적으로 무상태(Stateless)이므로, 현재 Phase가 어느 단계인지 매번 추론해야 합니다.

**해결**: 각 Phase 폴더에 `phase-X-Y-status.md` 파일을 생성하여 현재 상태를 명시적으로 기록합니다.

### Status 파일 구조

```yaml
---
phase: "10-1"
current_step: "4. 검증 단계"
last_action: "Verification Report 작성 완료"
last_action_result: "Pass"
next_action: "통합 테스트 시나리오 작성"
blockers: []
last_updated: "2026-02-07T10:30:00Z"
---
```

### Status 파일 업데이트 규칙

- **누가**: Orchestrator Agent
- **언제**: 각 단계 완료 시점 (Plan 작성 완료, 개발 완료, 검증 완료, 테스트 완료)
- **어떻게**: 단계 전환 시 자동으로 `phase-X-Y-status.md` 업데이트

### Status 파일 사용 방법

1. **Phase 진입 시**: Orchestrator가 `phase-X-Y-status.md` 파일을 먼저 읽습니다.
2. **현재 단계 확인**: `current_step` 필드를 확인하여 어디서부터 재개할지 판단합니다.
3. **Blocker 확인**: `blockers` 배열이 비어있지 않으면 해당 이슈부터 해결합니다.
4. **다음 단계 진행**: `next_action`에 명시된 작업을 수행합니다.

---

## 2. 계획 단계 실행

**참조**:

- [rules-index.md](./rules-index.md#75-개발-절차-체크리스트) → 개발 절차 체크리스트 (1번 항목)
- [ai-rule-phase-plan-todo-generation.md](./ai/references/ai-rule-phase-plan-todo-generation.md) — Plan·Todo 생성 규칙
- [1.2 역할 기반 AI 기능 룰·할일 배정](#12-역할-기반-ai-기능-룰할일-배정) — 역할별 계획 단계 할일 배정

### 생성 산출물

- `phase-X-Y-plan.md` — Phase 계획 문서
- `phase-X-Y-todo-list.md` — Phase Todo 리스트

### 실행 순서

1. Phase 계획 문서 작성 (`plan.md`, `todo-list.md`)

---

## 3. Task 생성 및 개발 단계

**참조**:

- [rules-index.md](./rules-index.md#71-phase-개발-워크플로우) → Phase 개발 워크플로우 (개발 단계)
- [ai-rule-task-creation.md](./ai/references/ai-rule-task-creation.md) — Task 문서 생성 규칙

### 생성 산출물

- `task-X-Y-Z.md` — Task 문서
- 코드 구현

### 실행 순서

2. Task 문서 생성 및 개발 진행

---

## 4. 검증 단계 실행 (Schema 강제)

**참조**:

- [rules-index.md](./rules-index.md#74-테스트-리포트-작성-규칙) → 테스트 리포트 작성 규칙
- [ai-rule-task-inspection.md](./ai/references/ai-rule-task-inspection.md) — Task 완료 검사 기준
- **🆕 [templates/verification-report-template.md](./templates/verification-report-template.md)** — 검증 리포트 템플릿 (필수 사용)

### Agent 활성화

```
[ACTIVATE] Tester Agent
[LOAD_PROMPT] prompts/agent-system-prompts.md#4-tester-agent
[TEMPLATE] templates/verification-report-template.md (필수)
[CONTEXT] phase-X-Y/tasks/*.md (모든 Task 문서)
[GOAL] phase-X-Y-verification-report.md 생성 (템플릿 기반)
```

### 생성 산출물

- `phase-X-Y-verification-report.md` — Phase 검증 리포트 (**템플릿 필수 사용**)

### 템플릿 사용 규칙

**⚠️ 중요**: Tester Agent는 **반드시** verification-report-template.md를 사용해야 합니다.

**체크리스트**:

- [ ] 템플릿의 모든 섹션(1-11) 작성
- [ ] 섹션 10.1 "최종 판정" 필드: `[PASS | FAIL | PARTIAL]` 중 하나만 사용
- [ ] 자유 텍스트로 판정 기록 금지 (예: "대체로 통과", "몇 가지 문제 있음" → ❌)
- [ ] 섹션 5 "코드 오류"에 모든 에러 기록 (재현 조건, Stack Trace 포함)
- [ ] 섹션 6 "미해결 이슈"에 Blocker와 Non-Blocker 구분 명시
- [ ] 섹션 10.2 "다음 단계"에 Orchestrator 지시사항 명확히 기록

### Schema 강제 예시

**✅ 올바른 판정**:

```markdown
### 10.1 판정 결과

**최종 판정**: `FAIL`

**판정 근거**:

- [ ] Syntax Check: Pass
- [x] Logic Check: Fail (API 엔드포인트 500 에러)
- [ ] Edge Case Check: Not tested (Logic Check 실패로 skip)
- 코드 오류: Critical 2건, High 1건, Low 0건
- Blocker 이슈: 2건
```

**❌ 잘못된 판정** (자유 텍스트):

```markdown
### 10.1 판정 결과

**최종 판정**: 거의 완료되었으나 몇 가지 개선 필요

← Orchestrator가 파싱할 수 없음! PASS/FAIL/PARTIAL 중 하나만 사용
```

### 실행 순서

3. 개발 완료 후 verification report 작성 (템플릿 필수 사용)

### 조건부 분기 (Conditional Branching)

**Orchestrator의 파싱 로직**:

```python
# Orchestrator가 verification-report.md를 읽는 방법
def parse_verification_report(report_path):
    """
    Section 10.1 판정 결과에서 "최종 판정" 필드를 파싱
    """
    with open(report_path) as f:
        content = f.read()

    # 정규식으로 "최종 판정" 필드 추출
    import re
    match = re.search(r'\*\*최종 판정\*\*:\s*`([A-Z]+)`', content)

    if not match:
        raise ValueError("최종 판정 필드를 찾을 수 없음 - 템플릿 사용 필수")

    decision = match.group(1)  # "PASS", "FAIL", or "PARTIAL"

    if decision == "PASS":
        return "proceed_to_integration_test"
    elif decision == "FAIL":
        return "rollback_to_development"
    elif decision == "PARTIAL":
        return "evaluate_risk"
    else:
        raise ValueError(f"유효하지 않은 판정: {decision}")
```

**검증 결과에 따른 다음 단계 결정**:

```
READ: phase-X-Y-verification-report.md
PARSE: Section "10.1 판정 결과" → Extract "최종 판정" field

IF 최종 판정 = "PASS"
  THEN
    → [5. 통합 테스트 단계 실행](#5-통합-테스트-단계-실행)으로 진행
    → phase-X-Y-status.md 업데이트: current_step = "5. 통합 테스트"

ELSE IF 최종 판정 = "FAIL"
  THEN
    → [3. Task 생성 및 개발 단계](#3-task-생성-및-개발-단계)로 Rollback
    → phase-X-Y-status.md 업데이트:
        blockers = [Section 6에서 추출한 Blocker 이슈 리스트]
        current_step = "3. 개발 단계 (Fix)"
    → Fix 태그가 붙은 새로운 Task 생성: task-X-Y-Z-fix.md
    → DO NOT proceed to 통합 테스트 단계

ELSE IF 최종 판정 = "PARTIAL"
  THEN
    → Orchestrator가 Section 6 "미해결 이슈" 읽고 위험도 평가
    → IF all issues are Low/Medium:
        - Technical Debt 등록
        - 다음 단계 진행 (조건부)
      ELSE:
        - FAIL로 처리, Rollback

```

**Rollback 처리 규칙**:

- 실패한 검증 항목을 `blockers` 배열에 명시적으로 기록
- 수정이 필요한 파일/기능을 Task 문서에 명시
- 수정 완료 후 재검증 실행 (다시 4번 단계로 진입)

3. 개발 완료 후 verification report 작성

---

## 5. 통합 테스트 단계 실행

**참조**:

- [rules-index.md](./rules-index.md#73-통합-테스트-시나리오-작성-규칙) → 통합 테스트 시나리오 작성 규칙
- [integration-test-guide.md](../devtest/integration-test-guide.md) — 통합 테스트 가이드

### 생성 위치

- **시나리오**: `docs/devtest/scenarios/phase-X-Y-scenarios.md`
- **결과 리포트**: `docs/devtest/reports/phase-X-Y-execution-report.md`

### 통합 테스트 시나리오 작성 규칙

| 항목            | 규칙                                                   |
| --------------- | ------------------------------------------------------ |
| **단위**        | Task당 시나리오 작성 (예: Task 11-1-1, 11-1-2, 11-1-3) |
| **시나리오 수** | Task당 최대 20가지 (세부 기능별 1개 시나리오)          |
| **필수 항목**   | ID, 제목, 전제 조건, 실행 단계, 기대 결과, 실제 결과   |

### 테스트 리포트 작성 규칙

**Task당 실행 후** 다음 항목을 포함한 **실행 결과 리포트** 작성:

| 항목              | 설명                                                   |
| ----------------- | ------------------------------------------------------ |
| **코드 오류**     | 테스트 중 발생한 오류, 재현 조건, 로그/메시지, 스택    |
| **미해결 이슈**   | 테스트 시점 미해결 이슈, 설명, 우선순위, 영향 범위     |
| **해결된 이슈**   | 테스트 중 발견 후 해결한 이슈, 해결 방법, 커밋/PR 참조 |
| **시나리오 결과** | 시나리오 ID별 통과/실패 개수, 비고                     |

### 실행 순서

4. 통합 테스트 시나리오 작성 (`docs/devtest/scenarios/`)
5. 통합 테스트 실행 및 결과 리포트 작성 (`docs/devtest/reports/`)

### 조건부 분기 (Conditional Branching)

**통합 테스트 결과에 따른 다음 단계 결정**:

```

IF 통합 테스트 결과 = "All Pass" (모든 시나리오 통과)
THEN
→ [6. E2E Spec 워크플로우 실행](#6-e2e-spec-워크플로우-실행)으로 진행
ELSE IF 결과 = "Partial Pass" (일부 시나리오 실패)
THEN
→ Blocker 등급 확인: - Critical/High Blocker → [3. Task 생성 및 개발 단계](#3-task-생성-및-개발-단계)로 Rollback - Low/Medium → 이슈 기록 후 다음 단계 진행 (Technical Debt로 등록)

```

---

## 6. E2E Spec 워크플로우 실행

**참조**: [rules-index.md](./rules-index.md#72-e2e-spec-워크플로우) → E2E Spec 워크플로우

### E2E Spec 워크플로우

**규칙**: E2E spec 파일이 없을 경우 워크플로우

```

1. E2E spec 파일 확인 (e2e/phase-X-Y.spec.js)
   ↓
2. 없음 → E2E spec 생성 OR 대체 테스트 방법 사용
   - 대체 방법: curl API 호출, HTTP 상태 확인, psql 직접 쿼리
     ↓
3. 실행 결과 리포트에 E2E spec 상태 문서화
   - E2E spec 부재 사실
   - 사용한 대체 방법
   - 향후 E2E spec 생성 필요 여부
     ↓
4. E2E spec 생성 시: 기존 spec 파일 참조 (e2e/phase-9-3.spec.js, e2e/phase-10-1.spec.js)

```

### 생성 산출물

- `e2e/phase-X-Y.spec.js` — Playwright E2E 테스트 스펙

### 참고 문서

- [integration-test-guide.md](../devtest/integration-test-guide.md#4-e2e-spec-파일-워크플로우) — E2E Spec 파일 워크플로우 섹션

### 실행 순서

6. E2E spec 파일 확인 및 생성 (`e2e/phase-X-Y.spec.js`)
7. E2E 테스트 실행 또는 대체 테스트 방법 사용

---

## 7. 웹 테스트 실행

**참조**:

- [common/common-rules-index.md](./common/common-rules-index.md) — 공통 규약 인덱스
- [phase-unit-user-test-guide.md](../webtest/phase-unit-user-test-guide.md) — Phase 단위 웹 테스트 수행 가이드

### 생성 위치

- **결과 리포트**: `docs/webtest/phase-X-Y/phase-X-Y-webtest-execution-report.md`

### 웹 테스트 수행 방법

| 방안                    | 실행 방법                                                                    | 비고                         |
| ----------------------- | ---------------------------------------------------------------------------- | ---------------------------- |
| **방안 A: MCP(Cursor)** | Cursor 채팅에서 테스트 계획 + 웹 체크리스트 문서를 @로 붙이고 지시           | CLI 명령 없음                |
| **방안 B: 페르소나**    | 위와 동일 + personas.md + 관점별 prompt로 기획자/개발자/UI·UX 관점 기록 지시 | Cursor에서 지시              |
| **방안 C: E2E**         | **[webtest: X-Y start]** 명령으로 해당 phase E2E 자동 실행                   | E2E 스펙이 있는 phase만 가능 |

### 실행 순서

8. 웹 테스트 실행 및 결과 리포트 작성 (`docs/webtest/phase-X-Y/`)

---

## 9. 실행 원칙 (Ver 2.0)

AI는 다음 원칙을 반드시 준수합니다:

### 9.1 기본 실행 순서

1. **Status 파일 우선 확인** — 실행 시작 시 `phase-X-Y-status.md` 먼저 로드 (현재 단계 파악)
2. **System Prompt 로드** — [prompts/agent-system-prompts.md](./prompts/agent-system-prompts.md)에서 현재 Agent의 System Prompt 로드
3. **Agent 활성화** — [1.3 Phase 단계별 Agent 활성화 매트릭스](#13-phase-단계별-agent-활성화-매트릭스) 참조하여 현재 단계에 필요한 Agent만 활성화
4. **템플릿 적용** — 산출물 생성 시 해당 템플릿 사용 (verification-report-template.md 등)
5. **산출물 생성** — 각 단계의 생성 산출물 작성 (템플릿 기반)
6. **조건부 분기 판단** — Pass/Fail 결과에 따라 다음 단계 or Rollback 결정
7. **Status 파일 업데이트** — 단계 완료 시 `phase-X-Y-status.md` 업데이트

### 9.2 Self-Correction (자가 수정) 원칙

**문제 발생 시 자동 복구 메커니즘**:

```

IF 단계 실패 감지 (Verification Fail, Test Fail, Build Error)
THEN 1. blockers 배열에 구체적 실패 이유 기록 2. 실패한 단계의 직전 단계로 Rollback 3. Fix Task 생성 (task-X-Y-Z-fix.md) 4. Fix 완료 후 실패했던 단계부터 재실행
ELSE
계속 진행

```

**Retry 제한**: 동일한 단계에서 3회 연속 실패 시 Orchestrator가 수동 개입 요청

### 9.3 Context 최소화 원칙

**효율성을 위해 불필요한 Context 로드 방지**:

- 각 단계에서 **해당 단계에 필요한 Agent만** 활성화
- Rules 문서는 **필요한 시점에만** 로드 (전체 Rules Index를 미리 로드하지 않음)
- 이전 Phase의 산출물은 **Summary Report만** 참조 (전체 Task 문서 읽지 않음)
- **System Prompt는 Agent 활성화 시점에만** 로드 (사전 로드 금지)

### 9.4 SSOT (Single Source of Truth) 원칙

**문서 간 충돌 방지**:

- **절차(Procedure)**: ai-execution-workflow.md (본 문서)가 유일한 출처
- **판단 기준(Decision Criteria)**: 각 AI rule 문서가 출처
- **참고(Reference)**: Guide 문서는 상세 절차만 기술
- **Agent 뇌(Brain)**: prompts/agent-system-prompts.md가 유일한 출처
- **템플릿(Template)**: templates/ 폴더 내 템플릿이 유일한 출처

충돌 시 우선순위: `Status 파일 > ai-execution-workflow.md > System Prompts > Templates > AI rules > Guide 문서`

### 9.5 템플릿 강제 원칙

**Schema 기반 산출물 생성**:

- **Verification Report**: verification-report-template.md 필수 사용
  - "최종 판정" 필드는 `[PASS | FAIL | PARTIAL]`만 허용
  - 자유 텍스트 판정 금지
  - Orchestrator가 기계적으로 파싱 가능해야 함

- **Task Document**: task-template.md 권장
  - Done Definition 섹션 필수
  - Test Command 섹션 필수

- **Integration Test Scenario**: integration-test-scenario-template.md 권장
  - Precondition, Steps, Expected Result, Actual Result 필수

**템플릿 검증**:

```

IF Tester가 verification report 작성 시:
THEN 1. 템플릿 파일 읽기 2. 모든 섹션 빈칸 없이 작성 3. "최종 판정" 필드 정규식 검증: ^(PASS|FAIL|PARTIAL)$ 4. 검증 실패 시 에러 발생, 재작성 요청

```

**참조**: [rules-index.md](./rules-index.md#75-개발-절차-체크리스트) → 개발 절차 체크리스트 (마지막 단계)

### 생성 산출물

- `phase-X-Y-final-summary.md` — Phase 최종 요약 문서

### 실행 순서

9. 최종 요약 문서 작성 (`phase-X-Y-final-summary.md`)

---

## 9. 실행 원칙

AI는 다음 원칙을 반드시 준수합니다:

### 9.1 기본 실행 순서

1. **Status 파일 우선 확인** — 실행 시작 시 `phase-X-Y-status.md` 먼저 로드 (현재 단계 파악)
2. **Rules Index 참조** — [rules-index.md](./rules-index.md)에서 해당 단계의 Rules 문서 링크 확인
3. **Agent 활성화** — [1.2 Phase 단계별 Agent 활성화 매트릭스](#12-phase-단계별-agent-활성화-매트릭스) 참조하여 현재 단계에 필요한 Agent만 활성화
4. **산출물 생성** — 각 단계의 생성 산출물 작성
5. **조건부 분기 판단** — Pass/Fail 결과에 따라 다음 단계 or Rollback 결정
6. **Status 파일 업데이트** — 단계 완료 시 `phase-X-Y-status.md` 업데이트

### 9.2 Self-Correction (자가 수정) 원칙

**문제 발생 시 자동 복구 메커니즘**:

```

IF 단계 실패 감지 (Verification Fail, Test Fail, Build Error)
THEN 1. blockers 배열에 구체적 실패 이유 기록 2. 실패한 단계의 직전 단계로 Rollback 3. Fix Task 생성 (task-X-Y-Z-fix.md) 4. Fix 완료 후 실패했던 단계부터 재실행
ELSE
계속 진행

```

**Retry 제한**: 동일한 단계에서 3회 연속 실패 시 Orchestrator가 수동 개입 요청

### 9.3 Context 최소화 원칙

**효율성을 위해 불필요한 Context 로드 방지**:

- 각 단계에서 **해당 단계에 필요한 Agent만** 활성화
- Rules 문서는 **필요한 시점에만** 로드 (전체 Rules Index를 미리 로드하지 않음)
- 이전 Phase의 산출물은 **Summary Report만** 참조 (전체 Task 문서 읽지 않음)

### 9.4 SSOT (Single Source of Truth) 원칙

**문서 간 충돌 방지**:

- **절차(Procedure)**: ai-execution-workflow.md (본 문서)가 유일한 출처
- **판단 기준(Decision Criteria)**: 각 AI rule 문서가 출처
- **참고(Reference)**: Guide 문서는 상세 절차만 기술

충돌 시 우선순위: `Status 파일 > ai-execution-workflow.md > AI rules > Guide 문서`

---

## 참고 링크

**Rules 인덱스**:

- [rules-index.md](./rules-index.md) — 통합 Rules 인덱스
- [common/common-rules-index.md](./common/common-rules-index.md)
- [ai/ai-rules-index.md](../ai/ai-rules-index.md)
- [n8n/n8n-rules-index.md](./n8n/n8n-rules-index.md)
- [backend/backend-rules-index.md](./backend/backend-rules-index.md)

**Guide 문서**:

- [integration-test-guide.md](../devtest/integration-test-guide.md)
- [phase-unit-user-test-guide.md](../webtest/phase-unit-user-test-guide.md)

**문서 역할 구분**:

| 문서 유형         | 역할        | 위치                                            |
| ----------------- | ----------- | ----------------------------------------------- |
| **Status 파일**   | "현재 상태" | `docs/phases/phase-X-Y/phase-X-Y-status.md`     |
| **Workflow 문서** | "실행 순서" | `docs/rules/ai-execution-workflow.md` (본 문서) |
| **Rules 문서**    | "판단 기준" | `docs/rules/*/ai-rule-*.md`                     |
| **Guide 문서**    | "상세 절차" | `docs/devtest/`, `docs/webtest/`                |

**우선순위 (충돌 시)**: Status 파일 > Workflow 문서 > Rules 문서 > Guide 문서

**Rules 인덱스**:

- [rules-index.md](./rules-index.md) — 통합 Rules 인덱스
- [common/common-rules-index.md](./common/common-rules-index.md)
- [ai/ai-rules-index.md](../ai/ai-rules-index.md)
- [n8n/n8n-rules-index.md](./n8n/n8n-rules-index.md)
- [backend/backend-rules-index.md](./backend/backend-rules-index.md)

**Guide 문서**:

- [integration-test-guide.md](../devtest/integration-test-guide.md)
- [phase-unit-user-test-guide.md](../webtest/phase-unit-user-test-guide.md)

```

```
