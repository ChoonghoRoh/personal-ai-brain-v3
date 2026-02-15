# Task 12-1-3: [INFRA] HTTPS/HSTS 환경변수 기반 활성화

**우선순위**: 12-1 내 3순위
**예상 작업량**: 소 (config + middleware 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-1-todo-list.md`
**Plan**: `phase-12-1-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

HSTS(HTTP Strict Transport Security) 헤더를 환경변수 기반으로 제어할 수 있도록 구현한다. 프로덕션 환경에서 자동 활성화, 개발 환경에서 비활성화되도록 한다.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/config.py` | HSTS_ENABLED, HSTS_MAX_AGE, HSTS_INCLUDE_SUBDOMAINS, HSTS_PRELOAD 환경변수 |
| `backend/middleware/security.py` | Strict-Transport-Security 헤더 조건부 설정 |
| `.env.example` | HSTS 설정 문서화 |

---

## 3. 작업 체크리스트

- [x] `backend/config.py` HSTS 환경변수 추가 (4개)
- [x] `backend/middleware/security.py` HSTS 조건부 활성화 구현
- [x] `.env.example` HSTS 설정 문서화
- [x] 개발 환경 HSTS 비활성화 확인 (HSTS_ENABLED 기본값 = ENVIRONMENT=="production")
- [x] 프로덕션 환경 HSTS 헤더 포함 확인

---

## 4. 참조

- Phase 12 Master Plan §12-1-3
- HSTS max-age: 31536000 (1년)
