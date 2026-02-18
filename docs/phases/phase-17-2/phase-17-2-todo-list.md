# Phase 17-2 Todo List — 키워드 추천 아키텍처 분리

**Phase**: 17-2
**기준**: [phase-17-2-plan.md](phase-17-2-plan.md)

---

- [x] Task 17-2-1: [BE] ChunkLabelRecommender 전용 클래스 분리 (Owner: backend-dev)
  - `backend/services/reasoning/chunk_label_recommender.py` 신규 생성
  - 청크 텍스트 → 키워드 추출 전용 로직
  - 전용 프롬프트 (추출형)
  - chunk_id 필수, 청크 컨텍스트 활용
  - 완료 기준: ChunkLabelRecommender.recommend() 단독 동작

- [x] Task 17-2-2: [BE] GroupKeywordRecommender 전용 클래스 분리 (Owner: backend-dev)
  - `backend/services/reasoning/group_keyword_recommender.py` 신규 생성
  - 그룹 설명 → 키워드 생성 전용 로직
  - 전용 프롬프트 (생성형 + few-shot)
  - 기존 키워드 제외 로직
  - 완료 기준: GroupKeywordRecommender.recommend() 단독 동작

- [x] Task 17-2-3: [BE] recommendation_llm.py 공통 유틸 함수 추출 (Owner: backend-dev)
  - `backend/services/reasoning/recommendation_llm.py` 리팩토링
  - resolve_model, generate_keywords_via_llm 등 공통 함수 추출
  - `backend/utils/korean_utils.py` 키워드 정제 함수 강화
  - 완료 기준: 공통 유틸 함수가 두 Recommender에서 재사용 가능

- [x] Task 17-2-4: [BE] labels_handlers.py 라우터 연동 수정 (Owner: backend-dev)
  - `backend/routers/knowledge/labels_handlers.py` 기존 recommend_labels_with_llm 호출 → 새 Recommender 클래스 호출로 전환
  - API 엔드포인트 동작 하위 호환 유지
  - 완료 기준: /api/labels/groups/suggest-keywords 기존 응답 형식 유지

- [x] Task 17-2-5: [BE] 단위 테스트 23건 작성 (Owner: backend-dev)
  - `tests/test_keyword_recommenders.py` 신규 생성
  - ChunkLabelRecommender 테스트 케이스
  - GroupKeywordRecommender 테스트 케이스
  - 공통 유틸 함수 테스트
  - 완료 기준: pytest tests/test_keyword_recommenders.py — 23건 전건 PASS
