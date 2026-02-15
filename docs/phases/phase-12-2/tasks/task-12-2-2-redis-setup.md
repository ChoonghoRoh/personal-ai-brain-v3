# Task 12-2-2: [INFRA] Redis 도입 (docker-compose)

**우선순위**: 12-2 내 1순위
**예상 작업량**: 소 (docker-compose + .env 수정만, 코드 변경 불필요)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-2-todo-list.md`
**Plan**: `phase-12-2-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

Redis 7-alpine을 docker-compose에 추가하여 향후 캐싱/세션/Rate Limit 백엔드로 활용할 수 있는 인프라를 구축한다. 기존 rate_limit.py가 이미 REDIS_URL을 지원하므로 코드 변경 불필요.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `docker-compose.yml` | redis 서비스 추가 (7-alpine, AOF, healthcheck) |
| `docker-compose.yml` | backend depends_on에 redis 추가 |
| `docker-compose.yml` | backend environment에 REDIS_URL 추가 |
| `.env.example` | REDIS_URL 기본값 설정 |

---

## 3. 작업 체크리스트

- [x] docker-compose.yml에 Redis 7-alpine 서비스 추가
- [x] 이미지: `redis:7-alpine`, 포트: `6379:6379`
- [x] 커맨드: `redis-server --appendonly yes`
- [x] 헬스체크: `redis-cli ping`
- [x] 네트워크: `pab-network`
- [x] backend depends_on에 redis 추가 (condition: service_healthy)
- [x] `.env.example` REDIS_URL 설정

---

## 4. 참조

- Phase 12 Master Plan §12-2-2
- 기존 rate_limit.py REDIS_URL 지원 확인 완료
