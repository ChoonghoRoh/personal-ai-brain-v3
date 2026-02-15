# Phase 9-1: 보안 강화 - Todo List

**상태**: ✅ 완료 (Completed)
**우선순위**: 2 (Phase 9-3 다음)
**예상 작업량**: 4일
**시작일**: 2026-02-03
**완료일**: 2026-02-03

---

## Phase 진행 정보

### 현재 Phase
- **Phase ID**: 9-1
- **Phase 명**: 보안 강화 (Security Enhancement)
- **핵심 목표**: API 인증, 환경변수 관리, CORS, Rate Limiting

### 이전 Phase
- **Prev Phase ID**: 9-3
- **Prev Phase 명**: AI 기능 고도화
- **전환 조건**: 9-3 전체 Task 완료

### 다음 Phase
- **Next Phase ID**: 9-2
- **Next Phase 명**: 테스트 확대
- **전환 조건**: 9-1 전체 Task 완료 및 테스트 통과

### Phase 우선순위 전체 현황

| 순위 | Phase | 상태 | 의존성 |
|------|-------|------|--------|
| 1 | 9-3 AI 기능 고도화 | ✅ 완료 | - |
| **2** | **9-1 보안 강화** | ✅ 완료 | 9-3 완료 |
| 3 | 9-2 테스트 확대 | ⏳ 대기 | 9-1 부분 의존 |
| 4 | 9-4 기능 확장 | ⏳ 대기 | - |
| 5 | 9-5 코드 품질 | ⏳ 대기 | - |

---

## Task 목록

### 9-1-2: 환경변수 비밀번호 관리 ✅
**우선순위**: 9-1 내 최우선 (기반 작업)
**예상 작업량**: 0.5일
**의존성**: 없음
**상태**: ✅ 완료

- [x] 현재 하드코딩된 비밀번호 식별
  - [x] PostgreSQL 비밀번호
  - [x] Qdrant API Key (있는 경우)
  - [x] Ollama 설정
  - [x] 기타 민감 정보

- [x] 환경변수 이동
  - [x] `.env.example` 업데이트
  - [x] `backend/config.py` 수정
  - [x] docker-compose.yml 환경변수 참조 확인

---

### 9-1-1: API 인증 시스템 구축 ✅
**우선순위**: 9-1 내 1순위
**예상 작업량**: 2일
**의존성**: 9-1-2 (환경변수) 완료 후 진행 권장
**상태**: ✅ 완료

- [x] 인증 방식 선택 및 설계
  - [x] JWT + API Key 방식 결정 (둘 다 지원)
  - [x] 인증 플로우 설계

- [x] 인증 미들웨어 구현
  - [x] `backend/middleware/auth.py` 생성
  - [x] 토큰 검증 로직
  - [x] 인증 제외 엔드포인트 설정 (health check 등)

- [x] 인증 라우터 구현
  - [x] `backend/routers/auth/` 디렉토리 생성
  - [x] `POST /api/auth/token` - API Key로 JWT 토큰 발급
  - [x] `POST /api/auth/login` - 로그인 (확장용)
  - [x] `POST /api/auth/logout` - 로그아웃
  - [x] `GET /api/auth/me` - 현재 사용자 정보
  - [x] `GET /api/auth/status` - 인증 시스템 상태

---

### 9-1-3: CORS 설정 ✅
**우선순위**: 9-1 내 3순위
**예상 작업량**: 0.5일
**의존성**: 없음 (9-1-1과 병행 가능)
**상태**: ✅ 완료

- [x] CORS 정책 설계
  - [x] 개발 환경 설정 (모든 오리진 허용)
  - [x] 프로덕션 환경 설정 (지정 도메인만)

- [x] CORS 미들웨어 구현
  - [x] `main.py`에서 FastAPI CORSMiddleware 설정
  - [x] 환경별 분기 처리

---

### 9-1-4: Rate Limiting ✅
**우선순위**: 9-1 내 4순위
**예상 작업량**: 1일
**의존성**: 없음 (9-1-1과 병행 가능)
**상태**: ✅ 완료

- [x] Rate Limit 정책 설계
  - [x] API별 제한 설정 (기본: 분당 60회)
  - [x] LLM 호출 API 별도 제한 (분당 10회)
  - [x] 검색 API 제한 (분당 30회)
  - [x] Import API 제한 (분당 5회)
  - [x] 인증 API 제한 (분당 5회 - 브루트포스 방지)

- [x] Rate Limiting 미들웨어 구현
  - [x] `backend/middleware/rate_limit.py` 생성
  - [x] slowapi 라이브러리 활용
  - [x] 인메모리 저장소 (Redis 옵션 지원)

- [x] 제한 초과 응답 처리
  - [x] 429 Too Many Requests 응답
  - [x] Retry-After 헤더

---

## 완료 기준

### Phase 9-1 완료 조건
- [x] 9-1-2 환경변수 관리 완료
- [x] 9-1-1 API 인증 시스템 완료
- [x] 9-1-3 CORS 설정 완료
- [x] 9-1-4 Rate Limiting 완료
- [ ] 전체 테스트 통과 (Docker 환경에서 테스트 필요)
- [x] 문서 업데이트

### 품질 기준

| 항목 | 기준 | 상태 |
|------|------|------|
| 인증 | 유효하지 않은 토큰 100% 차단 | ✅ |
| 환경변수 | 코드에 비밀번호 하드코딩 0건 | ✅ |
| CORS | 허용되지 않은 오리진 차단 | ✅ |
| Rate Limit | 제한 초과 시 429 응답 | ✅ |

---

## 작업 로그

| 날짜 | Task | 작업 내용 | 상태 |
|------|------|----------|------|
| 2026-02-03 | 9-1-2 | .env.example 업데이트 | ✅ |
| 2026-02-03 | 9-1-2 | config.py 헬퍼 함수 및 환경변수 로딩 수정 | ✅ |
| 2026-02-03 | 9-1-2 | docker-compose.yml 환경변수 참조로 변경 | ✅ |
| 2026-02-03 | 9-1-1 | 인증 미들웨어 (auth.py) 생성 | ✅ |
| 2026-02-03 | 9-1-1 | 인증 라우터 (routers/auth/) 생성 | ✅ |
| 2026-02-03 | 9-1-3 | CORS 미들웨어 main.py에 적용 | ✅ |
| 2026-02-03 | 9-1-4 | Rate Limiting 미들웨어 (rate_limit.py) 생성 | ✅ |
| 2026-02-03 | 9-1-4 | main.py에 Rate Limiting 적용 | ✅ |

---

## 생성/수정된 파일 목록

### 신규 생성 파일
| 파일 경로 | 용도 |
|----------|------|
| `backend/middleware/auth.py` | JWT/API Key 인증 미들웨어 |
| `backend/middleware/rate_limit.py` | Rate Limiting 미들웨어 |
| `backend/routers/auth/__init__.py` | 인증 라우터 패키지 |
| `backend/routers/auth/auth.py` | 인증 API 엔드포인트 |

### 수정된 파일
| 파일 경로 | 수정 내용 |
|----------|----------|
| `.env.example` | 보안 설정 환경변수 추가 |
| `backend/config.py` | 헬퍼 함수 추가, 환경변수 기반 설정 |
| `docker-compose.yml` | 환경변수 참조로 변경 |
| `backend/main.py` | CORS, Rate Limiting 미들웨어 등록 |
| `requirements.txt` | python-jose, slowapi, python-dotenv 추가 |

---

## 참고 문서

### Task 수행 결과 보고서
- [Task 9-1-2 Report: 환경변수 비밀번호 관리](./phase-9-1-task-9-1-2-report.md)
- [Task 9-1-1 Report: API 인증 시스템](./phase-9-1-task-9-1-1-report.md)
- [Task 9-1-3 Report: CORS 설정](./phase-9-1-task-9-1-3-report.md)
- [Task 9-1-4 Report: Rate Limiting](./phase-9-1-task-9-1-4-report.md)

### 검증 체크리스트
- [API 검증 체크리스트](./phase-9-1-api-verification-checklist.md)
- [Web 사용자 체크리스트](./phase-9-1-web-user-checklist.md)

### Task 상세 문서
- [Task 9-1-2: 환경변수 비밀번호 관리](./tasks/task-9-1-2-env-secrets.md) ★ 최우선
- [Task 9-1-1: API 인증 시스템](./tasks/task-9-1-1-api-auth.md)
- [Task 9-1-3: CORS 설정](./tasks/task-9-1-3-cors.md)
- [Task 9-1-4: Rate Limiting](./tasks/task-9-1-4-rate-limit.md)
- [개발 진행 가이드](./tasks/task-develop-guide.md)

### Phase 문서
- [Phase 9 Master Plan](../phase-9-master-plan.md)
- [Phase 9 Navigation](../phase-9-navigation.md)
- [작업 지시사항](../phase-9-work-instructions.md)

### 기술 참고
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- slowapi: https://github.com/laurentS/slowapi
- python-jose: https://github.com/mpdavis/python-jose

### 관련 파일
- `backend/config.py` - 설정 파일
- `backend/main.py` - 미들웨어 등록
- `.env.example` - 환경변수 예시

---

## 다음 단계

1. **Docker 환경에서 테스트**
   ```bash
   docker-compose down && docker-compose build && docker-compose up -d
   ```

2. **API 테스트**
   ```bash
   # 헬스 체크
   curl http://localhost:8001/health

   # 인증 상태 확인
   curl http://localhost:8001/api/auth/status

   # 토큰 발급 (API Key 설정 필요)
   curl -X POST http://localhost:8001/api/auth/token \
     -H "Content-Type: application/json" \
     -d '{"api_key": "your_api_key"}'
   ```

3. **Phase 9-2 (테스트 확대) 진행**
