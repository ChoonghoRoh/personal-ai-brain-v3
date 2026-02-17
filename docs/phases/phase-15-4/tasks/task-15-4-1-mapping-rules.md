# Task 15-4-1: [DOC] 지식관리 지정 폴더와 DB 매핑 규칙

**우선순위**: 15-4 내 1순위
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

지식관리 지정 폴더(`KNOWLEDGE_FOLDER_PATH`)의 파일들이 DB 테이블(documents, projects, labels, knowledge_chunks, knowledge_labels, knowledge_relations)과 어떻게 매핑되는지 규칙을 정의하는 문서를 작성한다.

Phase 15-1에서 구현된 폴더 관리 기능과 Phase 15-2의 AI 자동화 파이프라인이 동일한 매핑 규칙을 공유하도록, 단일 진실 소스(SSOT) 역할의 매핑 규칙 문서를 산출한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `docs/phases/phase-15-4/mapping-rules.md` | 신규 | 폴더 경로 -> Document 매핑, Project 매핑, Label 분류, 청크-라벨 연결 규칙 정의 |

## §3. 작업 체크리스트 (Done Definition)

- [x] 폴더 경로 규칙 정의 (기본 폴더, DB 설정, 환경변수 우선순위)
- [x] Document 필드 매핑 테이블 작성 (file_path, file_name, file_type, size, project_id, category_label_id)
- [x] 폴더 구조 -> Project 매핑 정책 정의 (1단계 하위 디렉토리 = Project)
- [x] 파일 경로 -> Label(Category) 자동 분류 규칙 정의 (경로 키워드 패턴 매칭)
- [x] 청크 -> Labels 연결 규칙 정의 (knowledge_labels, knowledge_relations)
- [x] 시드 데이터 흐름 다이어그램 포함
- [x] 허용 파일 확장자 목록 명시

## §4. 참조

- `docs/phases/phase-15-4/mapping-rules.md` -- 산출물 (매핑 규칙 문서)
- `backend/services/knowledge/folder_service.py` -- 폴더 경로 조회/스캔 로직
- `backend/models/models.py` -- Document, Project, Label, KnowledgeChunk 모델
- `scripts/db/seed_sample_data.py` -- 시드 스크립트 (매핑 규칙 구현체)
