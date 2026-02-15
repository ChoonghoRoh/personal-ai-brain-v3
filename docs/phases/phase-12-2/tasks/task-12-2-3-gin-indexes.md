# Task 12-2-3: [DB] PostgreSQL GIN 인덱스 추가 (4개)

**우선순위**: 12-2 내 2순위
**예상 작업량**: 소 (SQL 마이그레이션 1파일)
**의존성**: 없음
**상태**: ✅ 완료

**기반 문서**: `phase-12-2-todo-list.md`
**Plan**: `phase-12-2-plan.md`
**작업 순서**: `phase-12-navigation.md`

---

## 1. 개요

### 1.1 목표

전문 검색 성능 향상을 위해 knowledge_chunks, conversations, memories 테이블의 텍스트 컬럼에 GIN 인덱스를 추가한다.

---

## 2. 파일 변경 계획

### 2.1 신규 생성

| 파일 | 용도 |
|------|------|
| `scripts/migrations/001_add_gin_indexes.sql` | GIN 인덱스 4개 생성 SQL |
| `scripts/migrations/README.md` | 마이그레이션 실행 가이드 |

---

## 3. 작업 체크리스트

- [x] `scripts/migrations/` 디렉토리 생성
- [x] `001_add_gin_indexes.sql` 작성
- [x] `knowledge_chunks.content` GIN 인덱스 (to_tsvector simple)
- [x] `conversations.question` GIN 인덱스 (to_tsvector simple)
- [x] `conversations.answer` GIN 인덱스 (to_tsvector simple)
- [x] `memories.content` GIN 인덱스 (to_tsvector simple)
- [x] CONCURRENTLY 옵션 사용
- [x] IF NOT EXISTS 방어 코드

---

## 4. 참조

- Phase 12 Master Plan §12-2-3
