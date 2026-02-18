# Task 17-2-3: [BE] recommendation_llm.py 공통 유틸 함수 추출

**우선순위**: 17-2 내 최우선 (다른 Task의 선행)
**예상 작업량**: 중간
**의존성**: 없음
**담당 팀원**: backend-dev
**상태**: 완료

---

## §1. 개요

recommendation_llm.py에서 두 Recommender가 공통으로 사용할 유틸리티 함수를 추출한다. 모델 해결(resolve_model), LLM 키워드 생성(generate_keywords_via_llm), 한국어 키워드 정제 함수를 분리하여 재사용 가능하게 한다.

## §2. 파일 변경 계획

| 구분 | 파일 | 변경 내용 |
|------|------|----------|
| 수정 | `backend/services/reasoning/recommendation_llm.py` | 공통 함수 추출, 기존 함수 리팩토링 (396줄→축소) |
| 수정 | `backend/utils/korean_utils.py` | 키워드 정제 함수 강화 (68줄 추가) |

## §3. 작업 체크리스트 (Done Definition)

- [x] resolve_model() — 모델 이름 해결 + 폴백 로직
- [x] generate_keywords_via_llm() — Ollama 호출 + 응답 파싱 공통화
- [x] 한국어 키워드 정제 (clean, normalize, dedup) 함수
- [x] recommendation_llm.py 기존 공개 인터페이스 하위 호환 유지

## §4. 참조

- [Phase 17 개발 요구사항 §5.4](../../../planning/260218-0830-phase17-개발-요구사항.md)
