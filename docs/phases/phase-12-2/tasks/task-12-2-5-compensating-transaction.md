# Task 12-2-5: [BE] PG-Qdrant 보상 트랜잭션 도입

**우선순위**: 12-2 내 4순위
**예상 작업량**: 중 (서비스 2파일 신규)
**의존성**: 12-2-4 (에러 표준화 연계)
**상태**: ✅ 완료

**기반 문서**: `phase-12-2-todo-list.md`
**Plan**: `phase-12-2-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

PostgreSQL과 Qdrant 간 데이터 정합성을 보장하기 위한 보상 트랜잭션(Compensating Transaction) 패턴을 도입한다. Forward 실행 실패 시 역순으로 보상 액션을 수행하여 분산 시스템 간 일관성을 유지한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 | 용도 |
|------|------|
| `backend/services/knowledge/transaction_manager.py` | CompensatingTransaction 클래스 |
| `backend/services/knowledge/chunk_sync_service.py` | PG-Qdrant 동기화 서비스 |

---

## 3. 작업 체크리스트

- [x] `transaction_manager.py` 생성
  - [x] CompensatingTransaction 클래스 구현
  - [x] execute: 순차 실행 + 실패 시 보상 액션 역순 실행
  - [x] 단계별 성공/실패 로깅
- [x] `chunk_sync_service.py` 생성
  - [x] Qdrant upsert → PG qdrant_point_id 업데이트 플로우
  - [x] PG 업데이트 실패 → Qdrant 포인트 삭제 (보상 액션)
- [x] 에러 시 표준 에러 응답 연계 (12-2-4)

---

## 4. 참조

- Phase 12 Master Plan §12-2-5
- Saga 패턴 (Compensating Transaction)
