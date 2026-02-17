# Task 15-4-3: [QA] 검증 체크리스트 작성

**우선순위**: 15-4 내 3순위
**의존성**: 15-4-1, 15-4-2
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

Phase 15-4의 산출물(매핑 규칙 문서, 시드 스크립트 확장)이 정상 동작하는지 검증하기 위한 QA 체크리스트를 작성한다. 매핑 규칙 검증, 시드 데이터 정합성, 동기화 검증, AI 자동화 결과 포함 여부를 체계적으로 확인할 수 있도록 한다.

검증 체크리스트는 향후 Phase 회귀 테스트 및 시드 재실행 시 참조 문서로 활용된다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `docs/phases/phase-15-4/verification-checklist.md` | 신규 | QA 검증 체크리스트 5개 섹션 (매핑 규칙, 시드 데이터, 동기화, AI 자동화, 데이터 정합성) |

## §3. 작업 체크리스트 (Done Definition)

- [x] 매핑 규칙 검증 항목 작성 (폴더 경로 API, system_settings, file_path 매핑)
- [x] 기본 시드 검증 항목 작성 (Projects/Labels/Documents/Chunks/Relations 건수 기준)
- [x] `--with-knowledge` 시드 검증 항목 작성 (절대 경로, project_id 매핑, 카테고리 분류)
- [x] 동기화 검증 항목 작성 (sync API 신규/삭제/기존 파일 처리)
- [x] AI 자동화 결과 포함 여부 검증 항목 작성 (source, status 필드)
- [x] 데이터 정합성 검증 항목 작성 (외래키 참조, 멱등성)

## §4. 참조

- `docs/phases/phase-15-4/verification-checklist.md` -- 산출물 (QA 검증 체크리스트)
- `docs/phases/phase-15-4/mapping-rules.md` -- 매핑 규칙 (검증 기준)
- `scripts/db/seed_sample_data.py` -- 시드 스크립트 (검증 대상)
- `backend/routers/knowledge/folder_management.py` -- 폴더 관리 API (검증 대상)
