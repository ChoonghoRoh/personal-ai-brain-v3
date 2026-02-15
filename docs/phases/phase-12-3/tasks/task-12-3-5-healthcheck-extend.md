# Task 12-3-5: [BE] 헬스체크 확장 (/health/live, /health/ready)

**우선순위**: 12-3 내 2순위
**예상 작업량**: 소 (main.py + docker-compose.yml 수정)
**의존성**: 12-2-2 (Redis 도입)
**상태**: ✅ 완료

**기반 문서**: `phase-12-3-todo-list.md`
**Plan**: `phase-12-3-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

Kubernetes-style liveness/readiness 프로브 패턴을 적용한다. `/health/live`(프로세스 생존)와 `/health/ready`(의존성 연결 상태)를 분리하여 세밀한 헬스 모니터링을 지원한다.

---

## 2. 파일 변경 계획

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/main.py` | `/health/live`, `/health/ready` 엔드포인트 추가 |
| `docker-compose.yml` | backend healthcheck URL을 `/health/live`로 변경 |

---

## 3. 작업 체크리스트

- [x] `/health/live` 엔드포인트 추가 (단순 200 OK)
- [x] `/health/ready` 엔드포인트 추가 (PG + Qdrant 연결 검사)
- [x] 기존 `/health` 유지 (하위 호환)
- [x] docker-compose.yml backend healthcheck URL → `/health/live`

---

## 4. 참조

- Phase 12 Master Plan §12-3-5
- Kubernetes liveness/readiness probe 패턴
