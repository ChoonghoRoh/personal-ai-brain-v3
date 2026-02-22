# Phase 19-1: 키워드 추천 엔진 고도화 (P0)

## 목표

LLM 키워드 추천 파이프라인의 5건 구조적 결함(FIX-1~5)을 수정하여 PAB 핵심 기능을 정상화한다.

## 근거

- 키워드 추천은 PAB의 기반 리소스 수집 경로. 키워드 품질 = 라벨 품질 = 검색 품질 = 전체 시스템 품질
- 현재 5건 버그로 약 30% 데이터 손실 발생
- [Master Plan](../phase-19-master-plan.md) §Phase 19-1
- [정밀 분석](../../planning/260221-phase19-정밀분석.md) §0

## 영향 범위

`generate_keywords_via_llm()`, `match_and_score_labels()`, `postprocess_korean_keywords()`는 아래 두 Recommender가 공유:

| Recommender | 사용처 | FIX-1~4 영향 |
|-------------|--------|--------------|
| `GroupKeywordRecommender` | 키워드 그룹 설명 → 키워드 추천 | 직접 영향 (수정 대상) |
| `ChunkLabelRecommender` | 청크 콘텐츠 → 라벨 추천 | 간접 영향 (동일 함수 사용, 품질 동일 개선) |

## 수정 의존성

```
FIX-2 (계층 매칭) ──→ FIX-1 (공백 분리) ──→ FIX-3+4 (유틸) ──→ FIX-5 (FE 이중 정제)
  [BE 핵심]             [BE 핵심]             [BE 유틸]            [FE]
```

## Task 구조

| Task | 내용 | 도메인 | 담당 | 의존성 |
|------|------|--------|------|--------|
| 19-1-1 | FIX-2: 3단계 계층 매칭 도입 | [BE] | backend-dev | 없음 |
| 19-1-2 | FIX-1: 공백 분리 로직 개선 | [BE] | backend-dev | 19-1-1 |
| 19-1-3 | FIX-3+4: 유틸 함수 개선 | [BE] | backend-dev | 19-1-2 |
| 19-1-4 | FIX-5: FE 이중 정제 제거 | [FE] | frontend-dev | 19-1-3 (BE 정제 완료 후) |
| 19-1-5 | 통합 테스트 | [TEST] | tester | 19-1-4 |

## 완료 기준

- [ ] FIX-1~5 모두 적용
- [ ] "머신 러닝, 데이터 분석" → 쉼표 분리 정상 동작
- [ ] "화성" → 정확 매칭만, Tier 2/3 오매칭 없음
- [ ] "C++", "C#", "R&D" → 특수문자 유지
- [ ] "서버less" → garbled 판정 통과
- [ ] FE 이중 정제 제거 후 키워드 온전히 표시
- [ ] pytest 전체 통과
- [ ] GroupKeywordRecommender + ChunkLabelRecommender 양쪽 정상

## 리스크

| 리스크 | 심각도 | 대응 |
|--------|:------:|------|
| FIX-2 성능 (DB 쿼리 3단계) | 중간 | `Label.name` 인덱스 추가 검토 |
| LLM 응답 극단 포맷 | 중간 | 프롬프트 정규화 + 폴백 로직 |
| 공유 함수 영향도 | 낮음 | 양쪽 Recommender 테스트 |
