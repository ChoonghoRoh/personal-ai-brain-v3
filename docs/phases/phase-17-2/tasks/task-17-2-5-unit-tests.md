# Task 17-2-5: [BE] 단위 테스트 23건 작성

**우선순위**: 17-2 내 최종
**예상 작업량**: 중간
**의존성**: 17-2-1, 17-2-2, 17-2-3, 17-2-4 (전체 구현 완료 후)
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

새로 분리된 ChunkLabelRecommender, GroupKeywordRecommender, 공통 유틸 함수에 대한 단위 테스트 23건을 작성한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 신규 | `tests/test_keyword_recommenders.py` | 단위 테스트 23건 (327줄) |

## §3. 작업 체크리스트 (Done Definition)

- [x] ChunkLabelRecommender 테스트 케이스
  - 정상 추출, 빈 텍스트, 모델 폴백, 에러 처리
- [x] GroupKeywordRecommender 테스트 케이스
  - 정상 생성, 기존 키워드 제외, few-shot 동작, 에러 처리
- [x] 공통 유틸 함수 테스트
  - resolve_model, generate_keywords_via_llm, 한국어 정제
- [x] pytest tests/test_keyword_recommenders.py → 23건 전건 PASS

## §4. 참조

- [Phase 17 Master Plan §5](../../phase-17-master-plan.md)
