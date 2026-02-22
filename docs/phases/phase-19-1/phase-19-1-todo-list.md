# Phase 19-1 Todo List

## Task 19-1-1: FIX-2 — 3단계 계층 매칭 도입 [BE] (Owner: backend-dev)

- [ ] `recommendation_llm.py` L93-154 현재 ILIKE 부분매칭 로직 파악
- [ ] `match_and_score_labels()` 함수를 3단계 계층 매칭으로 교체
  - Tier 1: 정확 매칭 (`func.lower(Label.name) == kw_lower`)
  - Tier 2: 접두사 매칭 (`Label.name.ilike(f"{kw}%")`), 3자 이상만
  - Tier 3: 부분 매칭 (`Label.name.ilike(f"%{kw}%")`), 4자 이상만
- [ ] 2자 키워드(IT, AI): Tier 1만 → 미매칭 시 new_keywords
- [ ] 3자 키워드(화성, 우주): Tier 1 → Tier 2 → 미매칭 시 new_keywords
- [ ] 4자+ 키워드: Tier 1 → Tier 2 → Tier 3
- [ ] Tier별 신뢰도 차등: base_conf, ×0.85, ×0.7
- [ ] `Label.name` DB 인덱스 확인 + 필요 시 추가
- [ ] 기존 테스트 통과 확인

## Task 19-1-2: FIX-1 — 공백 분리 로직 개선 [BE] (Owner: backend-dev)

- [ ] `recommendation_llm.py` L76-90 현재 공백 분리 로직 파악
- [ ] 분리 우선순위 변경: 1순위 쉼표/세미콜론, 2순위 개행, 3순위 공백(조건부)
- [ ] `_is_single_concept_word()` 헬퍼 함수 추가
  - `^[가-힣]{2,}$` 또는 `^[a-zA-Z]{2,}$` 매칭 시에만 공백 분리 허용
- [ ] 테스트: "머신 러닝, 데이터 분석" → ["머신 러닝", "데이터 분석"]
- [ ] 테스트: "Python\nJava\nC++" → ["Python", "Java", "C++"]
- [ ] 기존 테스트 통과 확인

## Task 19-1-3: FIX-3+4 — 유틸 함수 개선 [BE] (Owner: backend-dev)

- [ ] `korean_utils.py` L15-34 `_clean_disallowed_chars()` 허용 문자 확장
  - 정규식: `[^가-힣a-zA-Z0-9\s\-\./_]` → `[^가-힣a-zA-Z0-9\s\-\./_+#&@]`
- [ ] 테스트: "C++" → "C++", "C#" → "C#", "R&D" → "R&D"
- [ ] `korean_utils.py` L37-58 `_is_garbled_keyword()` 오탐 완화
  - 한글→영문: 영어 부분 3자 이상이면 허용 ("서버less" → 통과)
  - 영문→한글: 기존대로 차단
- [ ] 테스트: "서버less" → 유지, "딥러닝model" → 유지
- [ ] 기존 테스트 통과 확인

## Task 19-1-4: FIX-5 — FE 이중 정제 제거 [FE] (Owner: frontend-dev)

- [ ] `keyword-group-suggestion.js` L82 `extractKeywordsOnly()` 호출 제거
- [ ] `.map(kw => kw.trim()).filter(kw => kw.length >= 2)` 최소 처리만 유지
- [ ] `extractKeywordsOnly()`, `cleanKeyword()` 함수 자체는 삭제하지 않음
- [ ] 키워드 추천 UI에서 백엔드 응답이 온전히 표시되는지 확인

## Task 19-1-5: 통합 테스트 [TEST] (Owner: tester)

- [ ] `tests/test_keyword_recommenders.py` 기존 테스트 통과 확인
- [ ] FIX-2 계층 매칭 테스트 케이스 추가/확인
- [ ] FIX-1 공백 분리 테스트 케이스 추가/확인
- [ ] FIX-3+4 유틸 함수 테스트 케이스 추가/확인
- [ ] GroupKeywordRecommender + ChunkLabelRecommender 양쪽 동작 확인
- [ ] pytest 전체 통과 (기존 테스트 회귀 없음)
