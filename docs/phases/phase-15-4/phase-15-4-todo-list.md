# Phase 15-4 Todo List: DB 샘플 고도화 연동

**Phase**: 15-4
**G1 판정**: PASS
**작성일**: 2026-02-16

---

- [x] Task 15-4-1: [DOC] 지식관리 지정 폴더와 documents/projects/labels 매핑 규칙 (Owner: backend-dev)
  - 폴더 경로 → Document 필드 매핑 (file_path, file_name, file_type, size, project_id, category_label_id)
  - 폴더 구조 → Project 매핑 (1단계 하위 디렉토리 = Project, 루트 파일 = NULL)
  - 파일 경로 → Label(Category) 자동 분류 규칙 (경로 키워드 패턴 매칭)

- [x] Task 15-4-2: [SCRIPT] 시드 스크립트 `--with-knowledge` 옵션 확장 (Owner: backend-dev)
  - `seed_sample_data.py`에 argparse `--with-knowledge` 플래그 추가
  - `seed_knowledge_folder_documents()` 함수 구현 (폴더 스캔 → Document/Chunk/Label 시드)
  - 기존 시드 데이터와 충돌 없이 멱등성 보장 (file_path upsert)

- [x] Task 15-4-3: [QA] 검증 체크리스트 작성 (Owner: backend-dev)
  - 매핑 규칙 검증 (폴더 경로 API, system_settings, file_path 매핑)
  - 시드 데이터 검증 (기본 시드 건수, `--with-knowledge` 시드 정합성)
  - AI 자동화 결과 포함 여부 검증 (source, status 필드, 검색 연동)
