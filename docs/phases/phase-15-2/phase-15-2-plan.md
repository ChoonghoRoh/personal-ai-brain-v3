# Phase 15-2 Plan — 지식관리 AI 자동화

## 범위
지식관리 AI 자동화 통합 워크플로우(문서→청크→키워드→라벨→승인→임베딩), SSE 진행 상황, /admin/ai-automation 페이지.

## 설계 결정
- **SSE 상태 저장**: 메모리 딕셔너리 (reason_stream.py 패턴)
- **워크플로우**: 기존 서비스 오케스트레이션 (FileParser, StructureMatcher, chunk_sync)
- **취소**: asyncio.Event 플래그 (각 단계 전 체크)
- **승인**: auto_approve 옵션 (True: 즉시 승인+임베딩, False: draft→수동 승인)
- **Ollama fallback**: 미연결 시 regex 기반 키워드 추출, 라벨 매칭 fallback

## 재사용 서비스
- `FileParserService.parse_file()` → 문서 텍스트 추출
- `structure_matcher._extract_keywords()` → 키워드 추출 fallback
- `auto_labeler.label_on_import()` → 라벨 매칭
- `chunk_sync_service.sync_chunk_to_qdrant()` → Qdrant 임베딩
- `ollama_client.ollama_generate()` → LLM 키워드/라벨 추출

## Task 목록 (4개)
1. 15-2-1 [BE] API 엔드포인트 + SSE + 상태 관리 (backend-dev)
2. 15-2-2 [BE] 6단계 워크플로우 파이프라인 (backend-dev)
3. 15-2-3 [FE] LNB 메뉴 + HTML 라우트 (frontend-dev)
4. 15-2-4 [FE] AI 자동화 페이지 (frontend-dev)

## 의존 관계
- 15-2-1, 15-2-3: 독립 병렬
- 15-2-2: 15-2-1에 의존
- 15-2-4: 15-2-1, 15-2-3에 의존
