# Task 15-2-2: 6단계 워크플로우 파이프라인 서비스

**우선순위**: 15-2 내 2순위
**의존성**: 15-2-1
**담당 팀원**: backend-dev
**상태**: 대기

---

## §1. 개요

문서 선택부터 임베딩까지 6단계 AI 자동화 파이프라인을 구현한다. 기존 서비스를 오케스트레이션하고, 각 단계별 진행 상황을 상태 관리자에 업데이트한다.

## §2. 파일 변경 계획

| 파일 | 유형 | 변경 내용 |
|------|------|----------|
| `backend/services/automation/ai_workflow_service.py` | 신규 | 6단계 파이프라인 서비스 |
| `tests/test_ai_workflow_service.py` | 신규 | 워크플로우 테스트 |

## §3. 작업 체크리스트 (Done Definition)

### 6단계 파이프라인
- [ ] **1단계: 문서 텍스트 추출**
  - document_ids로 Document 조회 → FileParserService.parse_file() 호출
  - 각 문서의 parsed_content 또는 file_path에서 텍스트 추출
  - 진행률: 0-15%
- [ ] **2단계: 청크 생성**
  - 텍스트를 KnowledgeChunk로 분할 (문단 기반, 최대 1000자)
  - DB에 status='draft' 로 저장
  - 진행률: 15-30%
- [ ] **3단계: 키워드 추출**
  - 각 청크에서 키워드 추출
  - Ollama 가용 시: ollama_generate()로 키워드 추출 프롬프트
  - Ollama 미가용: structure_matcher._extract_keywords() fallback
  - Label 테이블에 label_type='keyword'로 저장 (없으면 생성)
  - 진행률: 30-50%
- [ ] **4단계: 라벨 생성/매칭**
  - 청크 내용 기반 카테고리/도메인 라벨 추천
  - Ollama 가용 시: LLM 기반 라벨 추천
  - Ollama 미가용: auto_labeler.label_on_import() fallback
  - KnowledgeLabel에 status='suggested', source='ai'로 저장
  - 진행률: 50-70%
- [ ] **5단계: 승인 처리**
  - auto_approve=True: 청크 status='approved', 라벨 status='confirmed'
  - auto_approve=False: 그대로 유지 (draft/suggested)
  - 진행률: 70-80%
- [ ] **6단계: Qdrant 임베딩** (auto_approve=True인 경우만)
  - 승인된 청크에 대해 chunk_sync_service.sync_chunk_to_qdrant() 호출
  - Qdrant 미연결 시 skip (qdrant_point_id=None)
  - 진행률: 80-100%

### 상태 연동
- [ ] 각 단계 시작/완료 시 ai_workflow_state.update_progress() 호출
- [ ] 각 단계 전 cancel 플래그 체크 → True면 즉시 중단
- [ ] 실패 시 error 정보를 상태에 저장

### 결과 저장
- [ ] TaskState.results에 생성 결과 기록:
  - chunks_created, keywords_extracted, labels_matched, chunks_approved, chunks_embedded
- [ ] 부분 실패 시 실패 단계 + 에러 메시지 저장

### 공통
- [ ] 테스트 추가 (Ollama/Qdrant mock 사용)

## §4. 참조

- `backend/services/ingest/file_parser_service.py` — FileParserService.parse_file()
- `backend/services/knowledge/structure_matcher.py` — _extract_keywords()
- `backend/services/knowledge/auto_labeler.py` — label_on_import()
- `backend/services/knowledge/chunk_sync_service.py` — sync_chunk_to_qdrant()
- `backend/services/ai/ollama_client.py` — ollama_generate(), ollama_available()
