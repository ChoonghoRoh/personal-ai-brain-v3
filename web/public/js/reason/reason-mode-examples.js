/**
 * Reasoning Lab — 모드 예시 화면
 * 4개 모드별 예시 질문/결과를 미리보기 패널로 표시.
 */
(function () {
  "use strict";

  var EXAMPLES = {
    design_explain: {
      question: "라벨 시스템의 트리 구조는?",
      title: "설계/배경 설명 예시",
      content:
        '<div class="example-diagram">' +
        '<div class="example-diagram-title">구조 다이어그램</div>' +
        '<div class="example-tree">' +
        '<div class="tree-node tree-root">Label System</div>' +
        '<div class="tree-children">' +
        '<div class="tree-branch">' +
        '<div class="tree-node">Tree Structure</div>' +
        '<div class="tree-children">' +
        '<div class="tree-node tree-leaf">Parent-Child</div>' +
        '<div class="tree-node tree-leaf">Depth Limit</div>' +
        "</div>" +
        "</div>" +
        '<div class="tree-branch">' +
        '<div class="tree-node">Inheritance</div>' +
        '<div class="tree-children">' +
        '<div class="tree-node tree-leaf">Auto Propagation</div>' +
        "</div>" +
        "</div>" +
        "</div>" +
        "</div>" +
        '<p class="example-desc">설계 배경: 라벨의 계층 구조를 통해 지식을 체계적으로 분류하고, 상위 라벨의 속성이 하위로 전파됩니다.</p>' +
        "</div>",
    },
    risk_review: {
      question: "현재 아키텍처의 위험 요소는?",
      title: "리스크 분석 예시",
      content:
        '<div class="example-risk">' +
        '<table class="example-risk-table">' +
        "<thead><tr><th>위험 요소</th><th>영향도</th><th>발생 확률</th><th>등급</th></tr></thead>" +
        "<tbody>" +
        '<tr><td>단일 DB 의존</td><td>높음</td><td>중간</td><td class="risk-badge risk-high">HIGH</td></tr>' +
        '<tr><td>캐시 미적용</td><td>중간</td><td>높음</td><td class="risk-badge risk-medium">MED</td></tr>' +
        '<tr><td>인증 만료 처리</td><td>낮음</td><td>낮음</td><td class="risk-badge risk-low">LOW</td></tr>' +
        "</tbody>" +
        "</table>" +
        "</div>",
    },
    next_steps: {
      question: "다음 개발 우선순위는?",
      title: "다음 단계 제안 예시",
      content:
        '<div class="example-steps">' +
        '<div class="example-step-item">' +
        '<span class="example-step-num">1</span>' +
        '<div class="example-step-body">' +
        '<strong>API 성능 최적화</strong>' +
        "<p>캐시 레이어 도입 및 쿼리 최적화</p>" +
        "</div>" +
        "</div>" +
        '<div class="example-step-item">' +
        '<span class="example-step-num">2</span>' +
        '<div class="example-step-body">' +
        "<strong>테스트 커버리지 확대</strong>" +
        "<p>핵심 비즈니스 로직 단위 테스트 추가</p>" +
        "</div>" +
        "</div>" +
        '<div class="example-step-item">' +
        '<span class="example-step-num">3</span>' +
        '<div class="example-step-body">' +
        "<strong>문서화 강화</strong>" +
        "<p>API 스펙 및 아키텍처 결정 기록</p>" +
        "</div>" +
        "</div>" +
        "</div>",
    },
    history_trace: {
      question: "인증 시스템 변경 이력은?",
      title: "히스토리 추적 예시",
      content:
        '<div class="example-timeline">' +
        '<div class="example-timeline-item">' +
        '<div class="example-timeline-dot"></div>' +
        '<div class="example-timeline-body">' +
        '<div class="example-timeline-date">2025-12-01</div>' +
        "<p>JWT 기반 인증 도입</p>" +
        "</div>" +
        "</div>" +
        '<div class="example-timeline-item">' +
        '<div class="example-timeline-dot"></div>' +
        '<div class="example-timeline-body">' +
        '<div class="example-timeline-date">2026-01-15</div>' +
        "<p>리프레시 토큰 메커니즘 추가</p>" +
        "</div>" +
        "</div>" +
        '<div class="example-timeline-item">' +
        '<div class="example-timeline-dot"></div>' +
        '<div class="example-timeline-body">' +
        '<div class="example-timeline-date">2026-02-10</div>' +
        "<p>OAuth 2.0 소셜 로그인 연동</p>" +
        "</div>" +
        "</div>" +
        "</div>",
    },
  };

  var panelEl = null;

  function createPanel() {
    if (document.getElementById("mode-example-panel")) return;

    var panel = document.createElement("div");
    panel.id = "mode-example-panel";
    panel.className = "mode-example-panel";
    panel.style.display = "none";

    panel.innerHTML =
      '<div class="mode-example-header">' +
      '<span class="mode-example-badge">EXAMPLE</span>' +
      '<span id="mode-example-title" class="mode-example-title"></span>' +
      '<button type="button" class="mode-example-close" onclick="window.ReasonModeExamples.hide()" aria-label="닫기">&times;</button>' +
      "</div>" +
      '<div class="mode-example-question">' +
      '<span class="mode-example-q-label">Q:</span>' +
      '<span id="mode-example-question-text"></span>' +
      "</div>" +
      '<div id="mode-example-content" class="mode-example-content"></div>';

    // .reasoning-form 하단, .form-actions 이전에 삽입
    var form = document.getElementById("reasoning-form");
    var formActions = form ? form.querySelector(".form-actions") : null;
    if (form && formActions) {
      form.insertBefore(panel, formActions);
    } else {
      var reasoningForm = document.querySelector(".reasoning-form");
      if (reasoningForm) reasoningForm.appendChild(panel);
    }

    panelEl = panel;
  }

  function show(mode) {
    if (!panelEl) createPanel();
    var example = EXAMPLES[mode];
    if (!example) {
      hide();
      return;
    }

    var titleEl = document.getElementById("mode-example-title");
    var questionEl = document.getElementById("mode-example-question-text");
    var contentEl = document.getElementById("mode-example-content");

    if (titleEl) titleEl.textContent = example.title;
    if (questionEl) questionEl.textContent = example.question;
    if (contentEl) contentEl.innerHTML = example.content;
    if (panelEl) panelEl.style.display = "block";
  }

  function hide() {
    if (panelEl) panelEl.style.display = "none";
  }

  function init() {
    createPanel();

    var modeSelect = document.getElementById("mode");
    if (modeSelect) {
      modeSelect.addEventListener("change", function () {
        show(modeSelect.value);
      });
    }

    // form submit 시 숨기기
    var form = document.getElementById("reasoning-form");
    if (form) {
      form.addEventListener("submit", function () {
        hide();
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.ReasonModeExamples = {
    show: show,
    hide: hide,
    init: init,
  };
})();
