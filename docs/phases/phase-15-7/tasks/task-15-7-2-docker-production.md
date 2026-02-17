# Task 15-7-2: Docker Production 환경 설정 검증

**우선순위**: 15-7 내 2순위 (1순위와 병렬 가능)
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Docker Production 환경에서의 안정적 운영을 위해 docker-compose.production.yml 오버라이드 파일을 작성하고, 환경변수 분리, 리소스 제한, 헬스체크, 보안 설정을 검증한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `docker-compose.production.yml` | 신규 | Production 오버라이드 (리소스 제한, 보안 설정) |

## §3. 작업 체크리스트 (Done Definition)

### Docker 오버라이드 파일
- [x] 기존 docker-compose.yml과 병합 가능한 오버라이드 구조
- [x] `docker compose -f docker-compose.yml -f docker-compose.production.yml up` 실행 확인

### 환경변수 분리
- [x] `DEBUG=false`, `LOG_LEVEL=warning`
- [x] `CORS_ORIGINS` 운영 도메인 한정
- [x] `SECRET_KEY` 외부 주입 (환경변수 또는 Docker Secret)
- [x] `.env.production` 분리 가이드

### 리소스 제한
- [x] `mem_limit`: backend 512MB, postgres 256MB, redis 128MB, qdrant 512MB
- [x] `cpus`: 서비스별 CPU 제한
- [x] `restart: unless-stopped`

### 헬스체크
- [x] backend: `GET /api/health` (interval 30s, timeout 10s, retries 3)
- [x] postgres: `pg_isready` 커맨드
- [x] redis: `redis-cli ping`
- [x] qdrant: HTTP 헬스체크

### 보안 설정
- [x] `read_only: true` (쓰기 필요 경로만 tmpfs)
- [x] `security_opt: [no-new-privileges:true]`
- [x] 불필요 포트 노출 제거 (내부 네트워크만)
- [x] 볼륨 퍼미션 검증

### 통합 검증
- [x] Production 설정으로 전체 서비스 기동 확인
- [x] 헬스체크 통과 확인
- [x] 리소스 제한 내 정상 동작 확인

## §4. 참조

- `docker-compose.yml` -- 기존 개발 환경 설정
- `docs/phases/phase-15-7/operations-checklist.md` -- Docker 섹션
- `.env.example` -- 환경변수 목록
