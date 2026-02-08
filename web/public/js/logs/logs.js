/**
 * Logs 메인 모듈
 * 작업 로그 및 활동 기록 기능을 제공
 */

/**
 * 빈 상태 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 메시지
 */
function showEmptyState(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="no-logs">${escapeHtml(message)}</div>`;
  }
}

/**
 * 에러 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 에러 메시지
 */
function showError(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="no-logs">${escapeHtml(message)}</div>`;
  }
}

// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "📋 Personal AI Brain - Logs",
      subtitle: "작업 로그 및 활동 기록",
      currentPath: "/logs",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

let allLogs = [];

// 페이징 컴포넌트
let pagination;

// 필터 상태
let currentDateFilter = "";
let currentActionFilter = "";
let currentSearchText = "";

// 페이징 컴포넌트 초기화
pagination = new PaginationComponent({
  initialPage: 1,
  initialLimit: 20,
  onPageChange: loadLogs,
  onLimitChange: loadLogs
});

/**
 * 로그 목록 로드
 * API에서 로그 목록을 가져와서 표시 (페이징 및 필터링 지원)
 */
async function loadLogs() {
  try {
    // 페이징 상태 가져오기
    const state = pagination.getState();
    const offset = state.offset;

    // URL 구성
    let url = "/api/logs?";
    const params = [];
    params.push(`limit=${state.limit}`);
    params.push(`offset=${offset}`);
    if (currentDateFilter) {
      params.push(`date=${currentDateFilter}`);
    }
    if (currentActionFilter) {
      params.push(`action=${currentActionFilter}`);
    }
    url += params.join("&");

    const response = await fetch(url);
    const data = await response.json();

    // 새로운 API 응답 형식 처리
    allLogs = data.entries || [];

    // 페이징 상태 업데이트
    pagination.updateState(data);

    // 검색 필터 적용 (클라이언트 측)
    let filteredLogs = allLogs;
    if (currentSearchText) {
      filteredLogs = allLogs.filter(
        (log) =>
          (log.description || "").toLowerCase().includes(currentSearchText) ||
          (log.action || "").toLowerCase().includes(currentSearchText) ||
          (log.files || []).some((f) => f.toLowerCase().includes(currentSearchText))
      );
    }

    displayLogs(filteredLogs);
    pagination.updateUI();
  } catch (error) {
    console.error("로그 로드 오류:", error);
    showError("logs-timeline", "로그를 불러올 수 없습니다.");
    // 페이징 UI 숨기기
    pagination.hide();
  }
}

/**
 * 로그 통계 로드
 * 로그 통계 정보를 가져와서 표시
 */
async function loadStats() {
  try {
    const response = await fetch("/api/logs/stats");
    const data = await response.json();

    const statsHtml = `
      <div class="stat-item">
        <div class="stat-label">총 로그 수</div>
        <div class="stat-value">${data.total_entries || 0}</div>
      </div>
      ${Object.entries(data.by_action || {})
        .map(
          ([action, count]) => `
        <div class="stat-item">
          <div class="stat-label">${escapeHtml(action)}</div>
          <div class="stat-value">${count}</div>
        </div>
      `
        )
        .join("")}
    `;
    document.getElementById("stats-grid").innerHTML = statsHtml;
  } catch (error) {
    console.error("통계 로드 오류:", error);
  }
}

/**
 * 로그 목록 표시
 * 로그 배열을 받아서 HTML로 렌더링하여 표시
 * @param {Array} logs - 로그 배열
 */
function displayLogs(logs) {
  if (logs.length === 0) {
    showEmptyState("logs-timeline", "로그가 없습니다.");
    // 페이징 UI 숨기기
    pagination.hide();
    return;
  }

  const logsHtml = logs
    .map((log) => {
      const emojiMap = {
        commit: "💾",
        file_change: "📝",
        embed: "🔍",
        search: "🔎",
        system: "⚙️",
        test: "🧪",
      };
      const emoji = emojiMap[log.action] || "📌";

      const filesHtml =
        log.files && log.files.length > 0
          ? `<div class="log-files">📎 ${log.files.map((f) => createDocumentLink(f, f)).join(" ")}</div>`
          : "";

      return `
        <div class="log-entry">
          <div class="log-header">
            <div>
              <span class="log-action">${emoji} ${escapeHtml(log.action || "-")}</span>
              <span class="log-time">${escapeHtml(log.date || "")} ${escapeHtml(log.time || "")}</span>
            </div>
          </div>
          <div class="log-description">${escapeHtml(log.description || "")}</div>
          ${filesHtml}
        </div>
      `;
    })
    .join("");

  document.getElementById("logs-timeline").innerHTML = logsHtml;
}

/**
 * 필터 적용
 * 날짜, 액션, 검색어 필터를 적용하여 로그 목록을 다시 로드
 */
function applyFilters() {
  const dateFilter = document.getElementById("date-filter").value;
  const actionFilter = document.getElementById("action-filter").value;
  const searchText = document.getElementById("search-input").value.toLowerCase();

  // 필터 상태 저장
  currentDateFilter = dateFilter;
  currentActionFilter = actionFilter;
  currentSearchText = searchText;

  // 필터 변경 시 첫 페이지로
  pagination.currentPage = 1;

  // 로그 다시 로드 (백엔드 필터링 + 페이징)
  loadLogs();
}

/**
 * 필터 초기화
 * 모든 필터를 초기화하고 로그 목록을 다시 로드
 */
function resetFilters() {
  document.getElementById("date-filter").value = "";
  document.getElementById("action-filter").value = "";
  document.getElementById("search-input").value = "";
  
  // 필터 상태 초기화
  currentDateFilter = "";
  currentActionFilter = "";
  currentSearchText = "";
  pagination.currentPage = 1;

  // 로그 다시 로드
  loadLogs();
}

let currentView = "json";

async function loadWorkLogMarkdown() {
  try {
    const response = await fetch("/api/system/work-log");
    const data = await response.json();

    // marked.js를 사용하여 Markdown을 HTML로 변환
    if (typeof marked !== "undefined") {
      let html = marked.parse(data.content || "");

      // XSS 방지: <script> 태그 제거
      html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");

      document.getElementById("work-log-content").innerHTML = html;
    } else {
      // marked.js가 없으면 기본 텍스트로 표시
      document.getElementById("work-log-content").innerHTML = '<pre style="white-space: pre-wrap;">' + escapeHtml(data.content || "") + "</pre>";
    }
  } catch (error) {
    console.error("작업 로그 Markdown 로드 오류:", error);
    showError("work-log-content", `작업 로그를 불러올 수 없습니다: ${error.message}`);
  }
}

/**
 * 뷰 전환
 * JSON 뷰와 Markdown 뷰 사이를 전환
 * @param {string} view - 뷰 이름 ("json" 또는 "markdown")
 */
function switchView(view) {
  currentView = view;

  if (view === "json") {
    document.getElementById("json-view").style.display = "block";
    document.getElementById("markdown-view").style.display = "none";
    document.getElementById("view-json-btn").className = "view-btn-active";
    document.getElementById("view-md-btn").className = "view-btn-inactive";
  } else {
    document.getElementById("json-view").style.display = "none";
    document.getElementById("markdown-view").style.display = "block";
    document.getElementById("view-json-btn").className = "view-btn-inactive";
    document.getElementById("view-md-btn").className = "view-btn-active";
    loadWorkLogMarkdown();
  }
}

// 페이지 로드 시 실행
loadLogs();
loadStats();

// Enter 키로 필터 적용
document.getElementById("search-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    applyFilters();
  }
});

