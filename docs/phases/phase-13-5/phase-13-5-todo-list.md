# Phase 13-5 Todo List — Backend Local LLM·Ollama 개선

**Phase**: 13-5
**작성일**: 2026-02-16

---

## Task 13-5-1 [BE] True Streaming (ollama_generate_stream 기반 SSE)

- [ ] ollama_client.py에 `ollama_generate_stream` 함수 구현 (또는 기존 확장)
- [ ] Ollama `/api/generate` stream=true 연동
- [ ] `backend/routers/ai/ai.py` `/api/ask/stream` 엔드포인트 전환:
  - [ ] 기존 Pseudo-streaming (전체 응답 대기 후 청크 전송) 제거
  - [ ] Ollama 토큰 생성 즉시 SSE 이벤트로 전달
- [ ] SSE 이벤트 형식 유지 (기존 클라이언트 호환)
- [ ] TTFT(Time To First Token) 개선 확인
- [ ] 에러 처리: Ollama 스트림 중단 시 SSE 에러 이벤트
- [ ] 프론트엔드 ask/stream 소비부 호환 확인

## Task 13-5-2 [BE] 토큰 관리 정밀화

- [ ] tiktoken 또는 transformers Tokenizer 중 선택
- [ ] requirements.txt 의존성 추가
- [ ] 토큰 계산 유틸리티 함수 구현:
  - [ ] 모델별 토크나이저 로드
  - [ ] 정확한 토큰 수 계산
- [ ] ContextManager 한국어 친화 수정:
  - [ ] `chars // 4` 근사치 → 정확한 토큰 계산으로 교체
  - [ ] 모델별 최대 컨텍스트(4k~32k) 동적 조정
- [ ] RAG 범위 동적 조정 (Context Window 초과 방어)
- [ ] 기존 답변 품질 회귀 확인

## Task 13-5-3 [BE] System Prompt 활용

- [ ] Ollama `/api/chat` 엔드포인트 사용으로 전환 (또는 `/api/generate` system 파라미터)
- [ ] `role: system` 메시지에 페르소나·제약사항 분리:
  - [ ] "한국어로만 답변"
  - [ ] "중국어(中文) 사용 금지"
  - [ ] 기타 페르소나 지시
- [ ] User Prompt에서 시스템 지시 제거 (중복 해소)
- [ ] 과도한 후처리 정규식 축소:
  - [ ] 코드블록 삭제 정규식 검토
  - [ ] 영문 삭제 정규식 검토
- [ ] 프롬프트 구조 문서화
- [ ] A/B 비교: System Prompt 적용 전후 답변 품질

## Task 13-5-4 [BE] (선택) 구조화 출력·프롬프트 주입 방어

- [ ] Ollama `format="json"` 옵션 활용 경로 식별:
  - [ ] 지식 추출 (키워드, 라벨)
  - [ ] 요약 생성
- [ ] JSON 출력 파싱 로직 구현
- [ ] 기존 정규식 기반 파싱과 비교
- [ ] LLM 프롬프트 주입 방어 현황 검토:
  - [ ] 현재 방어 수준 문서화
  - [ ] 주요 공격 벡터 식별
  - [ ] 방어 로직 개선 권고안 작성
- [ ] 보안 검토 문서 작성
