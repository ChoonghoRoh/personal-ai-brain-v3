# Phase 15-4-3: 검증 체크리스트

**작성일**: 2026-02-16
**Phase**: 15-4-3 [QA]

---

## 1. 매핑 규칙 검증

- [ ] 지식관리 폴더 경로 조회 API (`GET /api/knowledge/folder-config`) 정상 응답
- [ ] 폴더 경로 변경 후 파일 목록이 새 경로 기준으로 반환
- [ ] `system_settings` 테이블에 `knowledge.folder_path` 키가 정상 저장

## 2. 시드 데이터 검증

### 2.1 기본 시드 (`--with-knowledge` 미지정)

- [ ] Projects 8건 이상 생성
- [ ] Labels (keyword, category, domain) 30건 이상 생성
- [ ] Documents 100건 이상 생성 (docs/ 폴더 기준)
- [ ] KnowledgeChunks 300건 이상 생성
- [ ] KnowledgeLabels 500건 이상 생성
- [ ] KnowledgeRelations 50건 이상 생성

### 2.2 지식관리 폴더 시드 (`--with-knowledge`)

- [ ] `brain/knowledge/` 폴더 내 허용 확장자 파일이 Documents에 등록
- [ ] 등록된 Document의 `file_path`가 절대 경로
- [ ] 하위 폴더명이 기존 Project.name과 일치 시 `project_id` 정상 매핑
- [ ] 카테고리 분류 규칙에 따라 `category_label_id` 정상 할당
- [ ] 폴더 내 파일에 대한 KnowledgeChunks 정상 생성

## 3. 동기화 검증

- [ ] `POST /api/knowledge/sync` 호출 시 신규 파일 Documents에 추가
- [ ] 삭제된 파일이 missing_files에 보고
- [ ] 기존 동기화된 파일은 unchanged로 처리

## 4. AI 자동화 결과 포함 여부

- [ ] AI 자동화(`/api/automation/run-full`) 실행 후 생성된 labels의 `source` = `"ai"`
- [ ] 승인 전 labels의 `status` = `"suggested"`, 승인 후 `"confirmed"`
- [ ] 자동 생성된 KnowledgeLabels가 검색 결과에 포함

## 5. 데이터 정합성

- [ ] Documents → KnowledgeChunks 외래키 정합 (orphan chunk 없음)
- [ ] KnowledgeLabels의 chunk_id, label_id가 유효한 레코드 참조
- [ ] KnowledgeRelations의 source/target_chunk_id가 유효한 레코드 참조
- [ ] 시드 재실행 시 중복 생성 방지 (멱등성)
