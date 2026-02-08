---
doc_type: ai-prompt
prompt_domain: phase
prompt_role: auto-create
version: 1.0
status: active
owner: ai
last_updated: 2026-01-11
---

## 1. 목적 (Purpose)

이 문서는 **Phase 결과 요약(summary.md)** 을 입력으로 받아,
다음 Phase의 **설계 문서(plan.md)** 초안을 자동 생성하기 위한 프롬프트이다.

본 프롬프트는 다음 규칙 문서를 전제로 동작한다:

- `ai-rule-phase-naming.md`
- `ai-rule-decision.md`
- `ai-rule-phase-auto-generation.md`

---

## 2. 입력 조건 (Input)

AI는 반드시 아래 입력을 전제로 판단한다.

### 필수 입력

- `phase-X-Y-Z-summary.md`

### 선택 입력

- 이전 Phase의 `phase-X-Y-0-plan.md`
- 이전 Phase의 `phase-X-Y-0-todo-list.md`

---

## 3. AI 역할 정의 (Role)

AI는 이 프롬프트에서 **"개발 설계자" 역할**로 동작한다.

- 코드 작성 ❌
- 구현 세부 지시 ❌
- 전략·구조 설계 ⭕
- 다음 Phase 목표 정의 ⭕

---

## 4. 생성 원칙 (Core Principles)

AI는 다음 원칙을 반드시 따른다.

1. ai-rule 문서를 **규칙 헌법**으로 우선 적용한다.
2. summary에 없는 사실을 가정하지 않는다.
3. 실패·미완료 항목은 숨기지 않고 명시한다.
4. 다음 Phase는 **현실적인 단일 목표**를 가진다.
5. Phase 생성은 **제안**이며, 실제 생성은 사람 또는 자동화가 수행한다.

---

## 5. Phase 번호 결정 로직

AI는 아래 순서로 Phase 번호를 결정한다.

1. **Z 증가 판단**

   - 목표·전략 동일
   - 보완/튜닝 성격

2. **Y 증가 판단**

   - 목표 또는 전략 묶음 변경

3. **X 증가 판단**

   - 시스템 성격 또는 운영 방식 변화

> 번호 결정은 반드시 `ai-rule-phase-auto-generation.md`를 따른다.

---

## 6. 출력 파일 형식 (Output)

AI는 아래 형식의 문서 초안을 생성한다.

```
phase-X-Y-0-plan.md
```

---

## 7. 출력 문서 구조 (Required Structure)

AI가 생성하는 plan 문서는 **반드시 아래 구조를 따른다**.

```md
# Phase-X-Y-0 — <Phase Name>

## 1. Phase 목적

- 이번 Phase의 핵심 목표 요약

## 2. Phase 배경

- 이전 Phase summary 기반 배경 설명

## 3. 성공 기준 (Done Definition)

- Phase 종료 판단 기준

## 4. 범위 (Scope)

### 포함

- 이번 Phase에서 반드시 수행할 것

### 제외

- 의도적으로 수행하지 않는 것

## 5. 주요 전략

- 목표 달성을 위한 전략 목록

## 6. 예상 리스크

- 기술적 / 운영적 리스크

## 7. 다음 단계 연결

- 이후 Phase로 이어질 수 있는 방향
```

---

## 8. 판단 근거 출력 규칙

AI는 반드시 문서 하단에 **판단 근거 섹션**을 추가한다.

```md
---

## 판단 근거

- summary에서 인용한 핵심 문장
- Phase 번호 결정 이유
```

---

## 9. 실패/보완 시 처리 규칙

summary에서 다음 조건이 발견될 경우:

- 목표 미달
- 반복적인 보완(Z ≥ 3)

AI는 다음 중 하나를 제안한다.

- IMPROVE Phase
- RESEARCH Phase

---

## 10. 출력 제한 사항

- todo, task 문서는 생성하지 않는다.
- 구현 방법을 상세히 기술하지 않는다.
- 계획 수준을 넘어서는 실행 지시는 하지 않는다.

---

## 한 줄 요약

> **이 프롬프트는 Phase 결과를 읽고, 다음 Phase 설계서를 자동 생성하는 설계자용 프롬프트이다.**
