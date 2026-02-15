# Phase 12-2 Todo List — P1 계획적 개선

**Phase**: 12-2
**기준 문서**: [Phase 12-2 Plan](phase-12-2-plan.md)
**범위 조정**: 12-2-1 (API 버전 관리) Phase 13으로 연기

---

## 전체 진행률

```
Phase 12-2: ░░░░░░░░░░░░░░░░░░░░ 0%

├── 12-2-1 [FS] API 버전 관리        ➡️ Phase 13 연기
├── 12-2-2 [INFRA] Redis 도입        ⏳ 대기   ░░░░░ 0%
├── 12-2-3 [DB] GIN 인덱스           ⏳ 대기   ░░░░░ 0%
├── 12-2-4 [BE] 에러 표준화          ⏳ 대기   ░░░░░ 0%
└── 12-2-5 [BE] 보상 트랜잭션        ⏳ 대기   ░░░░░ 0%
```

---

## Task 12-2-1 [FS] API 버전 관리 — ➡️ Phase 13 연기

**사유**: 82+ 파일 영향, 단일 Task 부적절. Phase 13 독립 Phase로 분리.

---

## Task 12-2-2 [INFRA] Redis 도입

- [ ] docker-compose.yml에 Redis 7-alpine 서비스 추가
  - [ ] 이미지: `redis:7-alpine`
  - [ ] 포트: `6379:6379`
  - [ ] 커맨드: `redis-server --appendonly yes`
  - [ ] 헬스체크: `redis-cli ping`
  - [ ] 네트워크: `pab-network`
- [ ] docker-compose.yml backend depends_on에 redis 추가
- [ ] docker-compose.yml backend environment에 `REDIS_URL` 추가
- [ ] .env.example REDIS_URL 주석 해제 + 기본값 설정

---

## Task 12-2-3 [DB] PostgreSQL GIN 인덱스 추가

- [ ] `scripts/migrations/` 디렉토리 생성
- [ ] `scripts/migrations/001_add_gin_indexes.sql` 작성
  - [ ] `knowledge_chunks.content` GIN 인덱스 (to_tsvector simple)
  - [ ] `conversations.question` GIN 인덱스 (to_tsvector simple)
  - [ ] `conversations.answer` GIN 인덱스 (to_tsvector simple)
  - [ ] `memories.content` GIN 인덱스 (to_tsvector simple)
  - [ ] CONCURRENTLY 옵션 사용
  - [ ] IF NOT EXISTS 방어 코드
- [ ] `scripts/migrations/README.md` 마이그레이션 실행 가이드 작성

---

## Task 12-2-4 [BE] API 에러 응답 형식 표준화

- [ ] `backend/middleware/request_id.py` 생성
  - [ ] UUID v4 기반 Request ID 생성
  - [ ] 클라이언트 `X-Request-ID` 헤더 우선 사용
  - [ ] 응답 헤더에 `X-Request-ID` 포함
  - [ ] `request.state.request_id`에 저장
- [ ] `backend/middleware/error_handler.py` 생성
  - [ ] 표준 에러 응답 형식 정의 (ErrorResponse)
  - [ ] HTTPException 전역 핸들러
  - [ ] RequestValidationError 핸들러
  - [ ] General Exception 핸들러 (500)
  - [ ] request_id, timestamp, path 자동 포함
- [ ] `backend/main.py` 수정
  - [ ] RequestIDMiddleware 등록
  - [ ] 에러 핸들러 등록 함수 호출
  - [ ] 기존 RateLimitExceeded 핸들러 유지 (충돌 방지)

---

## Task 12-2-5 [BE] PG-Qdrant 보상 트랜잭션 도입

- [ ] `backend/services/knowledge/transaction_manager.py` 생성
  - [ ] CompensatingTransaction 클래스
  - [ ] execute: 순차 실행 + 실패 시 보상 액션 역순 실행
  - [ ] 로깅: 각 단계별 성공/실패 로그
- [ ] 기존 임베딩 플로우에 보상 트랜잭션 적용
  - [ ] Qdrant upsert 성공 → PG qdrant_point_id 업데이트
  - [ ] PG 업데이트 실패 → Qdrant 포인트 삭제 (보상)
- [ ] 에러 시 표준 에러 응답 (12-2-4 연계)

---

## 검증 체크리스트 (G3/G4)

- [ ] **12-2-2**: docker compose config 유효성 확인
- [ ] **12-2-3**: SQL 구문 유효성, CONCURRENTLY 사용 확인
- [ ] **12-2-4**: 에러 응답 형식 일관성, Request ID 포함 여부
- [ ] **12-2-5**: 보상 로직 정확성, 롤백 시나리오 커버
- [ ] **회귀**: 기존 API 정상 동작 (특히 Rate Limit 핸들러)
