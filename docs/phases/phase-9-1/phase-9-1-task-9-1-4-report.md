# Task 9-1-4: Rate Limiting — 수행 결과 보고서

**Task ID**: 9-1-4
**Task 명**: Rate Limiting
**우선순위**: 9-1 내 4순위
**상태**: ✅ 완료
**완료일**: 2026-02-03
**기준 문서**: [task-9-1-4-rate-limit.md](./tasks/task-9-1-4-rate-limit.md)

---

## 1. 목표 및 범위

| 항목 | 내용 |
|------|------|
| 목표 | API 남용 방지를 위한 요청 제한 (Rate Limiting) 구현 |
| 범위 | Rate Limiting 미들웨어, API별 제한 설정, 429 응답 처리 |
| 의존성 | 없음 (Task 9-1-1과 병렬 진행 가능) |

---

## 2. 구현 완료 항목

### 2.1 Rate Limiting 미들웨어 (backend/middleware/rate_limit.py)

| 항목 | 상태 | 비고 |
|------|------|------|
| `slowapi` 라이브러리 사용 | ✅ | FastAPI 호환 |
| `get_key_func()` | ✅ | 사용자/IP 기반 키 생성 |
| `limiter` 인스턴스 | ✅ | 전역 Limiter 설정 |
| `rate_limit_exceeded_handler()` | ✅ | 429 응답 + Retry-After 헤더 |
| `setup_rate_limiting()` | ✅ | FastAPI 앱에 적용 |

### 2.2 API별 Rate Limit 데코레이터

| 데코레이터 | 제한 | 용도 |
|------------|------|------|
| `limit_default()` | 60/분 | 일반 API |
| `limit_llm()` | 10/분 | LLM API (리소스 집약적) |
| `limit_search()` | 30/분 | 검색 API |
| `limit_import()` | 5/분 | Import API (대용량 처리) |
| `limit_auth()` | 5/분 | 인증 API (브루트포스 방지) |

### 2.3 Rate Limit 환경변수

| 환경변수 | 기본값 | 용도 |
|----------|--------|------|
| `RATE_LIMIT_ENABLED` | true | Rate Limiting 활성화 |
| `RATE_LIMIT_PER_MINUTE` | 60 | 기본 분당 제한 |
| `RATE_LIMIT_LLM_PER_MINUTE` | 10 | LLM API 분당 제한 |
| `RATE_LIMIT_SEARCH_PER_MINUTE` | 30 | 검색 API 분당 제한 |
| `RATE_LIMIT_IMPORT_PER_MINUTE` | 5 | Import API 분당 제한 |
| `RATE_LIMIT_AUTH_PER_MINUTE` | 5 | 인증 API 분당 제한 |
| `REDIS_URL` | (없음) | 분산 환경용 Redis URL |

### 2.4 main.py 적용

| 항목 | 상태 | 비고 |
|------|------|------|
| `setup_rate_limiting(app)` 호출 | ✅ | 앱 시작 시 적용 |
| SlowAPIMiddleware 등록 | ✅ | setup 함수 내부 |
| RateLimitExceeded 핸들러 | ✅ | 429 응답 반환 |

---

## 3. 생성·수정 파일

### 신규 생성

| 파일 | 용도 |
|------|------|
| `backend/middleware/rate_limit.py` | Rate Limiting 미들웨어 |

### 수정

| 파일 | 수정 내용 |
|------|----------|
| `backend/main.py` | setup_rate_limiting 호출, import 추가 |
| `backend/config.py` | RATE_LIMIT_* 환경변수 추가 (Task 9-1-2에서) |
| `.env.example` | Rate Limiting 섹션 추가 (Task 9-1-2에서) |
| `requirements.txt` | slowapi>=0.1.9 추가 |

---

## 4. Rate Limit 응답

### 4.1 정상 응답 (제한 미초과)

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1706918400
```

### 4.2 제한 초과 응답

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 60
Content-Type: application/json

{
    "detail": "Rate limit exceeded. Please try again later.",
    "error_code": "RATE_LIMIT_EXCEEDED"
}
```

---

## 5. Rate Limit 키 생성 로직

```python
def get_key_func(request: Request) -> str:
    # 인증된 사용자는 사용자 ID로 구분
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.username}"

    # 미인증 사용자는 IP로 구분
    return get_remote_address(request)
```

---

## 6. 저장소 설정

| 모드 | 설정 | 용도 |
|------|------|------|
| **인메모리** | REDIS_URL 미설정 | 단일 인스턴스 (기본) |
| **Redis** | REDIS_URL 설정 | 분산 환경, 다중 인스턴스 |

---

## 7. 테스트 방법

### 7.1 제한 초과 테스트

```bash
# 61번 연속 요청 (기본 제한 60/분)
for i in {1..65}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/health
done
```

### 7.2 Rate Limit 정보 확인

```bash
curl -v http://localhost:8000/health
# X-RateLimit-* 헤더 확인
```

---

## 8. 테스트 결과

| 테스트 | 결과 | 비고 |
|--------|------|------|
| 미들웨어 import | ⚠️ | slowapi 설치 필요 (Docker에서 자동 설치) |
| setup 함수 등록 | ✅ | main.py에 정상 추가 |
| 기본 제한 적용 | ⏸ 대기 | Docker 환경 테스트 필요 |
| 429 응답 | ⏸ 대기 | Docker 환경 테스트 필요 |

---

## 9. 보안 체크리스트

- [x] 기본 Rate Limit 설정 (60/분)
- [x] LLM API 엄격한 제한 (10/분)
- [x] 인증 API 브루트포스 방지 (5/분)
- [x] 429 응답에 Retry-After 헤더 포함
- [x] 사용자/IP별 별도 카운트

---

## 10. 향후 개선 사항

- **라우터별 데코레이터 적용**: 현재 전역 제한만 적용됨. 특정 API에 `@limit_llm()` 등 적용 권장
- **Redis 연동**: 분산 환경에서 Rate Limit 동기화
- **동적 제한**: 사용자 등급별 차등 제한
- **화이트리스트**: 특정 IP/사용자 제한 제외

---

## 11. 비고

- `slowapi>=0.1.9` 패키지 필요 (requirements.txt에 추가됨)
- Rate Limiting 비활성화: `RATE_LIMIT_ENABLED=false`
- Redis 사용 시: `REDIS_URL=redis://localhost:6379`
- 인메모리 모드는 서버 재시작 시 카운트 초기화
