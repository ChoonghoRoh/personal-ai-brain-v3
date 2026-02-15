# Phase 12-2 Plan — P1 계획적 개선

**작성일**: 2026-02-15
**Phase**: 12-2
**상태**: PLANNING
**선행 조건**: Phase 12-1 완료 (2026-02-15)
**기준 문서**: [Phase 12 Master Plan](../phase-12-master-plan.md)

---

## 1. 범위 조정 (Scope Change)

### 1.1 연기: 12-2-1 [FS] API 버전 관리 → Phase 13

**사유**: Deep Review 결과, `/api/v1/` prefix 도입은 아래 영향도로 인해 단일 Task로 부적절.
- 33개 라우터 (`backend/routers/` 하위)
- 44개 프론트엔드 JS 파일 (106개 fetch() 호출)
- 테스트·문서까지 포함하면 82+ 파일 동시 변경
- **위험**: 1건의 경로 누락으로 전체 프론트엔드 장애 가능

**결정**: Phase 13에서 독립 Phase로 분리 실행 (전용 마이그레이션 가이드 포함).

### 1.2 조정: 12-2-2 Redis 범위 축소

**발견**: `backend/middleware/rate_limit.py`가 이미 `storage_uri = REDIS_URL if REDIS_URL else None`으로 Redis 연동 완비.
- **코드 변경 불필요**: docker-compose.yml에 Redis 서비스 추가 + `.env.example` REDIS_URL 활성화만 필요.

---

## 2. 확정 Task 목록 (4개)

| 순서 | Task ID | 도메인 | Task 명 | 변경 파일 수 | 비고 |
|------|---------|--------|---------|:----------:|------|
| 1 | 12-2-2 | [INFRA] | Redis 도입 (docker-compose) | 2 | docker-compose.yml, .env.example |
| 2 | 12-2-3 | [DB] | PostgreSQL GIN 인덱스 추가 | 2 | SQL 마이그레이션 스크립트, init_db 보강 |
| 3 | 12-2-4 | [BE] | API 에러 응답 형식 표준화 | 3 | main.py, 신규 middleware, 신규 models |
| 4 | 12-2-5 | [BE] | PG-Qdrant 보상 트랜잭션 도입 | 2~3 | 신규 서비스 레이어 |

### 2.1 작업 순서

```
12-2-2 Redis (인프라, 가장 안전)
   │
   ▼
12-2-3 GIN 인덱스 (DB, 독립)
   │
   ▼
12-2-4 에러 표준화 (BE, main.py 수정)
   │
   ▼
12-2-5 보상 트랜잭션 (BE, 서비스 레이어 신규)
```

- 12-2-2 → 12-2-3: 독립이지만 인프라 먼저 안정화 후 DB 작업
- 12-2-4 → 12-2-5: 에러 표준화 후 보상 트랜잭션이 표준 에러 형식 활용

---

## 3. Task별 상세 계획

### 3.1 Task 12-2-2 [INFRA] Redis 도입

**목표**: docker-compose에 Redis 서비스 추가, 환경변수 연동

**변경 파일**:
| 파일 | 변경 내용 |
|------|----------|
| `docker-compose.yml` | Redis 7-alpine 서비스 추가 (6379 포트, AOF, healthcheck) |
| `.env.example` | `REDIS_URL=redis://redis:6379/0` 활성화 |

**코드 변경 없음**: `backend/middleware/rate_limit.py`와 `backend/config.py`는 이미 REDIS_URL 지원 완비.

**docker-compose Redis 설정**:
- 이미지: `redis:7-alpine`
- 포트: `6379:6379`
- 영속성: AOF (appendonly yes)
- 헬스체크: `redis-cli ping`
- 네트워크: `pab-network`
- backend depends_on에 redis 추가

**검증**: `docker compose up redis` → `redis-cli ping` → PONG

### 3.2 Task 12-2-3 [DB] PostgreSQL GIN 인덱스 추가

**목표**: 텍스트 검색 성능 개선을 위한 GIN 인덱스 생성

**대상 컬럼** (Deep Review 결과):
| 테이블 | 컬럼 | 현재 인덱스 | 추가 인덱스 |
|--------|------|:----------:|-----------|
| `knowledge_chunks` | `content` | 없음 | GIN `to_tsvector('simple', content)` |
| `conversations` | `question` | 없음 | GIN `to_tsvector('simple', question)` |
| `conversations` | `answer` | 없음 | GIN `to_tsvector('simple', answer)` |
| `memories` | `content` | 없음 | GIN `to_tsvector('simple', content)` |

**주의사항**:
- `to_tsvector('simple', ...)` 사용 — 한국어 콘텐츠이므로 `english` 대신 `simple` 파서 사용
- `CREATE INDEX CONCURRENTLY` 사용하여 테이블 잠금 방지
- Alembic 미사용 프로젝트 → SQL 마이그레이션 스크립트 `scripts/migrations/` 폴더에 작성

**변경 파일**:
| 파일 | 변경 내용 |
|------|----------|
| `scripts/migrations/001_add_gin_indexes.sql` | 신규: GIN 인덱스 4개 생성 SQL |
| `scripts/migrations/README.md` | 신규: 마이그레이션 실행 가이드 |

**검증**: `EXPLAIN ANALYZE SELECT ... WHERE to_tsvector('simple', content) @@ to_tsquery('simple', 'test')` → Index Scan 확인

### 3.3 Task 12-2-4 [BE] API 에러 응답 형식 표준화

**목표**: 전역 예외 핸들러 + Request ID 미들웨어 도입

**현재 상태** (Deep Review):
- 전역 예외 핸들러: `RateLimitExceeded`만 등록 (rate_limit.py)
- HTTPException: 각 라우터에서 개별 사용, 형식 불통일
- Request ID: 미존재

**표준 에러 응답 형식**:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Document with id 123 not found",
    "status": 404,
    "timestamp": "2026-02-15T18:00:00Z",
    "request_id": "req_abc123",
    "path": "/api/knowledge/chunks/123"
  }
}
```

**변경 파일**:
| 파일 | 변경 내용 |
|------|----------|
| `backend/middleware/request_id.py` | 신규: Request ID 미들웨어 (UUID v4) |
| `backend/middleware/error_handler.py` | 신규: 전역 HTTPException + Exception 핸들러 |
| `backend/main.py` | 미들웨어 등록, 에러 핸들러 등록 |

**구현 상세**:
1. **Request ID 미들웨어**: 모든 요청에 `X-Request-ID` 헤더 부여 (클라이언트 전달 or 자동 생성)
2. **HTTPException 핸들러**: FastAPI HTTPException을 표준 형식으로 변환
3. **General Exception 핸들러**: 미처리 예외를 500 표준 형식으로 변환 (디버그 모드에서만 스택트레이스)

### 3.4 Task 12-2-5 [BE] PG-Qdrant 보상 트랜잭션 도입

**목표**: PostgreSQL-Qdrant 간 데이터 정합성 보장

**현재 상태** (Deep Review):
- 청크 생성 시 PG만 기록, `qdrant_point_id=None`
- Qdrant 기록은 별도 임베딩 프로세스에서 수행
- 청크 PUT/DELETE 엔드포인트 미존재
- **실질적 위험**: 임베딩 후 PG 업데이트(`qdrant_point_id` 설정) 실패 시 데이터 불일치

**구현 범위** (최소 범위):
- 기존 임베딩 프로세스에서 PG-Qdrant 간 보상 패턴 적용
- Qdrant 기록 성공 → PG `qdrant_point_id` 업데이트 실패 시 → Qdrant 포인트 삭제 (롤백)
- 향후 청크 삭제 시에도 동일 패턴 적용 가능하도록 범용 설계

**변경 파일**:
| 파일 | 변경 내용 |
|------|----------|
| `backend/services/knowledge/transaction_manager.py` | 신규: CompensatingTransaction 패턴 |
| `backend/services/knowledge/embedding_service.py` 또는 관련 파일 | 보상 트랜잭션 적용 |

---

## 4. 품질 게이트

| Gate | 검증 대상 | 판정 기준 |
|------|----------|----------|
| G1 PLAN_REVIEW | 본 문서 | 4개 Task 범위·순서·변경파일 확인 |
| G2 CODE_REVIEW | 12-2-2~5 구현 코드 | 보안·구조·코딩 표준 |
| G3 TEST_GATE | 기능 검증 | Redis ping, GIN EXPLAIN, 에러 형식, 보상 로직 |
| G4 FINAL_GATE | 전체 통합 | 모든 Task DONE, 회귀 없음 |

---

## 5. 리스크

| ID | 리스크 | 대응 |
|----|--------|------|
| R-001 | GIN 인덱스 생성 시 대용량 테이블 잠금 | CONCURRENTLY 사용 |
| R-002 | Redis 미기동 시 Rate Limit 장애 | 기존 In-Memory 폴백 유지 (REDIS_URL 미설정 시) |
| R-003 | 에러 핸들러가 기존 rate_limit 핸들러와 충돌 | rate_limit 핸들러 우선 유지, 일반 HTTPException만 가로채기 |
| R-004 | 보상 트랜잭션 복잡도 | 임베딩 플로우에만 최소 적용 |
