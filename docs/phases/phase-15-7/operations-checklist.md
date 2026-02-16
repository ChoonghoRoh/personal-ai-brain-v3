# Phase 15-7-3: 운영 체크리스트 및 검증 리포트

**작성일**: 2026-02-16

---

## 1. 프로덕션 배포 체크리스트

### 1.1 환경변수 필수 설정

| 환경변수 | 설명 | 필수 |
|---------|------|------|
| `JWT_SECRET_KEY` | JWT 시크릿 (기본값 사용 금지) | **필수** |
| `POSTGRES_PASSWORD` | DB 비밀번호 (기본값 변경) | **필수** |
| `ENVIRONMENT` | `production` 설정 | 필수 |
| `AUTH_ENABLED` | `true` | 필수 |
| `ADMIN_DEFAULT_PASSWORD` | 초기 관리자 비밀번호 변경 | 권장 |
| `REDIS_URL` | Redis 연결 URL | 권장 |
| `API_SECRET_KEY` | API Key (설정 시 API Key 인증 활성) | 선택 |

### 1.2 보안 체크리스트

- [ ] JWT_SECRET_KEY가 기본값이 아닌 강력한 랜덤 문자열로 설정
- [ ] POSTGRES_PASSWORD가 기본값(`brain_password`)이 아닌 값으로 변경
- [ ] ADMIN_DEFAULT_PASSWORD가 변경되었거나, 첫 로그인 후 비밀번호 변경
- [ ] AUTH_ENABLED=true 설정 확인
- [ ] HSTS_ENABLED=true 설정 확인 (HTTPS 운영 시)
- [ ] CORS_ORIGINS에 실제 도메인만 허용
- [ ] Redis AOF 영속성 활성화 (`--appendonly yes`)

### 1.3 인프라 체크리스트

- [ ] Docker 컨테이너 리소스 제한 설정 (docker-compose.production.yml)
- [ ] PostgreSQL 헬스체크 정상 (`pg_isready`)
- [ ] Qdrant 헬스체크 정상 (`wget --spider`)
- [ ] Redis 헬스체크 정상 (`redis-cli ping`)
- [ ] Backend 헬스체크 정상 (`/health/live`)
- [ ] 볼륨 백업 정책 수립 (postgres_data_ver3, redis_data_ver3, qdrant-data-ver3)

---

## 2. 부하 테스트 시나리오 (15-7-1)

### 2.1 테스트 도구

```bash
python scripts/tests/load_test.py --base-url http://localhost:8001 --concurrency 10 --requests 100
```

### 2.2 대상 엔드포인트

| 엔드포인트 | 타입 | 목표 응답 시간 |
|-----------|------|---------------|
| `/health/live` | GET | < 10ms |
| `/api/auth/status` | GET | < 50ms |
| `/api/knowledge/chunks?limit=10` | GET | < 200ms |
| `/api/labels?limit=10` | GET | < 100ms |
| `/api/search?q=test&limit=5` | GET | < 500ms |

### 2.3 합격 기준

| 지표 | 목표 |
|------|------|
| P95 응답 시간 | < 500ms |
| 에러율 | < 1% |
| 동시 접속 | 10 이상 |

---

## 3. 메모리 누수 점검 (15-7-1)

### 3.1 점검 방법

```bash
# Docker 컨테이너 메모리 모니터링
docker stats pab-backend-ver3 --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# 10분간 반복 요청 후 메모리 증가 확인
watch -n 60 'docker stats pab-backend-ver3 --no-stream --format "{{.MemUsage}}"'
```

### 3.2 합격 기준

- 1시간 연속 운영 후 메모리 사용량 증가 < 50MB
- 반복 요청(1000회) 전후 메모리 증가 < 20MB

---

## 4. Docker Production 환경 (15-7-2)

### 4.1 실행 방법

```bash
# Production 오버라이드 적용
docker compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

### 4.2 리소스 제한

| 서비스 | Memory Limit | CPU Limit |
|--------|-------------|-----------|
| postgres | 1GB | 1.0 |
| qdrant | 2GB | 1.0 |
| redis | 512MB | 0.5 |
| backend | 2GB | 2.0 |

### 4.3 검증 항목

- [ ] `docker compose config` 오류 없음
- [ ] 모든 서비스 healthy 상태
- [ ] 환경변수 필수값 미설정 시 시작 실패 확인 (`JWT_SECRET_KEY`, `POSTGRES_PASSWORD`)
- [ ] Backend 시작 시 `validate_production_config()` 경고 확인
