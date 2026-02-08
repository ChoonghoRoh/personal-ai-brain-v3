# Task 11-2-1: 공통 CRUD 모듈 + Schema·Template·PromptPreset CRUD API

**우선순위**: 11-2 내 1순위  
**예상 작업량**: 2.5일  
**의존성**: 11-1 완료  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-2-0-todo-list.md](../phase-11-2-0-todo-list.md)  
**Plan**: [phase-11-2-0-plan.md](../phase-11-2-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

**공통 CRUD 모듈**(의존성·유틸, 공통 Pydantic, 공통 라우터 패턴)을 세분화·구현한 뒤, **Schema·Template·PromptPreset** 리소스별 CRUD API를 공통 모듈을 사용해 하나의 기능으로 통합한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| `backend/routers/admin/` 또는 `backend/services/admin/` | 공통 의존성·유틸(DB 세션, 예외 404/409/422, 로깅) |
| 공통 Pydantic 모듈 | 목록 조회 쿼리(필터·페이징), 공통 응답 래퍼(목록/단건) |
| 베이스 라우터 또는 팩토리 | List / Get / Create / Update / Delete 시그니처·에러 처리 |
| Schema·Template·PromptPreset 라우터·모델 | 각 CRUD 엔드포인트 |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| `backend/main.py` (필요 시) | Admin 라우터 등록 |

---

## 3. 작업 체크리스트 (Done Definition)

### 3.1 공통 CRUD 모듈(세분화)

- [ ] 의존성·유틸: DB 세션, 예외 변환(404/409/422), 로깅 (`backend/routers/admin/` 또는 `backend/services/admin/`)
- [ ] 공통 Pydantic: 목록 조회 쿼리(필터·페이징), 공통 응답 래퍼(목록/단건)
- [ ] 공통 라우터 패턴: List / Get / Create / Update / Delete 시그니처·에러 처리(베이스 라우터 또는 팩토리)

### 3.2 리소스별 CRUD 통합

- [ ] Schema CRUD 엔드포인트(공통 모듈 사용)
- [ ] Template CRUD 엔드포인트(공통 모듈 사용)
- [ ] PromptPreset CRUD 엔드포인트(공통 모듈 사용)
- [ ] OpenAPI 반영·문서화
- [ ] Task 계획·report 문서화 (`phase-11-2/`)

---

## 4. 참조

- [phase-11-2-0-plan.md](../phase-11-2-0-plan.md) §2 — 공통 CRUD 모듈화 및 통합 방안
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — Admin API 상세 참고
