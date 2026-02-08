# Phase 9-1: API 검증 체크리스트

**작성일**: 2026-02-03
**대상**: Phase 9-1 보안 강화 (Task 9-1-2, 9-1-1, 9-1-3, 9-1-4)
**용도**: Task별 **API 검증** 2차 점검 — Task report 기반, 샘플 데이터 지정·점검 기록

**Web 브라우저 기능 점검**(기능 flow, 메뉴/라우터별 시나리오)은 별도 문서 → [phase-9-1-web-user-checklist.md](phase-9-1-web-user-checklist.md)

---

## 검증 절차

| 단계 | 내용 |
|------|------|
| 1차 | Task별 수행 결과 report 확인 ([phase-9-1-task-9-1-X-report.md](phase-9-1-task-9-1-1-report.md) 등) |
| 2차 | **API 검증**: report 기준으로 샘플 데이터를 지정하고 Postman/curl 등으로 API 호출 후 점검 기록 |
| 기록 | 각 Task별 "샘플 데이터(예)", "점검 기록" 란에 실제 사용한 값·결과 요약 기입 |

**전제 조건**: 백엔드 서버 기동, python-jose·slowapi 패키지 설치됨.

---

## Postman 기본 설정 (API 단독 조회)

| 항목 | 값 |
|------|---|
| **Base URL** | `http://localhost:8000` |
| **인증 (JWT)** | `Authorization: Bearer <access_token>` |
| **인증 (API Key)** | `X-API-Key: <api_key>` |
| **공통 헤더** | `Content-Type: application/json` (POST/PUT 시) |

---

## 1. Task 9-1-2: 환경변수 비밀번호 관리 — API 검증

**참조 report**: [phase-9-1-task-9-1-2-report.md](phase-9-1-task-9-1-2-report.md)

### 1.1 환경변수 적용 확인

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 1.1.1 | 서버 시작 시 config.py 로드 | docker-compose up -d | [ ] | |
| 1.1.2 | .env 파일 없이 기본값 동작 | .env 삭제 후 서버 시작 | [ ] | |
| 1.1.3 | 환경변수 오버라이드 | POSTGRES_PASSWORD=test123 설정 후 시작 | [ ] | |
| 1.1.4 | 프로덕션 환경 경고 로그 | ENVIRONMENT=production, 기본 비밀번호 사용 | [ ] | |

### 1.2 Database 연결 확인

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 1.2.1 | GET /health | - | [ ] | 200 OK 응답 |
| 1.2.2 | 환경변수 기반 DB 연결 | 청크/문서 API 호출 | [ ] | |

---

## 2. Task 9-1-1: API 인증 시스템 — API 검증

**참조 report**: [phase-9-1-task-9-1-1-report.md](phase-9-1-task-9-1-1-report.md)

### 2.1 인증 상태 API

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 2.1.1 | GET /api/auth/status | - | [ ] | auth_enabled 값 확인 |
| 2.1.2 | GET /api/auth/me (미인증) | 헤더 없음 | [ ] | authenticated=false |
| 2.1.3 | GET /api/auth/me (JWT 인증) | Authorization: Bearer <token> | [ ] | authenticated=true, auth_type=jwt |
| 2.1.4 | GET /api/auth/me (API Key 인증) | X-API-Key: <api_key> | [ ] | authenticated=true, auth_type=api_key |

### 2.2 토큰 발급 API

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 2.2.1 | POST /api/auth/token (성공) | {"api_key": "valid_key"} | [ ] | 200, access_token 반환 |
| 2.2.2 | POST /api/auth/token (실패) | {"api_key": "wrong_key"} | [ ] | 401 Unauthorized |
| 2.2.3 | POST /api/auth/token (API Key 미설정) | API_SECRET_KEY 미설정 시 | [ ] | 503 Service Unavailable |

### 2.3 로그인/로그아웃 API

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 2.3.1 | POST /api/auth/login | {"username": "test", "password": "test"} | [ ] | 501 Not Implemented |
| 2.3.2 | POST /api/auth/logout | Authorization: Bearer <token> | [ ] | 200, 로그아웃 메시지 |

### 2.4 인증 필수 엔드포인트 (AUTH_ENABLED=true 시)

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 2.4.1 | 보호된 API (미인증) | POST /api/ask (헤더 없음) | [ ] | 401 Unauthorized |
| 2.4.2 | 보호된 API (인증) | POST /api/ask (Bearer token) | [ ] | 200 또는 정상 응답 |
| 2.4.3 | 인증 제외 경로 | GET /health (헤더 없음) | [ ] | 200 OK |

### 2.5 JWT 토큰 검증

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 2.5.1 | 유효한 토큰 | 정상 발급 토큰 | [ ] | 인증 성공 |
| 2.5.2 | 만료된 토큰 | JWT_EXPIRE_MINUTES=1 후 2분 대기 | [ ] | 401 Unauthorized |
| 2.5.3 | 잘못된 서명 | 임의 조작 토큰 | [ ] | 401 Unauthorized |
| 2.5.4 | 형식 오류 | "Bearer invalid_token" | [ ] | 401 Unauthorized |

---

## 3. Task 9-1-3: CORS 설정 — API 검증

**참조 report**: [phase-9-1-task-9-1-3-report.md](phase-9-1-task-9-1-3-report.md)

### 3.1 프리플라이트 요청 (OPTIONS)

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 3.1.1 | OPTIONS /api/ask (허용 오리진) | Origin: http://localhost:3000 | [ ] | 200, CORS 헤더 포함 |
| 3.1.2 | OPTIONS /api/ask (미허용 오리진, 프로덕션) | Origin: http://evil.com | [ ] | CORS 헤더 없음 |

### 3.2 CORS 응답 헤더

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 3.2.1 | Access-Control-Allow-Origin | Origin: http://localhost:3000 | [ ] | 헤더 값 확인 |
| 3.2.2 | Access-Control-Allow-Credentials | - | [ ] | true (프로덕션) / 미포함 (개발) |
| 3.2.3 | Access-Control-Expose-Headers | - | [ ] | X-Request-ID, X-RateLimit-* |

### 3.3 환경별 CORS 동작

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 3.3.1 | 개발 환경 (ENVIRONMENT=development) | 임의 Origin | [ ] | Allow-Origin: * |
| 3.3.2 | 프로덕션 환경 (ENVIRONMENT=production) | CORS_ORIGINS에 없는 Origin | [ ] | CORS 에러 |

---

## 4. Task 9-1-4: Rate Limiting — API 검증

**참조 report**: [phase-9-1-task-9-1-4-report.md](phase-9-1-task-9-1-4-report.md)

### 4.1 Rate Limit 헤더

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 4.1.1 | X-RateLimit-Limit | GET /health | [ ] | 헤더 값 확인 (60) |
| 4.1.2 | X-RateLimit-Remaining | 여러 번 요청 후 | [ ] | 감소 확인 |
| 4.1.3 | X-RateLimit-Reset | - | [ ] | 리셋 시간 확인 |

### 4.2 Rate Limit 초과

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 4.2.1 | 기본 제한 초과 (60/분) | 65번 연속 요청 | [ ] | 429 Too Many Requests |
| 4.2.2 | Retry-After 헤더 | 429 응답 시 | [ ] | 헤더 값 확인 (60) |
| 4.2.3 | 제한 리셋 후 재요청 | 1분 대기 후 요청 | [ ] | 200 OK |

### 4.3 사용자별 Rate Limit

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 4.3.1 | IP별 별도 카운트 | X-Forwarded-For: 1.1.1.1 vs 2.2.2.2 | [ ] | 각각 별도 카운트 |
| 4.3.2 | 인증 사용자별 카운트 | 다른 사용자 토큰으로 요청 | [ ] | 각각 별도 카운트 |

### 4.4 Rate Limit 비활성화

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 4.4.1 | RATE_LIMIT_ENABLED=false | 환경변수 설정 후 재시작 | [ ] | 제한 없이 요청 가능 |

---

## 5. 통합·회귀 (API)

| # | 항목 | 샘플 데이터(예) | 결과 | 점검 기록 |
|---|------|----------------|------|----------|
| 5.1 | 기존 검색 API 동작 | GET /api/search?q=test | [ ] | 200, 정상 응답 |
| 5.2 | 기존 Ask API 동작 | POST /api/ask (question) | [ ] | 200, 정상 응답 |
| 5.3 | 기존 Reason API 동작 | POST /api/reason (mode, inputs) | [ ] | 200, 정상 응답 |
| 5.4 | 기존 Knowledge API 동작 | GET /api/knowledge/chunks | [ ] | 200, 정상 응답 |
| 5.5 | 인증+CORS+RateLimit 통합 | 모든 미들웨어 적용 상태 | [ ] | 정상 동작 |

---

## 6. API 검증 결과 요약

| Task | 총 항목 | 성공 | 실패 | 비고 |
|------|--------|------|------|------|
| 9-1-2 환경변수 | 6 | | | |
| 9-1-1 인증 | 16 | | | |
| 9-1-3 CORS | 7 | | | |
| 9-1-4 Rate Limit | 10 | | | |
| 통합·회귀 | 5 | | | |
| **합계** | 44 | | | |

**API 검증 수행일**: _______________
**검증 수행자**: _______________
**환경**: localhost:8000, Docker 환경

---

## 7. curl 명령어 예시

### 7.1 인증 토큰 발급

```bash
# API Key로 JWT 토큰 발급
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_api_secret_key"}'
```

### 7.2 인증된 요청

```bash
# JWT Bearer 토큰 사용
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."

# API Key 사용
curl http://localhost:8000/api/auth/me \
  -H "X-API-Key: your_api_secret_key"
```

### 7.3 CORS 프리플라이트

```bash
curl -X OPTIONS http://localhost:8000/api/ask \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v
```

### 7.4 Rate Limit 테스트

```bash
# 65번 연속 요청 (제한 초과 테스트)
for i in {1..65}; do
  echo "Request $i: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)"
done
```
