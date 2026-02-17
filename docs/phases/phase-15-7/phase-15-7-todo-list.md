# Phase 15-7 Todo List: 서비스 안정화 및 최종 검증

**Phase**: 15-7
**G1 판정**: PASS
**작성일**: 2026-02-17

---

- [x] Task 15-7-1: [QA] 전체 시스템 부하 테스트 및 메모리 누수 점검 (Owner: backend-dev)
  - aiohttp 기반 비동기 부하 테스트 스크립트 작성
  - 엔드포인트별 동시 요청(10~50 concurrent) 시나리오
  - 목표 RPS 및 P95 지연 시간 검증
  - tracemalloc 기반 메모리 누수 점검 가이드
  - 장시간 반복 요청 후 메모리 사용량 비교

- [x] Task 15-7-2: [INFRA] Docker Production 환경 설정 검증 (Owner: backend-dev)
  - docker-compose.production.yml 오버라이드 파일 작성
  - 환경변수 분리 (DEBUG=false, LOG_LEVEL=warning 등)
  - 리소스 제한 (mem_limit, cpus)
  - 헬스체크 설정 (/api/health 엔드포인트)
  - 볼륨 마운트 및 퍼미션 검증
  - 보안 설정 (read_only, no-new-privileges 등)

- [x] Task 15-7-3: [DOC] 운영 체크리스트 및 검증 리포트 (Owner: backend-dev)
  - 보안 체크리스트 (CORS, HSTS, JWT, Rate Limit)
  - 인프라 체크리스트 (Docker, 환경변수, 볼륨, 백업)
  - 부하 테스트 결과 기록 (RPS, P95, 에러율)
  - 메모리 점검 결과 기록
  - Docker Production 환경 검증 결과
