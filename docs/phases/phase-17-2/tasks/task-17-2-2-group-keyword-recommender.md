# Task 17-2-2: [BE] GroupKeywordRecommender 전용 클래스 분리

**우선순위**: 17-2 내 2순위 (17-2-3 공통 유틸 후, 17-2-1과 병렬)
**예상 작업량**: 중간
**의존성**: 17-2-3 (공통 유틸 함수)
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

기존 recommendation_llm.py의 그룹 키워드 추천 로직을 GroupKeywordRecommender 전용 클래스로 분리한다. 그룹 설명 → 키워드 생성에 특화된 프롬프트(few-shot 포함)와 기존 키워드 제외 로직을 독립 관리한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 신규 | `backend/services/reasoning/group_keyword_recommender.py` | GroupKeywordRecommender 클래스 (102줄) |

## §3. 작업 체크리스트 (Done Definition)

- [x] GroupKeywordRecommender 클래스 생성
- [x] recommend() 메서드: 그룹 설명 입력 → 키워드 리스트 반환
- [x] 생성형 전용 프롬프트 + few-shot 예시
- [x] 기존 키워드 제외(existing_keyword_names) 로직
- [x] 공통 유틸 활용

## §4. 참조

- [Phase 17 개발 요구사항 §5.3~§5.5](../../../planning/260218-0830-phase17-개발-요구사항.md)
