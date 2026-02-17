// 상수 정의
const DASHBOARD_CONSTANTS = {
  AUTO_REFRESH_INTERVAL: 30000,
  MAX_CONTEXT_CHUNKS: 20,
  CHART_DAYS: 7,
  MAX_CONTEXT_LENGTH: 1000,
  DEFAULT_MAX_TOKENS: 500,
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_TOP_K: 5,
  DEFAULT_LIMIT: 20,
  DEFAULT_LIMIT_LARGE: 50,
  DEFAULT_LIMIT_XLARGE: 100,
};

/** Ollama 모델별 마지막 테스트 결과 */
let lastOllamaTestResult = null;

/**
 * 로딩/빈 상태/에러 메시지 표시
 */
function showLoading(elementId, message = "로딩 중...") {
  const element = document.getElementById(elementId);
  if (element) element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
}

function showEmptyState(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
}

function showError(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
}

// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🧠 Personal AI Brain",
      subtitle: "개인 지식 관리 시스템 대시보드",
      currentPath: "/dashboard",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

/**
 * 시스템 통계 업데이트
 */
function updateSystemStats(data) {
  document.getElementById("total-docs").textContent = data.files?.total_md_files || 0;
  document.getElementById("qdrant-points").textContent = data.qdrant?.points_count?.toLocaleString() || "-";
  document.getElementById("projects-count").textContent = data.files?.projects || 0;
  fetch("/api/logs/stats")
    .then((res) => res.json())
    .then((logsData) => { document.getElementById("total-works").textContent = logsData.total_entries || 0; })
    .catch(() => { document.getElementById("total-works").textContent = "-"; });
}

/**
 * 시스템 상태 HTML 생성 및 표시
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
  const statusHtml = summaryHtml + renderQdrantStatus(data) + renderDbStatus(data) + renderVenvStatus(data) + renderLlmStatus(data);
  document.getElementById("system-status").innerHTML = statusHtml;
}

function renderQdrantStatus(data) {
  return `<div class="status-item">
    Qdrant 연결 상태
    <span class="status-badge ${data.qdrant?.status === "connected" ? "connected" : "error"}">${data.qdrant?.status === "connected" ? "연결됨" : "오류"}</span>
    ${data.qdrant?.status === "connected" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">컬렉션: ${escapeHtml(data.qdrant?.collection_name || "-")} (${(data.qdrant?.points_count || 0).toLocaleString()} 포인트)</div>` : data.qdrant?.error ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.qdrant.error)}</div>` : ""}
  </div>`;
}

function renderDbStatus(data) {
  return `<div class="status-item">
    DB 연결 상태
    <span class="status-badge ${data.database?.status === "connected" ? "connected" : "error"}">${data.database?.status === "connected" ? "연결됨" : "오류"}</span>
    ${data.database?.status === "error" ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.database.error || "연결 실패")}</div>` : data.database?.status === "connected" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.database.message || "정상")}</div>` : ""}
  </div>`;
}

function renderVenvStatus(data) {
  const v = data.venv || {};
  return `<div class="status-item">
    실행 환경
    <span class="status-badge ${v.status === "docker" || v.status === "activated" ? "connected" : "error"}">${v.status === "docker" ? "Docker 컨테이너" : v.status === "activated" ? "가상환경 활성화됨" : v.status === "packages_missing" ? "패키지 누락" : "가상환경 비활성화됨"}</span>
    ${v.status !== "docker" ? `<button onclick="testVenvPackages()" style="margin-left: 10px; padding: 4px 12px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;" id="test-venv-btn">🔄 패키지 재확인</button>` : ""}
    ${v.status === "docker" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(v.message || "Docker 컨테이너에서 실행 중")}</div>` : v.status === "activated" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(v.venv_path || "")}</div>` : v.status === "packages_missing" ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(v.message || "누락된 패키지가 있습니다")}</div>` : v.status !== "docker" ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(v.message || "가상환경을 활성화하세요")}</div>` : ""}
    ${v.status !== "docker" && v.packages_status && Object.keys(v.packages_status).length > 0 ? `<div style="font-size: 11px; color: #666; margin-top: 5px; padding-left: 10px;">패키지: ${escapeHtml(Object.entries(v.packages_status).filter(([_, s]) => s === "installed").map(([n]) => n).join(", ") || "없음")}</div>` : ""}
  </div>`;
}

function renderLlmStatus(data) {
  const g = data.gpt4all || {};
  const llmOk = g.status === "available" || g.status === "available_via_host";
  const llmTitle = g.source === "ollama" ? "Ollama" : "GPT4All";
  let html = `<div class="status-item">
    로컬 LLM (${escapeHtml(llmTitle)}) 상태
    <span class="status-badge ${llmOk ? "connected" : "error"}">${g.status === "available" ? "사용 가능" : g.status === "available_via_host" ? "연결됨 (로컬)" : g.status === "not_installed" ? "미설치" : "오류"}</span>`;
  if (g.status === "available" && (!g.models || g.models.length < 2)) {
    html += `<button onclick="testGpt4All()" style="margin-left: 10px; padding: 4px 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;" id="test-gpt4all-btn">🧪 실행 테스트</button>`;
  }
  if (g.status === "available" && g.models?.length >= 2) {
    html += `<div style="font-size: 12px; color: #666; margin-top: 8px;">설치된 모델 (각각 테스트 가능):</div><div style="margin-top: 6px;">`;
    html += g.models.map((m) => {
      const last = lastOllamaTestResult && lastOllamaTestResult.model === m ? lastOllamaTestResult : null;
      const badge = last ? (last.test_result === "success" ? " ✅ 성공" : last.test_result === "timeout" ? " ⏱️ 시간 초과" : " ⚠️ 실패") : "";
      const safeM = escapeHtml(m);
      const attrModel = String(m).replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
      return `<div style="display: flex; align-items: center; gap: 8px; margin-top: 4px; padding-left: 10px;"><span style="font-family: monospace; font-size: 11px;">${safeM}</span>${badge}<button onclick="testGpt4AllWithButton(this)" class="test-ollama-model-btn" data-model="${attrModel}" style="padding: 2px 8px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;">🧪 테스트</button></div>`;
    }).join("");
    html += "</div>";
  } else if (g.status === "available") {
    html += `<div style="font-size: 12px; color: #666; margin-top: 5px;">모델: ${escapeHtml(g.model_name || "-")}${g.test_result === "success" ? " ✅ 실행 테스트 성공" : g.test_result === "error" ? " ⚠️ 실행 테스트 실패" : g.test_result === "timeout" ? " ⏱️ 실행 테스트 시간 초과" : g.test_result === "not_tested" ? " (테스트 미실행)" : ""}</div>`;
  } else if (g.status === "available_via_host") {
    html += `<div style="font-size: 12px; color: #666; margin-top: 5px;">로컬(호스트)에 로컬 LLM 설치됨. AI 추론은 로컬 환경에서 사용 가능</div>`;
  } else if (g.status === "not_installed") {
    html += `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(g.install_command || "pip install gpt4all")}</div>`;
  } else if (g.error) {
    html += `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(g.error)}</div>`;
  }
  if (g.test_error && (!g.models || g.models.length < 2)) {
    html += `<div style="font-size: 11px; color: #dc2626; margin-top: 3px; padding-left: 10px;">테스트 오류: ${escapeHtml(g.test_error)}</div>`;
  }
  if (g.message) html += `<div style="font-size: 11px; color: #666; margin-top: 3px; padding-left: 10px;">${escapeHtml(g.message)}</div>`;
  html += "</div>";
  return html;
}

/**
 * 최근 작업 표시
 */
function renderRecentWork(recentWork) {
  if (recentWork.length > 0) {
    document.getElementById("recent-work").innerHTML = recentWork.map((work) => `
      <div class="work-item">
        <strong>${escapeHtml(work.action || "-")}</strong>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(work.description || "")}</div>
        <div style="font-size: 11px; color: #999; margin-top: 5px;">${escapeHtml(work.date || "")} ${escapeHtml(work.time || "")}</div>
      </div>
    `).join("");
  } else {
    showEmptyState("recent-work", "최근 작업이 없습니다.");
  }
}

/**
 * 자동화 상태 표시
 */
function renderAutomationStatus(automation) {
  document.getElementById("automation-status").innerHTML = `
    <div class="status-item">파일 감시 시스템 <span class="status-badge ${automation.watcher_running ? "connected" : "error"}">${automation.watcher_running ? "실행 중" : "중지됨"}</span></div>
    <div class="status-item">Git 자동 커밋: ${automation.git_auto_commit ? "활성화" : "비활성화"}</div>
  `;
}

/**
 * 최근 업데이트 문서 표시
 */
function renderRecentDocuments(recentDocs) {
  if (recentDocs.length > 0) {
    document.getElementById("recent-documents").innerHTML = recentDocs.map((doc) => `
      <div class="work-item">
        <strong>${createDocumentLink(doc.file_path, doc.name, { style: "color: #2563eb; text-decoration: none;" })}</strong>
        <div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(doc.file_path)}</div>
      </div>
    `).join("");
  } else {
    showEmptyState("recent-documents", "최근 문서가 없습니다.");
  }
}

/**
 * 활동 차트 HTML 생성
 */
function renderActivityChart(logsData) {
  const byDate = logsData.by_date || {};
  const dates = Object.keys(byDate).slice(0, DASHBOARD_CONSTANTS.CHART_DAYS).reverse();
  const maxValue = Math.max(...Object.values(byDate), 1);
  if (dates.length > 0) {
    document.getElementById("activity-chart").innerHTML = `
      <div class="chart-container"><div class="activity-chart">
        ${dates.map((date) => `<div class="chart-bar" style="height: ${(byDate[date] / maxValue) * 100}%" title="${escapeHtml(date)}: ${byDate[date]}개"><div class="chart-label">${escapeHtml(date.split("-")[2] || date)}</div></div>`).join("")}
      </div></div>
    `;
  } else {
    showEmptyState("activity-chart", "활동 데이터가 없습니다.");
  }
}

/**
 * 활동 요약 표시
 */
function renderActivitySummary(logsData) {
  document.getElementById("activity-summary").innerHTML = `
    <div class="summary-item"><div class="summary-label">총 작업</div><div class="summary-value">${logsData.total_entries || 0}</div></div>
    <div class="summary-item"><div class="summary-label">커밋</div><div class="summary-value">${logsData.by_action?.commit || 0}</div></div>
    <div class="summary-item"><div class="summary-label">파일 변경</div><div class="summary-value">${logsData.by_action?.file_change || 0}</div></div>
    <div class="summary-item"><div class="summary-label">임베딩</div><div class="summary-value">${logsData.by_action?.embed || 0}</div></div>
  `;
}

/**
 * 문서 관련 함수
 */
function groupDocumentsByFolder(documents) {
  const grouped = {};
  documents.forEach((doc) => {
    const pathParts = doc.file_path.split("/");
    const folder = pathParts.slice(0, -1).join("/") || "루트";
    if (!grouped[folder]) grouped[folder] = [];
    grouped[folder].push(doc);
  });
  return grouped;
}

function renderDocumentItem(doc) {
  const sizeKB = (doc.size / 1024).toFixed(1);
  const date = new Date(doc.modified * 1000);
  const dateStr = date.toLocaleDateString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit" });
  const timeStr = date.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit" });
  return `<div class="document-item" onclick="openDocument('${doc.file_path.replace(/'/g, "\\'")}')">
    <div class="document-info"><div class="document-name">${escapeHtml(doc.name)}</div><div class="document-path">${escapeHtml(doc.file_path)}</div></div>
    <div class="document-meta"><div class="document-size">${escapeHtml(sizeKB)} KB</div><div class="document-date">${escapeHtml(dateStr)} ${escapeHtml(timeStr)}</div></div>
  </div>`;
}

function displayDocuments(documents) {
  if (documents.length === 0) { showEmptyState("documents-list", "문서가 없습니다."); return; }
  const grouped = groupDocumentsByFolder(documents);
  const sortedFolders = Object.keys(grouped).sort();
  let html = '<div class="documents-list">';
  sortedFolders.forEach((folder) => {
    html += `<div class="folder-group"><div class="folder-header">📁 ${escapeHtml(folder)}</div>`;
    grouped[folder].forEach((doc) => { html += renderDocumentItem(doc); });
    html += "</div>";
  });
  html += "</div>";
  document.getElementById("documents-list").innerHTML = html;
}

function filterDocuments() {
  const searchTerm = document.getElementById("document-search").value.toLowerCase();
  if (!searchTerm) { displayDocuments(allDocuments); return; }
  displayDocuments(allDocuments.filter((doc) => doc.name.toLowerCase().includes(searchTerm) || doc.file_path.toLowerCase().includes(searchTerm)));
}

/**
 * 상태 업데이트 헬퍼
 */
function renderVenvStatusHtml(data) {
  return `<div class="status-item">
    가상환경 상태
    <span class="status-badge ${data.status === "activated" ? "connected" : "error"}">${data.status === "activated" ? "활성화됨" : data.status === "packages_missing" ? "패키지 누락" : "비활성화됨"}</span>
    <button onclick="testVenvPackages()" style="margin-left: 10px; padding: 4px 12px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;" id="test-venv-btn">🔄 패키지 재확인</button>
    ${data.status === "activated" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">${escapeHtml(data.venv_path || "")}</div>` : data.status === "packages_missing" ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.message || "누락된 패키지가 있습니다")}</div>` : `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.message || "가상환경을 활성화하세요")}</div>`}
    ${data.packages_status && Object.keys(data.packages_status).length > 0 ? `<div style="font-size: 11px; color: #666; margin-top: 5px; padding-left: 10px;">패키지: ${escapeHtml(Object.entries(data.packages_status).filter(([_, s]) => s === "installed").map(([n]) => n).join(", ") || "없음")}</div>` : ""}
  </div>`;
}

function updateSystemStatusSection(statusHtml, pattern) {
  const systemStatusDiv = document.getElementById("system-status");
  if (systemStatusDiv) {
    const currentHtml = systemStatusDiv.innerHTML;
    const match = currentHtml.match(pattern);
    if (match) systemStatusDiv.innerHTML = currentHtml.replace(match[0], statusHtml);
  }
}

function renderGpt4AllStatusHtml(data) {
  return `<div class="status-item">
    GPT4All 상태
    <span class="status-badge ${data.status === "available" ? "connected" : "error"}">${data.status === "available" ? "사용 가능" : data.status === "not_installed" ? "미설치" : "오류"}</span>
    ${data.status === "available" ? `<button onclick="testGpt4All()" style="margin-left: 10px; padding: 4px 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;" id="test-gpt4all-btn">🧪 실행 테스트</button>` : ""}
    ${data.status === "available" ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">모델: ${escapeHtml(data.model_name || "-")}${data.test_result === "success" ? " ✅ 실행 테스트 성공" : data.test_result === "error" ? " ⚠️ 실행 테스트 실패" : data.test_result === "timeout" ? " ⏱️ 실행 테스트 시간 초과" : data.test_result === "not_tested" ? " (테스트 미실행)" : ""}</div>` : data.status === "not_installed" ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.install_command || "pip install gpt4all")}</div>` : data.error ? `<div style="font-size: 12px; color: #dc2626; margin-top: 5px;">${escapeHtml(data.error)}</div>` : ""}
    ${data.test_error ? `<div style="font-size: 11px; color: #dc2626; margin-top: 3px; padding-left: 10px;">테스트 오류: ${escapeHtml(data.test_error)}</div>` : ""}
    ${data.message ? `<div style="font-size: 11px; color: #666; margin-top: 3px; padding-left: 10px;">${escapeHtml(data.message)}</div>` : ""}
  </div>`;
}

function showGpt4AllTestResult(data, model) {
  const modelLabel = (data.tested_model || model) ? " (" + (data.tested_model || model) + ")" : "";
  if (data.test_result === "success") alert("로컬 LLM 실행 테스트 성공!" + modelLabel);
  else if (data.test_result === "timeout") alert("실행 테스트 시간 초과 (90초). 모델이 로딩 중일 수 있습니다." + modelLabel);
  else if (data.test_result === "error") alert("실행 테스트 실패: " + (data.test_error || data.error || "알 수 없는 오류") + modelLabel);
  else alert("로컬 LLM 테스트 완료" + modelLabel);
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
