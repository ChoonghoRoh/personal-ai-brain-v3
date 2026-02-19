/**
 * Reasoning Lab — Session 레이어 (Phase 17-4)
 * 멀티턴 대화 세션 관리, 스레드 UI, 대화 기록 그리드
 */
(function () {
  "use strict";

  function esc(s) {
    return typeof escapeHtml === "function"
      ? escapeHtml(s)
      : String(s || "").replace(/[&<>"']/g, function (c) {
          var m = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
          return m[c] || c;
        });
  }

  // ---------- 세션 상태 ----------
  var _currentPage = 1;
  var _pageSize = 10;
  var _selectedSessions = new Set();

  function getCurrentSessionId() {
    return window.__currentSessionId || null;
  }

  function setCurrentSessionId(sessionId) {
    window.__currentSessionId = sessionId;
    try {
      if (sessionId) {
        localStorage.setItem("reason-session-id", sessionId);
      } else {
        localStorage.removeItem("reason-session-id");
      }
    } catch (e) {}
  }

  function restoreSessionId() {
    try {
      var saved = localStorage.getItem("reason-session-id");
      if (saved) window.__currentSessionId = saved;
    } catch (e) {}
  }

  // ---------- 새 세션 생성 ----------
  async function createNewSession() {
    try {
      var resp = await fetch("/api/reason/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: null }),
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      var data = await resp.json();
      setCurrentSessionId(data.session_id);
      clearThreadUI();
      // 폼 초기화
      var questionEl = document.getElementById("question");
      if (questionEl) questionEl.value = "";
      // 결과 영역 숨기기
      var resultsDiv = document.getElementById("results");
      var resultsContent = document.getElementById("results-content");
      if (resultsDiv) { resultsDiv.style.display = "none"; resultsDiv.classList.remove("active"); }
      if (resultsContent) resultsContent.style.display = "none";
      // 이어서 질문 버튼 숨기기
      var continueArea = document.getElementById("continue-question-area");
      if (continueArea) continueArea.style.display = "none";
      showThreadPanel();
    } catch (e) {
      console.error("세션 생성 실패:", e);
    }
  }

  // ---------- 스레드 UI ----------
  function showThreadPanel() {
    var panel = document.getElementById("session-thread");
    if (panel) panel.style.display = "block";
  }

  function clearThreadUI() {
    var turnsEl = document.getElementById("session-turns");
    if (turnsEl) turnsEl.innerHTML = "";
  }

  async function refreshThread() {
    var sessionId = getCurrentSessionId();
    if (!sessionId) return;
    showThreadPanel();
    try {
      var resp = await fetch("/api/reason/sessions/" + encodeURIComponent(sessionId));
      if (!resp.ok) return;
      var data = await resp.json();
      renderThreadTurns(data.turns || []);
      // 이어서 질문 버튼 표시
      var continueArea = document.getElementById("continue-question-area");
      if (continueArea && data.turns && data.turns.length > 0) {
        continueArea.style.display = "block";
      }
    } catch (e) {
      console.error("스레드 갱신 실패:", e);
    }
  }

  function renderThreadTurns(turns) {
    var container = document.getElementById("session-turns");
    if (!container) return;
    if (turns.length === 0) {
      container.innerHTML = '<div class="thread-empty">아직 대화가 없습니다.</div>';
      return;
    }
    container.innerHTML = turns.map(function (turn, index) {
      var timeStr = "";
      if (turn.created_at) {
        var d = new Date(turn.created_at);
        timeStr = d.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
      }
      var questionPreview = (turn.question || "").substring(0, 60);
      if ((turn.question || "").length > 60) questionPreview += "...";
      var summaryText = turn.summary ? '<div class="turn-summary">' + esc(turn.summary) + '</div>' : '';
      return '<div class="thread-turn" data-turn-index="' + index + '" data-turn-id="' + esc(String(turn.id)) + '">' +
        '<div class="turn-number">턴 ' + (index + 1) + '</div>' +
        '<div class="turn-question">' + esc(questionPreview) + '</div>' +
        summaryText +
        '<div class="turn-time">' + esc(timeStr) + '</div>' +
      '</div>';
    }).join("");

    // 턴 클릭 이벤트
    container.querySelectorAll(".thread-turn").forEach(function (el) {
      el.addEventListener("click", function () {
        var turnIndex = parseInt(this.getAttribute("data-turn-index"), 10);
        if (turns[turnIndex]) {
          displayTurnResult(turns[turnIndex]);
        }
      });
    });
  }

  function displayTurnResult(turn) {
    if (window.ReasonRender && window.ReasonRender.displayResults) {
      window.ReasonRender.displayResults(turn);
    }
    var resultsDiv = document.getElementById("results");
    var resultsContent = document.getElementById("results-content");
    var resultsLoading = document.getElementById("results-loading");
    if (resultsDiv) { resultsDiv.style.display = "block"; resultsDiv.classList.add("active"); }
    if (resultsContent) resultsContent.style.display = "block";
    if (resultsLoading) resultsLoading.style.display = "none";
  }

  // ---------- 이어서 질문하기 ----------
  function continueQuestion() {
    var questionEl = document.getElementById("question");
    if (questionEl) {
      questionEl.value = "";
      questionEl.focus();
    }
    // 결과 영역 초기화하지 않음 — 스레드는 유지
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ---------- 대화 기록 그리드 (Task #6) ----------
  async function loadSessionHistory(page) {
    if (page) _currentPage = page;
    try {
      var resp = await fetch("/api/reason/sessions?page=" + _currentPage + "&size=" + _pageSize);
      if (!resp.ok) return;
      var data = await resp.json();
      var section = document.getElementById("session-history-section");
      if (!section) return;
      if (data.total === 0) {
        section.style.display = "none";
        return;
      }
      section.style.display = "block";
      renderSessionGrid(data.sessions || []);
      renderPagination(data.total, data.page, data.total_pages);
    } catch (e) {
      console.error("대화 기록 로드 실패:", e);
    }
  }

  function renderSessionGrid(sessions) {
    var container = document.getElementById("session-history-grid");
    if (!container) return;
    _selectedSessions.clear();
    updateBulkDeleteBtn();

    container.innerHTML = sessions.map(function (s) {
      var dateStr = "";
      if (s.created_at) {
        var d = new Date(s.created_at);
        dateStr = d.toLocaleDateString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit" });
      }
      var title = s.title || "제목 없음";
      var lastQ = s.last_question ? esc(s.last_question.substring(0, 50)) : "";
      return '<div class="session-card" data-session-id="' + esc(s.session_id) + '">' +
        '<div class="session-card-check"><input type="checkbox" class="session-checkbox" data-sid="' + esc(s.session_id) + '" /></div>' +
        '<div class="session-card-body">' +
          '<div class="session-card-title">' + esc(title) + '</div>' +
          '<div class="session-card-meta">' +
            '<span>' + esc(String(s.turn_count)) + '턴</span>' +
            '<span>' + esc(dateStr) + '</span>' +
          '</div>' +
          (lastQ ? '<div class="session-card-last-q">' + lastQ + '</div>' : '') +
        '</div>' +
      '</div>';
    }).join("");

    // 카드 클릭 → 세션 로드
    container.querySelectorAll(".session-card-body").forEach(function (el) {
      el.addEventListener("click", function () {
        var card = this.closest(".session-card");
        var sid = card ? card.getAttribute("data-session-id") : null;
        if (sid) loadSession(sid);
      });
    });

    // 체크박스 이벤트
    container.querySelectorAll(".session-checkbox").forEach(function (cb) {
      cb.addEventListener("change", function () {
        var sid = this.getAttribute("data-sid");
        if (this.checked) _selectedSessions.add(sid);
        else _selectedSessions.delete(sid);
        updateBulkDeleteBtn();
      });
    });
  }

  function renderPagination(total, currentPage, totalPages) {
    var container = document.getElementById("session-pagination");
    if (!container || totalPages <= 1) {
      if (container) container.innerHTML = "";
      return;
    }
    var html = '<div class="pagination-controls">';
    html += '<button class="btn btn-sm pagination-btn" data-page="' + (currentPage - 1) + '"' + (currentPage <= 1 ? ' disabled' : '') + '>&laquo; 이전</button>';
    html += '<span class="pagination-info">' + currentPage + ' / ' + totalPages + '</span>';
    html += '<button class="btn btn-sm pagination-btn" data-page="' + (currentPage + 1) + '"' + (currentPage >= totalPages ? ' disabled' : '') + '>다음 &raquo;</button>';
    html += '</div>';
    container.innerHTML = html;
    container.querySelectorAll(".pagination-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var page = parseInt(this.getAttribute("data-page"), 10);
        if (page >= 1 && page <= totalPages) loadSessionHistory(page);
      });
    });
  }

  function updateBulkDeleteBtn() {
    var btn = document.getElementById("bulk-delete-btn");
    if (btn) {
      btn.style.display = _selectedSessions.size > 0 ? "inline-block" : "none";
      btn.textContent = "선택 삭제 (" + _selectedSessions.size + ")";
    }
  }

  async function bulkDeleteSessions() {
    if (_selectedSessions.size === 0) return;
    if (!confirm(_selectedSessions.size + "개 세션을 삭제하시겠습니까?")) return;
    try {
      var resp = await fetch("/api/reason/sessions/bulk", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_ids: Array.from(_selectedSessions) }),
      });
      if (!resp.ok) throw new Error("HTTP " + resp.status);
      _selectedSessions.clear();
      updateBulkDeleteBtn();
      loadSessionHistory(_currentPage);
    } catch (e) {
      console.error("일괄 삭제 실패:", e);
    }
  }

  async function loadSession(sessionId) {
    setCurrentSessionId(sessionId);
    await refreshThread();
    // 결과 표시
    var resultsDiv = document.getElementById("results");
    if (resultsDiv) { resultsDiv.style.display = "block"; resultsDiv.classList.add("active"); }
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // ---------- 초기화 ----------
  function initSession() {
    restoreSessionId();

    // 새 대화 버튼
    var newSessionBtn = document.getElementById("new-session-btn");
    if (newSessionBtn) {
      newSessionBtn.addEventListener("click", createNewSession);
    }

    // 이어서 질문하기 버튼
    var continueBtn = document.getElementById("continue-question-btn");
    if (continueBtn) {
      continueBtn.addEventListener("click", continueQuestion);
    }

    // 일괄 삭제 버튼
    var bulkDeleteBtn = document.getElementById("bulk-delete-btn");
    if (bulkDeleteBtn) {
      bulkDeleteBtn.addEventListener("click", bulkDeleteSessions);
    }

    // 기존 세션이 있으면 스레드 표시
    if (getCurrentSessionId()) {
      refreshThread();
    }

    // 대화 기록 로드
    loadSessionHistory(1);
  }

  window.ReasonSession = {
    initSession: initSession,
    createNewSession: createNewSession,
    refreshThread: refreshThread,
    loadSessionHistory: loadSessionHistory,
    loadSession: loadSession,
    getCurrentSessionId: getCurrentSessionId,
    setCurrentSessionId: setCurrentSessionId,
    continueQuestion: continueQuestion,
    bulkDeleteSessions: bulkDeleteSessions,
  };
})();
