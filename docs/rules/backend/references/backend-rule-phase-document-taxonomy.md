---
doc_type: taxonomy
taxonomy_domain: phase-document
version: 1.0
status: active
owner: human
last_updated: 2026-01-28
---

# Phase Document Taxonomy

이 문서는 Phase 기반 개발·운영 체계에서 사용되는
모든 문서의 **목적, 역할, 생성 주체, 자동화 가능 여부**를
명확히 정의하기 위한 공식 분류 문서이다.

본 taxonomy는 ai-rule 문서들의 판단 대상이 되는
“문서의 존재 구조”를 정의한다.

**저장 위치 (Option 1)**: 문서 종류별 Phase 폴더·tasks 하위 규칙은 `docs/ai/ai-rule-decision.md` §2, `docs/ai/ai-rule-phase-naming.md` §7 참고. Phase 전체 계획은 `docs/phases/phaseX-master-plan.md` 등 Phase 루트 허용.

---

## 1. Core Documents (헌법급 문서)

Phase의 시작과 종료를 정의하는 핵심 문서

### 1.1 phase-_-_\*-plan.md

- 목적: Phase 수행을 위한 공식 계획 수립
- 역할: Phase 시작 선언
- 생성 주체: Human 또는 AI
- 자동 생성: 가능 (phase-auto-create-prompt)
- 수정 가능 시점: Phase 시작 전
- 포함 내용:
  - Phase Goal
  - Scope
  - Task 개요
  - Validation / Exit Criteria

---

### 1.2 phase-_-_\*-summary.md

- 목적: Phase 결과 요약 및 종료 판단
- 역할: Phase 종료 선언
- 생성 주체: Human 또는 AI
- 자동 생성: 가능
- 수정: 제한적
- 포함 내용:
  - 결과 요약
  - 완료 항목
  - 이슈 / 한계
  - 다음 Phase 신호

---

## 2. Execution Documents (실행·운영 문서)

Phase 내부 실행을 관리하기 위한 문서

### 2.1 phase-_-_\*-todo-list.md

- 목적: 세부 작업 실행 관리
- 역할: 작업 진행 상태 추적
- 생성 주체: Human
- 자동 생성: 불가
- 특징:
  - 체크리스트 기반
  - Phase 계획을 세분화한 실행 문서
  - AI는 todo-list의 항목을 생성·수정하지 않으며,
    오직 판단 및 task 제안의 입력값으로만 사용한다.

---

### 2.2 phase-_-_\*-test-checklist.md

- 목적: 테스트 기준 정의
- 역할: 검증 항목 명세
- 생성 주체: Human
- 자동 생성: 불가

---

### 2.3 phase-_-_\*-user-test-results.md

- 목적: 사용자 테스트 결과 기록
- 역할: 정성·정량 테스트 로그
- 생성 주체: Human
- 자동 생성: 불가

---

### 2.4 Task 문서 (docs/phases/phase-X-Y/tasks/)

Task 문서는 **todo-list에서 유도된 항목**에 대해서만 생성·저장한다. 저장 위치: `docs/phases/phase-X-Y/tasks/`.

| 문서 종류        | 파일명 패턴 (권장)             | 파일명 패턴 (변형, phase-8-0 실적)  | 구분 기준           |
| ---------------- | ------------------------------ | ----------------------------------- | ------------------- |
| Task 실행 계획   | phaseX-Y-N-task.md             | (선택)                              | 실행 지시·Done 정의 |
| Task 테스트 결과 | phaseX-Y-N-task-test-result.md | phaseX-Y-N-<topic>-test-report.md   | 테스트 증빙         |
| Task 변경 이력   | (통합 가능)                    | phaseX-Y-N-<topic>-change-report.md | 변경 이력           |

- **생성**: Task는 todo-list 항목 순번(N)에 따라 생성. 변경·테스트 문서는 Task 실행·테스트 후 생성.
- **구분**: change-report = 변경 이력, test-report = 테스트 결과. topic = kebab-case 작업 주제.
- 상세: `docs/ai/ai-rule-decision.md` §2-2, `docs/ai/ai-rule-phase-naming.md` §7.

---

## 3. Evidence Documents (증거·근거 문서)

변경 사항, 성능, 결과를 증명하기 위한 문서

### 3.1 phase-_-_\*-test-report.md

- 목적: 기능/성능 검증 결과를 “증거 문서”로 남김
- 역할: 성능·기능 검증 근거
- 생성 주체: Human 또는 AI
- 자동 생성: 조건부 가능
- 특징:
  - 수치, 로그, 스크린샷, 비교표, 벤치마크 포함

---

### 3.2 phase-_-_\*-change-report.md

- 목적: 변경 내역 기록
- 역할: 변경 이력 추적
- 생성 주체: Human 또는 AI
- 자동 생성: 조건부 가능

---

## 4. Decision / External Documents (판단·외부 공유)

### 4.1 phase-_-_\*-decision.md

- 목적: 주요 판단 기록
- 역할: 방향 전환, 포기, 유지 결정 근거
- 생성 주체: Human
- 자동 생성: 불가

---

### 4.2 phase-_-_\*-report.md

- 목적: 외부 공유용 보고
- 역할: 이해관계자 전달
- 생성 주체: Human
- 자동 생성: 불가

---

## 5. Automation Scope Rules

- AI 자동 생성 대상:
  - plan.md
  - summary.md
  - (조건부) test-report.md, change-report.md
  - (조건부) tasks/ 내 task.md, task-test-result.md 또는 <topic>-change-report.md, <topic>-test-report.md

- AI 생성 금지 대상:
  - todo‑list
  - test‑checklist
  - user‑test‑results
  - decision
  - external report

- Task 문서 생성: todo-list 유도 후 Human 또는 워크플로우에 의해 생성. 저장·구분은 §2.4 및 ai-rule-decision §2-2 준수.

---

## 6. Relationship to ai-rule

- ai-rule 문서는 본 taxonomy를 전제로 판단한다.
- taxonomy는 판단 규칙을 포함하지 않는다.
- taxonomy는 “대상 정의”, ai-rule은 “행동 규칙”이다.

---

## 7. Change Policy

- taxonomy 변경은 Phase 단위 합의 후 수행한다.
- 변경 시 version을 반드시 증가시킨다.
