# Task 15-1-3: 파일 업로드/동기화 API

**우선순위**: 15-1 내 3순위
**의존성**: 15-1-1, 15-1-2
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

지정 폴더로 파일을 업로드하고, 폴더 전체를 documents 테이블과 동기화하는 API를 구현한다. 기존 FileParserService를 재사용하여 업로드된 파일의 텍스트 파싱을 수행한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/routers/knowledge/folder_management.py` | 수정 | POST `/api/knowledge/upload`, POST `/api/knowledge/sync` 추가 |
| `backend/services/knowledge/folder_service.py` | 수정 | 업로드 저장, 동기화 비교 로직 추가 |
| `tests/test_folder_management.py` | 수정 | 업로드/동기화 테스트 추가 |

## §3. 작업 체크리스트 (Done Definition)

### upload
- [ ] `POST /api/knowledge/upload` — multipart 파일 수신
- [ ] 파일을 지정 폴더에 저장
- [ ] documents 테이블에 레코드 생성 (file_path, file_name, file_type, size)
- [ ] FileParserService로 텍스트 파싱 (parsed_content 저장)
- [ ] 중복 file_path 시 409 Conflict 또는 upsert 처리
- [ ] 파일 크기 제한 (기본 50MB, config에서 설정)
- [ ] 허용 확장자 검증

### sync
- [ ] `POST /api/knowledge/sync` — 지정 폴더 전체 스캔
- [ ] 폴더에 있으나 DB에 없는 파일 → documents에 추가
- [ ] DB에 있으나 폴더에 없는 파일 → 감지하여 응답에 포함 (삭제는 옵션)
- [ ] 동기화 결과 반환: added_count, missing_count, unchanged_count

### 공통
- [ ] `Depends(require_admin_knowledge)` 적용
- [ ] 테스트 추가

## §4. 참조

- `backend/services/ingest/file_parser_service.py` — `FileParserService.parse_file()` 재사용
- `backend/routers/ingest/file_parser.py` — 기존 업로드 API 패턴 참조
