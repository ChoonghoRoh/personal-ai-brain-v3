# Task 15-4-2: [SCRIPT] 시드 스크립트 `--with-knowledge` 옵션 확장

**우선순위**: 15-4 내 2순위
**의존성**: 15-4-1
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

`scripts/db/seed_sample_data.py`에 `--with-knowledge` CLI 옵션을 추가하여, 시드 실행 시 지식관리 지정 폴더(`brain/knowledge/`)의 파일도 Documents/KnowledgeChunks/Labels에 포함되도록 확장한다.

기본 시드(프로젝트 docs/ 폴더 기반)와 별도로, `--with-knowledge` 플래그가 지정된 경우에만 지정 폴더 파일을 추가 시드한다. 기존 데이터와 충돌하지 않도록 `file_path` 기반 upsert 패턴을 적용하여 멱등성을 보장한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `scripts/db/seed_sample_data.py` | 수정 | argparse `--with-knowledge` 플래그 추가 |
| `scripts/db/seed_sample_data.py` | 수정 | `seed_knowledge_folder_documents()` 함수 구현 |
| `scripts/db/seed_sample_data.py` | 수정 | `classify_document()` 경로 기반 카테고리 분류 함수 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [x] argparse에 `--with-knowledge` 플래그 추가 (기본값: False)
- [x] `seed_knowledge_folder_documents()` 함수 구현 -- 지정 폴더 재귀 스캔, 허용 확장자 필터링, Document/Chunk 생성
- [x] 폴더명 -> Project 매핑 로직 구현 (1단계 하위 디렉토리 = 기존 Project 매칭)
- [x] `classify_document()` 경로 키워드 기반 카테고리 분류 구현
- [x] file_path unique 제약에 의한 중복 방지 (upsert 패턴)
- [x] 기본 시드 실행 시 `--with-knowledge` 미지정이면 기존 동작과 동일
- [x] 시드 실행 로그에 knowledge 폴더 시드 결과 출력

## §4. 참조

- `scripts/db/seed_sample_data.py` -- 수정 대상 스크립트
- `docs/phases/phase-15-4/mapping-rules.md` -- 매핑 규칙 (구현 기준 문서)
- `backend/services/knowledge/folder_service.py` -- ALLOWED_EXTENSIONS 참조
- `backend/services/ingest/file_parser_service.py` -- 파일 파싱 서비스 참조
