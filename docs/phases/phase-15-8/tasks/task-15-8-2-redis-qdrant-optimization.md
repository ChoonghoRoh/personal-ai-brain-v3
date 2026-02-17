# Task 15-8-2: Redis 캐싱 확대 및 Qdrant 벡터 양자화

**우선순위**: 15-8 내 2순위 (1순위와 병렬 가능)
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: DONE

---

## §1. 개요

Redis 캐싱 범위를 Reasoning과 Graph 영역으로 확대하고, Qdrant 벡터 양자화 설정을 추가하여 시스템 성능을 최적화한다. config.py에 환경변수 기반 설정을 통합하여 운영 환경에서 유연하게 튜닝할 수 있도록 한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/config.py` | 수정 | Redis/Qdrant 관련 환경변수 추가 |

## §3. 작업 체크리스트 (Done Definition)

### Redis 캐싱 확대
- [x] `REDIS_REASONING_CACHE_TTL` 환경변수 추가 (기본값 300초)
  - Reasoning API 응답 캐시에 사용
  - 동일 질의+컨텍스트 해시 키 기반
- [x] `REDIS_GRAPH_CACHE_TTL` 환경변수 추가 (기본값 600초)
  - Knowledge Graph API 응답 캐시에 사용
  - 그래프 데이터 변경 빈도 낮으므로 긴 TTL
- [x] 캐시 히트 시 성능 목표
  - Redis 히트: 10ms 이하
  - 캐시 미스 시 DB 조회 후 캐시 저장

### Qdrant 벡터 양자화
- [x] `QDRANT_QUANTIZATION_ENABLED` 환경변수 추가 (기본값 false)
  - 운영 환경에서 true로 설정하여 메모리 절감
- [x] `QDRANT_QUANTIZATION_TYPE` 환경변수 추가 (기본값 "scalar")
  - Scalar: 32bit -> 8bit, 메모리 약 75% 절감
  - 정확도 손실 최소화 (코사인 유사도 기준 < 1%)
- [x] Qdrant 검색 성능 목표: 100ms 이하

### config.py 통합
- [x] Settings 클래스에 환경변수 필드 추가
- [x] 기본값 설정 및 타입 검증
- [x] `.env.example`에 샘플 값 추가

## §4. 참조

- `docs/phases/phase-15-master-plan.md` -- SS2.3.6 Redis/Qdrant 성능 최적화
- `backend/config.py` -- 기존 설정 구조
- `backend/services/ai/qdrant_client.py` -- Qdrant 클라이언트
- `backend/services/cache/redis_service.py` -- Redis 서비스
