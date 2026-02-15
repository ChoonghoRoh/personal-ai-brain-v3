# Phase 12-3 Plan — P2 조기 대응

**작성일**: 2026-02-15
**Phase**: 12-3
**상태**: PLANNING
**선행 조건**: Phase 12-2 완료 (2026-02-15)
**기준 문서**: [Phase 12 Master Plan](../phase-12-master-plan.md)

---

## 1. Task 목록 (5개)

| 순서 | Task ID | 도메인 | Task 명 | 변경 파일 수 | 비고 |
|------|---------|--------|---------|:----------:|------|
| 1 | 12-3-2 | [BE] | Rate Limit X-Forwarded-For 대응 | 1 | rate_limit.py 수정 |
| 2 | 12-3-5 | [BE] | 헬스체크 확장 (/health → /health/live, /health/ready) | 2 | main.py, docker-compose.yml |
| 3 | 12-3-4 | [BE] | memories TTL 스케줄러 | 3 | main.py, config.py, 신규 scheduler |
| 4 | 12-3-3 | [TEST] | pytest-cov CI 통합 | 3 | requirements.txt, pytest.ini, CI workflow |
| 5 | 12-3-1 | [FE] | innerHTML XSS 방어 | 2~3 | JS 파일 수정 |

### 1.1 작업 순서 근거

```
12-3-2 Rate Limit IP (가장 작은 변경, 1파일)
   │
   ▼
12-3-5 헬스체크 확장 (main.py 수정 포함)
   │
   ▼
12-3-4 memories TTL (main.py 수정 포함, 스케줄러 추가)
   │
   ▼
12-3-3 pytest-cov (설정 파일, CI)
   │
   ▼
12-3-1 XSS 방어 (FE, 사용자 화면 — 마지막 순서 per 사용자 지시)
```

---

## 2. Task별 상세 계획

### 2.1 Task 12-3-2 [BE] Rate Limit X-Forwarded-For 대응

**현재 상태** (Deep Review):
- `get_remote_address(request)` → `request.client.host` 반환 (실제 클라이언트 IP 아님)
- 리버스 프록시 뒤에서 모든 요청이 동일 IP로 인식 → Rate Limit 무력화 가능

**구현**:
- `get_key_func()`에서 `X-Forwarded-For` 헤더 직접 파싱
- 신뢰할 수 있는 프록시 뒤에서만 사용 (첫 번째 IP 추출)

**변경 파일**: `backend/middleware/rate_limit.py`

### 2.2 Task 12-3-5 [BE] 헬스체크 확장

**현재 상태** (Deep Review):
- `/health` → `{"status": "ok"}` (static, 의존성 미검사)
- Backend Docker healthcheck 미설정

**구현**:
- `/health/live` — Liveness probe (앱 프로세스 살아있는지)
- `/health/ready` — Readiness probe (PG, Qdrant, Redis 연결 검사)
- `/health` — 기존 호환 유지 (live와 동일)
- Docker healthcheck 추가

**변경 파일**: `backend/main.py`, `docker-compose.yml`

### 2.3 Task 12-3-4 [BE] memories TTL 스케줄러

**현재 상태** (Deep Review):
- `MemoryService.delete_expired_memories()` 메서드 존재
- `DELETE /api/memory/expired` 수동 엔드포인트 존재
- 자동 스케줄러 없음

**구현**:
- FastAPI lifespan 이벤트에서 백그라운드 태스크로 주기적 실행
- `asyncio` 기반 간단한 스케줄러 (APScheduler 의존성 추가 불필요)
- 설정: `MEMORY_CLEANUP_INTERVAL_MINUTES` 환경변수 (기본 60분)

**변경 파일**: `backend/services/cognitive/memory_scheduler.py` (신규), `backend/main.py`, `backend/config.py`

### 2.4 Task 12-3-3 [TEST] pytest-cov CI 통합

**현재 상태** (Deep Review):
- `tests/` 디렉토리 존재 (13개 파일)
- `pytest.ini` 설정 존재
- CI workflow에서 `pytest-cov` 설치하지만 `--cov` 플래그 미사용
- `requirements.txt`에 `pytest-cov` 미포함

**구현**:
- `requirements.txt`에 `pytest-cov` 추가
- `pytest.ini`에 `--cov=backend --cov-report=term-missing` 추가
- CI workflow에 커버리지 리포트 생성 추가

**변경 파일**: `requirements.txt`, `pytest.ini`, `.github/workflows/test.yml`

### 2.5 Task 12-3-1 [FE] innerHTML XSS 방어

**현재 상태** (Deep Review):
- `layout-component.js`: innerHTML 3건 (line 65, 86, 88)
- knowledge-admin.html.backup: 다수 innerHTML (backup 파일, 비활성)
- DOMPurify, esc() 등 sanitize 함수 미존재

**구현**:
- `web/public/js/components/utils.js`에 `escapeHTML()` 유틸 함수 추가
- `layout-component.js`의 위험한 innerHTML → 안전한 패턴으로 교체
- 활성 JS 파일만 대상 (backup 파일 제외)

**변경 파일**: `web/public/js/components/utils.js` (기존 파일에 추가), `web/public/js/components/layout-component.js`

---

## 3. 품질 게이트

| Gate | 검증 대상 | 판정 기준 |
|------|----------|----------|
| G1 PLAN_REVIEW | 본 문서 | 5개 Task 범위·순서·변경파일 확인 |
| G2 CODE_REVIEW | 12-3-1~5 구현 코드 | 보안·구조·코딩 표준, XSS 방어 정확성 |
| G3 TEST_GATE | 기능 검증 | import 검증, 회귀 테스트 |
| G4 FINAL_GATE | 전체 통합 | 모든 Task DONE, 회귀 없음 |

---

## 4. 리스크

| ID | 리스크 | 대응 |
|----|--------|------|
| R-001 | X-Forwarded-For 스푸핑 | 첫 번째 IP만 사용, 신뢰 프록시 환경만 활성화 |
| R-002 | 헬스체크 DB 쿼리 부하 | SELECT 1 최소 쿼리, 캐시 또는 interval 제한 |
| R-003 | 스케줄러 메모리 누수 | asyncio 기반 단순 루프, 별도 라이브러리 불필요 |
| R-004 | innerHTML 교체 시 UI 깨짐 | 활성 JS만 대상, backup 제외 |
