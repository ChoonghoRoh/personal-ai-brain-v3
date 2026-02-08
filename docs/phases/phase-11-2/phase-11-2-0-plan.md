# Phase 11-2-0 Plan — Admin 설정 Backend API

**Phase ID**: 11-2  
**Phase 명**: Admin 설정 Backend API  
**Z**: 0 (초기 설계)  
**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)  
**명명 규칙**: [ai-rule-phase-naming.md](../../ai/ai-rule-phase-naming.md)

---

## 1. Phase Goal

Phase 11-1에서 구축한 DB 스키마를 기반으로 **Admin 설정 CRUD API**를 구현한다.  
**공통 CRUD 모듈**을 먼저 세분화·개발하고, **각 리소스(Schema, Template, Preset, RAG, Policy)별로 하나의 기능으로 통합**한다.  
**버전 관리·정책 해석**은 이번 Phase에서 **디테일한 설계만** 수행하고, 구현은 다음 Phase에서 진행한다.  
**Web에서 CRUD 필요 부분**은 검토·적용 검토 후, 실제 개발은 다음 Phase(11-3)에서 진행하도록 조치한다.

---

## 2. 공통 CRUD 모듈화 및 통합 방안

### 2.1 원칙

| 원칙 | 내용 |
|------|------|
| **공통 모듈 우선** | CRUD에 공통화할 수 있는 부분(라우터 패턴, Pydantic 기반 검증, DB 세션·예외 처리, 응답 포맷)을 모듈로 개발한 뒤, 리소스별로 조합. |
| **리소스별 하나의 기능으로 통합** | Schema, Template, Preset, RAG Profile, Policy Set 각각을 공통 모듈을 사용하는 하나의 CRUD 단위로 구현. |
| **세분화 후 적용** | 공통 CRUD 기능을 단계별로 세분화(§2.2)하여 이번 개발에 적용. |

### 2.2 공통 CRUD 세분화(이번 개발 적용)

| 세분 항목 | 내용 | 산출물 |
|-----------|------|--------|
| **공통 의존성·유틸** | DB 세션, 예외 변환(404/409/422), 로깅. | `backend/routers/admin/` 또는 `backend/services/admin/` 하위 공통 모듈 |
| **공통 Pydantic 패턴** | 목록 조회 쿼리(필터·페이징), 공통 응답 래퍼(목록/단건). | 공통 스키마 모듈 |
| **공통 라우터 패턴** | List / Get / Create / Update / Delete 공통 시그니처·에러 처리. | 베이스 라우터 또는 팩토리 함수 |
| **리소스별 CRUD 통합** | Schema, Template, Preset, RAG, Policy Set 각각 위 공통 모듈을 사용해 엔드포인트 구현. | 리소스별 라우터·모델 |

### 2.3 통합 흐름

```
[공통 CRUD 모듈]
  ├── 의존성·유틸 (세션, 예외, 로깅)
  ├── 공통 Pydantic (쿼리·응답)
  └── 공통 라우터 패턴 (List/Get/Create/Update/Delete)

        ↓ 적용

[리소스별 CRUD]
  ├── 11-2-1  Schema, Template, PromptPreset
  ├── 11-2-2  RAG Profile, Policy Set
  └── (각각 하나의 기능으로 통합된 API)
```

---

## 3. Scope

### 3.1 이번 Phase 개발 범위(In Scope)

| Task ID | 항목 | 이번 Phase | 예상 |
|---------|------|------------|------|
| 11-2-1 | **공통 CRUD 모듈** + Schema·Template·PromptPreset CRUD API | 구현 | 2.5일 |
| 11-2-2 | RAG Profile·Policy Set CRUD API (공통 모듈 사용) | 구현 | 1.5일 |
| 11-2-3 | 버전 관리·Publish/Rollback·Audit Log | **디테일 설계만** (구현은 다음 Phase) | 0.5일 |
| 11-2-4 | 정책 해석(resolve) API·Reasoning 연동 | **디테일 설계만** (구현은 다음 Phase) | 0.5일 |
| 11-2-5 | Web에서 CRUD 필요 부분 검토·적용 검토·다음 Phase 연계 | 검토·문서화·조치 | 0.5일 |

### 3.2 다음 Phase로 이관

| 항목 | 이번 Phase | 다음 Phase |
|------|------------|------------|
| 버전 관리·Publish/Rollback·Audit Log **API 구현** | 상세 설계 문서 | 구현 |
| 정책 해석(resolve) **API 구현** 및 reason.py 연동 | 상세 설계 문서 | 구현 |
| Web CRUD **기능 개발** (Admin UI에서 API 호출·화면 구현) | 필요 부분 검토·적용 검토 | Phase 11-3에서 개발 |

### 3.3 Out of Scope

- Admin UI 구현(Phase 11-3), 통합 테스트·운영 매뉴얼(Phase 11-4).
- 멀티 테넌시·A/B 테스트(마스터 플랜과 동일).

---

## 4. Task 개요

| Task ID | Task 명 | 이번 Phase | 예상 | 의존성 |
|---------|---------|------------|------|--------|
| 11-2-1 | 공통 CRUD 모듈 + Schema·Template·PromptPreset CRUD API | 구현 | 2.5일 | 11-1 완료 |
| 11-2-2 | RAG Profile·Policy Set CRUD API | 구현 | 1.5일 | 11-2-1 공통 모듈 |
| 11-2-3 | 버전 관리·Audit Log **상세 설계** | 설계만 | 0.5일 | 11-2-1·11-2-2 |
| 11-2-4 | 정책 해석(resolve) **상세 설계** | 설계만 | 0.5일 | 11-2-3 설계 참고 |
| 11-2-5 | Web CRUD 필요 부분 검토·다음 Phase 연계 | 검토·조치 | 0.5일 | 11-2-1·11-2-2 |

**진행 순서**: 11-2-1(공통 모듈 + 첫 번째 CRUD) → 11-2-2 → 11-2-3(설계) → 11-2-4(설계) → 11-2-5(검토·연계).

---

## 5. Task별 상세

### 5.1 Task 11-2-1: 공통 CRUD 모듈 + Schema·Template·PromptPreset CRUD

- **공통 CRUD 모듈(세분화)**  
  - 의존성·유틸(세션, 예외, 로깅).  
  - 공통 Pydantic(목록 쿼리·응답 래퍼).  
  - 공통 라우터 패턴(List/Get/Create/Update/Delete).  
- **리소스별 통합**  
  - Schema, Template, PromptPreset 각각 공통 모듈을 사용해 CRUD 엔드포인트 구현.  
- **산출물**: `backend/routers/admin/`(또는 동일 구조), Pydantic 모델, OpenAPI 반영. Task 계획·report(`phase-11-2/`).

### 5.2 Task 11-2-2: RAG Profile·Policy Set CRUD API

- 공통 CRUD 모듈을 사용해 RAG Profile, Policy Set CRUD 구현.  
- 산출물: 동일 라우터·모델 확장, OpenAPI 반영, task report.

### 5.3 Task 11-2-3: 버전 관리·Publish/Rollback·Audit Log (상세 설계)

- **이번 Phase**: API 스펙(엔드포인트·요청/응답)·상태 전이·Audit Log 기록 규칙 등 **디테일한 설계 문서** 작성.  
- **구현**: 다음 Phase(또는 별도 Phase)에서 설계 문서 기반으로 진행.  
- 산출물: `phase-11-2/` 내 설계 문서(예: `phase-11-2-3-version-audit-design.md`).

### 5.4 Task 11-2-4: 정책 해석(resolve) API (상세 설계)

- **이번 Phase**: resolve API 스펙·Reasoning(reason.py) 연동 방식·우선순위 규칙 등 **디테일한 설계 문서** 작성.  
- **구현**: 다음 Phase에서 설계 문서 기반으로 진행.  
- 산출물: `phase-11-2/` 내 설계 문서(예: `phase-11-2-4-resolve-policy-design.md`).

### 5.5 Task 11-2-5: Web에서 CRUD 필요 부분 검토·다음 Phase 연계

- **목적**: CRUD가 필요한 Web(Admin UI) 화면·플로우를 검토하고, 이번 Phase에서 적용 가능한 범위를 정한 뒤, **실제 Web 개발은 Phase 11-3에서 수행**하도록 조치.  
- **내용**  
  - Web(Admin 설정 관리 화면)에서 필요한 CRUD 목록 정리(어떤 리소스, 어떤 작업: 목록/상세/생성/수정/삭제).  
  - 11-2-1·11-2-2 API와의 매핑·부족한 엔드포인트 여부 적용 검토.  
  - Phase 11-3에서 구현할 항목·우선순위·연계 사항 문서화.  
- **산출물**: `phase-11-2/phase-11-2-5-web-crud-review.md`(또는 동일 명칭). Phase 11-3 plan/todo에 "11-2-5 검토 결과 반영" 참조 추가.

---

## 6. Validation / Exit Criteria

- [ ] **11-2-1** 공통 CRUD 모듈 구현 + Schema·Template·PromptPreset CRUD API·OpenAPI 반영
- [ ] **11-2-2** RAG Profile·Policy Set CRUD API·OpenAPI 반영
- [ ] **11-2-3** 버전 관리·Audit Log 상세 설계 문서 완료(구현은 다음 Phase)
- [ ] **11-2-4** 정책 해석(resolve) 상세 설계 문서 완료(구현은 다음 Phase)
- [ ] **11-2-5** Web CRUD 필요 부분 검토·적용 검토·다음 Phase(11-3) 연계 조치 완료
- [ ] Task 테스트·설계 결과는 `docs/phases/phase-11-2/`에 저장([ai-rule-task-inspection](../../ai/ai-rule-task-inspection.md) §3).

---

## 7. 참고 문서

| 문서 | 용도 |
|------|------|
| [phase-11-master-plan.md](../phase-11-master-plan.md) | Phase 11 전체 계획 |
| [phase-11-2-0-todo-list.md](phase-11-2-0-todo-list.md) | 본 Phase 할 일 목록 |
| [phase-11-master-plan-sample.md](../phase-11-master-plan-sample.md) | Admin API 상세 참고 |
| Phase 11-3 plan/todo | 11-2-5 검토 결과 반영·Web CRUD 개발 범위 |
