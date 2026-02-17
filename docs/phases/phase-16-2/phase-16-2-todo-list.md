# Phase 16-2 Todo List — AI 자동화 성능 개선

**Phase**: 16-2
**기준**: [phase-16-2-plan.md](phase-16-2-plan.md)

---

- [ ] Task 16-2-4: [BE] 라벨 매칭 역인덱스 (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` _match_labels() 수정
  - label_index: keyword_token → [label_id] 딕셔너리 구축
  - 청크별로 토큰화 후 label_index 조회 → 후보 라벨만 확정 매칭
  - 완료 기준: 기존 브루트포스와 동일 결과, 매칭 시간 단축

- [ ] Task 16-2-1: [BE] Qdrant 배치 임베딩 (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` _embed_chunks() 수정
  - 단건 루프 대신 50건 단위로 묶어 embedding_model.encode(texts, batch_size=50)
  - qdrant_client.upsert(points=[]) 한 번에 전송
  - 완료 기준: 960청크 시 Qdrant 호출 약 20회 이하

- [ ] Task 16-2-2: [BE] LLM 키워드 추출 묶음 호출 (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` _extract_keywords() 수정
  - 5~10 청크 텍스트를 하나의 프롬프트로 묶어 1회 LLM 호출
  - 응답 파싱 후 청크별 키워드 할당
  - 완료 기준: 960청크 시 LLM 호출 약 96~192회

- [ ] Task 16-2-3: [BE] 자동 배치 분할 실행 (Owner: backend-dev)
  - `backend/services/automation/ai_workflow_service.py` execute_workflow() 수정
  - document_ids를 20개 단위 배치로 분할
  - 배치마다 6단계 전체 실행, 배치 간 gc.collect()
  - 진행률: 배치 1/4 → 0~25%, 2/4 → 25~50% 등
  - 완료 기준: 80문서 시 4배치 순차 처리, 중간 배치 실패 시 이전 결과 유지
