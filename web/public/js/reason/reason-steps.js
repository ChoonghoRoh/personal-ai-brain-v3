/**
 * Reasoning Lab — Step UI 컴포넌트
 * 순차 진행 Step 1~4 프레임 생성 및 상태 관리.
 * Step 1: 컨텍스트 수집 / Step 2: 분석 중 / Step 3: 결과 / Step 4: 후속 작업
 */
(function () {
  "use strict";

  var STEPS = [
    { num: 1, label: "컨텍스트 수집", icon: "📋" },
    { num: 2, label: "분석 중", icon: "🔍" },
    { num: 3, label: "결과", icon: "📊" },
    { num: 4, label: "후속 작업", icon: "🚀" },
  ];

  var STATE_PENDING = "pending";
  var STATE_ACTIVE = "active";
  var STATE_COMPLETED = "completed";

  var stepStates = [STATE_PENDING, STATE_PENDING, STATE_PENDING, STATE_PENDING];
  var containerEl = null;
  var initialized = false;

  // ---------- DOM 생성 ----------
  function createStepContainer() {
    var resultsDiv = document.getElementById("results");
    if (!resultsDiv || document.getElementById("reason-steps-container")) return;

    var container = document.createElement("div");
    container.id = "reason-steps-container";
    container.className = "reason-steps-ui";
    container.setAttribute("role", "group");
    container.setAttribute("aria-label", "Reasoning 진행 단계");

    // Step 헤더 바
    var headerBar = document.createElement("div");
    headerBar.className = "steps-header-bar";

    STEPS.forEach(function (step, idx) {
      if (idx > 0) {
        var connector = document.createElement("div");
        connector.className = "step-connector";
        connector.setAttribute("data-after-step", String(idx));
        headerBar.appendChild(connector);
      }
      var stepIndicator = document.createElement("div");
      stepIndicator.className = "step-indicator pending";
      stepIndicator.setAttribute("data-step", String(step.num));
      stepIndicator.setAttribute("aria-label", "Step " + step.num + ": " + step.label);

      var iconSpan = document.createElement("span");
      iconSpan.className = "step-indicator-icon";
      iconSpan.textContent = step.icon;

      var numSpan = document.createElement("span");
      numSpan.className = "step-indicator-num";
      numSpan.textContent = String(step.num);

      var checkSpan = document.createElement("span");
      checkSpan.className = "step-indicator-check";
      checkSpan.textContent = "\u2713";

      var labelSpan = document.createElement("span");
      labelSpan.className = "step-indicator-label";
      labelSpan.textContent = step.label;

      stepIndicator.appendChild(iconSpan);
      stepIndicator.appendChild(numSpan);
      stepIndicator.appendChild(checkSpan);
      stepIndicator.appendChild(labelSpan);
      headerBar.appendChild(stepIndicator);
    });

    container.appendChild(headerBar);

    // Step 본문 패널들
    var panelsWrapper = document.createElement("div");
    panelsWrapper.className = "steps-panels";

    // Step 1: 컨텍스트 수집 — 수집된 문서 목록
    var panel1 = createPanel(1);
    var docsList = document.createElement("div");
    docsList.id = "step1-docs-list";
    docsList.className = "step-docs-list";
    docsList.innerHTML = '<p class="step-empty-msg">수집된 문서가 여기에 표시됩니다.</p>';
    panel1.querySelector(".step-panel-body").appendChild(docsList);
    panelsWrapper.appendChild(panel1);

    // Step 2: 분석 중 — 프로그레스 바 + 미리보기
    var panel2 = createPanel(2);
    var body2 = panel2.querySelector(".step-panel-body");

    var progressWrap = document.createElement("div");
    progressWrap.className = "step2-progress-wrap";
    var progressBarBg = document.createElement("div");
    progressBarBg.className = "step2-progress-bg";
    var progressBarFill = document.createElement("div");
    progressBarFill.id = "step2-progress-bar";
    progressBarFill.className = "step2-progress-fill";
    progressBarBg.appendChild(progressBarFill);
    progressWrap.appendChild(progressBarBg);
    body2.appendChild(progressWrap);

    var previewArea = document.createElement("div");
    previewArea.id = "step2-preview";
    previewArea.className = "step2-preview";
    previewArea.style.display = "none";
    var previewLabel = document.createElement("div");
    previewLabel.className = "step2-preview-label";
    previewLabel.textContent = "중간 결과 미리보기:";
    var previewContent = document.createElement("div");
    previewContent.id = "step2-preview-content";
    previewContent.className = "step2-preview-content";
    previewArea.appendChild(previewLabel);
    previewArea.appendChild(previewContent);
    body2.appendChild(previewArea);
    panelsWrapper.appendChild(panel2);

    // Step 3: 결과 — 기존 results-content 래핑 영역
    var panel3 = createPanel(3);
    var body3 = panel3.querySelector(".step-panel-body");
    var resultSlot = document.createElement("div");
    resultSlot.id = "step3-result-slot";
    resultSlot.className = "step3-result-slot";
    body3.appendChild(resultSlot);
    panelsWrapper.appendChild(panel3);

    // Step 4: 후속 작업 — 버튼 그룹
    var panel4 = createPanel(4);
    var body4 = panel4.querySelector(".step-panel-body");
    var actionsGroup = document.createElement("div");
    actionsGroup.id = "step4-actions";
    actionsGroup.className = "step4-actions";
    body4.appendChild(actionsGroup);
    panelsWrapper.appendChild(panel4);

    container.appendChild(panelsWrapper);

    // #results 안 맨 앞에 삽입 (#results-loading 이전)
    var loadingDiv = document.getElementById("results-loading");
    if (loadingDiv) {
      resultsDiv.insertBefore(container, loadingDiv);
    } else {
      resultsDiv.insertBefore(container, resultsDiv.firstChild);
    }

    containerEl = container;
    initialized = true;
  }

  function createPanel(num) {
    var panel = document.createElement("div");
    panel.className = "step-panel";
    panel.id = "step-panel-" + num;
    panel.setAttribute("data-step", String(num));
    panel.style.display = "none";

    var panelBody = document.createElement("div");
    panelBody.className = "step-panel-body";
    panel.appendChild(panelBody);

    return panel;
  }

  // ---------- 상태 관리 ----------
  function updateIndicators() {
    STEPS.forEach(function (step, idx) {
      var el = document.querySelector('.step-indicator[data-step="' + step.num + '"]');
      if (!el) return;
      el.classList.remove(STATE_PENDING, STATE_ACTIVE, STATE_COMPLETED);
      el.classList.add(stepStates[idx]);
    });
    // connector 업데이트
    var connectors = document.querySelectorAll(".step-connector");
    connectors.forEach(function (conn) {
      var afterStep = parseInt(conn.getAttribute("data-after-step"), 10);
      conn.classList.remove(STATE_ACTIVE, STATE_COMPLETED);
      if (afterStep >= 1) {
        var prevState = stepStates[afterStep - 1];
        if (prevState === STATE_COMPLETED) conn.classList.add(STATE_COMPLETED);
        else if (prevState === STATE_ACTIVE) conn.classList.add(STATE_ACTIVE);
      }
    });
  }

  function showPanel(num) {
    STEPS.forEach(function (step) {
      var panel = document.getElementById("step-panel-" + step.num);
      if (panel) panel.style.display = step.num === num ? "block" : "none";
    });
  }

  function activate(num) {
    if (!initialized) createStepContainer();
    if (num < 1 || num > 4) return;

    // 이전 Step들 완료 처리
    for (var i = 0; i < num - 1; i++) {
      if (stepStates[i] !== STATE_COMPLETED) stepStates[i] = STATE_COMPLETED;
    }
    stepStates[num - 1] = STATE_ACTIVE;

    updateIndicators();
    showPanel(num);

    // Step 4 활성화 시 후속 작업 버튼 자동 구성
    if (num === 4) populateStep4Actions();

    // Step 컨테이너 표시
    if (containerEl) containerEl.style.display = "block";
  }

  // Step 4: 기존 버튼들을 Step 4 액션 영역으로 구성
  function populateStep4Actions() {
    var container = document.getElementById("step4-actions");
    if (!container || container.children.length > 0) return;

    var buttons = [
      { id: "step4-continue-btn", label: "이어서 질문", className: "step4-btn-continue", srcId: "continue-question-btn" },
      { id: "step4-export-btn", label: "PDF 내보내기", className: "step4-btn-export", srcId: "export-pdf-btn" },
      { id: "step4-share-btn", label: "공유", className: "step4-btn-share", srcId: "share-btn" },
      { id: "step4-save-btn", label: "저장", className: "step4-btn-save", srcId: "save-decision-btn" },
    ];

    buttons.forEach(function (def) {
      var el = document.createElement("button");
      el.type = "button";
      el.id = def.id;
      el.className = "btn step4-action-btn " + def.className;
      el.textContent = def.label;
      // 기존 버튼의 onclick 위임
      el.addEventListener("click", function () {
        var srcBtn = document.getElementById(def.srcId);
        if (srcBtn) srcBtn.click();
      });
      container.appendChild(el);
    });

    // 기존 continue-question-area 숨김 (Step 4가 대체)
    var continueArea = document.getElementById("continue-question-area");
    if (continueArea) continueArea.style.display = "none";
  }

  function complete(num) {
    if (num < 1 || num > 4) return;
    stepStates[num - 1] = STATE_COMPLETED;
    updateIndicators();
  }

  function reset() {
    stepStates = [STATE_PENDING, STATE_PENDING, STATE_PENDING, STATE_PENDING];
    updateIndicators();
    STEPS.forEach(function (step) {
      var panel = document.getElementById("step-panel-" + step.num);
      if (panel) panel.style.display = "none";
    });
    // 미리보기 초기화
    var preview = document.getElementById("step2-preview");
    if (preview) preview.style.display = "none";
    var previewContent = document.getElementById("step2-preview-content");
    if (previewContent) previewContent.textContent = "";
    var progressBar = document.getElementById("step2-progress-bar");
    if (progressBar) progressBar.style.width = "0%";
    // Step 1 문서 목록 초기화
    var docsList = document.getElementById("step1-docs-list");
    if (docsList) {
      docsList.innerHTML = '<p class="step-empty-msg">수집된 문서가 여기에 표시됩니다.</p>';
    }
    // Step 4 액션 초기화
    var actions = document.getElementById("step4-actions");
    if (actions) actions.innerHTML = "";

    if (containerEl) containerEl.style.display = "none";
  }

  // ---------- Step 2 미리보기 ----------
  function appendPreviewToken(token) {
    var preview = document.getElementById("step2-preview");
    var content = document.getElementById("step2-preview-content");
    if (!preview || !content) return;
    if (preview.style.display === "none") preview.style.display = "block";
    content.textContent += token;
  }

  function getPreviewContent() {
    var content = document.getElementById("step2-preview-content");
    return content ? content.textContent : "";
  }

  function updateProgress(percent) {
    var bar = document.getElementById("step2-progress-bar");
    if (bar) bar.style.width = Math.min(100, Math.max(0, percent)) + "%";
  }

  // ---------- Step 1 문서 목록 ----------
  function setDocsList(docs) {
    var docsList = document.getElementById("step1-docs-list");
    if (!docsList) return;
    if (!docs || docs.length === 0) {
      docsList.innerHTML = '<p class="step-empty-msg">수집된 문서가 없습니다.</p>';
      return;
    }
    var html = "";
    docs.forEach(function (doc) {
      var name = typeof doc === "string" ? doc : doc.name || doc.title || "문서";
      html += '<div class="step1-doc-item">' + escapeStr(name) + "</div>";
    });
    docsList.innerHTML = html;
  }

  // ---------- Step 4 후속 작업 ----------
  function setActions(actionButtons) {
    var container = document.getElementById("step4-actions");
    if (!container) return;
    container.innerHTML = "";
    if (!actionButtons || actionButtons.length === 0) return;
    actionButtons.forEach(function (btn) {
      var el = document.createElement("button");
      el.type = "button";
      el.className = "btn step4-action-btn " + (btn.className || "");
      el.textContent = btn.label || "";
      if (btn.onclick) el.onclick = btn.onclick;
      if (btn.id) el.id = btn.id;
      container.appendChild(el);
    });
  }

  function isActive(num) {
    if (num < 1 || num > 4) return false;
    return stepStates[num - 1] === STATE_ACTIVE;
  }

  function escapeStr(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  // ---------- 초기화 ----------
  function init() {
    createStepContainer();
  }

  // DOMContentLoaded 시 자동 초기화
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  window.ReasonSteps = {
    activate: activate,
    complete: complete,
    reset: reset,
    appendPreviewToken: appendPreviewToken,
    getPreviewContent: getPreviewContent,
    updateProgress: updateProgress,
    setDocsList: setDocsList,
    setActions: setActions,
    isActive: isActive,
    init: init,
  };
})();
