# Phase 9-1: Web 사용자 체크리스트 (브라우저 기능·보안 시나리오)

**작성일**: 2026-02-03
**대상**: Phase 9-1 보안 강화
**용도**: **USER가 Web 브라우저에서 실행**하는 보안 관련 기능 점검 — 인증, CORS, Rate Limiting 동작 확인

**API 검증**(Task report 기반, 샘플 데이터·2차 점검 기록)은 → [phase-9-1-api-verification-checklist.md](../../../phases/phase-9-1/phase-9-1-api-verification-checklist.md)

**테스트 전 환경 구축** (백엔드 기동, Base URL, Docker/Playwright/MCP 브라우저) → [frontend-webtest-setup-guide.md](frontend-webtest-setup-guide.md)

---

## 사용자 화면 링크 (Web UI)

백엔드 기동 후 브라우저에서 아래 주소로 접속합니다. (기본: `http://localhost:8000`)

| Task         | 화면               | URL                             |
| ------------ | ------------------ | ------------------------------- |
| **공통**     | 대시보드           | http://localhost:8000/dashboard |
| **공통**     | 헬스 체크          | http://localhost:8000/health    |
| **9-1-1**    | API 문서 (Swagger) | http://localhost:8000/docs      |
| **9-1-1**    | API 문서 (ReDoc)   | http://localhost:8000/redoc     |
| **테스트용** | 검색               | http://localhost:8000/search    |
| **테스트용** | AI 질의            | http://localhost:8000/ask       |
| **테스트용** | Reasoning Lab      | http://localhost:8000/reason    |

---

## 환경 설정 시나리오

### 개발 환경 (.env 설정)

```bash
ENVIRONMENT=development
AUTH_ENABLED=false
RATE_LIMIT_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 프로덕션 환경 (.env 설정)

```bash
ENVIRONMENT=production
AUTH_ENABLED=true
JWT_SECRET_KEY=your_secure_secret_key_here
API_SECRET_KEY=your_api_key_here
RATE_LIMIT_ENABLED=true
CORS_ORIGINS=https://your-domain.com
```

---

## 메뉴(라우터)별 시나리오 체크리스트

USER가 브라우저에서 **메뉴 진입 → 화면 동작 → 결과 확인** 순으로 점검합니다.

---

### 1. 대시보드 및 공개 페이지 (/dashboard)

| #    | 시나리오                                     | 결과 | 비고 |
| ---- | -------------------------------------------- | ---- | ---- |
| W1.1 | 대시보드 접속 → 페이지 정상 로드 (인증 없이) | [ ]  |      |
| W1.2 | /health 접속 → {"status": "ok"} 응답         | [ ]  |      |
| W1.3 | /docs 접속 → Swagger UI 표시 (인증 없이)     | [ ]  |      |
| W1.4 | /redoc 접속 → ReDoc UI 표시 (인증 없이)      | [ ]  |      |

---

### 2. 인증 관련 동작 (AUTH_ENABLED=true 시) — Task 9-1-1

| #    | 시나리오                                                  | 결과 | 비고 |
| ---- | --------------------------------------------------------- | ---- | ---- |
| W2.1 | 인증 없이 보호된 API 호출 → 401 응답 확인 (브라우저 콘솔) | [ ]  |      |
| W2.2 | /docs에서 "Authorize" 버튼 → API Key 입력 → 인증 적용     | [ ]  |      |
| W2.3 | 인증 후 API 호출 → 정상 응답                              | [ ]  |      |
| W2.4 | 잘못된 토큰으로 API 호출 → 401 응답                       | [ ]  |      |

---

### 3. 인증 관련 동작 (AUTH_ENABLED=false 시) — Task 9-1-1

| #    | 시나리오                                        | 결과 | 비고 |
| ---- | ----------------------------------------------- | ---- | ---- |
| W3.1 | 인증 없이 모든 API 정상 동작                    | [ ]  |      |
| W3.2 | /api/auth/status 호출 → auth_enabled=false 확인 | [ ]  |      |
| W3.3 | Ask 페이지에서 질문 전송 → 정상 응답            | [ ]  |      |
| W3.4 | Reason 페이지에서 추론 실행 → 정상 응답         | [ ]  |      |

---

### 4. CORS 동작 — Task 9-1-3

| #    | 시나리오                                                        | 결과 | 비고 |
| ---- | --------------------------------------------------------------- | ---- | ---- |
| W4.1 | 브라우저 콘솔에서 fetch API 호출 → CORS 에러 없음 (허용 오리진) | [ ]  |      |
| W4.2 | 다른 포트(예: 3001)에서 API 호출 시 CORS 에러 (프로덕션)        | [ ]  |      |
| W4.3 | 개발 환경에서 모든 오리진 허용 확인                             | [ ]  |      |

**브라우저 콘솔 테스트 코드:**

```javascript
// 허용된 오리진에서 테스트
fetch("http://localhost:8000/health")
  .then((r) => r.json())
  .then(console.log)
  .catch(console.error);
```

---

### 5. Rate Limiting 동작 — Task 9-1-4

| #    | 시나리오                                                      | 결과 | 비고 |
| ---- | ------------------------------------------------------------- | ---- | ---- |
| W5.1 | 정상적인 API 호출 → 응답 정상                                 | [ ]  |      |
| W5.2 | 빠른 연속 클릭 (60회 이상) → 429 응답 (브라우저 콘솔)         | [ ]  |      |
| W5.3 | 429 응답 후 1분 대기 → 다시 정상 응답                         | [ ]  |      |
| W5.4 | 응답 헤더에 X-RateLimit-\* 포함 확인 (개발자 도구 Network 탭) | [ ]  |      |

**Rate Limit 테스트 코드 (브라우저 콘솔):**

```javascript
// 65번 연속 요청 테스트
for (let i = 0; i < 65; i++) {
  fetch("http://localhost:8000/health")
    .then((r) => console.log(`${i + 1}: ${r.status}`))
    .catch((e) => console.error(`${i + 1}: Error`));
}
```

---

### 6. 검색 페이지 (/search) — 보안 통합 테스트

| #    | 시나리오                                               | 결과 | 비고 |
| ---- | ------------------------------------------------------ | ---- | ---- |
| W6.1 | 검색 페이지 접속 → 정상 로드                           | [ ]  |      |
| W6.2 | 검색어 입력 후 검색 → 결과 표시 (인증/Rate Limit 통과) | [ ]  |      |
| W6.3 | 빠른 연속 검색 시 Rate Limit 동작 확인                 | [ ]  |      |

---

### 7. AI 질의 페이지 (/ask) — 보안 통합 테스트

| #    | 시나리오                                             | 결과 | 비고 |
| ---- | ---------------------------------------------------- | ---- | ---- |
| W7.1 | Ask 페이지 접속 → 정상 로드                          | [ ]  |      |
| W7.2 | 질문 입력 후 전송 → 답변 표시 (인증/Rate Limit 통과) | [ ]  |      |
| W7.3 | LLM API Rate Limit (10/분) 동작 확인                 | [ ]  |      |

---

### 8. Reasoning Lab (/reason) — 보안 통합 테스트

| #    | 시나리오                                     | 결과 | 비고 |
| ---- | -------------------------------------------- | ---- | ---- |
| W8.1 | Reason 페이지 접속 → 정상 로드               | [ ]  |      |
| W8.2 | 추론 실행 → 결과 표시 (인증/Rate Limit 통과) | [ ]  |      |
| W8.3 | LLM API Rate Limit 동작 확인                 | [ ]  |      |

---

### 9. Swagger UI (/docs) — 인증 테스트

| #    | 시나리오                                     | 결과 | 비고 |
| ---- | -------------------------------------------- | ---- | ---- |
| W9.1 | /docs 접속 → Swagger UI 표시                 | [ ]  |      |
| W9.2 | "Authorize" 버튼 클릭 → 인증 팝업 표시       | [ ]  |      |
| W9.3 | Bearer Token 입력 → "Authorize" 클릭         | [ ]  |      |
| W9.4 | 인증 후 "Try it out" → API 테스트 정상 동작  | [ ]  |      |
| W9.5 | Auth API (/api/auth/\*) 엔드포인트 표시 확인 | [ ]  |      |

---

## 기능 Flow 요약 (브라우저)

| Flow                  | 경로 순서                     | 확인 항목           |
| --------------------- | ----------------------------- | ------------------- |
| **공개 접근**         | /dashboard, /health, /docs    | 인증 없이 접근 가능 |
| **인증 흐름**         | /docs → Authorize → API 호출  | 토큰 발급 및 적용   |
| **CORS 테스트**       | 브라우저 콘솔 fetch           | 허용/차단 오리진    |
| **Rate Limit 테스트** | 연속 요청 → 429 → 대기 → 정상 | 제한 및 리셋        |
| **통합 테스트**       | /search, /ask, /reason        | 모든 보안 기능 통과 |

---

## Web 사용자 점검 결과 요약

| 메뉴(라우터)              | 총 항목 | 성공 | 실패 | 비고 |
| ------------------------- | ------- | ---- | ---- | ---- |
| 대시보드/공개 페이지      | 4       |      |      |      |
| 인증 (AUTH_ENABLED=true)  | 4       |      |      |      |
| 인증 (AUTH_ENABLED=false) | 4       |      |      |      |
| CORS                      | 3       |      |      |      |
| Rate Limiting             | 4       |      |      |      |
| 검색 페이지               | 3       |      |      |      |
| Ask 페이지                | 3       |      |      |      |
| Reason 페이지             | 3       |      |      |      |
| Swagger UI                | 5       |      |      |      |
| **합계**                  | 33      |      |      |      |

**Web 점검 수행일**: ******\_\_\_******
**점검 수행자**: ******\_\_\_******
**브라우저/환경**: ******\_\_\_******

---

## 문제 해결 가이드

### CORS 에러 발생 시

```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000'
has been blocked by CORS policy
```

**해결:**

1. CORS_ORIGINS 환경변수에 해당 오리진 추가
2. 개발 환경에서는 ENVIRONMENT=development 설정

### 401 Unauthorized 발생 시

**해결:**

1. AUTH_ENABLED=false로 인증 비활성화 (개발용)
2. 또는 /api/auth/token으로 토큰 발급 후 사용

### 429 Too Many Requests 발생 시

**해결:**

1. 1분 대기 후 재시도
2. 또는 RATE_LIMIT_ENABLED=false로 비활성화 (개발용)

---

## 환경별 기대 동작 요약

| 기능       | 개발 환경                 | 프로덕션 환경                       |
| ---------- | ------------------------- | ----------------------------------- |
| 인증       | 비활성화 (모든 요청 허용) | 활성화 (토큰 필수)                  |
| CORS       | 모든 오리진 허용          | 지정 오리진만 허용                  |
| Rate Limit | 활성화                    | 활성화                              |
| Swagger UI | 접근 가능                 | 접근 가능 (인증 필요 API는 인증 후) |
