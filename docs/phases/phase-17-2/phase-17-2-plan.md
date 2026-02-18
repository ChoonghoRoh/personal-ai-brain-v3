# Phase 17-2 Plan — 키워드 추천 아키텍처 분리

**Phase**: 17-2
**목표**: 단일 함수(recommend_labels_with_llm) → 전용 Recommender 2종 클래스 분리
**선행**: Phase 17-1 완료
**기준 문서**: [Phase 17 개발 요구사항 §5](../../planning/260218-0830-phase17-개발-요구사항.md)

---

## 1. 배경

청크 라벨 추천과 키워드 그룹 키워드 추천이 동일한 함수(`recommend_labels_with_llm`)를 공유하며, chunk_id 유무로 분기하는 구조이다. 이로 인해:
- 단일 함수 과부하 (조건 분기 누적)
- 추출형/생성형 프롬프트 관리 혼재
- 한쪽 기능 수정 시 다른 쪽 영향도 확인 필요
- 테스트 복잡도 증가

## 2. 범위

| Task | 도메인 | 내용 | 담당 |
|------|--------|------|------|
| 17-2-1 | [BE] | ChunkLabelRecommender 전용 클래스 분리 | backend-dev |
| 17-2-2 | [BE] | GroupKeywordRecommender 전용 클래스 분리 | backend-dev |
| 17-2-3 | [BE] | recommendation_llm.py 공통 유틸 함수 추출 | backend-dev |
| 17-2-4 | [BE] | labels_handlers.py 라우터 연동 수정 | backend-dev |
| 17-2-5 | [BE] | 단위 테스트 23건 작성 | backend-dev |

## 3. 완료 기준

- [x] ChunkLabelRecommender: 청크 텍스트 → 키워드 추출 전용
- [x] GroupKeywordRecommender: 그룹 설명 → 키워드 생성 전용
- [x] 공통 유틸 (resolve_model, generate_keywords_via_llm 등) 분리
- [x] 기존 API 엔드포인트 동작 하위 호환 유지
- [x] 단위 테스트 23건 전건 통과

## 4. 의존성

- 17-2-3 (공통 유틸) → 17-2-1, 17-2-2 (각 Recommender가 공통 유틸 사용)
- 17-2-4 (라우터)는 17-2-1, 17-2-2 완료 후
- 17-2-5 (테스트)는 전체 구현 완료 후
- 권장 순서: 17-2-3 → 17-2-1 + 17-2-2 병렬 → 17-2-4 → 17-2-5

## 5. 리스크

| 리스크 | 대응 |
|--------|------|
| recommendation_llm.py 대규모 수정으로 기존 기능 깨짐 | 단위 테스트 23건으로 회귀 검증 |
| 프롬프트 분리 시 기존 추천 품질 저하 | 동일 프롬프트 유지, 클래스 구조만 분리 |
