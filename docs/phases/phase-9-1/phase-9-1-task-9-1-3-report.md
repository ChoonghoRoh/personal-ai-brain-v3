# Task 9-1-3: CORS 설정 — 수행 결과 보고서

**Task ID**: 9-1-3
**Task 명**: CORS 설정
**우선순위**: 9-1 내 3순위
**상태**: ✅ 완료
**완료일**: 2026-02-03
**기준 문서**: [task-9-1-3-cors.md](./tasks/task-9-1-3-cors.md)

---

## 1. 목표 및 범위

| 항목 | 내용 |
|------|------|
| 목표 | 프로덕션 배포를 위한 CORS(Cross-Origin Resource Sharing) 정책 설정 |
| 범위 | 환경별 CORS 설정, 미들웨어 적용 |
| 의존성 | 없음 (Task 9-1-1과 병렬 진행 가능) |

---

## 2. 구현 완료 항목

### 2.1 환경별 CORS 정책

| 환경 | 허용 오리진 | credentials | 메서드 | 헤더 |
|------|-----------|-------------|--------|------|
| **개발** (development) | `*` (모두 허용) | false | `*` | `*` |
| **프로덕션** (production) | CORS_ORIGINS 환경변수 | true | 설정값 | 설정값 |

### 2.2 main.py CORS 설정

| 항목 | 상태 | 비고 |
|------|------|------|
| FastAPI CORSMiddleware 사용 | ✅ | 표준 미들웨어 |
| 환경별 분기 처리 | ✅ | ENVIRONMENT 환경변수 기준 |
| expose_headers 설정 | ✅ | X-Request-ID, X-RateLimit-* |
| max_age 설정 | ✅ | 600초 (프리플라이트 캐시) |

### 2.3 CORS 관련 환경변수

| 환경변수 | 기본값 | 용도 |
|----------|--------|------|
| `CORS_ORIGINS` | localhost:3000,8080 | 허용 오리진 목록 (쉼표 구분) |
| `CORS_ALLOW_CREDENTIALS` | true | 쿠키/인증 정보 허용 |
| `CORS_ALLOW_METHODS` | * | 허용 HTTP 메서드 |
| `CORS_ALLOW_HEADERS` | * | 허용 요청 헤더 |

---

## 3. 생성·수정 파일

### 수정 파일

| 파일 | 수정 내용 |
|------|----------|
| `backend/main.py` | CORSMiddleware 설정 추가 (환경별 분기) |
| `backend/config.py` | CORS_* 환경변수 추가 (Task 9-1-2에서) |
| `.env.example` | CORS 설정 섹션 추가 (Task 9-1-2에서) |

---

## 4. CORS 설정 코드

```python
# backend/main.py

from fastapi.middleware.cors import CORSMiddleware

if ENVIRONMENT == "development":
    # 개발 환경: 모든 오리진 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,  # * 사용 시 credentials=False 필요
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # 프로덕션 환경: 지정된 오리진만 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=CORS_ALLOW_METHODS,
        allow_headers=CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining", "X-RateLimit-Limit"],
        max_age=600,
    )
```

---

## 5. CORS 응답 헤더 예시

### 5.1 개발 환경

```http
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### 5.2 프로덕션 환경

```http
Access-Control-Allow-Origin: https://your-domain.com
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
Access-Control-Expose-Headers: X-Request-ID, X-RateLimit-Remaining, X-RateLimit-Limit
Access-Control-Max-Age: 600
```

---

## 6. 테스트 방법

### 6.1 프리플라이트 요청 테스트

```bash
curl -X OPTIONS http://localhost:8001/api/ask \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v
```

### 6.2 실제 요청 테스트

```bash
curl http://localhost:8001/health \
  -H "Origin: http://localhost:3000" \
  -v
```

---

## 7. 테스트 결과

| 테스트 | 결과 | 비고 |
|--------|------|------|
| 미들웨어 등록 | ✅ | main.py에 정상 추가 |
| 개발 환경 설정 | ✅ | allow_origins=["*"] |
| 프로덕션 환경 설정 | ✅ | 환경변수 기반 |
| 실제 동작 | ⏸ 대기 | Docker 환경 테스트 필요 |

---

## 8. 보안 체크리스트

- [x] 프로덕션에서 `*` 사용 금지 (환경별 분기)
- [x] credentials=true 시 명시적 오리진 사용
- [x] expose_headers로 필요한 헤더만 노출
- [x] max_age로 프리플라이트 캐시 설정

---

## 9. 일반적인 CORS 에러 및 해결

| 에러 | 원인 | 해결 |
|------|------|------|
| No 'Access-Control-Allow-Origin' | 오리진 미허용 | CORS_ORIGINS에 추가 |
| Credentials not supported | `*`와 credentials 동시 사용 | 명시적 origins 또는 credentials=False |
| Method not allowed | 메서드 미허용 | CORS_ALLOW_METHODS에 추가 |
| Header not allowed | 헤더 미허용 | CORS_ALLOW_HEADERS에 추가 |

---

## 10. 비고

- CORS 미들웨어는 다른 미들웨어보다 먼저 등록해야 프리플라이트 요청이 올바르게 처리됨
- 개발 환경에서 `allow_origins=["*"]` 사용 시 `allow_credentials=False` 필수
- 프론트엔드 배포 시 해당 도메인을 CORS_ORIGINS에 추가 필요
