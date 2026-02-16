# Task 15-1-2: 폴더 내 파일 목록 API

**우선순위**: 15-1 내 2순위
**의존성**: 15-1-1
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

지정 폴더의 파일시스템을 스캔하고 documents 테이블과 매칭하여 파일 상태 정보를 반환하는 API를 구현한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/knowledge/folder_management.py` | 수정 | GET `/api/knowledge/folder-files` 엔드포인트 추가 |
| `backend/services/knowledge/folder_service.py` | 수정 | 폴더 스캔 + DB 매칭 로직 추가 |
| `tests/test_folder_management.py` | 수정 | 파일 목록 API 테스트 추가 |

## §3. 작업 체크리스트 (Done Definition)

- [ ] `GET /api/knowledge/folder-files` 엔드포인트 동작
- [ ] 지정 폴더 내 파일 재귀 스캔 (depth 제한: 기본 3)
- [ ] 각 파일에 대해 documents 테이블 `file_path` 매칭
- [ ] 응답 필드: file_name, file_path, size, updated_at, document_id, chunk_count, status(synced/unsynced/new)
- [ ] 허용 확장자 필터링 (.md, .txt, .pdf, .docx, .hwp, .xlsx, .pptx)
- [ ] 페이징: `limit`, `offset` 쿼리 파라미터
- [ ] `Depends(require_admin_knowledge)` 적용
- [ ] Pydantic 응답 스키마 정의
- [ ] 테스트 추가

## §4. 참조

- `backend/models/models.py` — `Document` 모델 (`file_path`, `file_name`, `file_type`, `size` 필드)
- `backend/services/ingest/file_parser_service.py` — 지원 확장자 목록
