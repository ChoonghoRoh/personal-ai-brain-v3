/**
 * Reasoning Lab — Model 레이어
 * 상수·전역 상태·데이터 형태 정의.
 * 의존성: 없음 (utils만 필요 시 사용)
 */
(function () {
  "use strict";

  /** 모드 ID → 설명 문구 */
  var MODE_DESCRIPTIONS = {
    design_explain:
      "설계 의도와 배경을 명확히 설명합니다. 왜 이렇게 설계했는지, 어떤 맥락에서 결정했는지를 파악할 때 사용합니다.",
    risk_review:
      "잠재적 리스크와 문제점을 식별합니다. 관계 그래프를 통해 영향도를 추적하고 위험 요소를 발견할 때 사용합니다.",
    next_steps:
      "현재 상태를 기반으로 논리적인 다음 단계를 제안합니다. 프로젝트 진행 방향이나 개선 사항을 찾을 때 사용합니다.",
    history_trace:
      "지식의 진화와 맥락을 시간적/논리적 순서로 추적합니다. 의사결정 과정이나 변화 흐름을 이해할 때 사용합니다.",
  };

  /** 모드 ID → 시각화 섹션 제목 */
  var MODE_VIZ_TITLES = {
    design_explain: "📐 설계/배경 시각화",
    risk_review: "⚠️ 리스크 매트릭스",
    next_steps: "🚀 다음 단계 로드맵",
    history_trace: "📜 히스토리 타임라인",
  };

  /**
   * Reasoning 실행 상태 (전역 단일 객체)
   * - taskId: 현재 진행 중인 태스크 ID
   * - elapsedTimerId: 경과 시간 setInterval ID
   * - eventSource: (미사용 시 null)
   * - startTime: 시작 시각 (ms)
   */
  var REASONING_STATE = {
    taskId: null,
    elapsedTimerId: null,
    eventSource: null,
    startTime: null,
  };

  // REASONING_REQUEST_SHAPE (주석): mode, inputs{ projects, labels }, question, model
  // REASONING_RESPONSE_SHAPE (주석): answer, context_chunks, relations, reasoning_steps, recommendations{ related_chunks, suggested_labels, sample_questions, explore_more }

  window.ReasonModel = {
    MODE_DESCRIPTIONS: MODE_DESCRIPTIONS,
    MODE_VIZ_TITLES: MODE_VIZ_TITLES,
    REASONING_STATE: REASONING_STATE,
  };
})();
