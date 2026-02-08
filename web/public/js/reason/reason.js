/**
 * Reasoning Lab — 진입점 (기능)
 * 초기화·이벤트 바인딩만 담당.
 * 의존성: reason-model, reason-common, reason-render, reason-control
 * 스크립트 로드 순서: model → common → render → control → reason.js
 */
(function () {
  "use strict";

  var ReasonModel = window.ReasonModel;
  var ReasonCommon = window.ReasonCommon;
  var ReasonRender = window.ReasonRender;
  var ReasonControl = window.ReasonControl;

  /**
   * HTML/폼에서 호출: Reasoning 실행
   */
  function runReasoning(event) {
    if (ReasonControl && ReasonControl.runReasoning) {
      ReasonControl.runReasoning(event);
    }
  }

  /**
   * 취소 버튼/HTML에서 호출: Reasoning 취소
   */
  function cancelReasoning() {
    if (ReasonControl && ReasonControl.cancelReasoning) {
      ReasonControl.cancelReasoning();
    }
  }

  /**
   * HTML onclick: 컨텍스트 탭 전환 (chunks | documents)
   */
  function switchContextTab(tab) {
    if (ReasonRender && ReasonRender.switchContextTab) {
      ReasonRender.switchContextTab(tab);
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initDarkMode();
    if (typeof initLayout === "function") initLayout();

    if (typeof renderHeader === "function") {
      renderHeader({
        title: "🧠 Reasoning Lab",
        subtitle: "지식 기반 추론 및 방향 제안",
        currentPath: "/reason",
      });
    }

    var modeEl = document.getElementById("mode");
    var modeDescEl = document.getElementById("mode-description");
    if (modeEl && modeDescEl && ReasonModel && ReasonModel.MODE_DESCRIPTIONS) {
      modeDescEl.textContent = ReasonModel.MODE_DESCRIPTIONS[modeEl.value] || "각 모드의 용도를 선택하세요";
      modeEl.addEventListener("change", function () {
        modeDescEl.textContent = ReasonModel.MODE_DESCRIPTIONS[this.value] || "각 모드의 용도를 선택하세요";
      });
    }

    if (typeof loadOllamaModelOptions === "function") {
      loadOllamaModelOptions("reason-model");
    }

    if (ReasonCommon && ReasonCommon.loadReasoningOptions) {
      ReasonCommon.loadReasoningOptions();
    }

    if (ReasonCommon && ReasonCommon.initSeedFromUrl) {
      ReasonCommon.initSeedFromUrl();
    }

    var cancelBtn = document.getElementById("cancel-btn");
    if (cancelBtn) {
      cancelBtn.addEventListener("click", cancelReasoning);
    }
  });

  /**
   * Phase 10-3-4: 다크 모드 토글
   */
  function toggleDarkMode() {
    var html = document.documentElement;
    var isDark = html.getAttribute("data-theme") === "dark";
    var newTheme = isDark ? "light" : "dark";
    html.setAttribute("data-theme", newTheme);
    try {
      localStorage.setItem("reason-theme", newTheme);
    } catch (e) {}
    if (window.ReasonVizLoader && window.ReasonVizLoader.updateTheme) {
      window.ReasonVizLoader.updateTheme(newTheme === "dark");
    }
  }

  /** 다크 모드 초기화 (저장값 → 시스템 설정) */
  function initDarkMode() {
    var saved = null;
    try {
      saved = localStorage.getItem("reason-theme");
    } catch (e) {}
    if (saved) {
      document.documentElement.setAttribute("data-theme", saved);
    } else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
      document.documentElement.setAttribute("data-theme", "dark");
    }
  }

  // ---------- Phase 10-4-2: 결과 공유 ----------
  var _lastReasoningResult = null;

  /** 결과를 전역에 저장 (processReasoningResult 시점에 호출) */
  function storeLastResult(result) {
    _lastReasoningResult = result;
  }

  function buildFallbackResult() {
    var questionEl = document.getElementById("question");
    var answerEl = document.getElementById("answer");
    var modeEl = document.getElementById("mode");
    var question = questionEl ? questionEl.value || "" : "";
    var answer = answerEl ? answerEl.textContent || "" : "";
    var mode = modeEl ? modeEl.value || null : null;
    if (!answer.trim()) return null;
    return {
      question: question,
      answer: answer,
      mode: mode,
      reasoning_steps: [],
      context_chunks: [],
      relations: [],
      recommendations: null,
    };
  }

  async function shareResult() {
    var r = _lastReasoningResult || buildFallbackResult();
    if (!r) {
      showToast("공유할 결과가 없습니다.", "error");
      return;
    }
    if (!_lastReasoningResult) _lastReasoningResult = r;
    try {
      var resp = await fetch("/api/reason/share", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: r.question || document.getElementById("question").value || "",
          answer: r.answer || "",
          mode: (document.getElementById("mode") || {}).value || null,
          reasoning_steps: r.reasoning_steps || [],
          context_chunks: r.context_chunks || [],
          relations: r.relations || [],
          recommendations: r.recommendations || null,
          expires_in_days: window.__shareExpiresDays || null,
          is_private: !!window.__shareIsPrivate,
        }),
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var data = await resp.json();
      var shareUrl = location.origin + data.url;
      try {
        await navigator.clipboard.writeText(shareUrl);
      } catch (e) {}
      showToast("공유 URL이 클립보드에 복사되었습니다: " + shareUrl);
    } catch (error) {
      console.error("공유 실패:", error);
      showToast("공유 URL 생성에 실패했습니다.", "error");
    }
  }

  function showToast(msg, type) {
    var toast = document.getElementById("share-toast");
    if (!toast) return;
    toast.textContent = msg;
    toast.className = "share-toast" + (type === "error" ? " toast-error" : " toast-success");
    toast.style.display = "block";
    setTimeout(function () {
      toast.style.display = "none";
    }, 4000);
  }

  // ---------- Phase 10-4-3: 의사결정 문서 저장 ----------
  function showSaveDecisionModal() {
    if (!_lastReasoningResult) {
      var fallback = buildFallbackResult();
      if (!fallback) {
        showToast("저장할 결과가 없습니다.", "error");
        return;
      }
      _lastReasoningResult = fallback;
    }
    var modal = document.getElementById("save-decision-modal");
    if (modal) {
      // 먼저 inline 스타일 완전 제거
      modal.removeAttribute("style");
      // 그 다음 display flex 설정
      modal.style.display = "flex";
      modal.classList.remove("hidden");
      // 강제 리플로우
      void modal.offsetHeight;
      modal.style.visibility = "visible";
      modal.style.opacity = "1";
    }
    var titleEl = document.getElementById("decision-title");
    if (titleEl) {
      titleEl.value = "";
      titleEl.focus();
    }
    var summaryEl = document.getElementById("decision-summary");
    if (summaryEl) summaryEl.value = "";
  }

  function closeSaveDecisionModal() {
    var modal = document.getElementById("save-decision-modal");
    if (modal) {
      modal.style.display = "none";
      modal.style.visibility = "hidden";
    }
  }

  async function saveDecision() {
    var titleEl = document.getElementById("decision-title");
    var summaryEl = document.getElementById("decision-summary");
    var title = titleEl ? titleEl.value.trim() : "";
    if (!title) {
      showToast("제목을 입력하세요.", "error");
      return;
    }
    var r = _lastReasoningResult || buildFallbackResult();
    if (!r) {
      showToast("저장할 결과가 없습니다.", "error");
      return;
    }
    if (!_lastReasoningResult) _lastReasoningResult = r;
    try {
      var resp = await fetch("/api/reason/decisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title,
          summary: summaryEl ? summaryEl.value.trim() || null : null,
          question: r.question || document.getElementById("question").value || "",
          answer: r.answer || "",
          mode: (document.getElementById("mode") || {}).value || null,
          reasoning_steps: r.reasoning_steps || [],
          context_chunks: r.context_chunks || [],
          relations: r.relations || [],
          recommendations: r.recommendations || null,
        }),
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      closeSaveDecisionModal();
      showToast("의사결정 문서가 저장되었습니다.");
      loadDecisionsList();
    } catch (error) {
      console.error("저장 실패:", error);
      showToast("저장에 실패했습니다.", "error");
    }
  }

  async function loadDecisionsList() {
    try {
      var resp = await fetch("/api/reason/decisions");
      if (!resp.ok) return;
      var data = await resp.json();
      var section = document.getElementById("decisions-list-section");
      var listEl = document.getElementById("decisions-list");
      if (!section || !listEl) return;
      if (!data.decisions || data.decisions.length === 0) {
        section.style.display = "none";
        return;
      }
      section.style.display = "block";
      listEl.innerHTML = data.decisions
        .map(function (d) {
          var date = d.created_at ? new Date(d.created_at).toLocaleDateString("ko-KR") : "";
          return (
            '<div class="decision-item" data-id="' +
            d.id +
            '">' +
            '<div class="decision-info">' +
            "<strong>" +
            escHtml(d.title) +
            "</strong>" +
            (d.summary ? '<p class="decision-summary-text">' + escHtml(d.summary) + "</p>" : "") +
            '<span class="decision-meta">' +
            escHtml(d.mode || "") +
            " · " +
            date +
            "</span>" +
            "</div>" +
            '<div class="decision-actions">' +
            '<button class="btn btn-sm" onclick="loadDecisionDetail(' +
            d.id +
            ')">보기</button>' +
            '<button class="btn btn-sm btn-danger" onclick="deleteDecision(' +
            d.id +
            ')">삭제</button>' +
            "</div></div>"
          );
        })
        .join("");
    } catch (e) {
      console.debug("decisions list load failed:", e);
    }
  }

  async function loadDecisionDetail(id) {
    try {
      var resp = await fetch("/api/reason/decisions/" + id);
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var data = await resp.json();
      if (ReasonRender && ReasonRender.displayResults) {
        ReasonRender.displayResults(data);
      }
      _lastReasoningResult = data;
      var resultsDiv = document.getElementById("results");
      var resultsContent = document.getElementById("results-content");
      var resultsLoading = document.getElementById("results-loading");
      if (resultsDiv) {
        resultsDiv.style.display = "block";
        resultsDiv.classList.add("active");
      }
      if (resultsLoading) resultsLoading.style.display = "none";
      if (resultsContent) resultsContent.style.display = "block";
      showToast("의사결정 문서를 불러왔습니다.");
    } catch (e) {
      showToast("문서 불러오기 실패", "error");
    }
  }

  async function deleteDecision(id) {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
      var resp = await fetch("/api/reason/decisions/" + id, { method: "DELETE" });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      showToast("삭제 완료");
      loadDecisionsList();
    } catch (e) {
      showToast("삭제 실패", "error");
    }
  }

  function escHtml(s) {
    return typeof escapeHtml === "function"
      ? escapeHtml(s || "")
      : String(s || "").replace(/[&<>"']/g, function (c) {
          var m = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
          return m[c] || c;
        });
  }

  // ---------- Phase 10-4-2: 공유 뷰 (읽기 전용) ----------
  async function checkSharedView() {
    var params = new URLSearchParams(location.search);
    var shareId = params.get("share");
    if (!shareId) return false;
    try {
      var resp = await fetch("/api/reason/share/" + encodeURIComponent(shareId));
      if (!resp.ok) {
        showToast("공유 결과를 찾을 수 없습니다 (만료 또는 존재하지 않음).", "error");
        return false;
      }
      var data = await resp.json();
      // 폼 숨기기 (읽기 전용)
      var form = document.querySelector(".reasoning-form");
      if (form) form.style.display = "none";
      // 결과 표시
      _lastReasoningResult = data;
      if (ReasonRender && ReasonRender.displayResults) {
        ReasonRender.displayResults(data);
      }
      var resultsDiv = document.getElementById("results");
      var resultsContent = document.getElementById("results-content");
      var resultsLoading = document.getElementById("results-loading");
      if (resultsDiv) {
        resultsDiv.style.display = "block";
        resultsDiv.classList.add("active");
      }
      if (resultsLoading) resultsLoading.style.display = "none";
      if (resultsContent) resultsContent.style.display = "block";
      // 공유 뷰 안내
      showToast("공유된 Reasoning 결과입니다 (읽기 전용).");
      return true;
    } catch (e) {
      showToast("공유 결과 로드 실패", "error");
      return false;
    }
  }

  // DOMContentLoaded 내에서 결과 저장 훅 설치
  var origProcessResult = (ReasonControl && ReasonControl.processReasoningResult) || function () {};
  if (ReasonControl) {
    var _origProcess = ReasonControl.processReasoningResult;
    ReasonControl.processReasoningResult = function (result) {
      storeLastResult(result);
      if (_origProcess) _origProcess(result);
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    checkSharedView().then(function (isShared) {
      if (!isShared) loadDecisionsList();
    });
  });

  window.runReasoning = runReasoning;
  window.cancelReasoning = cancelReasoning;
  window.switchContextTab = switchContextTab;
  window.toggleDarkMode = toggleDarkMode;
  window.shareResult = shareResult;
  window.showSaveDecisionModal = showSaveDecisionModal;
  window.closeSaveDecisionModal = closeSaveDecisionModal;
  window.saveDecision = saveDecision;
  window.loadDecisionDetail = loadDecisionDetail;
  window.deleteDecision = deleteDecision;
})();
