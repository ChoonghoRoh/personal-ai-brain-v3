/**
 * 대시보드 API 모듈
 * 데이터 로딩, LLM 테스트 등 API 호출 함수
 * Traditional script 패턴 (전역 함수)
 */

/**
 * 대시보드 로드 (메인 함수)
 */
async function loadDashboard() {
  try {
    const response = await fetch("/api/system/status");
    const data = await response.json();
    updateSystemStats(data);
    renderSystemStatus(data);
    renderRecentWork(data.recent_work || []);
    renderAutomationStatus(data.automation || {});
    renderRecentDocuments(data.recent_documents || []);
  } catch (error) {
    console.error("대시보드 로드 오류:", error);
    showError("system-status", "오류가 발생했습니다.");
  }
}

/**
 * 분석 데이터 로드
 */
async function loadAnalytics() {
  try {
    const [statusResponse, logsResponse] = await Promise.all([fetch("/api/system/status"), fetch("/api/logs/stats")]);
    const logsData = await logsResponse.json();
    renderActivityChart(logsData);
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
    const response = await fetch("/api/system/test/venv-packages", { method: "POST" });
    const data = await response.json();
    const statusHtml = renderVenvStatusHtml(data);
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
 * 모델별 테스트 버튼 클릭 시
 */
function testGpt4AllWithButton(btn) {
  const model = btn && btn.getAttribute ? btn.getAttribute("data-model") : null;
  testGpt4All(model || undefined, btn);
}

/**
 * GPT4All(Ollama) 실행 테스트
 * @param {string} [model] - 테스트할 모델명
 * @param {HTMLElement} [btn] - 클릭된 버튼
 */
async function testGpt4All(model, btn) {
  const targetBtn = btn || document.getElementById("test-gpt4all-btn");
  if (targetBtn) {
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
