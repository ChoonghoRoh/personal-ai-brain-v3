# Phase Navigation 문서 생성 규칙

**용도**: `phase-X-master-plan.md`가 존재할 때 `phase-X-navigation.md`를 생성·갱신하기 위한 규칙과 명령을 정의한다.
**기준 문서**: [common/common-phase-document-taxonomy.md](../../common/references/common-phase-document-taxonomy.md), [ai-rule-phase-naming.md](ai-rule-phase-naming.md)
**참조 형식**: [common/common-phase-10-navigation.md](../../common/references/common-phase-10-navigation.md), [common/common-phase-9-navigation.md](../../common/references/common-phase-9-navigation.md), [common/common-phase-11-navigation.md](../../common/references/common-phase-11-navigation.md)
**버전**: 1.0
**작성일**: 2026-02-04

---

## 1. 명령 등록

### 1.1 [phase-x-navi:make] 명령

| 항목       | 내용                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------- |
| **명령**   | `[phase-x-navi:make]` 또는 `[phase-X-navi:make]` (X = Phase Major 번호, 예: 11)               |
| **트리거** | 사용자가 해당 명령을 요청하거나, `phase-X-master-plan.md` 생성 후 Navigation 문서가 필요할 때 |
| **입력**   | `docs/phases/phase-X-master-plan.md` (필수). 해당 파일이 없으면 생성 불가 안내                |
| **출력**   | `docs/phases/phase-X-navigation.md` 생성 또는 갱신                                            |

### 1.2 실행 절차

1. **phase-X-master-plan.md 확인**: `docs/phases/phase-X-master-plan.md` 존재 여부 확인.
2. **내용 추출**: Master Plan에서 Phase ID(X-Y), Phase 명, Task ID(X-Y-N), Task 명, 예상 작업량, 의존성, 전환 조건 추출.
3. **형식 적용**: §2 구조·§3 작성 규약에 따라 `phase-X-navigation.md` 본문 생성.
4. **저장**: `docs/phases/phase-X-navigation.md`에 저장. 기존 파일이 있으면 섹션별로 보완·병합 가능.

---

## 2. phase-X-navigation.md 문서 구조

아래 섹션은 **필수**이며, [common/common-phase-10-navigation.md](../../common/references/common-phase-10-navigation.md), [common/common-phase-11-navigation.md](../../common/references/common-phase-11-navigation.md)와 동일한 순서·제목을 유지한다.

| 순서 | 섹션 제목                          | 내용                                                                 |
| ---- | ---------------------------------- | -------------------------------------------------------------------- |
| 1    | (상단)                             | 제목, 최종 수정, 기준 문서, 현재 Phase, 다음 작업                    |
| 2    | 작업 순서 (Phase X-1 ~ X-Y)        | 순서·Phase ID·Phase 명·전환 조건·병행 가능·예상 표                   |
| 3    | 전체 진행 현황                     | Progress 바, Phase별 진행률(⏳/🔄/✅)                                |
| 4    | Phase 상태 테이블                  | 순위·Phase ID·Phase 명·상태·진행률·시작일·완료일·Plan·Todo List 링크 |
| 5    | 의존성 그래프                      | Phase 순서·Phase 내부 Task 순서 ASCII 다이어그램                     |
| 6    | Phase별 Task 작업 순서             | X-1 ~ X-Y별 Task 표(순서·Task ID·Task 명·예상)·진행 안내             |
| 7    | 현재 진행 상황                     | 다음 Phase 목표·Task 목록                                            |
| 8    | 전체 Phase 대기열 (작업 순서 요약) | 표                                                                   |
| 9    | 빠른 링크                          | 문서·Phase Plan·Todo List·Tasks·코드 등                              |
| 10   | 완료 이력                          | Phase ID·완료일·주요 산출물·비고                                     |
| 11   | 예상 일정                          | Phase ID·예상 시작·예상 종료·작업일                                  |
| 12   | 상태 범례                          | ⏳ 대기·🔄 진행중·✅ 완료·⏸️ 보류·❌ 취소                            |
| 13   | 업데이트 방법                      | Phase 시작 시·완료 시·진행률 계산                                    |

---

## 3. 작성 규약

### 3.1 파일명·저장 위치

| 항목          | 규칙                                                          |
| ------------- | ------------------------------------------------------------- |
| **파일명**    | `phase-X-navigation.md` (X = Major Phase 번호, 예: 9, 10, 11) |
| **저장 위치** | `docs/phases/phase-X-navigation.md`                           |

### 3.2 링크 규칙

- Plan: `phase-X-Y/phase-X-Y-0-plan.md` (또는 해당 Phase의 plan 파일명)
- Todo List: `phase-X-Y/phase-X-Y-0-todo-list.md` (또는 해당 Phase의 todo-list 파일명)
- Task README: `phase-X-Y/tasks/README.md`
- Master Plan: `phase-X-master-plan.md`
- 이전/다음 Phase Navigation: `phase-(X-1)-navigation.md`, `phase-(X+1)-navigation.md` (존재 시)

### 3.3 상태·진행률

- 초기 상태: 모든 Phase **⏳ 대기**, 진행률 **0%**.
- 완료 이력·예상 일정은 Master Plan의 예상 작업량을 반영하여 표 작성.

### 3.4 금지 사항

- Phase ID(X-Y), Task ID(X-Y-N)를 Master Plan과 다르게 기재하지 않는다.
- 필수 섹션(§2 표 기준)을 생략하지 않는다.

---

## 4. 참조 문서 (룰집 연동)

| 문서                                                                                          | 용도                                  |
| --------------------------------------------------------------------------------------------- | ------------------------------------- |
| [rules-index.md](../../rules-index.md)                                                        | 통합 Rules 인덱스 — 본 규칙 링크 등록 |
| [common/common-phase-10-navigation.md](../../common/references/common-phase-10-navigation.md) | 형식·섹션 순서 참조                   |
| [common/common-phase-9-navigation.md](../../common/references/common-phase-9-navigation.md)   | 형식·의존성 그래프 참조               |
| [common/common-phase-11-navigation.md](../../common/references/common-phase-11-navigation.md) | Phase 11 적용 예시                    |
| [ai-rule-phase-naming.md](ai-rule-phase-naming.md)                                            | Phase ID·Task ID 명명 규칙            |

---

## 5. 다음 단계 (연동)

- **phase-X-navigation.md** 생성 후, 각 phase-X-Y별 **plan·todo-list**가 필요하면 **[phase-x-plan-todo:make]** 명령 사용. [ai-rule-phase-plan-todo-generation.md](ai-rule-phase-plan-todo-generation.md) 참조.

---

## 6. 한 줄 요약

**`phase-X-master-plan.md`가 있을 때 [phase-x-navi:make] 명령으로 `phase-X-navigation.md`를 생성·갱신하며, 문서 구조와 작성 규약은 phase-10/phase-11 navigation을 참조한다.**
