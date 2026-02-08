// 상수 정의
const DASHBOARD_CONSTANTS = {
  AUTO_REFRESH_INTERVAL: 30000, // 30초 (밀리초)
  MAX_CONTEXT_CHUNKS: 20, // 최대 컨텍스트 청크 수
  CHART_DAYS: 7, // 차트에 표시할 일수
  MAX_CONTEXT_LENGTH: 1000, // 최대 컨텍스트 길이 (문자)
  DEFAULT_MAX_TOKENS: 500, // 기본 최대 토큰 수
  DEFAULT_TEMPERATURE: 0.7, // 기본 온도
  DEFAULT_TOP_K: 5, // 기본 top_k
  DEFAULT_LIMIT: 20, // 기본 limit
  DEFAULT_LIMIT_LARGE: 50, // 기본 limit (큰 값)
  DEFAULT_LIMIT_XLARGE: 100, // 기본 limit (매우 큰 값)
};

/** Ollama 모델별 마지막 테스트 결과 (모델명 → { test_result, test_error }) */
let lastOllamaTestResult = null;

/**
 * 로딩 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 메시지 (기본값: "로딩 중...")
 */
function showLoading(elementId, message = "로딩 중...") {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
  }
}

/**
 * 빈 상태 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 메시지
 */
function showEmptyState(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
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
    element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
  }
}

// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🧠 Personal AI Brain",
      subtitle: "개인 지식 관리 시스템 대시보드",
      currentPath: "/dashboard",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다. header-component.js가 로드되었는지 확인하세요.");
  }
});

/**
 * 시스템 통계 업데이트
 * @param {Object} data - 시스템 상태 데이터
 */
function updateSystemStats(data) {
  document.getElementById("total-docs").textContent = data.files?.total_md_files || 0;
  document.getElementById("qdrant-points").textContent = data.qdrant?.points_count?.toLocaleString() || "-";
  document.getElementById("projects-count").textContent = data.files?.projects || 0;

  // 총 작업 수 (로그 통계에서 가져오기)
  fetch("/api/logs/stats")
    .then((res) => res.json())
    .then((logsData) => {
      document.getElementById("total-works").textContent = logsData.total_entries || 0;
    })
    .catch(() => {
      document.getElementById("total-works").textContent = "-";
    });
}

/**
 * 시스템 상태 HTML 생성 및 표시
 * @param {Object} data - 시스템 상태 데이터
 */
function renderSystemStatus(data) {
  const dbOk = data.database?.status === "connected";
  const qdrantOk = data.qdrant?.status === "connected";
  const envLabel = data.venv?.status === "docker" ? "Docker 컨테이너" : data.venv?.status === "activated" ? "가상환경 활성화" : "가상환경 비활성화";
  const llmOk = data.gpt4all?.status === "available" || data.gpt4all?.status === "available_via_host";
  const llmLabel = data.gpt4all?.status === "available" ? "사용 가능" : data.gpt4all?.status === "available_via_host" ? "연결됨 (로컬)" : "미설치";
  const llmTitle = data.gpt4all?.source === "ollama" ? "Ollama" : "GPT4All";
  const summaryHtml = `
    <div style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 13px;">
      <strong>설치/연결 상태</strong>
      <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-top: 8px;">
        <span>PostgreSQL: <span class="status-badge ${dbOk ? "connected" : "error"}">${dbOk ? "연결됨" : "오류"}</span></span>
        <span>Qdrant: <span class="status-badge ${qdrantOk ? "connected" : "error"}">${qdrantOk ? "연결됨" : "오류"}</span></span>
        <span>실행 환경: <span class="status-badge ${data.venv?.status === "docker" || data.venv?.status === "activated" ? "connected" : "error"}">${escapeHtml(envLabel)}</span></span>
        <span>${escapeHtml(llmTitle)}: <span class="status-badge ${llmOk ? "connected" : "error"}">${escapeHtml(llmLabel)}</span></span>
      </div>
    </div>
  `;
  const statusHtml = summaryHtml + `
              <div class="status-item">
                  Qdrant 연결 상태
                  <span class="status-badge ${data.qdrant?.status === "connected" ? "connected" : "error"}">
                      ${data.qdrant?.status === "connected" ? "연결됨" : "오류"}
                  </span>
                  ${
                    data.qdrant?.status === "connected"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">컬렉션: ${escapeHtml(data.qdrant?.collection_name || "-")} (${(
                          data.qdrant?.points_count || 0
                        ).toLocaleString()} 포인트)</div>`
                      : data.qdrant?.error
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.qdrant.error)}</div>`
                      : ""
                  }
              </div>
              <div class="status-item">
                  DB 연결 상태
                  <span class="status-badge ${data.database?.status === "connected" ? "connected" : "error"}">
                      ${data.database?.status === "connected" ? "연결됨" : "오류"}
                  </span>
                  ${
                    data.database?.status === "error"
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.database.error || "연결 실패")}</div>`
                      : data.database?.status === "connected"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.database.message || "정상")}</div>`
                      : ""
                  }
              </div>
              <div class="status-item">
                  실행 환경
                  <span class="status-badge ${data.venv?.status === "docker" ? "connected" : data.venv?.status === "activated" ? "connected" : data.venv?.status === "packages_missing" ? "error" : "error"}">
                      ${data.venv?.status === "docker" ? "Docker 컨테이너" : data.venv?.status === "activated" ? "가상환경 활성화됨" : data.venv?.status === "packages_missing" ? "패키지 누락" : "가상환경 비활성화됨"}
                  </span>
                  ${
                    data.venv?.status !== "docker"
                      ? `<button 
                    onclick="testVenvPackages()" 
                    style="margin-left: 10px; padding: 4px 12px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;"
                    id="test-venv-btn"
                  >
                    🔄 패키지 재확인
                  </button>`
                      : ""
                  }
                  ${
                    data.venv?.status === "docker"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.venv?.message || "Docker 컨테이너에서 실행 중")}</div>`
                      : data.venv?.status === "activated"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.venv.venv_path || "")}</div>`
                      : data.venv?.status === "packages_missing"
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.venv?.message || "누락된 패키지가 있습니다")}</div>`
                      : data.venv?.status !== "docker"
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.venv?.message || "가상환경을 활성화하세요")}</div>`
                      : ""
                  }
                  ${
                    data.venv?.status !== "docker" && data.venv?.packages_status && Object.keys(data.venv.packages_status).length > 0
                      ? `<div style="font-size: 11px; color: #666; margin-top: 5px; padding-left: 10px;">
                          패키지: ${escapeHtml(
                            Object.entries(data.venv.packages_status)
                              .filter(([_, status]) => status === "installed")
                              .map(([name, _]) => name)
                              .join(", ") || "없음"
                          )}
                        </div>`
                      : ""
                  }
              </div>
              <div class="status-item">
                  로컬 LLM (${data.gpt4all?.source === "ollama" ? "Ollama" : "GPT4All"}) 상태
                  <span class="status-badge ${data.gpt4all?.status === "available" || data.gpt4all?.status === "available_via_host" ? "connected" : data.gpt4all?.status === "not_installed" ? "error" : "error"}">
                      ${data.gpt4all?.status === "available" ? "사용 가능" : data.gpt4all?.status === "available_via_host" ? "연결됨 (로컬)" : data.gpt4all?.status === "not_installed" ? "미설치" : "오류"}
                  </span>
                  ${
                    data.gpt4all?.status === "available" && (!data.gpt4all?.models || data.gpt4all.models.length < 2)
                      ? `<button 
                          onclick="testGpt4All()" 
                          style="margin-left: 10px; padding: 4px 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;"
                          id="test-gpt4all-btn"
                        >
                          🧪 실행 테스트
                        </button>`
                      : ""
                  }
                  ${
                    data.gpt4all?.status === "available" && data.gpt4all?.models?.length >= 2
                      ? `<div style="font-size: 12px; color: #666; margin-top: 8px;">설치된 모델 (각각 테스트 가능):</div>
                         <div style="margin-top: 6px;">${data.gpt4all.models.map((m) => {
                           const last = lastOllamaTestResult && lastOllamaTestResult.model === m ? lastOllamaTestResult : null;
                           const badge = last ? (last.test_result === "success" ? " ✅ 성공" : last.test_result === "timeout" ? " ⏱️ 시간 초과" : " ⚠️ 실패") : "";
                           const safeM = escapeHtml(m);
                           const attrModel = String(m).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
                           return `<div style="display: flex; align-items: center; gap: 8px; margin-top: 4px; padding-left: 10px;">
                             <span style="font-family: monospace; font-size: 11px;">${safeM}</span>${badge}
                             <button onclick="testGpt4AllWithButton(this)" class="test-ollama-model-btn" data-model="${attrModel}" style="padding: 2px 8px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;">🧪 테스트</button>
                           </div>`;
                         }).join("")}</div>`
                      : data.gpt4all?.status === "available"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">
                          모델: ${escapeHtml(data.gpt4all.model_name || "-")}
                          ${data.gpt4all.test_result === "success" ? " ✅ 실행 테스트 성공" : data.gpt4all.test_result === "error" ? " ⚠️ 실행 테스트 실패" : data.gpt4all.test_result === "timeout" ? " ⏱️ 실행 테스트 시간 초과" : data.gpt4all.test_result === "not_tested" ? " (테스트 미실행)" : ""}
                        </div>`
                      : data.gpt4all?.status === "available_via_host"
                      ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">로컬(호스트)에 로컬 LLM 설치됨. AI 추론은 로컬 환경에서 사용 가능</div>`
                      : data.gpt4all?.status === "not_installed"
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.gpt4all.install_command || "pip install gpt4all")}</div>`
                      : data.gpt4all?.error
                      ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.gpt4all.error)}</div>`
                      : ""
                  }
                  ${
                    data.gpt4all?.test_error && (!data.gpt4all?.models || data.gpt4all.models.length < 2)
                      ? `<div style="font-size: 11px; color: #dc2626; margin-top: 3px; padding-left: 10px;">테스트 오류: ${escapeHtml(data.gpt4all.test_error)}</div>`
                      : ""
                  }
                  ${data.gpt4all?.message ? `<div style="font-size: 11px; color: #666; margin-top: 3px; padding-left: 10px;">${escapeHtml(data.gpt4all.message)}</div>` : ""}
              </div>
          `;
  document.getElementById("system-status").innerHTML = statusHtml;
}

/**
 * 최근 작업 표시
 * @param {Array} recentWork - 최근 작업 배열
 */
function renderRecentWork(recentWork) {
  if (recentWork.length > 0) {
    const workHtml = recentWork
      .map(
        (work) => `
                    <div class="work-item">
                        <strong>${escapeHtml(work.action || "-")}</strong>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            ${escapeHtml(work.description || "")}
                        </div>
                        <div style="font-size: 11px; color: #999; margin-top: 5px;">
                            ${escapeHtml(work.date || "")} ${escapeHtml(work.time || "")}
                        </div>
                    </div>
                `
      )
      .join("");
    document.getElementById("recent-work").innerHTML = workHtml;
  } else {
    showEmptyState("recent-work", "최근 작업이 없습니다.");
  }
}

/**
 * 자동화 상태 표시
 * @param {Object} automation - 자동화 상태 데이터
 */
function renderAutomationStatus(automation) {
  const automationHtml = `
      <div class="status-item">
        파일 감시 시스템
        <span class="status-badge ${automation.watcher_running ? "connected" : "error"}">
          ${automation.watcher_running ? "실행 중" : "중지됨"}
        </span>
      </div>
      <div class="status-item">
        Git 자동 커밋: ${automation.git_auto_commit ? "활성화" : "비활성화"}
      </div>
    `;
  document.getElementById("automation-status").innerHTML = automationHtml;
}

/**
 * 최근 업데이트 문서 표시
 * @param {Array} recentDocs - 최근 문서 배열
 */
function renderRecentDocuments(recentDocs) {
  if (recentDocs.length > 0) {
    const docsHtml = recentDocs
      .map(
        (doc) => `
        <div class="work-item">
          <strong>${createDocumentLink(doc.file_path, doc.name, { style: "color: #2563eb; text-decoration: none;" })}</strong>
          <div style="font-size: 12px; color: #666; margin-top: 5px;">
            ${escapeHtml(doc.file_path)}
          </div>
        </div>
      `
      )
      .join("");
    document.getElementById("recent-documents").innerHTML = docsHtml;
  } else {
    showEmptyState("recent-documents", "최근 문서가 없습니다.");
  }
}

/**
 * 대시보드 로드 (메인 함수)
 */
async function loadDashboard() {
  try {
    const response = await fetch("/api/system/status");
    const data = await response.json();

    // 통계 업데이트
    updateSystemStats(data);

    // 시스템 상태 표시
    renderSystemStatus(data);

    // 최근 작업 표시
    renderRecentWork(data.recent_work || []);

    // 자동화 상태 표시
    renderAutomationStatus(data.automation || {});

    // 최근 업데이트 문서 표시
    renderRecentDocuments(data.recent_documents || []);
  } catch (error) {
    console.error("대시보드 로드 오류:", error);
    showError("system-status", "오류가 발생했습니다.");
  }
}

/**
 * 활동 차트 HTML 생성
 * @param {Object} logsData - 로그 데이터
 * @returns {string} 차트 HTML
 */
function renderActivityChart(logsData) {
  const byDate = logsData.by_date || {};
  const dates = Object.keys(byDate).slice(0, DASHBOARD_CONSTANTS.CHART_DAYS).reverse();
  const maxValue = Math.max(...Object.values(byDate), 1);

  if (dates.length > 0) {
    const chartHtml = `
      <div class="chart-container">
        <div class="activity-chart">
          ${dates
            .map(
              (date) => `
            <div class="chart-bar" style="height: ${(byDate[date] / maxValue) * 100}%" title="${escapeHtml(date)}: ${byDate[date]}개">
              <div class="chart-label">${escapeHtml(date.split("-")[2] || date)}</div>
            </div>
          `
            )
            .join("")}
        </div>
      </div>
    `;
    document.getElementById("activity-chart").innerHTML = chartHtml;
  } else {
    showEmptyState("activity-chart", "활동 데이터가 없습니다.");
  }
}

/**
 * 활동 요약 HTML 생성
 * @param {Object} logsData - 로그 데이터
 */
function renderActivitySummary(logsData) {
  const summaryHtml = `
    <div class="summary-item">
      <div class="summary-label">총 작업</div>
      <div class="summary-value">${logsData.total_entries || 0}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">커밋</div>
      <div class="summary-value">${logsData.by_action?.commit || 0}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">파일 변경</div>
      <div class="summary-value">${logsData.by_action?.file_change || 0}</div>
    </div>
    <div class="summary-item">
      <div class="summary-label">임베딩</div>
      <div class="summary-value">${logsData.by_action?.embed || 0}</div>
    </div>
  `;
  document.getElementById("activity-summary").innerHTML = summaryHtml;
}

/**
 * 분석 데이터 로드
 */
async function loadAnalytics() {
  try {
    const [statusResponse, logsResponse] = await Promise.all([fetch("/api/system/status"), fetch("/api/logs/stats")]);
    const logsData = await logsResponse.json();

    // 활동 차트 생성
    renderActivityChart(logsData);

    // 활동 요약 표시
    renderActivitySummary(logsData);
  } catch (error) {
    console.error("분석 데이터 로드 오류:", error);
  }
}

let allDocuments = [];

async function loadDocuments() {
  try {
    const response = await fetch("/api/documents");
    allDocuments = await response.json();
    displayDocuments(allDocuments);
  } catch (error) {
    console.error("문서 목록 로드 오류:", error);
    showError("documents-list", "문서를 불러올 수 없습니다.");
  }
}

/**
 * 문서를 폴더별로 그룹화
 * @param {Array} documents - 문서 배열
 * @returns {Object} 폴더별로 그룹화된 문서 객체
 */
function groupDocumentsByFolder(documents) {
  const grouped = {};
  documents.forEach((doc) => {
    const pathParts = doc.file_path.split("/");
    const folder = pathParts.slice(0, -1).join("/") || "루트";
    if (!grouped[folder]) {
      grouped[folder] = [];
    }
    grouped[folder].push(doc);
  });
  return grouped;
}

/**
 * 문서 아이템 HTML 생성
 * @param {Object} doc - 문서 객체
 * @returns {string} 문서 아이템 HTML
 */
function renderDocumentItem(doc) {
  const sizeKB = (doc.size / 1024).toFixed(1);
  const date = new Date(doc.modified * 1000);
  const dateStr = date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
  const timeStr = date.toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return `
    <div class="document-item" onclick="openDocument('${doc.file_path.replace(/'/g, "\\'")}')">
      <div class="document-info">
        <div class="document-name">${escapeHtml(doc.name)}</div>
        <div class="document-path">${escapeHtml(doc.file_path)}</div>
      </div>
      <div class="document-meta">
        <div class="document-size">${escapeHtml(sizeKB)} KB</div>
        <div class="document-date">${escapeHtml(dateStr)} ${escapeHtml(timeStr)}</div>
      </div>
    </div>
  `;
}

/**
 * 문서 목록 표시
 * @param {Array} documents - 문서 배열
 */
function displayDocuments(documents) {
  if (documents.length === 0) {
    showEmptyState("documents-list", "문서가 없습니다.");
    return;
  }

  // 폴더별로 그룹화
  const grouped = groupDocumentsByFolder(documents);

  // 폴더명으로 정렬
  const sortedFolders = Object.keys(grouped).sort();

  let html = '<div class="documents-list">';
  sortedFolders.forEach((folder) => {
    html += `
      <div class="folder-group">
        <div class="folder-header">📁 ${escapeHtml(folder)}</div>
    `;
    grouped[folder].forEach((doc) => {
      html += renderDocumentItem(doc);
    });
    html += "</div>";
  });
  html += "</div>";

  document.getElementById("documents-list").innerHTML = html;
}

/**
 * 문서 필터링
 * 검색어를 기반으로 문서 목록을 필터링하여 표시
 */
function filterDocuments() {
  const searchTerm = document.getElementById("document-search").value.toLowerCase();
  if (!searchTerm) {
    displayDocuments(allDocuments);
    return;
  }

  const filtered = allDocuments.filter((doc) => {
    return doc.name.toLowerCase().includes(searchTerm) || doc.file_path.toLowerCase().includes(searchTerm);
  });

  displayDocuments(filtered);
}

// 페이지 로드 시 실행
loadDashboard();
loadAnalytics();
loadDocuments();

// 자동 새로고침
setInterval(() => {
  loadDashboard();
  loadAnalytics();
  loadDocuments();
}, DASHBOARD_CONSTANTS.AUTO_REFRESH_INTERVAL);

/**
 * 가상환경 상태 HTML 생성
 * @param {Object} data - 가상환경 상태 데이터
 * @returns {string} 상태 HTML
 */
function renderVenvStatusHtml(data) {
  return `
    <div class="status-item">
      가상환경 상태
      <span class="status-badge ${data.status === "activated" ? "connected" : data.status === "packages_missing" ? "error" : "error"}">
        ${data.status === "activated" ? "활성화됨" : data.status === "packages_missing" ? "패키지 누락" : "비활성화됨"}
      </span>
      <button 
        onclick="testVenvPackages()" 
        style="margin-left: 10px; padding: 4px 12px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;"
        id="test-venv-btn"
      >
        🔄 패키지 재확인
      </button>
      ${
        data.status === "activated"
          ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.venv_path || "")}</div>`
          : data.status === "packages_missing"
          ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.message || "누락된 패키지가 있습니다")}</div>`
          : `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.message || "가상환경을 활성화하세요")}</div>`
      }
      ${
        data.packages_status && Object.keys(data.packages_status).length > 0
          ? `<div style="font-size: 11px; color: #666; margin-top: 5px; padding-left: 10px;">
              패키지: ${escapeHtml(
                Object.entries(data.packages_status)
                  .filter(([_, status]) => status === "installed")
                  .map(([name, _]) => name)
                  .join(", ") || "없음"
              )}
            </div>`
          : ""
      }
    </div>
  `;
}

/**
 * 시스템 상태 HTML에서 특정 부분 업데이트
 * @param {string} statusHtml - 새로운 상태 HTML
 * @param {string} pattern - 찾을 패턴
 */
function updateSystemStatusSection(statusHtml, pattern) {
  const systemStatusDiv = document.getElementById("system-status");
  if (systemStatusDiv) {
    const currentHtml = systemStatusDiv.innerHTML;
    const match = currentHtml.match(pattern);
    if (match) {
      systemStatusDiv.innerHTML = currentHtml.replace(match[0], statusHtml);
    }
  }
}

/**
 * 가상환경 패키지 재확인
 */
async function testVenvPackages() {
  const btn = document.getElementById("test-venv-btn");
  if (!btn) return;
  
  const originalText = btn.textContent;
  btn.disabled = true;
  btn.textContent = "확인 중...";
  btn.style.opacity = "0.6";
  
  try {
    const response = await fetch("/api/system/test/venv-packages", {
      method: "POST",
    });
    const data = await response.json();
    
    // 가상환경 상태 HTML 생성
    const statusHtml = renderVenvStatusHtml(data);
    
    // 시스템 상태 HTML에서 가상환경 부분 찾아서 교체
    updateSystemStatusSection(statusHtml, /<div class="status-item">[\s\S]*?가상환경 상태[\s\S]*?<\/div>/);
    
    alert("가상환경 패키지 확인 완료");
  } catch (error) {
    console.error("가상환경 패키지 확인 오류:", error);
    alert("가상환경 패키지 확인 중 오류가 발생했습니다: " + error.message);
  } finally {
    btn.disabled = false;
    btn.textContent = originalText;
    btn.style.opacity = "1";
  }
}

/**
 * GPT4All 상태 HTML 생성
 * @param {Object} data - GPT4All 상태 데이터
 * @returns {string} 상태 HTML
 */
function renderGpt4AllStatusHtml(data) {
  return `
    <div class="status-item">
      GPT4All 상태
      <span class="status-badge ${data.status === "available" ? "connected" : data.status === "not_installed" ? "error" : "error"}">
        ${data.status === "available" ? "사용 가능" : data.status === "not_installed" ? "미설치" : "오류"}
      </span>
      ${
        data.status === "available"
          ? `<button 
              onclick="testGpt4All()" 
              style="margin-left: 10px; padding: 4px 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;"
              id="test-gpt4all-btn"
            >
              🧪 실행 테스트
            </button>`
          : ""
      }
      ${
        data.status === "available"
          ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">
              모델: ${escapeHtml(data.model_name || "-")}
              ${data.test_result === "success" ? " ✅ 실행 테스트 성공" : data.test_result === "error" ? " ⚠️ 실행 테스트 실패" : data.test_result === "timeout" ? " ⏱️ 실행 테스트 시간 초과" : data.test_result === "not_tested" ? " (테스트 미실행)" : ""}
            </div>`
          : data.status === "not_installed"
          ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.install_command || "pip install gpt4all")}</div>`
          : data.error
          ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.error)}</div>`
          : ""
      }
      ${
        data.test_error
          ? `<div style="font-size: 11px; color: #dc2626; margin-top: 3px; padding-left: 10px;">테스트 오류: ${escapeHtml(data.test_error)}</div>`
          : ""
      }
      ${data.message ? `<div style="font-size: 11px; color: #666; margin-top: 3px; padding-left: 10px;">${escapeHtml(data.message)}</div>` : ""}
    </div>
  `;
}

/**
 * 테스트 결과 메시지 표시
 * @param {Object} data - 테스트 결과 데이터
 * @param {string} [model] - 테스트한 모델명 (다중 모델일 때 알림에 표시)
 */
function showGpt4AllTestResult(data, model) {
  const modelLabel = (data.tested_model || model) ? " (" + (data.tested_model || model) + ")" : "";
  if (data.test_result === "success") {
    alert("로컬 LLM 실행 테스트 성공!" + modelLabel);
  } else if (data.test_result === "timeout") {
    alert("실행 테스트 시간 초과 (90초). 모델이 로딩 중일 수 있습니다." + modelLabel);
  } else if (data.test_result === "error") {
    alert("실행 테스트 실패: " + (data.test_error || data.error || "알 수 없는 오류") + modelLabel);
  } else {
    alert("로컬 LLM 테스트 완료" + modelLabel);
  }
}

/**
 * 모델별 테스트 버튼 클릭 시 (data-model에서 모델명 읽어 testGpt4All 호출)
 */
function testGpt4AllWithButton(btn) {
  const model = btn && btn.getAttribute ? btn.getAttribute("data-model") : null;
  testGpt4All(model || undefined, btn);
}

/**
 * GPT4All(Ollama) 실행 테스트. model이 있으면 해당 모델만 테스트.
 * @param {string} [model] - 테스트할 모델명 (없으면 기본 모델)
 * @param {HTMLElement} [btn] - 클릭된 버튼 (로딩 표시용, 없으면 test-gpt4all-btn 사용)
 */
async function testGpt4All(model, btn) {
  const targetBtn = btn || document.getElementById("test-gpt4all-btn");
  if (targetBtn) {
    const originalText = targetBtn.textContent;
    targetBtn.disabled = true;
    targetBtn.textContent = "테스트 중... (최대 90초)";
    targetBtn.style.opacity = "0.6";
  }

  try {
    const url = model
      ? "/api/system/test/gpt4all?model=" + encodeURIComponent(model)
      : "/api/system/test/gpt4all";
    const response = await fetch(url, { method: "POST" });
    const data = await response.json();

    lastOllamaTestResult = {
      model: data.tested_model || model || data.model_name,
      test_result: data.test_result,
      test_error: data.test_error,
    };

    // 단일 모델 UI인 경우 기존 방식으로 섹션만 갱신, 다중 모델이면 전체 상태 재조회해 배지 반영
    if (!data.models || data.models.length < 2) {
      const statusHtml = renderGpt4AllStatusHtml(data);
      updateSystemStatusSection(statusHtml, /<div class="status-item">[\s\S]*?GPT4All 상태[\s\S]*?<\/div>/);
    } else {
      const statusRes = await fetch("/api/system/status");
      const statusData = await statusRes.json();
      updateSystemStats(statusData);
      renderSystemStatus(statusData);
      renderRecentWork(statusData.recent_work || []);
      renderAutomationStatus(statusData.automation || {});
      renderRecentDocuments(statusData.recent_documents || []);
    }

    showGpt4AllTestResult(data, model);
  } catch (error) {
    console.error("GPT4All 테스트 오류:", error);
    alert("GPT4All 테스트 중 오류가 발생했습니다: " + error.message);
  } finally {
    if (targetBtn) {
      targetBtn.disabled = false;
      targetBtn.textContent = targetBtn.getAttribute("data-model") ? "🧪 테스트" : "🧪 실행 테스트";
      targetBtn.style.opacity = "1";
    }
  }
}
