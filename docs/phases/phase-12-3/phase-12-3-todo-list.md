# Phase 12-3 Todo List — P2 조기 대응

**Phase**: 12-3
**기준 문서**: [Phase 12-3 Plan](phase-12-3-plan.md)

---

## 전체 진행률

```
Phase 12-3: ░░░░░░░░░░░░░░░░░░░░ 0%

├── 12-3-1 [FE] XSS 방어            ⏳ 대기   ░░░░░ 0%
├── 12-3-2 [BE] Rate Limit IP       ⏳ 대기   ░░░░░ 0%
├── 12-3-3 [TEST] pytest-cov        ⏳ 대기   ░░░░░ 0%
├── 12-3-4 [BE] memories TTL        ⏳ 대기   ░░░░░ 0%
└── 12-3-5 [BE] 헬스체크 확장       ⏳ 대기   ░░░░░ 0%
```

---

## Task 12-3-2 [BE] Rate Limit X-Forwarded-For

- [ ] `backend/middleware/rate_limit.py` 수정
  - [ ] `get_key_func()`에서 X-Forwarded-For 헤더 파싱
  - [ ] 첫 번째 IP 추출 (신뢰 프록시 환경)
  - [ ] 폴백: X-Forwarded-For 없으면 기존 `get_remote_address()` 사용

---

## Task 12-3-5 [BE] 헬스체크 확장

- [ ] `backend/main.py` 수정
  - [ ] `/health/live` 엔드포인트 추가 (Liveness)
  - [ ] `/health/ready` 엔드포인트 추가 (Readiness: PG + Qdrant + Redis)
  - [ ] 기존 `/health` 유지 (live와 동일)
- [ ] `docker-compose.yml` 수정
  - [ ] backend 서비스에 healthcheck 추가

---

## Task 12-3-4 [BE] memories TTL 스케줄러

- [ ] `backend/config.py` 수정
  - [ ] `MEMORY_CLEANUP_INTERVAL_MINUTES` 환경변수 추가 (기본 60)
  - [ ] `MEMORY_CLEANUP_ENABLED` 환경변수 추가 (기본 true)
- [ ] `backend/services/cognitive/memory_scheduler.py` 신규 생성
  - [ ] asyncio 기반 주기적 클린업 루프
  - [ ] 로깅: 삭제 건수, 실행 시간
  - [ ] graceful shutdown 지원
- [ ] `backend/main.py` 수정
  - [ ] lifespan 이벤트에서 스케줄러 시작/종료

---

## Task 12-3-3 [TEST] pytest-cov CI 통합

- [ ] `requirements.txt` 수정
  - [ ] `pytest-cov>=4.0.0` 추가
- [ ] `pytest.ini` 수정
  - [ ] `addopts`에 `--cov=backend --cov-report=term-missing` 추가
- [ ] `.github/workflows/test.yml` 수정
  - [ ] pytest 명령에 `--cov` 옵션 추가
  - [ ] 커버리지 리포트 생성

---

## Task 12-3-1 [FE] innerHTML XSS 방어

- [ ] `web/public/js/components/utils.js` 수정
  - [ ] `escapeHTML()` 유틸 함수 추가
- [ ] `web/public/js/components/layout-component.js` 수정
  - [ ] 위험한 innerHTML 사용 → 안전한 패턴으로 교체
- [ ] 활성 JS 파일의 innerHTML 사용처 전수 조사 및 필요 시 수정

---

## 검증 체크리스트 (G3/G4)

- [ ] **12-3-2**: X-Forwarded-For 파싱 로직 정확성
- [ ] **12-3-5**: /health/live 200, /health/ready DB 검사 포함
- [ ] **12-3-4**: 스케줄러 시작/종료 로깅 확인
- [ ] **12-3-3**: pytest-cov import 정상, pytest.ini 설정 유효
- [ ] **12-3-1**: innerHTML 사용 최소화, escapeHTML 적용 확인
- [ ] **회귀**: 기존 /health, Rate Limit, 에러 핸들러 정상 동작
