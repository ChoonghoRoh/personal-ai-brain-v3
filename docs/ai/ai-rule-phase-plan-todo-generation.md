# Phase-X-Y Plan · Todo-List 생성 규칙

**용도**: `phase-X-master-plan.md`와 `phase-X-navigation.md`를 기반으로 **phase-X-Y별 plan·todo-list** 문서를 누락 없이 생성·갱신하기 위한 규칙과 명령을 정의한다. AI가 이 규칙을 보고 개발·생성할 수 있는 구조로 작성한다.  
**기준 문서**: [phase-document-taxonomy.md](../phase-document-taxonomy.md), [ai-rule-phase-naming.md](ai-rule-phase-naming.md)  
**참조 형식**: [phase-10-1-0-plan.md](../phases/phase-10-1/phase-10-1-0-plan.md), [phase-10-1-0-todo-list.md](../phases/phase-10-1/phase-10-1-0-todo-list.md), [phase-9-1-todo-list.md](../phases/phase-9-1/phase-9-1-todo-list.md)  
**버전**: 1.0  
**작성일**: 2026-02-04

---

## 1. 명령 등록

### 1.1 [phase-x-plan-todo:make] 명령

| 항목 | 내용 |
|------|------|
| **명령** | `[phase-x-plan-todo:make]` (X = Phase Major 번호, 예: 10, 11) |
| **트리거** | 사용자가 해당 명령을 요청하거나, phase-X-navigation 생성 후 phase-X-Y별 plan·todo-list가 필요할 때 |
| **필수 입력** | `docs/phases/phase-X-master-plan.md`, `docs/phases/phase-X-navigation.md` (둘 다 없으면 생성 불가 안내) |
| **출력** | 각 phase-X-Y에 대해 `phase-X-Y/phase-X-Y-0-plan.md`, `phase-X-Y/phase-X-Y-0-todo-list.md` 생성 또는 갱신 |

### 1.2 실행 절차

1. **phase-X-master-plan.md 확인**: 존재 여부·§3 단계 번호 체계·§4 상세 Task 목록·§6 성공 기준 확인.
2. **phase-X-navigation.md 확인**: 작업 순서(Phase X-1 ~ X-Y), Phase 상태 테이블, Phase별 Task 작업 순서, 전환 조건, 예상 작업량 확인.
3. **대상 Phase-X-Y 목록 추출**: Master Plan §3.3 Phase 구조 또는 Navigation "작업 순서" 표에서 Phase ID(X-1, X-2, …) 및 Phase 명·Task ID·Task 명·예상·의존성 추출.
4. **누락 검사**: Master Plan §4 Task 목록·Navigation "Phase별 Task 작업 순서"와 비교하여 Task ID·Task 명·예상이 누락되지 않았는지 확인.
5. **phase-X-Y 폴더 생성**: `docs/phases/phase-X-Y/` 없으면 생성.
6. **plan 생성**: §3 Plan 공통 규약에 따라 `phase-X-Y-0-plan.md` 작성.
7. **todo-list 생성**: §4 Todo-List 공통 규약에 따라 `phase-X-Y-0-todo-list.md` 작성(권장). 기존에 `phase-X-Y-todo-list.md`(Z 없음)를 쓰는 Phase는 호환 유지 가능.
8. **상호 참조**: plan에 todo-list 링크, todo-list에 plan·기준 문서 링크 반영.

---

## 2. 파일명·저장 위치

| 구분 | 파일명 (권장) | 파일명 (변형, phase-9 실적) | 저장 위치 |
|------|----------------|-----------------------------|-----------|
| **Plan** | `phase-X-Y-0-plan.md` | `phase-X-Y-Z-plan.md` (Z=0,1,2…) | `docs/phases/phase-X-Y/` |
| **Todo-List** | `phase-X-Y-0-todo-list.md` | `phase-X-Y-todo-list.md` (Z 없음) | `docs/phases/phase-X-Y/` |

- **Z**: 반복·보완 단계. 초기 설계는 Z=0. [ai-rule-phase-naming.md](ai-rule-phase-naming.md) §7 준수.
- Phase 9는 `phase-9-1-todo-list.md` 등 Z 없이 사용한 실적이 있으므로, 기존 Phase는 기존 파일명 유지 가능. **신규 생성 시에는 `phase-X-Y-0-todo-list.md` 권장.**

---

## 3. Plan 파일 공통 규약 (phase-X-Y-0-plan.md)

AI가 동일한 구조로 plan을 생성·검증할 수 있도록 **필수 섹션과 순서**를 고정한다.

### 3.1 문서 상단 (메타)

```markdown
# Phase X-Y-Z Plan — <Phase 명>

**Phase ID**: X-Y
**Phase 명**: <Phase 명>
**Z**: 0 (초기 설계)
**기준 문서**: [phase-X-master-plan.md](../phase-X-master-plan.md)
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/ai-rule-phase-naming.md)
```

- `<Phase 명>`: Master Plan §3.2 Phase 구조 또는 Navigation "작업 순서" 표의 Phase 명과 **동일**하게 기재.

### 3.2 §1. Phase Goal

- **1문장**: 해당 Phase의 목표를 한 문장으로 기술.
- **출처**: Master Plan §2 목표 및 범위, §4 해당 Phase 블록 요약 또는 Navigation "현재 진행 상황 → 다음: Phase X-Y" 목표.

### 3.3 §2. Scope

- **2.1 In Scope**: 해당 Phase에 포함되는 Task·항목을 표로 정리. Task ID, Task 명(또는 항목), 예상 작업량 포함. Master Plan §4 해당 Phase 표와 **일치**시킴.
- **2.2 Out of Scope**: 해당 Phase에서 제외되는 항목(다른 Phase 영역, 마스터 플랜 Out of Scope). Master Plan §2.2와 동일하거나 해당 Phase에 맞게 축약.

### 3.4 §3. Task 개요

- **표**: Task ID | Task 명 | 예상 작업량 | 의존성. Navigation "Phase별 Task 작업 순서" 및 Master Plan §4 해당 Phase와 **누락 없이** 일치.
- **진행 순서**: Master Plan §5 의존성 또는 Navigation 의존성 그래프에 맞게 "10-1-1 → 10-1-2, 10-1-3" 등으로 한 줄 안내.

### 3.5 §4. Validation / Exit Criteria

- **체크리스트**: `- [ ]` 또는 `- [x]`. Master Plan §6 성공 기준 해당 Phase 항목 + (해당 시) "Phase X-1 회귀 테스트 유지" 등. Navigation에 있는 완료 조건 반영.

### 3.6 §5. 참고 문서

- **필수 링크**: [phase-X-master-plan.md](../phase-X-master-plan.md), [phase-X-Y-0-todo-list.md](phase-X-Y-0-todo-list.md) (또는 해당 todo-list 파일명).
- **선택**: 해당 Phase에서 수정·참조하는 코드 경로(예: `web/src/pages/reason.html`).

### 3.7 Plan 누락 방지 체크리스트 (AI 검증용)

- [ ] Phase ID·Phase 명이 Master Plan·Navigation과 일치하는가?
- [ ] Task 개요의 Task ID·Task 명·예상·의존성이 Master Plan §4 및 Navigation "Phase별 Task 작업 순서"와 모두 반영되었는가?
- [ ] Validation / Exit Criteria가 Master Plan §6 성공 기준 해당 Phase와 대응하는가?
- [ ] Out of Scope가 Master Plan §2.2 또는 상위 Phase와 충돌하지 않는가?

---

## 4. Todo-List 파일 공통 규약 (phase-X-Y-0-todo-list.md)

### 4.1 문서 상단 (메타)

```markdown
# Phase X-Y: <Phase 명> — Todo List

**상태**: ⏳ 대기 (또는 🔄 진행중 / ✅ 완료)
**우선순위**: Phase X 내 N순위
**예상 작업량**: N일
**시작일**: -
**완료일**: -

**기준 문서**: [phase-X-master-plan.md](../phase-X-master-plan.md)
**Plan**: [phase-X-Y-0-plan.md](phase-X-Y-0-plan.md)
```

- **상태**: Navigation "Phase 상태 테이블"과 갱신 시 일치시키기. ⏳ 대기 / 🔄 진행중 / ✅ 완료.
- **우선순위·예상 작업량**: Navigation "작업 순서" 표 또는 Master Plan §3.1 우선순위 요약과 일치.

### 4.2 Phase 진행 정보

- **현재 Phase**: Phase ID, Phase 명, 핵심 목표 (Plan §1 Phase Goal와 동일).
- **이전 Phase**: Prev Phase ID, Phase 명, 전환 조건 (Navigation "작업 순서" 전환 조건).
- **다음 Phase**: Next Phase ID, Phase 명, 전환 조건.
- **Phase X 내 우선순위** (또는 Phase 우선순위 전체 현황): Navigation "Phase 상태 테이블" 또는 "전체 Phase 대기열"과 동일한 표. 순위 | Phase ID | Phase 명 | 상태.

### 4.3 Task 목록

- **각 Task마다**:
  - 제목: `### X-Y-N: <Task 명> [✅/⏳]`
  - **우선순위**: 해당 Phase 내 순위.
  - **예상 작업량**: Plan §3·Navigation과 동일.
  - **의존성**: 없음 / X-Y-N 완료 후 권장 / Phase X-Y 완료 후 권장 등.
  - **상태**: ✅ 완료 / ⏳ 대기 등.
  - **체크리스트**: `- [ ]` 또는 `- [x]` 세부 작업. Plan §4 Validation과 연결되도록 세분화 가능.

- **순서**: Navigation "Phase별 Task 작업 순서" 또는 Plan §3 Task 개요 표 순서와 **동일**.

### 4.4 Todo-List 누락 방지 체크리스트 (AI 검증용)

- [ ] Phase 진행 정보의 이전/다음 Phase·전환 조건이 Navigation "작업 순서"·"의존성 그래프"와 일치하는가?
- [ ] Task 목록의 Task ID·Task 명·예상·의존성이 Plan §3 및 Master Plan §4와 모두 반영되었는가?
- [ ] Task 순서가 Plan §3 진행 순서·Navigation "Phase별 Task 작업 순서"와 일치하는가?

---

## 5. Master Plan · Navigation 기반 누락 방지 규약

### 5.1 반드시 참조할 Master Plan 위치

| Master Plan 섹션 | Plan/Todo-List에 반영할 내용 |
|------------------|-----------------------------|
| §2 목표 및 범위 (In/Out Scope) | Plan §1 Goal, §2 Scope (In/Out) |
| §3.2 우선순위 요약, §3.3 Phase 구조 | Phase ID, Phase 명, 순위, 예상 |
| §4 상세 Task 목록·산출물 | Task ID, Task 명, 예상, 산출물 요약(선택) |
| §5 의존성 및 진행 순서 | Plan §3 진행 순서, Todo-List 의존성 |
| §6 성공 기준 (체크리스트) | Plan §4 Validation / Exit Criteria, Todo-List Task 체크리스트 |

### 5.2 반드시 참조할 Navigation 위치

| Navigation 섹션 | Plan/Todo-List에 반영할 내용 |
|-----------------|-----------------------------|
| 작업 순서 (Phase X-1 ~ X-Y) | Phase 목록, 전환 조건, 병행 가능, 예상 |
| Phase 상태 테이블 | Phase ID, Phase 명, Plan·Todo 링크(경로) |
| 의존성 그래프 | Plan §3 진행 순서, Todo-List 이전/다음 Phase |
| Phase별 Task 작업 순서 | Task ID, Task 명, 예상, 진행 안내 |
| 현재 진행 상황 / 다음 Phase | Todo-List 현재 Phase 핵심 목표 |

### 5.3 교차 검증

- **Master Plan §4**의 Task 표와 **Navigation "Phase별 Task 작업 순서"** 표를 **Task ID 단위로 비교**. 하나라도 빠지면 plan·todo-list에 추가.
- **Navigation "전체 Phase 대기열"**에 있는 Phase ID는 **모두** plan·todo-list 생성 대상. Phase 폴더가 없으면 생성 후 plan·todo-list 작성.

---

## 6. 참조 예시 (기존 Phase)

| 경로 | 용도 |
|------|------|
| [phase-10-1/phase-10-1-0-plan.md](../phases/phase-10-1/phase-10-1-0-plan.md) | Plan 형식·§1~§5 구조 |
| [phase-10-1/phase-10-1-0-todo-list.md](../phases/phase-10-1/phase-10-1-0-todo-list.md) | Todo-List 형식·Phase 진행 정보·Task 목록 |
| [phase-10-2/phase-10-2-0-plan.md](../phases/phase-10-2/phase-10-2-0-plan.md) | Task 개요 표·Validation |
| [phase-10-4/phase-10-4-0-plan.md](../phases/phase-10-4/phase-10-4-0-plan.md) | 선택 Phase·Out of Scope |
| [phase-9-1/phase-9-1-todo-list.md](../phases/phase-9-1/phase-9-1-todo-list.md) | Todo-List 변형(phase-X-Y-todo-list.md, Z 없음) |
| [phase-9-3/phase-9-3-todo-list.md](../phases/phase-9-3/phase-9-3-todo-list.md) | Phase 진행 정보·Task 체크리스트 세부 |

---

## 7. 룰집 연동

| 문서 | 용도 |
|------|------|
| [04-rules-and-conventions.md](../README/04-rules-and-conventions.md) | 룰·규약 인덱스 — 본 규칙·[phase-x-plan-todo:make] 링크 등록 |
| [ai-rule-phase-navigation-generation.md](ai-rule-phase-navigation-generation.md) | phase-X-navigation 생성 후 본 명령으로 plan·todo-list 생성 가능 |

---

## 8. 한 줄 요약

**phase-X-master-plan.md와 phase-X-navigation.md를 기반으로 [phase-x-plan-todo:make] 명령으로 각 phase-X-Y에 대해 phase-X-Y-0-plan.md·phase-X-Y-0-todo-list.md를 누락 없이 생성·갱신하며, Plan·Todo-List 공통 규약과 누락 방지 체크리스트를 따른다.**
