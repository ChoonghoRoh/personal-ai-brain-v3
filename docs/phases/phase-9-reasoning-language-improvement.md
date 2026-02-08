# Phase 9: Reasoning 결과 한자(중국어) 출력 개선 방안

**목적**: Reasoning/AI 결과가 한자(중국어, 中文)로 나오는 경우를 줄이고, 한국어만 출력되도록 개선  
**관련 코드**: `backend/services/reasoning/dynamic_reasoning_service.py`, `recommendation_service.py`, `backend/routers/ai/ai.py`  
**참고**: Master Plan 7.2 — "다국어 지원" 제외, **한국어 전용 프로젝트**

---

## 1. 원인

- LLM(Ollama/Claude 등)이 프롬프트 언어를 잘못 해석하거나, 학습 데이터 영향으로 **중국어(中文)** 로 답변하는 경우가 있음.
- Reasoning API(`POST /api/reason`), 추천(샘플 질문 등), AI 질의(`POST /api/ask`) 모두 동일 LLM을 사용하므로 동일 대응 필요.

---

## 2. 개선 방안

### 2.1 프롬프트 강화 (우선 적용)

| 위치                             | 내용                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------- |
| **dynamic_reasoning_service.py** | 모든 모드 프롬프트에 **「반드시 한국어로만 답변하세요. 중국어(中文)로 답변하지 마세요.」** 추가   |
| **recommendation_service.py**    | 샘플 질문 생성 프롬프트에 **「한국어로만 작성하세요. 中文 사용 금지.」** 추가                     |
| **ai.py**                        | 기존대로 **「한국어로만 답변하세요」** 유지 + 필요 시 **「중국어(中文)로 답변하지 마세요」** 명시 |

- 프롬프트 **맨 앞** 또는 **맨 뒤**에 언어 제약을 한 문장으로 반복하면 LLM 준수율이 높아짐.

### 2.2 후처리 (선택)

- **중국어 비중이 높은 문단 제거**:  
  출력 텍스트를 문단 단위로 나누고, 한자(중국어) 비율이 임계값을 넘는 문단은 제거하거나,  
  "해당 부분은 한국어로만 제공되는 시스템이라 다른 언어로 출력된 내용은 생략했습니다" 같은 안내로 대체.
- **구현 위치**:
  - Reasoning: `DynamicReasoningService._postprocess_reasoning()`
  - AI 질의: `ai.py`의 `postprocess_answer()`
- **한자 비율 계산**:  
  문단 내 CJK 문자 중 한자(Unicode 범위) 비율 또는 `[\u4e00-\u9fff]` 등으로 중국어 구간 감지.

### 2.3 모델/파라미터

- **한국어 특화 모델** 사용 시 중국어 출력 가능성 감소 (예: EEVE-Korean 등).
- **temperature** 낮추면 지시 준수율이 올라가 언어 제약 준수에 유리함.

### 2.4 API/UI 안내

- API 문서 및 웹 UI에 **「응답 언어는 한국어만 지원합니다」** 명시.
- OpenAPI `description`에 "All responses are in Korean only. 中文 is not used." 등 추가 가능.

---

## 3. 적용 현황

| 항목                                       | 상태    | 비고                                                              |
| ------------------------------------------ | ------- | ----------------------------------------------------------------- |
| dynamic_reasoning_service.py 프롬프트 강화 | ✅ 적용 | NO_CONTEXT_PROMPT, MODE_PROMPTS에 「중국어(中文) 사용 금지」 추가 |
| recommendation_service.py 프롬프트 강화    | ✅ 적용 | 샘플 질문 생성에 「中文 사용 금지」 추가                          |
| \_postprocess_reasoning 중국어 문단 제거   | ✅ 적용 | 중국어 비중 높은 문단 제거 (선택 로직)                            |
| ai.py                                      | 유지    | 기존 한국어 지시 유지, 필요 시 동일 문구 추가                     |

---

## 4. 참고

- [phase-9-master-plan.md](phase-9-master-plan.md) §7.2 다국어 지원 제외
- [phase-9-final-summary-report.md](phase-9-final-summary-report.md) §5
- `backend/routers/ai/ai.py` — `build_prompt()`, `postprocess_answer()` (한국어/영어 후처리 참고)
