# Task 12-2-4: [BE] API 에러 응답 형식 표준화

**우선순위**: 12-2 내 3순위
**예상 작업량**: 중 (미들웨어 2파일 신규 + main.py 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-2-todo-list.md`
**Plan**: `phase-12-2-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

모든 API 에러 응답에 Request ID, 타임스탬프, 경로를 포함하는 표준 JSON 형식을 적용한다. UUID v4 기반 Request ID 미들웨어와 전역 에러 핸들러를 구현한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 | 용도 |
|------|------|
| `backend/middleware/request_id.py` | UUID v4 Request ID 미들웨어 |
| `backend/middleware/error_handler.py` | 전역 에러 핸들러 (표준 JSON 형식) |

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/main.py` | RequestIDMiddleware 등록, 에러 핸들러 등록 |

---

## 3. 작업 체크리스트

- [x] `backend/middleware/request_id.py` 생성
  - [x] UUID v4 기반 Request ID 생성
  - [x] 클라이언트 `X-Request-ID` 헤더 우선 사용
  - [x] 응답 헤더에 `X-Request-ID` 포함
  - [x] `request.state.request_id`에 저장
- [x] `backend/middleware/error_handler.py` 생성
  - [x] 표준 에러 응답 형식 (ErrorResponse)
  - [x] HTTPException 전역 핸들러
  - [x] RequestValidationError 핸들러
  - [x] General Exception 핸들러 (500)
  - [x] request_id, timestamp, path 자동 포함
- [x] `backend/main.py` 미들웨어/핸들러 등록
- [x] 기존 RateLimitExceeded 핸들러 충돌 방지

---

## 4. 참조

- Phase 12 Master Plan §12-2-4
