# Task 12-3-4: [BE] memories TTL 스케줄러

**우선순위**: 12-3 내 3순위
**예상 작업량**: 중 (스케줄러 신규 + config + main.py 수정)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-3-todo-list.md`
**Plan**: `phase-12-3-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

만료된 단기 기억(memories)을 자동으로 정리하는 asyncio 기반 백그라운드 스케줄러를 구현한다. APScheduler 등 외부 의존성 없이 asyncio.sleep 루프로 구현한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 | 용도 |
|------|------|
| `backend/services/cognitive/memory_scheduler.py` | asyncio 기반 TTL 정리 스케줄러 |

### 2.2 수정

| 파일 | 변경 내용 |
|------|----------|
| `backend/config.py` | MEMORY_CLEANUP_ENABLED, MEMORY_CLEANUP_INTERVAL_MINUTES 추가 |
| `backend/main.py` | lifespan에서 스케줄러 start/stop 호출 |

---

## 3. 작업 체크리스트

- [x] `backend/config.py`에 환경변수 추가
  - [x] `MEMORY_CLEANUP_ENABLED` (기본 true)
  - [x] `MEMORY_CLEANUP_INTERVAL_MINUTES` (기본 60)
- [x] `memory_scheduler.py` 신규 생성
  - [x] `_cleanup_loop()`: asyncio.sleep 기반 주기적 실행
  - [x] `_run_cleanup()`: 동기 DB 작업으로 만료 기억 삭제
  - [x] `start_memory_cleanup()` / `stop_memory_cleanup()` API
  - [x] graceful shutdown (CancelledError 처리)
- [x] `backend/main.py` lifespan에 통합
  - [x] startup: `start_memory_cleanup()` 호출
  - [x] shutdown: `stop_memory_cleanup()` 호출

---

## 4. 참조

- Phase 12 Master Plan §12-3-4
- 기존 `MemoryService.delete_expired_memories()` 메서드 활용
