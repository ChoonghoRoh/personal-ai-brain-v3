# Phase 11 Master Plan - Admin 설정 관리 시스템 구축

**작성일**: 2026-02-04
**최종 수정**: 2026-02-04
**상태**: 초안
**선행 조건**: Phase 10 완료
**기준 문서**: [phase-11-master-plan-sample.md](phase-11-master-plan-sample.md), [phase-10-master-plan.md](phase-10-master-plan.md)
**명명 규칙**: [ai-rule-phase-naming.md](../ai/ai-rule-phase-naming.md) — Phase ID **11-Y**, Task **11-Y-N**
**산출물 규칙**: [ai-rule-task-inspection.md](../ai/ai-rule-task-inspection.md) — Task 당 report 작성, task-test-report 저장 위치 **phase-11-Y**(`docs/phases/phase-11-Y/`)

---

## Phase 11 목표 (1문장)

**개발자 개입 없이 운영팀이 설정(템플릿·프리셋·RAG·정책)을 조정할 수 있는 Admin 설정 관리 시스템을 구축한다.**

---

## 목차

1. [관련 문서](#관련-문서)
2. [Phase 10 대비 및 Phase 11 위치](#1-phase-10-대비-및-phase-11-위치)
3. [목표 및 범위 (In / Out Scope)](#2-목표-및-범위-in--out-scope)
4. [단계 번호 체계 및 우선순위에 따른 단계별 계획](#3-단계-번호-체계-및-우선순위에-따른-단계별-계획)
5. [상세 Task 목록·산출물](#4-상세-task-목록산출물)
6. [의존성 및 진행 순서](#5-의존성-및-진행-순서)
7. [성공 기준 (체크리스트)](#6-성공-기준-체크리스트)
8. [예상 총 작업량](#7-예상-총-작업량)
9. [산출물 요약 (MD, DB)](#8-산출물-요약-md-db)
10. [부록](#부록)

---

## 관련 문서

| 문서                                                                       | 용도                                                                                                     |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| [Phase 명명 규칙](../ai/ai-rule-phase-naming.md)                           | Phase ID(11-Y)·Task(11-Y-N) 생성 기준                                                                    |
| [Task 검사 규정](../ai/ai-rule-task-inspection.md)                         | Task 완료 판단·산출물·파일명 저장 규칙                                                                   |
| [Phase 10 Master Plan](phase-10-master-plan.md)                            | 선행 Phase·Phase 11 착수 전제                                                                            |
| [Phase 11 Master Plan Sample](phase-11-master-plan-sample.md)              | Admin 설정·DB/API/UI 상세 참고                                                                           |
| [Phase 11 Navigation](phase-11-navigation.md)                              | 작업 순서·진행 현황·Phase 상태 (참조: [phase-x-navi:make](../ai/ai-rule-phase-navigation-generation.md)) |
| [Phase 10 Final Summary Report](phase-10-final-summary-report.md)          | Phase 10 완료 요약·11-5 고도화 검토 기준                                                                 |
| [Phase 11-5 Phase 10 고도화 계획](phase-11-5/phase-10-improvement-plan.md) | 11-5 검토·개발 계획서                                                                                    |
| [Phase 문서 분류](../phase-document-taxonomy.md)                           | plan/todo-list/task/test-report 저장 위치                                                                |
| [n8n 노드 명명 규칙](../n8n/rules/n8n%20node%20nameing%20Rules.md)         | Phase 자동화·워크플로우 시 노드 명명 기준                                                                |

---

## 1. Phase 10 대비 및 Phase 11 위치

### 1.1 Phase 10 완료 전제

Phase 10에서 Reasoning **페이지(UX/UI·시각화·결과물)** 고도화가 반영·검증된 후, Phase 11은 **운영 가능한 설정 관리**를 목표로 한다.

| Phase 10 산출물 (전제)             | Phase 11에서 활용·전제                    |
| ---------------------------------- | ----------------------------------------- |
| 10-1~10-3 UX/시각화/결과물         | Reasoning Lab 사용자 경험 유지, 회귀 유지 |
| 10-4 고급 기능(스트리밍·공유·저장) | 설정 연동 시 기존 API/UI와 통합           |

### 1.2 Phase 11에서 다루는 영역

Phase 10까지는 **프론트/백엔드 기능·UX**가 중심이었고, Phase 11은 **설정의 DB화·API화·Admin UI**로 "개발자 개입 없이 운영 조정"을 가능하게 한다.

| 영역      | Phase 10 결과      | Phase 11 목표                         |
| --------- | ------------------ | ------------------------------------- |
| 설정 관리 | 코드/환경변수 수정 | DB·API·Admin UI로 CRUD, Draft→Publish |
| 버전·감사 | 없음               | 템플릿/프리셋 버전, Audit Log         |
| 확장      | 단일 인스턴스      | 향후 멀티 테넌시 기반(선택)           |

---

## 2. 목표 및 범위 (In / Out Scope)

### 2.1 In Scope (포함)

| 분류         | 항목                                                                                                                                         |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **DB**       | Role 스키마(schemas), 템플릿(templates), 프롬프트 프리셋(prompt_presets), RAG 프로필(rag_profiles), 정책(policy_sets), 감사 로그(audit_logs) |
| **API**      | Admin 설정 CRUD API, 버전 관리·Publish/Rollback, 정책 해석(resolve) API                                                                      |
| **Admin UI** | 템플릿 편집, 프리셋·RAG 프로필 관리, 정책 대시보드, Audit Log 조회                                                                           |
| **운영**     | Draft→Review→Publish 워크플로우, 롤백, 운영 매뉴얼                                                                                           |

### 2.2 Out of Scope (제외)

| 항목                                          | 사유                                                    |
| --------------------------------------------- | ------------------------------------------------------- |
| 멀티 테넌시 풀 구현(회사별 격리·마켓플레이스) | Phase 11에서는 DB·API·UI 기반만 구축, 확장은 이후 Phase |
| A/B 테스트·품질 리포트 대시보드               | 고급 Admin 기능, 별도 Phase 권장                        |
| 외부 연동(Notion, Confluence)                 | 로컬 우선 방침 유지                                     |

---

## 3. 단계 번호 체계 및 우선순위에 따른 단계별 계획

### 3.1 단계 번호 체계

| 구분      | 형식          | 의미                                | 예시                                           |
| --------- | ------------- | ----------------------------------- | ---------------------------------------------- |
| **Phase** | **11-Y**      | Y = 목표·전략 단위 (1~5)             | 11-1~11-5 Admin·고도화                                                |
| **Task**  | **11-Y-N**    | N = 해당 Phase 내 todo 순번 (1부터) | 11-1-1, 11-2-3                                 |
| **폴더**  | `phase-11-Y/` | Phase 단위 문서·tasks 하위          | `docs/phases/phase-11-1/`, `phase-11-1/tasks/` |

[ai-rule-phase-naming.md](../ai/ai-rule-phase-naming.md) 준수. Phase 변화 시 Y 변경 → 새 폴더 `phase-11-Y` 생성.

### 3.2 우선순위 요약

Phase 10 완료를 전제로 **DB → API → UI → 통합·운영** 순으로 우선순위를 둔다.

| 순위  | Phase ID | Phase 명               | 사유                                | 예상   |
| ----- | -------- | ---------------------- | ----------------------------------- | ------ |
| **1** | 11-1     | DB 스키마·마이그레이션 | 설정 저장 기반                      | 2~3일  |
| **2** | 11-2     | Admin 설정 Backend API | CRUD·버전·감사                      | 5~7일  |
| **3** | 11-3     | Admin UI               | 설정 관리 대시보드                  | 7~10일 |
| **4** | 11-4     | 통합 테스트·운영 준비  | 검증·매뉴얼                         | 3~4일  |
| **5** | 11-5     | Phase 10 고도화        | Phase 10 검토·고도화 계획·회귀 확장 | 2~5일  |

### 3.3 Phase 11 구조 (우선순위 순)

```
Phase 11 (X=11, Y=목표 단위별 폴더 phase-11-Y)

1순위  Phase 11-1   DB 스키마·마이그레이션
       ├── Task 11-1-1   schemas·templates·prompt_presets 테이블
       ├── Task 11-1-2   rag_profiles·context_rules·policy_sets 테이블
       └── Task 11-1-3   audit_logs·마이그레이션·시딩

2순위  Phase 11-2   Admin 설정 Backend API
       ├── Task 11-2-1   Schema·Template·Preset CRUD API
       ├── Task 11-2-2   RAG Profile·Policy Set API
       ├── Task 11-2-3   버전 관리·Publish/Rollback·Audit Log API
       └── Task 11-2-4   정책 해석(resolve) API·Reasoning 연동

3순위  Phase 11-3   Admin UI
       ├── Task 11-3-1   Admin 레이아웃·라우팅
       ├── Task 11-3-2   템플릿·프리셋·RAG 프로필 편집 화면
       ├── Task 11-3-3   정책 대시보드·Audit Log 뷰어
       └── Task 11-3-4   API 연동·권한·에러 처리

4순위  Phase 11-4   통합 테스트·운영 준비
       ├── Task 11-4-1   통합 테스트 시나리오·회귀
       └── Task 11-4-2   운영 매뉴얼·롤백 절차

5순위  Phase 11-5   Phase 10 고도화 (phase-10-improvement-plan §2.1~§2.5 세분 반영)
       ├── Task 11-5-1   Phase 10 고도화 항목 검토·우선순위
       ├── Task 11-5-2   고도화 개발 계획서·Task 정의 (§2.1~2.5 세분)
       ├── Task 11-5-3   §2.1 Reasoning Lab 성능·안정성 고도화 (선택)
       ├── Task 11-5-4   §2.2 시각화 고도화 (선택)
       ├── Task 11-5-5   §2.3 결과물·접근성 고도화 (선택)
       ├── Task 11-5-6   §2.4 공유·저장 고도화 (선택)
       └── Task 11-5-7   §2.5 회귀·E2E·Phase 11 연동
```

---

## 4. 상세 Task 목록·산출물

### Phase 11-1 DB 스키마·마이그레이션 (1순위)

| Task   | 목표                                                              | 예상    | 산출물 (MD·DB)                                                                                            |
| ------ | ----------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------- |
| 11-1-1 | schemas, templates, prompt_presets 테이블 설계·마이그레이션       | 1일     | DB: 마이그레이션 파일. MD: `phase-11-1/tasks/task-11-1-1-*.md`, `phase-11-1/phase11-1-1-*-test-report.md` |
| 11-1-2 | rag_profiles, context_rules, policy_sets 테이블 설계·마이그레이션 | 1일     | DB: 마이그레이션 파일. MD: task 계획·report                                                               |
| 11-1-3 | audit_logs 테이블, 초기 시딩 스크립트, 관계 검증                  | 0.5~1일 | DB: audit_logs 마이그레이션, 시딩 스크립트. MD: task 계획·report                                          |

**Phase 11-1 산출물 요약**: Alembic 마이그레이션, 시딩 스크립트, `docs/phases/phase-11-1/` 내 plan·todo-list·task 문서·task report.

### Phase 11-2 Admin 설정 Backend API (2순위)

| Task   | 목표                                          | 예상  | 산출물 (MD·코드)                                                                                |
| ------ | --------------------------------------------- | ----- | ----------------------------------------------------------------------------------------------- |
| 11-2-1 | Schema·Template·PromptPreset CRUD API         | 2일   | `backend/routers/admin/`(또는 `api/admin/`), Pydantic 모델. MD: task 계획·report(`phase-11-2/`) |
| 11-2-2 | RAG Profile·Policy Set CRUD API               | 1.5일 | 동일 라우터·모델 확장. MD: task 계획·report                                                     |
| 11-2-3 | 버전 관리·Publish/Rollback·Audit Log API      | 1.5일 | 버전·감사 API. MD: task 계획·report                                                             |
| 11-2-4 | 정책 해석(resolve) API, Reasoning 서비스 연동 | 1일   | resolve 엔드포인트, reason.py 연동. MD: task 계획·report                                        |

**Phase 11-2 산출물 요약**: OpenAPI 반영, Task 테스트 결과는 `docs/phases/phase-11-2/`에 저장([ai-rule-task-inspection](../ai/ai-rule-task-inspection.md) §3).

### Phase 11-3 Admin UI (3순위)

| Task   | 목표                               | 예상  | 산출물 (MD·코드)                                   |
| ------ | ---------------------------------- | ----- | -------------------------------------------------- |
| 11-3-1 | Admin 레이아웃·네비게이션·라우팅   | 1.5일 | `web/` Admin 레이아웃·라우팅. MD: task 계획·report |
| 11-3-2 | 템플릿·프리셋·RAG 프로필 편집 화면 | 3일   | 편집 페이지·컴포넌트. MD: task 계획·report         |
| 11-3-3 | 정책 대시보드·Audit Log 뷰어       | 2일   | 대시보드·뷰어 화면. MD: task 계획·report           |
| 11-3-4 | API 연동·권한 체크·에러 처리       | 1.5일 | 연동·에러 처리. MD: task 계획·report               |

**Phase 11-3 산출물 요약**: `web/` 내 Admin 페이지·컴포넌트, 기존 Admin 그룹/라벨과 경로·메뉴 통합.

### Phase 11-4 통합 테스트·운영 준비 (4순위)

| Task   | 목표                                                      | 예상  | 산출물 (MD)                                                         |
| ------ | --------------------------------------------------------- | ----- | ------------------------------------------------------------------- |
| 11-4-1 | 통합 테스트 시나리오(Draft→Publish→Rollback), 회귀 테스트 | 2일   | 테스트 시나리오·결과. MD: `phase-11-4/phase11-4-1-*-test-report.md` |
| 11-4-2 | 운영 매뉴얼·롤백 절차·백업 연동 문서화                    | 1~2일 | 운영 매뉴얼(md). MD: `docs/phases/phase-11-4/` 또는 `docs/manual/`  |

### Phase 11-5 Phase 10 고도화 (5순위) — §2.1~§2.5 세분 반영

| Task   | 목표 (phase-10-improvement-plan §2 대응)     | 예상    | 산출물 (MD)                                                |
| ------ | -------------------------------------------- | ------- | ---------------------------------------------------------- |
| 11-5-1 | Phase 10 고도화 항목 검토·우선순위           | 0.5일   | `phase-11-5/phase-10-improvement-plan.md` 등               |
| 11-5-2 | 고도화 개발 계획서·Task 정의 (§2.1~2.5 세분) | 0.5일   | `phase-11-5-0-plan.md`, `phase-11-5-0-todo-list.md`, tasks |
| 11-5-3 | §2.1 Reasoning Lab 성능·안정성 고도화 (선택) | 0.5~1일 | 구현·검증. MD: task report                                 |
| 11-5-4 | §2.2 시각화 고도화 (선택)                    | 0.5~1일 | 구현·검증. MD: task report                                 |
| 11-5-5 | §2.3 결과물·접근성 고도화 (선택)             | 0.5~1일 | 구현·검증. MD: task report                                 |
| 11-5-6 | §2.4 공유·저장 고도화 (선택)                 | 0.5~1일 | 구현·검증. MD: task report                                 |
| 11-5-7 | §2.5 회귀·E2E·Phase 11 연동                  | 1일     | 회귀 시나리오·검증 범위. MD: `phase-11-5/` 또는 devtest    |

**Phase 11-5 산출물 요약**: [phase-11-5/phase-10-improvement-plan.md](phase-11-5/phase-10-improvement-plan.md) **§2.1~§2.5** 기준. 상세 계획·todo는 `docs/phases/phase-11-5/` 내 plan·todo-list·tasks.

---

## 5. 의존성 및 진행 순서

### 5.1 의존성

```
11-1-1 → 11-1-2 → 11-1-3  (순차)

11-2-1, 11-2-2  (11-1 완료 후 병렬 가능)
11-2-3 → 11-2-4  (버전/감사 후 정책 해석)

11-3-1 → 11-3-2, 11-3-3  (레이아웃 후 편집/뷰어)
11-3-4  (전 구간 API 연동)

11-4-1, 11-4-2  (11-2·11-3 완료 후)

11-5-1 → 11-5-2  (Phase 10 완료·최종 요약 보고서 기준)
11-5-3, 11-5-4, 11-5-5, 11-5-6  (선택, 11-5-2 완료 후)
11-5-7  (Phase 11-2·11-3 일부 완료 후 또는 11-4 통합 테스트 시)

```

### 5.2 Phase 10 대비 진행 시 유의사항

- Phase 11 개발·배포 시 **Phase 10 회귀 테스트**(Reasoning Lab UX/시각화/결과물) 유지.
- Admin 설정 API가 Reasoning 호출에 연동될 경우 기존 `reason.py`, RAG/프리셋 사용 경로와 충돌 없이 적용.

---

## 6. 성공 기준 (체크리스트)

Phase 11 완료 판정 시 아래 항목을 순서대로 확인한다.

### 6.1 Phase 11 완료 조건 체크리스트

#### DB (11-1)

- [ ] **11-1-1** schemas, templates, prompt_presets 테이블 마이그레이션 적용·시딩 완료
- [ ] **11-1-2** rag_profiles, context_rules, policy_sets 테이블 마이그레이션 적용·시딩 완료
- [ ] **11-1-3** audit_logs 테이블 마이그레이션 적용, 초기 시딩·관계 검증 완료

#### API (11-2)

- [ ] **11-2-1** Schema·Template·PromptPreset CRUD API 동작, OpenAPI 반영
- [ ] **11-2-2** RAG Profile·Policy Set CRUD API 동작
- [ ] **11-2-3** 버전 관리·Publish/Rollback·Audit Log API 동작
- [ ] **11-2-4** 정책 해석(resolve) API 동작, Reasoning 서비스 연동 검증

#### Admin UI (11-3)

- [ ] **11-3-1** Admin 레이아웃·네비게이션·라우팅 동작
- [ ] **11-3-2** 템플릿·프리셋·RAG 프로필 편집 화면 동작
- [ ] **11-3-3** 정책 대시보드·Audit Log 뷰어 동작
- [ ] **11-3-4** API 연동·권한·에러 처리 동작

#### 통합·운영 (11-4)

- [ ] **11-4-1** Draft→Publish→Rollback 시나리오 통합 테스트·회귀 검증 완료
- [ ] **11-4-2** 운영 매뉴얼·롤백 절차·백업 연동 문서화 완료

#### Phase 10 고도화 (11-5) — §2.1~§2.5 세분 반영

- [ ] **11-5-1** Phase 10 고도화 항목 검토·우선순위 목록 확정 문서화
- [ ] **11-5-2** 고도화 개발 계획서(§2.1~2.5 세분 Task·완료 기준) 완료
- [ ] **11-5-3** (선택) §2.1 Reasoning Lab 성능·안정성 고도화 구현·검증 완료
- [ ] **11-5-4** (선택) §2.2 시각화 고도화 구현·검증 완료
- [ ] **11-5-5** (선택) §2.3 결과물·접근성 고도화 구현·검증 완료
- [ ] **11-5-6** (선택) §2.4 공유·저장 고도화 구현·검증 완료
- [ ] **11-5-7** §2.5 회귀·E2E·Phase 11 연동 시나리오·검증 범위 문서화 완료

### 6.2 KPI (참고)

| 지표                     | 목표                                        |
| ------------------------ | ------------------------------------------- |
| 설정 변경(템플릿/프리셋) | 개발자 배포 없이 Admin UI에서 5분 이내 반영 |
| 롤백                     | 1분 이내 이전 버전 복구                     |
| API 응답                 | Admin API 200ms 이내(목표)                  |

---

## 7. 예상 총 작업량

| 단계                              | 예상 일수              |
| --------------------------------- | ---------------------- |
| Phase 11-1 DB 스키마·마이그레이션 | 2.5~3일                |
| Phase 11-2 Admin 설정 Backend API | 6일                    |
| Phase 11-3 Admin UI               | 8일                    |
| Phase 11-4 통합·운영 준비         | 3~4일                  |
| Phase 11-5 Phase 10 고도화        | 2~5일 (11-5-3 선택 시) |
| **합계**                                          | **약 21.5~26일** (Admin)|

---

## 8. 산출물 요약 (MD, DB)

### 8.1 MD 문서 산출물

| 구분                        | 파일명 패턴                                                                 | 저장 위치                                     |
| --------------------------- | --------------------------------------------------------------------------- | --------------------------------------------- |
| Phase plan                  | `phase-11-Y-0-plan.md`                                                      | `docs/phases/phase-11-Y/`                     |
| Phase todo-list             | `phase-11-Y-0-todo-list.md`                                                 | `docs/phases/phase-11-Y/`                     |
| Task 실행 계획              | `task-11-Y-N-<주제>.md`                                                     | `docs/phases/phase-11-Y/tasks/`               |
| Task 테스트 결과·report     | `phase11-Y-N-task-test-result.md` 또는 `phase11-Y-N-<topic>-test-report.md` | `docs/phases/phase-11-Y/`                     |
| Phase 단위 Task 수행 리포트 | `phase-11-Y-task-report.md`                                                 | `docs/phases/phase-11-Y/`                     |
| 운영 매뉴얼                 | 운영 가이드 md                                                              | `docs/phases/phase-11-4/` 또는 `docs/manual/` |

### 8.2 DB 산출물

| 구분             | 내용                                                                                                                 |
| ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| **마이그레이션** | Alembic 마이그레이션 파일 (schemas, templates, prompt_presets, rag_profiles, context_rules, policy_sets, audit_logs) |
| **시딩**         | 초기 데이터 시딩 스크립트·실행 결과 검증                                                                             |

### 8.3 개발 rule 준수 (산출물·문서)

- **Task 실행 계획**: `docs/phases/phase-11-Y/tasks/task-11-Y-N-<주제>.md` ([phase-document-taxonomy](../phase-document-taxonomy.md) §2.4).
- **Task 당 report 작성**: 각 Task 완료 시 수행·검증 결과 문서화. 테스트 대상 Task는 `phase11-Y-N-task-test-result.md` 또는 `phase11-Y-N-<topic>-test-report.md` 작성([ai-rule-task-inspection](../ai/ai-rule-task-inspection.md) §3).
- **task-test-report 저장 위치**: **phase-11-Y**(`docs/phases/phase-11-Y/`). `tasks/` 하위 아님.
- **Phase 단위 Task 수행 리포트**: `phase-11-Y-task-report.md` (Phase별 통합 리포트).

---

## 부록

### A. Phase 11 Sample·Phase 10 참조

| 출처                                                             | 내용                                                                           |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| [phase-11-master-plan-sample.md](phase-11-master-plan-sample.md) | Admin DB 스키마(SQL)·API 시그니처·Admin UI 구조·Phase 11 멀티 테넌시 확장 언급 |
| [phase-10-master-plan.md](phase-10-master-plan.md)               | Phase 10 구조·완료 기준·Phase 9 대비 위치                                      |

### C. Phase 10 구현물 (Phase 11에서 유지·연동)

| Phase 10       | 경로/내용                                                                                                                                             |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Reasoning Lab  | `web/src/pages/reason.html`, 시각화·결과물                                                                                                            |
| Reasoning API  | `backend/routers/reasoning/reason.py`, RAG·프리셋 사용 경로                                                                                           |
| Admin 기존     | `web/` 내 그룹·라벨·청크 등 Admin 페이지 — 11-3에서 설정 Admin과 경로·메뉴 통합 고려                                                                  |
| **Phase 11-5** | Phase 10 고도화: [phase-11-5/phase-10-improvement-plan.md](phase-11-5/phase-10-improvement-plan.md) — Reasoning Lab 성능·시각화·결과물·공유·회귀 확장 |

### D. 다음 단계

Phase 11 완료 후: **Phase 11-4** 통합·운영 준비 완료 및 회귀 검증 후, 필요 시 webtest 규정([docs/webtest/README.md](../webtest/README.md))에 따라 Admin UI 웹 테스트·시나리오 추가.
멀티 테넌시·A/B 테스트 등은 별도 Phase로 계획.

---

**문서 상태**: 초안
**명명 규칙**: [ai-rule-phase-naming.md](../ai/ai-rule-phase-naming.md) — Phase **11-Y**, Task **11-Y-N**
**다음 단계**: Phase 11-1(DB 스키마)부터 `phase-11-1/` 폴더·todo-list·Task(11-1-N) 문서 작성
