# Task 9-3-1: Reasoning AI 추천/샘플 기능 업그레이드 — 수행 결과 보고서

**Task ID**: 9-3-1  
**Task 명**: Reasoning AI 추천/샘플 기능 업그레이드  
**우선순위**: 9-3 내 2순위  
**상태**: ✅ 1차 구현 완료  
**완료일**: 2026-02-01  
**기준 문서**: [task-9-3-1-reasoning-recommendation.md](./tasks/task-9-3-1-reasoning-recommendation.md)

---

## 1. 목표 및 범위

| 항목 | 내용 |
|------|------|
| 목표 | 템플릿 기반 Reasoning을 LLM 기반 동적 추론으로 업그레이드하고, 관련 청크/라벨/질문 추천 기능 추가 |
| 범위 | RecommendationService, Recommendations API, DynamicReasoningService, Reason API 확장, Web UI(Reasoning Lab) |
| 의존성 | Task 9-3-3 (RAG 강화) 완료 후 진행 |

---

## 2. 구현 완료 항목

### 2.1 RecommendationService

| 항목 | 상태 | 비고 |
|------|------|------|
| `backend/services/reasoning/recommendation_service.py` 생성 | ✅ | RecommendationService |
| recommend_related_chunks() | ✅ | 관계·Hybrid·동일 라벨 기반 |
| recommend_labels() | ✅ | 키워드·유사 청크 라벨 |
| generate_sample_questions() | ✅ | Ollama 기반 |
| suggest_exploration() | ✅ | 프로젝트/라벨 제안 |

### 2.2 Recommendations API

| 항목 | 상태 | 비고 |
|------|------|------|
| `backend/routers/reasoning/recommendations.py` 생성 | ✅ | prefix /api/reason/recommendations |
| GET /chunks | ✅ | 관련 청크 추천 |
| GET /labels | ✅ | 라벨 추천 |
| GET /questions | ✅ | 샘플 질문 생성 |
| GET /explore | ✅ | 추가 탐색 제안 |

### 2.3 LLM 기반 동적 추론

| 항목 | 상태 | 비고 |
|------|------|------|
| `backend/services/reasoning/dynamic_reasoning_service.py` 생성 | ✅ | DynamicReasoningService |
| 모드별 프롬프트 (design_explain, risk_review, next_steps 등) | ✅ | Ollama 호출 |
| reason.py: LLM 우선, 실패 시 템플릿 폴백 | ✅ | generate_reasoning_answer 개선 |
| ReasonResponse에 recommendations 필드 | ✅ | related_chunks, suggested_labels, sample_questions, explore_more |

### 2.4 Web UI (Reasoning Lab)

| 항목 | 상태 | 비고 |
|------|------|------|
| web/src/pages/reason.html | ✅ | 관련 정보 섹션, 토글 버튼 |
| web/public/js/reason/reason.js | ✅ | displayRecommendations, 샘플 질문 클릭 시 폼 적용 |
| web/public/css/reason.css | ✅ | 추천 카드·태그·샘플 질문·탐색 스타일 |

### 2.5 테스트 및 검증

| 항목 | 상태 | 비고 |
|------|------|------|
| tests/test_reasoning_recommendations.py | ✅ | 단위 테스트 통과 |
| UI 기능 테스트 | ⏸ 선택 | 사용자 테스트 체크리스트 참고 |

---

## 3. 생성·수정 파일

### 신규 생성

| 파일 | 용도 |
|------|------|
| `backend/services/reasoning/recommendation_service.py` | 추천 로직 |
| `backend/routers/reasoning/recommendations.py` | 추천 API |
| `backend/services/reasoning/dynamic_reasoning_service.py` | LLM 동적 추론 |
| `tests/test_reasoning_recommendations.py` | 추천 기능 테스트 |

### 수정

| 파일 | 수정 내용 |
|------|----------|
| `backend/routers/reasoning/reason.py` | DynamicReasoningService 우선 사용, recommendations 필드 |
| `backend/routers/reasoning/__init__.py` | recommendations 라우터 |
| `backend/services/reasoning/__init__.py` | 새 서비스 export |
| `backend/main.py` | recommendations 라우터 등록 |
| `backend/services/reasoning/reasoning_chain_service.py` | search() 인자 수정 (limit → top_k) |
| `web/src/pages/reason.html` | 관련 정보 섹션, 토글 |
| `web/public/js/reason/reason.js` | 추천 표시·샘플 질문 클릭 |
| `web/public/css/reason.css` | 추천 UI 스타일 |

---

## 4. 테스트 결과

| 테스트 | 결과 | 비고 |
|--------|------|------|
| test_reasoning_recommendations.py | 통과 | API·서비스 동작 확인 |
| 기존 reason API | 정상 | 폴백 시 기존 템플릿 응답 |

---

## 5. 미완료·선택 항목

- **UI 기능 테스트**: 브라우저/수동 테스트는 사용자 테스트 체크리스트에서 별도 진행.
- **Ollama 미동작 시**: DynamicReasoningService 실패 시 자동으로 기존 템플릿 응답 사용.

---

## 6. 비고

- Ollama 서버 필요 (generate_sample_questions, 동적 추론).
- Reasoning Lab 페이지에서 "관련 정보" 토글로 추천 청크/라벨/샘플 질문/추가 탐색 확인 가능.
- 샘플 질문 클릭 시 해당 질문이 질의 폼에 반영됨.
