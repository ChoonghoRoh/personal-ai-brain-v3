# Phase 14-6: DB 샘플 데이터·고도화·검증 — Todo List

**상태**: ✅ 완료
**우선순위**: Phase 14 내 6순위 (P2)
**기준 문서**: `phase-14-master-plan-guide.md` §8.6, `260210-1400-db-sample-data-and-high-level-strategy.md`

---

## Task 목록

### 14-6-1: [DOC] 샘플 데이터 전략·시드 스크립트 설계 ✅

**우선순위**: 1순위
**상태**: ✅ 완료

- [x] 기존 DB 상태 분석 (테이블별 건수 확인)
- [x] 목표 건수 정의 (projects 8, docs 100+, chunks 300+, labels 100+ 등)
- [x] 시드 스크립트 아키텍처 설계 (멱등성, 실제 .md 파일 활용)
- [x] PostgreSQL 백업 수행 (`backups/backup_pre_seed_20260216.dump`)

### 14-6-2: [BE] 시드 스크립트 구현·실행 ✅

**우선순위**: 2순위
**상태**: ✅ 완료
**선행**: 14-6-1

- [x] `scripts/db/seed_sample_data.py` 작성 (16개 테이블 시드)
- [x] Projects 8건 (8개 서브 프로젝트)
- [x] Labels 232건 (기존 202 + 추가 30)
- [x] Documents 154건 (docs/ 하위 .md 파일 스캔)
- [x] Knowledge Chunks 300건 (heading 기반 분할)
- [x] Knowledge Labels 500건 (청크-라벨 매핑)
- [x] Knowledge Relations 50건 (랜덤 관계)
- [x] Memories 100건 (다양한 카테고리·타입)
- [x] Conversations 100건 (다양한 질의·세션)
- [x] Reasoning Results 100건 (raw SQL로 타입 호환 처리)
- [x] Admin Schemas 20건
- [x] Admin Templates 100건
- [x] Admin Prompt Presets 100건
- [x] Admin RAG Profiles 20건
- [x] Admin Context Rules 20건
- [x] Admin Policy Sets 20건
- [x] Admin Audit Logs 100건

### 14-6-3: [QC] 1차 검증 ✅

**우선순위**: 3순위
**상태**: ✅ 완료
**선행**: 14-6-2

- [x] 모든 테이블 목표 건수 충족 확인 (16/16 OK)
- [x] pytest 79 passed — 회귀 없음 (baseline 동일: 5 failed, 3 errors)
- [x] 14/16 API 엔드포인트 200 OK
  - conversations 500: 기존 baseline 이슈 (JSON 파싱, 시드 무관)
  - conversations/reasoning 422: 필수 파라미터 미제공 (정상 동작)
