/**
 * Reasoning Lab — Control 레이어
 * 사용자 액션·SSE·UI 상태 전환·진행/취소/ETA.
 * 의존성: reason-model(REASONING_STATE), reason-render(displayResults, clearReasoningResults)
 */
(function () {
  "use strict";

  function state() {
    return window.ReasonModel && window.ReasonModel.REASONING_STATE
      ? window.ReasonModel.REASONING_STATE
      : { taskId: null, elapsedTimerId: null, eventSource: null, startTime: null };
  }

  function render() {
    return window.ReasonRender || {};
  }

  function esc(s) {
    return typeof escapeHtml === "function"
      ? escapeHtml(s)
      : String(s).replace(/[&<>"']/g, function (c) {
          var m = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
          return m[c] || c;
        });
  }

  // ---------- 요청 준비 ----------
  function prepareReasoningRequest() {
    var modeEl = document.getElementById("mode");
    var mode = modeEl ? modeEl.value : "design_explain";
    var questionEl = document.getElementById("question");
    var question = questionEl ? questionEl.value.trim() : "";

    var projectsSelect = document.getElementById("projects-select");
    var projectsInputEl = document.getElementById("projects");
    var projectsInput = projectsInputEl ? projectsInputEl.value.trim() : "";
    var selectedProjectIds = projectsSelect
      ? Array.from(projectsSelect.selectedOptions)
          .map(function (o) {
            return parseInt(o.value, 10);
          })
          .filter(function (n) {
            return !isNaN(n);
          })
      : [];
    var parsedProjectIds = projectsInput
      ? projectsInput
          .split(",")
          .map(function (p) {
            return parseInt(p.trim(), 10);
          })
          .filter(function (p) {
            return !isNaN(p);
          })
      : [];
    var projects = Array.from(new Set(selectedProjectIds.concat(parsedProjectIds)));

    var labelsSelect = document.getElementById("labels-select");
    var labelsInputEl = document.getElementById("labels");
    var labelsInput = labelsInputEl ? labelsInputEl.value.trim() : "";
    var selectedLabelNames = labelsSelect
      ? Array.from(labelsSelect.selectedOptions)
          .map(function (o) {
            return o.value.trim();
          })
          .filter(Boolean)
      : [];
    var parsedLabelNames = labelsInput
      ? labelsInput
          .split(",")
          .map(function (l) {
            return l.trim();
          })
          .filter(Boolean)
      : [];
    var labels = Array.from(new Set(selectedLabelNames.concat(parsedLabelNames)));

    var modelSelect = document.getElementById("reason-model");
    var model = modelSelect && modelSelect.value ? modelSelect.value.trim() : null;

    // Phase 15-3: 문서 필터
    var filters = null;
    if (window.__reasonDocumentIds && window.__reasonDocumentIds.length > 0) {
      filters = { document_ids: window.__reasonDocumentIds };
    }

    return {
      mode: mode,
      inputs: { projects: projects, labels: labels },
      question: question || null,
      model: model || null,
      filters: filters,
    };
  }

  // ---------- 진행 단계·타이머·ETA ----------
  function updateProgressStage(currentStage, message, percent) {
    var stages = document.querySelectorAll(".progress-stage");
    var connectors = document.querySelectorAll(".progress-connector");
    stages.forEach(function (stage, index) {
      var stageNum = index + 1;
      stage.classList.remove("pending", "active", "completed");
      if (stageNum < currentStage) stage.classList.add("completed");
      else if (stageNum === currentStage) stage.classList.add("active");
      else stage.classList.add("pending");
    });
    connectors.forEach(function (connector, index) {
      var connectorNum = index + 1;
      connector.classList.remove("active", "completed");
      if (connectorNum < currentStage) connector.classList.add("completed");
      else if (connectorNum === currentStage) connector.classList.add("active");
    });
    var progressBar = document.getElementById("progress-bar");
    var pct = percent != null ? percent : 0;
    if (progressBar) progressBar.style.width = pct + "%";
    var progressBarContainer = document.querySelector(".progress-bar-container");
    if (progressBarContainer) progressBarContainer.setAttribute("aria-valuenow", String(Math.round(pct)));
    var progressMessage = document.getElementById("progress-message");
    if (progressMessage) progressMessage.textContent = "⏳ " + (message || "준비 중...");
  }

  function startElapsedTimer() {
    var elapsedEl = document.getElementById("reasoning-elapsed-text");
    if (!elapsedEl) return;
    elapsedEl.textContent = "잠시만 기다려주세요...";
    var st = state();
    if (st.elapsedTimerId) {
      clearInterval(st.elapsedTimerId);
      st.elapsedTimerId = null;
    }
    st.startTime = Date.now();
    st.elapsedTimerId = setInterval(function () {
      var seconds = Math.floor((Date.now() - st.startTime) / 1000);
      var el = document.getElementById("reasoning-elapsed-text");
      if (el) el.textContent = seconds <= 1 ? "잠시만 기다려주세요..." : "경과 시간: " + seconds + "초";
    }, 1000);
  }

  function stopElapsedTimer() {
    var st = state();
    if (st.elapsedTimerId) {
      clearInterval(st.elapsedTimerId);
      st.elapsedTimerId = null;
    }
  }

  function loadAndDisplayETA() {
    var modeEl = document.getElementById("mode");
    var mode = modeEl ? modeEl.value : "design_explain";
    fetch("/api/reason/eta?mode=" + encodeURIComponent(mode))
      .then(function (response) {
        if (response.ok) return response.json();
        return null;
      })
      .then(function (data) {
        var etaText = document.getElementById("eta-text");
        if (etaText) etaText.textContent = data && data.display_text ? "예상 소요 시간: " + data.display_text : "예상 소요 시간: 약 30초~1분";
      })
      .catch(function () {
        var etaText = document.getElementById("eta-text");
        if (etaText) etaText.textContent = "예상 소요 시간: 약 30초~1분";
      });
  }

  // ---------- UI 상태: 초기화·복원·비우기 ----------
  function resetProgressStages() {
    document.querySelectorAll(".progress-stage").forEach(function (stage) {
      stage.classList.remove("pending", "active", "completed");
      stage.classList.add("pending");
    });
    document.querySelectorAll(".progress-connector").forEach(function (connector) {
      connector.classList.remove("active", "completed");
    });
    var progressBar = document.getElementById("progress-bar");
    if (progressBar) {
      progressBar.style.width = "0%";
      progressBar.style.background = "";
    }
    var progressContainer = document.querySelector(".results-loading");
    if (progressContainer) progressContainer.classList.remove("progress-cancelled");
    var progressMessage = document.getElementById("progress-message");
    if (progressMessage) progressMessage.textContent = "⏳ Reasoning 준비 중...";
  }

  function initializeReasoningUI() {
    var submitBtn = document.getElementById("submit-btn");
    var cancelBtn = document.getElementById("cancel-btn");
    var resultsDiv = document.getElementById("results");
    var resultsLoading = document.getElementById("results-loading");
    var resultsContent = document.getElementById("results-content");
    var errorDiv = document.getElementById("error-message");

    render().clearReasoningResults && render().clearReasoningResults();
    resetProgressStages();

    if (errorDiv) errorDiv.style.display = "none";
    if (resultsContent) resultsContent.style.display = "none";
    if (resultsLoading) resultsLoading.style.display = "block";
    if (resultsDiv) {
      resultsDiv.style.display = "block";
      resultsDiv.classList.add("active");
    }
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.setAttribute("aria-busy", "true");
      submitBtn.textContent = "⏳ Reasoning 중";
    }
    if (cancelBtn) cancelBtn.style.display = "inline-block";
    startElapsedTimer();
    loadAndDisplayETA();
  }

  function restoreReasoningUI() {
    stopElapsedTimer();
    var resultsLoading = document.getElementById("results-loading");
    if (resultsLoading) resultsLoading.style.display = "none";
    var submitBtn = document.getElementById("submit-btn");
    var cancelBtn = document.getElementById("cancel-btn");
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.removeAttribute("aria-busy");
      submitBtn.textContent = "🚀 Reasoning 실행";
    }
    if (cancelBtn) cancelBtn.style.display = "none";
    state().taskId = null;
  }

  // ---------- 취소 ----------
  function showCancelledState() {
    var progressMessage = document.getElementById("progress-message");
    if (progressMessage) progressMessage.textContent = "❌ 사용자에 의해 취소됨";
    var progressContainer = document.querySelector(".results-loading");
    if (progressContainer) progressContainer.classList.add("progress-cancelled");
    var progressBar = document.getElementById("progress-bar");
    if (progressBar) progressBar.style.background = "#ef4444";
  }

  async function cancelReasoning() {
    var st = state();
    if (!st.taskId) {
      console.warn("취소할 태스크가 없습니다.");
      restoreReasoningUI();
      return;
    }
    try {
      if (st.eventSource) {
        st.eventSource.close();
        st.eventSource = null;
      }
      var response = await fetch("/api/reason/" + st.taskId + "/cancel", { method: "POST" });
      var result = await response.json();
      console.log("취소 결과:", result);
      showCancelledState();
      restoreReasoningUI();
      st.taskId = null;
      st.elapsedTimerId = null;
      // 11-5-3: 취소 후 결과·답변 영역 초기화 — 재실행 전 UI 정리
      setTimeout(function () {
        render().clearReasoningResults && render().clearReasoningResults();
        var resultsContent = document.getElementById("results-content");
        var resultsDiv = document.getElementById("results");
        if (resultsContent) resultsContent.style.display = "none";
        if (resultsDiv) resultsDiv.classList.remove("active");
      }, 800);
    } catch (error) {
      console.error("취소 요청 실패:", error);
      restoreReasoningUI();
      render().clearReasoningResults && render().clearReasoningResults();
    }
  }

  // ---------- 스트리밍 답변 (Phase 10-4-1) ----------
  function showStreamingAnswer(token) {
    var resultsContent = document.getElementById("results-content");
    if (resultsContent && resultsContent.style.display === "none") {
      resultsContent.style.display = "block";
    }
    var resultsDiv = document.getElementById("results");
    if (resultsDiv && resultsDiv.style.display === "none") {
      resultsDiv.style.display = "block";
      resultsDiv.classList.add("active");
    }
    var resultsLoading = document.getElementById("results-loading");
    if (resultsLoading && resultsLoading.style.display !== "none") {
      resultsLoading.style.display = "none";
    }
    var answerDiv = document.getElementById("answer");
    if (answerDiv) answerDiv.textContent += token;
  }

  // ---------- 에러 ----------
  function showReasoningError(error) {
    var errorDiv = document.getElementById("error-message");
    var errorMessage = "Reasoning 실행 중 오류가 발생했습니다.";
    if (error && (error.message || "").indexOf("Failed to fetch") !== -1) errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
    else if (error && error.message) errorMessage = error.message;
    if (errorDiv) {
      errorDiv.innerHTML =
        '<div style="padding: 15px; background: #fee2e2; border: 1px solid #dc2626; border-radius: 6px; color: #dc2626;">' +
        "<strong>❌ 오류 발생</strong>" +
        '<p style="margin: 10px 0 0 0;">' +
        esc(errorMessage) +
        "</p>" +
        "</div>";
      errorDiv.style.display = "block";
    }
    var resultsLoading = document.getElementById("results-loading");
    var resultsContent = document.getElementById("results-content");
    if (resultsLoading) resultsLoading.style.display = "none";
    if (resultsContent) resultsContent.style.display = "block";
  }

  // ---------- SSE·실행·결과 처리 ----------
  function handleSSEEvent(eventType, data) {
    var st = state();
    switch (eventType) {
      case "progress":
        if (data.task_id && !st.taskId) st.taskId = data.task_id;
        updateProgressStage(data.stage, data.message, data.percent);
        break;
      case "answer_token":
        showStreamingAnswer(data.token);
        break;
      case "result":
        processReasoningResult(data);
        break;
      case "cancelled":
        showCancelledState();
        restoreReasoningUI();
        break;
      case "error":
        showReasoningError(new Error(data.message));
        restoreReasoningUI();
        break;
      case "done":
        // 11-5-3: ETA 피드백 — 실제 소요 시간 전송 (향후 예측 보정용)
        if (st.startTime) {
          var actualSeconds = Math.round((Date.now() - st.startTime) / 1000);
          var modeEl = document.getElementById("mode");
          var mode = modeEl ? modeEl.value : "design_explain";
          fetch("/api/reason/eta/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mode: mode, actual_seconds: actualSeconds }),
          }).catch(function () {});
        }
        restoreReasoningUI();
        break;
      default:
        console.log("알 수 없는 이벤트:", eventType, data);
    }
  }

  function processReasoningResult(result) {
    var resultsLoading = document.getElementById("results-loading");
    var resultsContent = document.getElementById("results-content");
    var resultsDiv = document.getElementById("results");
    if (resultsLoading) resultsLoading.style.display = "none";
    if (resultsContent) resultsContent.style.display = "block";
    if (resultsDiv) {
      resultsDiv.style.display = "block";
      resultsDiv.classList.add("active");
    }
    if (render().displayResults) render().displayResults(result);
  }

  async function runReasoning(event) {
    if (event && event.preventDefault) event.preventDefault();
    var st = state();
    initializeReasoningUI();

    var requestBody = prepareReasoningRequest();
    try {
      var response = await fetch("/api/reason/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });
      if (!response.ok) throw new Error("HTTP " + response.status + ": " + response.statusText);

      st.taskId = response.headers.get("X-Task-ID");

      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var buffer = "";
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buffer += decoder.decode(chunk.value, { stream: true });
        var lines = buffer.split("\n");
        buffer = lines.pop() || "";
        var eventType = null;
        var eventData = null;
        for (var i = 0; i < lines.length; i++) {
          var line = lines[i];
          if (line.indexOf("event: ") === 0) {
            eventType = line.slice(7).trim();
          } else if (line.indexOf("data: ") === 0) {
            try {
              eventData = JSON.parse(line.slice(6));
            } catch (e) {
              console.warn("JSON 파싱 실패:", line);
              continue;
            }
            if (eventType && eventData) {
              handleSSEEvent(eventType, eventData);
              eventType = null;
              eventData = null;
            }
          }
        }
      }
    } catch (error) {
      console.error("Reasoning 실행 실패:", error);
      showReasoningError(error);
      restoreReasoningUI();
    }
  }

  window.ReasonControl = {
    runReasoning: runReasoning,
    cancelReasoning: cancelReasoning,
    prepareReasoningRequest: prepareReasoningRequest,
    initializeReasoningUI: initializeReasoningUI,
    restoreReasoningUI: restoreReasoningUI,
    updateProgressStage: updateProgressStage,
    resetProgressStages: resetProgressStages,
    startElapsedTimer: startElapsedTimer,
    stopElapsedTimer: stopElapsedTimer,
    loadAndDisplayETA: loadAndDisplayETA,
    showCancelledState: showCancelledState,
    showStreamingAnswer: showStreamingAnswer,
    showReasoningError: showReasoningError,
    handleSSEEvent: handleSSEEvent,
    processReasoningResult: processReasoningResult,
  };
})();
