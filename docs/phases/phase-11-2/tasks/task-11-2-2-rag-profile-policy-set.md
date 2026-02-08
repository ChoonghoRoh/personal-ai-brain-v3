# Task 11-2-2: RAG Profile·Policy Set CRUD API

**우선순위**: 11-2 내 2순위  
**예상 작업량**: 1.5일  
**의존성**: 11-2-1 공통 모듈 완료  
**상태**: ⏳ 대기

**기반 문서**: [phase-11-2-0-todo-list.md](../phase-11-2-0-todo-list.md)  
**Plan**: [phase-11-2-0-plan.md](../phase-11-2-0-plan.md)  
**작업 순서**: [phase-11-navigation.md](../../phase-11-navigation.md)

---

## 1. 개요

### 1.1 목표

11-2-1에서 구축한 **공통 CRUD 모듈**을 사용해 **RAG Profile·Policy Set** CRUD API를 구현한다. 동일 라우터·모델 확장으로 리소스별 하나의 기능으로 통합한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 경로 | 용도 |
|-----------|------|
| RAG Profile·Policy Set 라우터·Pydantic 모델 | 11-2-1 라우터·모델 확장, CRUD 엔드포인트 |

### 2.2 수정

| 파일 경로 | 용도 |
|-----------|------|
| `backend/routers/admin/` (기존) | RAG Profile·Policy Set 엔드포인트 추가 |

---

## 3. 작업 체크리스트 (Done Definition)

- [ ] RAG Profile CRUD 엔드포인트(공통 모듈 사용, 동일 라우터·모델 확장)
- [ ] Policy Set CRUD 엔드포인트(공통 모듈 사용)
- [ ] OpenAPI 반영·문서화
- [ ] Task 계획·report 문서화

---

## 4. 참조

- [phase-11-2-0-plan.md](../phase-11-2-0-plan.md) §2·§5.2
- [phase-11-master-plan-sample.md](../../phase-11-master-plan-sample.md) — RAG Profile·Policy Set API 참고
