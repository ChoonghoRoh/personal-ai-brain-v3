# Task 17-2-1: [BE] ChunkLabelRecommender 전용 클래스 분리

**우선순위**: 17-2 내 1순위 (17-2-3 공통 유틸 후)
**예상 작업량**: 중간
**의존성**: 17-2-3 (공통 유틸 함수)
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

기존 recommendation_llm.py의 청크 라벨 추천 로직을 ChunkLabelRecommender 전용 클래스로 분리한다. 청크 텍스트 → 키워드 추출에 특화된 프롬프트와 컨텍스트 처리 로직을 독립 관리한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 신규 | `backend/services/reasoning/chunk_label_recommender.py` | ChunkLabelRecommender 클래스 (174줄) |

## §3. 작업 체크리스트 (Done Definition)

- [x] ChunkLabelRecommender 클래스 생성
- [x] recommend() 메서드: 청크 텍스트 입력 → 키워드 리스트 반환
- [x] 추출형 전용 프롬프트 관리
- [x] chunk_id 기반 청크 컨텍스트 조회
- [x] 공통 유틸(resolve_model, generate_keywords_via_llm) 활용

## §4. 참조

- [Phase 17 개발 요구사항 §5.3](../../../planning/260218-0830-phase17-개발-요구사항.md)
