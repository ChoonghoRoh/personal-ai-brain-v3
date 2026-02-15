# Task 12-3-2: [BE] Rate Limit X-Forwarded-For

**우선순위**: 12-3 내 1순위
**예상 작업량**: 소 (rate_limit.py 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-3-todo-list.md`
**Plan**: `phase-12-3-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

리버스 프록시 환경에서 실제 클라이언트 IP를 식별할 수 있도록 X-Forwarded-For 헤더 파싱 로직을 구현한다. slowapi의 기본 `get_remote_address()`가 프록시 IP만 반환하는 문제를 해결한다.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/middleware/rate_limit.py` | `_get_client_ip()` 함수 추가, `get_key_func()` 수정 |

---

## 3. 작업 체크리스트

- [x] `_get_client_ip(request)` 함수 구현
- [x] X-Forwarded-For 헤더 파싱 (첫 번째 IP 추출)
- [x] X-Forwarded-For 없을 시 `request.client.host` 폴백
- [x] `get_key_func()`에서 인증 사용자 → user ID, 비인증 → IP 분기

---

## 4. 참조

- Phase 12 Master Plan §12-3-2
