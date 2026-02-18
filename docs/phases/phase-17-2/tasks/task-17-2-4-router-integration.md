# Task 17-2-4: [BE] labels_handlers.py 라우터 연동 수정

**우선순위**: 17-2 내 4순위
**예상 작업량**: 소
**의존성**: 17-2-1 (ChunkLabelRecommender), 17-2-2 (GroupKeywordRecommender)
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

기존 labels_handlers.py의 handle_suggest_keywords()가 recommend_labels_with_llm()을 직접 호출하던 것을 새로운 Recommender 클래스 호출로 전환한다. API 응답 형식은 변경하지 않는다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/routers/knowledge/labels_handlers.py` | import 변경, Recommender 클래스 인스턴스 생성 + 호출 |
| 수정 | `backend/routers/knowledge/labels.py` | 라우터 등록 확인 |
| 수정 | `backend/routers/knowledge/suggestions.py` | 추천 라우터 조정 |

## §3. 작업 체크리스트 (Done Definition)

- [x] handle_suggest_keywords() → chunk_id 유무에 따라 ChunkLabelRecommender / GroupKeywordRecommender 분기
- [x] /api/labels/groups/suggest-keywords 응답 형식 기존과 동일
- [x] 기존 추천 기능 정상 동작

## §4. 참조

- [Phase 17 개발 요구사항 §5.3](../../../planning/260218-0830-phase17-개발-요구사항.md)
