# Phase 11-2: Admin 설정 Backend API — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 11 내 2순위
**예상 작업량**: 5.5일 (이번 Phase: CRUD 구현 + 설계 + Web 검토)
**시작일**: 2026-02-06
**완료일**: 2026-02-06

**기준 문서**: [phase-11-master-plan.md](../phase-11-master-plan.md)  
**Plan**: [phase-11-2-0-plan.md](phase-11-2-0-plan.md)

---

## Phase 진행 정보

### 현재 Phase

- **Phase ID**: 11-2
- **Phase 명**: Admin 설정 Backend API
- **핵심 목표**: 공통 CRUD 모듈 + 리소스별 CRUD API 구현, 버전·정책 해석은 상세 설계만, Web CRUD 검토·다음 Phase 연계

### 이전 Phase

- **Prev Phase ID**: 11-1
- **Prev Phase 명**: DB 스키마·마이그레이션
- **전환 조건**: 11-1 전체 Task 완료

### 다음 Phase

- **Next Phase ID**: 11-3
- **Next Phase 명**: Admin UI
- **전환 조건**: 11-2 전체 Task 완료(CRUD 구현 + 설계 + Web 검토)

### Phase 11 내 우선순위

| 순위 | Phase ID | Phase 명 | 상태 |
|------|----------|----------|------|
| 1 | 11-1 | DB 스키마·마이그레이션 | ✅ 완료 |
| **2** | **11-2** | **Admin 설정 Backend API** | ✅ 완료 |
| 3 | 11-3 | Admin UI | ⏳ 대기 |
| 4 | 11-4 | 통합 테스트·운영 준비 | ⏳ 대기 |

---

## Task 목록 (공통 CRUD·설계·Web 검토 반영)

### 11-2-1: 공통 CRUD 모듈 + Schema·Template·PromptPreset CRUD API ✅

**우선순위**: 11-2 내 1순위
**예상 작업량**: 2.5일
**의존성**: 11-1 완료
**상태**: ✅ 완료

#### 공통 CRUD 모듈(세분화)

- [x] 의존성·유틸: DB 세션, 예외 변환(404/409/422), 로깅 (`backend/routers/admin/deps.py`)
- [x] 공통 Pydantic: 목록 조회 쿼리(필터·페이징), 공통 응답 래퍼(목록/단건) (`backend/routers/admin/schemas_pydantic.py`)
- [x] 공통 라우터 패턴: List / Get / Create / Update / Delete 시그니처·에러 처리

#### 리소스별 CRUD 통합

- [x] Schema CRUD 엔드포인트 (`backend/routers/admin/schema_crud.py`)
- [x] Template CRUD 엔드포인트 (`backend/routers/admin/template_crud.py`)
- [x] PromptPreset CRUD 엔드포인트 (`backend/routers/admin/preset_crud.py`)
- [x] OpenAPI 반영·문서화 (자동 생성)
- [x] main.py에 Admin 라우터 등록

---

### 11-2-2: RAG Profile·Policy Set CRUD API ✅

**우선순위**: 11-2 내 2순위
**예상 작업량**: 1.5일
**의존성**: 11-2-1 공통 모듈 완료
**상태**: ✅ 완료

- [x] RAG Profile CRUD 엔드포인트 (`backend/routers/admin/rag_profile_crud.py`)
- [x] Policy Set CRUD 엔드포인트 (`backend/routers/admin/policy_set_crud.py`)
- [x] OpenAPI 반영·문서화 (자동 생성)
- [x] __init__.py에 라우터 등록

---

### 11-2-3: 버전 관리·Publish/Rollback·Audit Log (상세 설계만) ✅

**우선순위**: 11-2 내 3순위
**예상 작업량**: 0.5일
**의존성**: 11-2-1·11-2-2 완료
**상태**: ✅ 완료
**비고**: **구현은 다음 Phase에서 진행.** 이번 Phase에서는 디테일한 설계만 수행.

- [x] 버전 관리·Publish/Rollback API 스펙(엔드포인트·요청/응답) 설계
- [x] Audit Log 기록 규칙·조회 API 스펙 설계
- [x] 상태 전이(draft → published) 정의
- [x] 설계 문서 작성: `phase-11-2/tasks/task-11-2-3-version-audit-design.md`
- [ ] 구현 작업은 다음 Phase에서 설계 문서 기반으로 진행

---

### 11-2-4: 정책 해석(resolve) API (상세 설계만) ✅

**우선순위**: 11-2 내 4순위
**예상 작업량**: 0.5일
**의존성**: 11-2-3 설계 참고
**상태**: ✅ 완료
**비고**: **구현은 다음 Phase에서 진행.** 이번 Phase에서는 디테일한 설계만 수행.

- [x] 정책 해석(resolve) API 스펙(엔드포인트·입출력) 설계
- [x] Reasoning(reason.py) 연동 방식·우선순위 규칙 설계
- [x] 설계 문서 작성: `phase-11-2/tasks/task-11-2-4-resolve-policy-design.md`
- [ ] 구현·reason.py 연동은 다음 Phase에서 설계 문서 기반으로 진행

---

### 11-2-5: Web에서 CRUD 필요 부분 검토·다음 Phase 연계 ✅

**우선순위**: 11-2 내 5순위
**예상 작업량**: 0.5일
**의존성**: 11-2-1·11-2-2 완료
**상태**: ✅ 완료
**비고**: **Web 기능 개발은 Phase 11-3에서 진행.** 이번 Task는 검토·적용 검토·연계 조치만 수행.

- [x] Web(Admin 설정 관리 화면)에서 필요한 CRUD 목록 정리
- [x] 11-2-1·11-2-2 API와 매핑·부족한 엔드포인트 적용 검토
- [x] Phase 11-3에서 구현할 항목·우선순위·연계 사항 문서화
- [x] 산출물: `phase-11-2/tasks/task-11-2-5-web-crud-review.md`
- [ ] Phase 11-3 plan/todo에 "11-2-5 검토 결과 반영" 참조 추가
