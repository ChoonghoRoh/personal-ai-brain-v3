# Task 17-3-1: [BE] hybrid_search.py 파일명 ILIKE 검색 추가

**우선순위**: 17-3 내 1순위
**예상 작업량**: 작음
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

기존 keyword_search는 KnowledgeChunk.content만 ILIKE 검색 대상으로 사용했다. 파일명(Document.file_path)도 검색 대상에 포함하여, 사용자가 파일명으로도 관련 청크를 찾을 수 있도록 개선한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/search/hybrid_search.py` | Document JOIN + file_path ILIKE 필터 추가, match_count에 filepath 포함 |

## §3. 작업 체크리스트 (Done Definition)

- [x] Document 모델 JOIN 추가 (KnowledgeChunk.document_id == Document.id)
- [x] ILIKE 조건에 Document.file_path 추가 (content + file_path OR 조건)
- [x] match_count 계산에 filepath_lower 포함
- [x] project_id 필터에서 중복 JOIN 제거 (이미 상위에서 JOIN)

## §4. 참조

- [Phase 17 개발 요구사항 §6](../../../planning/260218-0830-phase17-개발-요구사항.md)
