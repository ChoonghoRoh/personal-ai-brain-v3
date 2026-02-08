# 통합 Rules 인덱스

**용도**: `docs/` 하위에 분산된 **룰/규정 문서**를 한 곳에서 참조하기 위한 통합 인덱스.
**최종 수정**: 2026-02-07

---

## 목차

1. [공통 규약 (모든 도메인)](#1-공통-규약-모든-도메인)
2. [AI 룰 (판단·자동 생성)](#2-ai-룰-판단자동-생성)
3. [Backend 룰](#3-backend-룰)
4. [참고/연동 문서 (룰 관련)](#4-참고연동-문서-룰-관련)
5. [개발 절차 규약](#5-개발-절차-규약)
6. [업데이트 규칙](#6-업데이트-규칙)
7. [AI 실행 가이드](#7-ai-실행-가이드)

---

## 1. 공통 규약 (모든 도메인)

**인덱스**

- [common/common-rules-index.md](./common/common-rules-index.md)

**Phase 문서 분류 (Document Taxonomy)**

- **경로**: [common/common-phase-document-taxonomy.md](./common/references/common-phase-document-taxonomy.md)
- **용도**: Phase 문서의 목적, 역할, 생성 주체, 자동화 가능 여부 정의 (plan / todo-list / task / summary)
- **연동**: `ai-rule-decision.md`, `ai-rule-phase-naming.md`, phase 폴더·tasks 하위 규칙

---

## 3. AI 룰 (판단·자동 생성)

**인덱스**

- [ai/ai-rules-index.md](../ai/ai-rules-index.md)

**개별 규칙 문서**

| 문2                                                                                                 | 요약                                                |
| --------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| [ai/ai-rule-decision.md](./ai/references/ai-rule-decision.md)                                       | 문서 타입 인식, Phase/Task 시작·완료·보류 판단 규칙 |
| [ai/ai-rule-phase-naming.md](./ai/references/ai-rule-phase-naming.md)                               | Phase ID/이름/폴더/파일명 명명 규칙                 |
| [ai/ai-rule-phase-auto-generation.md](./ai/references/ai-rule-phase-auto-generation.md)             | Phase 자동 생성 규칙                                |
| [ai/ai-rule-task-inspection.md](./ai/references/ai-rule-task-inspection.md)                         | Task 완료 검사 기준, 산출물 규정, webtest 연결      |
| [ai/ai-rule-phase-navigation-generation.md](./ai/references/ai-rule-phase-navigation-generation.md) | phase-X-navigation 생성 규칙과 명령                 |
| [ai/ai-rule-phase-plan-todo-generation.md](./ai/references/ai-rule-phase-plan-todo-generation.md)   | plan·todo-list 생성 규칙과 명령                     |
| [ai/ai-rule-task-creation.md](./ai/references/ai-rule-task-creation.md)                             | Task 문서 생성 규칙과 명령                          |

---

## 3. Backend 룰

**인덱스**

- [backend/backend-rules-index.md](./backend/backend-rules-index.md)

---

## 5. 참고/연동 문서 (룰 관련)

| 문서                                                                                                                      | 설명                                          |
| ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| [common/common-phase-document-taxonomy.md](./common/references/common-phase-document-taxonomy.md)                         | Phase 문서 분류 기준 (plan/todo/task/summary) |
| [frontend/frontend-webtest-readme.md](./frontend/references/frontend-webtest-readme.md)                                   | webtest 절차·명령 인덱스                      |
| [frontend/frontend-rule-phase-unit-user-test-guide.md](./frontend/references/frontend-rule-phase-unit-user-test-guide.md) | Phase 단위 테스트 절차                        |

---

## 6. 개발 절차 규약

**용도**: Phase 개발부터 검증, 테스트, E2E까지의 전체 개발 워크플로우 규칙

**⚠️ 중요**: 본 섹션은 **목차(Map)** 역할만 수행합니다. 실제 실행 절차는 [ai-execution-workflow.md](./ai-execution-workflow.md) 참조.

**참조 문서**:

- [ai-execution-workflow.md](./ai-execution-workflow.md) — AI 실행 가이드 (단계별 상세 절차, 조건 분기, Agent 역할 정의)
- [integration-test-guide.md](./testing/integration-test-guide.md) — 통합 테스트 가이드
- [phase-unit-user-test-guide.md](./testing/phase-unit-user-test-guide.md) — 웹 테스트 수행 가이드

---

## 7. 업데이트 규칙

- 새로운 룰 문서가 추가되면 **본 인덱스**와 해당 영역 인덱스(예: `ai/ai-rules-index.md`, `backend/backend-rules-index.md`)를 함께 갱신.
- **본 인덱스(`rules-index.md`)가 유일한 진실 공급원(SSOT)**입니다.
- 룰 변경 시 관련 도메인별 인덱스(common, ai, backend)도 함께 갱신.

---

## 8. AI 실행 가이드

**문서**: [ai-execution-workflow.md](./ai-execution-workflow.md)

**용도**: Rules 인덱스를 기반으로 AI가 실제 실행 시 따라야 하는 단계별 워크플로우를 정의합니다.

**특징**:

- Rules 문서는 "판단 기준"으로 유지
- Execution 문서는 "실행 순서"로 구성
- 기존 Rules 인덱스를 실행 흐름으로 연결

**단계**: 0. Rules Index 로딩

1. Phase 개발 워크플로우 진입
2. 계획 단계 실행
3. Task 생성 및 개발 단계
4. 검증 단계 실행
5. 통합 테스트 단계 실행
6. E2E Spec 워크플로우 실행
7. 웹 테스트 실행
8. Phase 완료 처리
