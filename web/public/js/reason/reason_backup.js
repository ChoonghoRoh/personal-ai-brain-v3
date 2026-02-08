/**
 * Reasoning Lab 메인 모듈 (Phase 10-1, 10-2)
 *
 * 주요 기능:
 * - 지식 기반 추론 및 방향 제안
 * - 5단계 진행 상태 실시간 표시 (Phase 10-1-1)
 * - 분석 작업 취소 기능 (Phase 10-1-2)
 * - 예상 소요 시간 표시 (Phase 10-1-3)
 * - 모드별 시각화: design_explain(Mermaid), risk_review(5x5), next_steps(로드맵), history_trace(타임라인) (Phase 10-2)
 */

// ========================================
// 전역 변수
// ========================================

/** Reasoning 대기 중 경과 시간 타이머 */
let reasoningElapsedTimerId = null;

/** 현재 진행 중인 태스크 ID */
let currentTaskId = null;

/** EventSource 인스턴스 */
let currentEventSource = null;

/** 시작 시간 */
let reasoningStartTime = null;

// ========================================
// 유틸리티 함수
// ========================================

/**
 * 로딩 메시지 표시
 */
function showLoading(elementId, message = "로딩 중...", style = "") {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="loading" ${style ? `style="${style}"` : ""}>${escapeHtml(message)}</div>`;
  }
}

// ========================================
// 모드 설명
// ========================================

const modeDescriptions = {
  design_explain: "설계 의도와 배경을 명확히 설명합니다. 왜 이렇게 설계했는지, 어떤 맥락에서 결정했는지를 파악할 때 사용합니다.",
  risk_review: "잠재적 리스크와 문제점을 식별합니다. 관계 그래프를 통해 영향도를 추적하고 위험 요소를 발견할 때 사용합니다.",
  next_steps: "현재 상태를 기반으로 논리적인 다음 단계를 제안합니다. 프로젝트 진행 방향이나 개선 사항을 찾을 때 사용합니다.",
  history_trace: "지식의 진화와 맥락을 시간적/논리적 순서로 추적합니다. 의사결정 과정이나 변화 흐름을 이해할 때 사용합니다.",
};

// 모드 선택 시 설명 업데이트
const modeSelect = document.getElementById("mode");
if (modeSelect) {
  modeSelect.addEventListener("change", function () {
    const mode = this.value;
    const description = modeDescriptions[mode] || "각 모드의 용도를 선택하세요";
    const descEl = document.getElementById("mode-description");
    if (descEl) descEl.textContent = description;
  });
}

// ========================================
// 초기화
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🧠 Reasoning Lab",
      subtitle: "지식 기반 추론 및 방향 제안",
      currentPath: "/reason",
    });
  }

  // 초기 모드 설명 설정
  const modeEl = document.getElementById("mode");
  const modeDescEl = document.getElementById("mode-description");
  if (modeEl && modeDescEl) {
    modeDescEl.textContent = modeDescriptions[modeEl.value] || "각 모드의 용도를 선택하세요";
  }

  // LLM 모델 목록 로드
  if (typeof loadOllamaModelOptions === "function") {
    loadOllamaModelOptions("reason-model");
  }

  // 보조 조회: 프로젝트·라벨 목록 로드
  loadReasoningOptions();

  // 취소 버튼 이벤트 바인딩
  const cancelBtn = document.getElementById("cancel-btn");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", cancelReasoning);
  }
});

/**
 * Reasoning 보조 옵션 로드 (프로젝트, 라벨 목록)
 */
async function loadReasoningOptions() {
  try {
    const [projectsRes, labelsRes] = await Promise.all([
      fetch("/api/knowledge/projects"),
      fetch("/api/labels"),
    ]);
    const projects = projectsRes.ok ? await projectsRes.json() : [];
    let labels = [];
    if (labelsRes.ok) {
      const labelsData = await labelsRes.json();
      labels = Array.isArray(labelsData) ? labelsData : (labelsData.items || []);
    }
    const projectsSelect = document.getElementById("projects-select");
    const labelsSelect = document.getElementById("labels-select");
    if (projectsSelect) {
      projectsSelect.innerHTML = (projects || [])
        .map((p) => `<option value="${Number(p.id)}">${escapeHtml(p.name || "")}</option>`)
        .join("");
    }
    if (labelsSelect) {
      labelsSelect.innerHTML = (labels || [])
        .map((l) => {
          const id = l.id != null ? l.id : l.label_id;
          const name = l.name != null ? l.name : (l.label_name || "");
          return `<option value="${escapeHtml(String(name))}">${escapeHtml(name)}</option>`;
        })
        .join("");
    }
  } catch (e) {
    console.warn("Reasoning 옵션 로드 실패:", e);
  }
}

// URL 파라미터에서 seed_chunk 확인
const urlParams = new URLSearchParams(window.location.search);
const seedChunkId = urlParams.get("seed_chunk");

if (seedChunkId) {
  loadSeedChunk(seedChunkId);
}

/**
 * 시드 청크 로드
 */
async function loadSeedChunk(chunkId) {
  try {
    const response = await fetch(`/api/knowledge/chunks/${chunkId}`);
    const chunk = await response.json();
    document.getElementById("question").value = `다음 청크를 기반으로 Reasoning을 시작합니다:\n\n${chunk.content.substring(0, 200)}...`;
  } catch (error) {
    console.error("Seed chunk 로드 실패:", error);
  }
}

// ========================================
// Phase 10-1-1: 진행 상태 실시간 표시
// ========================================

/**
 * 진행 단계 UI 업데이트
 * @param {number} currentStage - 현재 단계 (1-5)
 * @param {string} message - 표시할 메시지
 * @param {number} percent - 진행률 (0-100)
 */
function updateProgressStage(currentStage, message, percent) {
  // 단계 아이콘 업데이트
  const stages = document.querySelectorAll(".progress-stage");
  const connectors = document.querySelectorAll(".progress-connector");

  stages.forEach((stage, index) => {
    const stageNum = index + 1;
    stage.classList.remove("pending", "active", "completed");

    if (stageNum < currentStage) {
      stage.classList.add("completed");
    } else if (stageNum === currentStage) {
      stage.classList.add("active");
    } else {
      stage.classList.add("pending");
    }
  });

  // 연결선 업데이트
  connectors.forEach((connector, index) => {
    const connectorNum = index + 1;
    connector.classList.remove("active", "completed");

    if (connectorNum < currentStage) {
      connector.classList.add("completed");
    } else if (connectorNum === currentStage) {
      connector.classList.add("active");
    }
  });

  // 진행률 바 업데이트
  const progressBar = document.getElementById("progress-bar");
  if (progressBar) {
    progressBar.style.width = `${percent}%`;
  }

  // 메시지 업데이트
  const progressMessage = document.getElementById("progress-message");
  if (progressMessage) {
    progressMessage.textContent = `⏳ ${message}`;
  }
}

/**
 * 경과 시간 타이머 시작
 */
function startElapsedTimer() {
  const elapsedEl = document.getElementById("reasoning-elapsed-text");
  if (!elapsedEl) return;

  elapsedEl.textContent = "잠시만 기다려주세요...";

  if (reasoningElapsedTimerId) {
    clearInterval(reasoningElapsedTimerId);
  }

  reasoningStartTime = Date.now();
  let seconds = 0;

  reasoningElapsedTimerId = setInterval(function () {
    seconds = Math.floor((Date.now() - reasoningStartTime) / 1000);
    const text = seconds <= 1 ? "잠시만 기다려주세요..." : `경과 시간: ${seconds}초`;
    const el = document.getElementById("reasoning-elapsed-text");
    if (el) el.textContent = text;
  }, 1000);
}

/**
 * 경과 시간 타이머 중지
 */
function stopElapsedTimer() {
  if (reasoningElapsedTimerId) {
    clearInterval(reasoningElapsedTimerId);
    reasoningElapsedTimerId = null;
  }
}

// ========================================
// Phase 10-1-2: 취소 기능
// ========================================

/**
 * Reasoning 작업 취소
 */
async function cancelReasoning() {
  if (!currentTaskId) {
    console.warn("취소할 태스크가 없습니다.");
    return;
  }

  try {
    // EventSource 닫기
    if (currentEventSource) {
      currentEventSource.close();
      currentEventSource = null;
    }

    // 서버에 취소 요청
    const response = await fetch(`/api/reason/${currentTaskId}/cancel`, {
      method: "POST",
    });

    const result = await response.json();
    console.log("취소 결과:", result);

    // UI 업데이트
    showCancelledState();
    restoreReasoningUI();

  } catch (error) {
    console.error("취소 요청 실패:", error);
  }
}

/**
 * 취소됨 상태 표시
 */
function showCancelledState() {
  const progressMessage = document.getElementById("progress-message");
  if (progressMessage) {
    progressMessage.textContent = "❌ 사용자에 의해 취소됨";
  }

  const progressContainer = document.querySelector(".results-loading");
  if (progressContainer) {
    progressContainer.classList.add("progress-cancelled");
  }

  const progressBar = document.getElementById("progress-bar");
  if (progressBar) {
    progressBar.style.background = "#ef4444";
  }
}

// ========================================
// Phase 10-1-3: 예상 소요 시간
// ========================================

/**
 * 예상 소요 시간 로드 및 표시
 */
async function loadAndDisplayETA() {
  const modeEl = document.getElementById("mode");
  const mode = modeEl ? modeEl.value : "design_explain";

  try {
    const response = await fetch(`/api/reason/eta?mode=${mode}`);
    if (response.ok) {
      const data = await response.json();
      const etaText = document.getElementById("eta-text");
      if (etaText) {
        etaText.textContent = `예상 소요 시간: ${data.display_text}`;
      }
    }
  } catch (error) {
    console.warn("ETA 로드 실패:", error);
    const etaText = document.getElementById("eta-text");
    if (etaText) {
      etaText.textContent = "예상 소요 시간: 약 30초~1분";
    }
  }
}

// ========================================
// UI 관리 함수
// ========================================

/**
 * 이전 결과 영역 비우기
 */
function clearReasoningResults() {
  const docCountEl = document.getElementById("summary-docs-count");
  const chunkCountEl = document.getElementById("summary-chunks-count");
  const relCountEl = document.getElementById("summary-relations-count");
  const answerDiv = document.getElementById("answer");
  const contextChunksDiv = document.getElementById("context-chunks");
  const contextDocumentsDiv = document.getElementById("context-documents");
  const stepsDiv = document.getElementById("reasoning-steps");

  if (docCountEl) docCountEl.textContent = "-";
  if (chunkCountEl) chunkCountEl.textContent = "-";
  if (relCountEl) relCountEl.textContent = "-";
  if (answerDiv) answerDiv.textContent = "";
  if (contextChunksDiv) contextChunksDiv.innerHTML = "";
  if (contextDocumentsDiv) contextDocumentsDiv.innerHTML = "";
  if (stepsDiv) stepsDiv.innerHTML = "";

  hideRecommendationsSection();

  const recSection = document.getElementById("recommendations-section");
  if (recSection) recSection.style.display = "none";

  ["related-chunks", "suggested-labels", "sample-questions", "explore-more"].forEach(function (id) {
    const el = document.getElementById(id);
    if (el) el.innerHTML = "";
  });

  clearModeViz();
}

/**
 * Phase 10-2: 모드별 시각화 영역 비우기
 */
function clearModeViz() {
  const container = document.getElementById("mode-viz-container");
  if (container) {
    container.style.display = "none";
  }
  ["viz-design-explain", "viz-risk-review", "viz-next-steps", "viz-history-trace"].forEach(function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.innerHTML = "";
      el.style.display = "none";
    }
  });
  if (window.__riskReviewChart) {
    try {
      window.__riskReviewChart.destroy();
    } catch (e) {}
    window.__riskReviewChart = null;
  }
}

/**
 * 진행 단계 초기화
 */
function resetProgressStages() {
  const stages = document.querySelectorAll(".progress-stage");
  stages.forEach((stage) => {
    stage.classList.remove("pending", "active", "completed");
    stage.classList.add("pending");
  });

  const connectors = document.querySelectorAll(".progress-connector");
  connectors.forEach((connector) => {
    connector.classList.remove("active", "completed");
  });

  const progressBar = document.getElementById("progress-bar");
  if (progressBar) {
    progressBar.style.width = "0%";
    progressBar.style.background = "";
  }

  const progressContainer = document.querySelector(".results-loading");
  if (progressContainer) {
    progressContainer.classList.remove("progress-cancelled");
  }

  const progressMessage = document.getElementById("progress-message");
  if (progressMessage) {
    progressMessage.textContent = "⏳ Reasoning 준비 중...";
  }
}

/**
 * UI 초기화 (버튼 비활성화 + 로딩 영역만 표시)
 */
function initializeReasoningUI() {
  const submitBtn = document.getElementById("submit-btn");
  const cancelBtn = document.getElementById("cancel-btn");
  const resultsDiv = document.getElementById("results");
  const resultsLoading = document.getElementById("results-loading");
  const resultsContent = document.getElementById("results-content");
  const errorDiv = document.getElementById("error-message");

  clearReasoningResults();
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

  // 취소 버튼 표시
  if (cancelBtn) {
    cancelBtn.style.display = "inline-block";
  }

  // 타이머 시작
  startElapsedTimer();

  // ETA 표시
  loadAndDisplayETA();
}

/**
 * UI 상태 복원
 */
function restoreReasoningUI() {
  stopElapsedTimer();

  const submitBtn = document.getElementById("submit-btn");
  const cancelBtn = document.getElementById("cancel-btn");

  if (submitBtn) {
    submitBtn.disabled = false;
    submitBtn.removeAttribute("aria-busy");
    submitBtn.textContent = "🚀 Reasoning 실행";
  }

  // 취소 버튼 숨기기
  if (cancelBtn) {
    cancelBtn.style.display = "none";
  }

  currentTaskId = null;
}

/**
 * Reasoning 요청 데이터 준비
 */
function prepareReasoningRequest() {
  const mode = document.getElementById("mode").value;
  const question = document.getElementById("question").value.trim();

  // 프로젝트: 선택 + 직접 입력 병합
  const projectsSelect = document.getElementById("projects-select");
  const projectsInput = document.getElementById("projects").value.trim();
  const selectedProjectIds = projectsSelect
    ? Array.from(projectsSelect.selectedOptions).map((o) => parseInt(o.value, 10)).filter((n) => !isNaN(n))
    : [];
  const parsedProjectIds = projectsInput
    ? projectsInput.split(",").map((p) => parseInt(p.trim())).filter((p) => !isNaN(p))
    : [];
  const projects = [...new Set([...selectedProjectIds, ...parsedProjectIds])];

  // 라벨: 선택 + 직접 입력 병합
  const labelsSelect = document.getElementById("labels-select");
  const labelsInput = document.getElementById("labels").value.trim();
  const selectedLabelNames = labelsSelect
    ? Array.from(labelsSelect.selectedOptions).map((o) => o.value.trim()).filter(Boolean)
    : [];
  const parsedLabelNames = labelsInput ? labelsInput.split(",").map((l) => l.trim()).filter(Boolean) : [];
  const labels = [...new Set([...selectedLabelNames, ...parsedLabelNames])];

  const modelSelect = document.getElementById("reason-model");
  const model = modelSelect && modelSelect.value ? modelSelect.value.trim() : null;

  return {
    mode: mode,
    inputs: {
      projects: projects,
      labels: labels,
    },
    question: question || null,
    model: model || null,
  };
}

// ========================================
// SSE 스트리밍 Reasoning 실행
// ========================================

/**
 * Reasoning 실행 (SSE 스트리밍)
 */
async function runReasoning(event) {
  if (event && event.preventDefault) event.preventDefault();

  initializeReasoningUI();

  const requestBody = prepareReasoningRequest();

  try {
    // SSE 연결
    const response = await fetch("/api/reason/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Task ID 추출
    currentTaskId = response.headers.get("X-Task-ID");

    // SSE 이벤트 처리
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE 이벤트 파싱
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // 마지막 불완전한 라인 유지

      let eventType = null;
      let eventData = null;

      for (const line of lines) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          try {
            eventData = JSON.parse(line.slice(6));
          } catch (e) {
            console.warn("JSON 파싱 실패:", line);
            continue;
          }

          // 이벤트 처리
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

/**
 * SSE 이벤트 핸들러
 */
function handleSSEEvent(eventType, data) {
  switch (eventType) {
    case "progress":
      // Task ID 저장
      if (data.task_id && !currentTaskId) {
        currentTaskId = data.task_id;
      }
      updateProgressStage(data.stage, data.message, data.percent);
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
      restoreReasoningUI();
      break;

    default:
      console.log("알 수 없는 이벤트:", eventType, data);
  }
}

/**
 * Reasoning 결과 처리
 */
function processReasoningResult(result) {
  const resultsLoading = document.getElementById("results-loading");
  const resultsContent = document.getElementById("results-content");
  const resultsDiv = document.getElementById("results");

  if (resultsLoading) resultsLoading.style.display = "none";
  if (resultsContent) resultsContent.style.display = "block";
  if (resultsDiv) {
    resultsDiv.style.display = "block";
    resultsDiv.classList.add("active");
  }

  displayResults(result);
}

/**
 * 에러 메시지 표시
 */
function showReasoningError(error) {
  const errorDiv = document.getElementById("error-message");

  let errorMessage = "Reasoning 실행 중 오류가 발생했습니다.";
  if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
    errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
  } else if (error.message) {
    errorMessage = error.message;
  }

  if (errorDiv) {
    errorDiv.innerHTML = `
      <div style="padding: 15px; background: #fee2e2; border: 1px solid #dc2626; border-radius: 6px; color: #dc2626;">
        <strong>❌ 오류 발생</strong>
        <p style="margin: 10px 0 0 0;">${escapeHtml(errorMessage)}</p>
      </div>
    `;
    errorDiv.style.display = "block";
  }

  // 로딩 숨기고 결과 영역 표시
  const resultsLoading = document.getElementById("results-loading");
  const resultsContent = document.getElementById("results-content");
  if (resultsLoading) resultsLoading.style.display = "none";
  if (resultsContent) resultsContent.style.display = "block";
}

// ========================================
// 결과 표시 함수
// ========================================

/**
 * 컨텍스트 탭 전환
 */
function switchContextTab(tab) {
  document.querySelectorAll(".tab-btn").forEach((btn) => btn.classList.remove("active"));
  document.querySelectorAll(".context-content").forEach((content) => content.classList.remove("active"));

  if (tab === "chunks") {
    document.querySelector(".tab-btn:first-child").classList.add("active");
    document.getElementById("context-chunks").classList.add("active");
  } else {
    document.querySelector(".tab-btn:last-child").classList.add("active");
    document.getElementById("context-documents").classList.add("active");
  }
}

/**
 * 결과 요약 표시
 */
function renderSummary(result) {
  const chunks = result.context_chunks || [];
  const relations = result.relations || [];
  const uniqueDocs = new Set(chunks.map((c) => c.document).filter((d) => d));

  const docCountEl = document.getElementById("summary-docs-count");
  const chunkCountEl = document.getElementById("summary-chunks-count");
  const relCountEl = document.getElementById("summary-relations-count");

  if (docCountEl) docCountEl.textContent = uniqueDocs.size;
  if (chunkCountEl) chunkCountEl.textContent = chunks.length;
  if (relCountEl) relCountEl.textContent = relations.length;
}

/**
 * 최종 결론 표시
 */
function renderConclusion(result) {
  const answerDiv = document.getElementById("answer");
  if (answerDiv) {
    answerDiv.textContent = result.answer || "답변을 생성할 수 없습니다.";
  }
}

/**
 * 컨텍스트 청크 표시
 */
function renderContextChunks(chunks) {
  const contextChunksDiv = document.getElementById("context-chunks");
  if (!contextChunksDiv) return;

  if (chunks.length > 0) {
    contextChunksDiv.innerHTML = chunks
      .map((chunk) => {
        const metaParts = [];
        if (chunk.project) metaParts.push(`<strong>${escapeHtml(chunk.project)}</strong>`);
        if (chunk.project_id != null) metaParts.push(`프로젝트 ID: ${chunk.project_id}`);
        metaParts.push(escapeHtml(chunk.document || "알 수 없음"));
        metaParts.push(`청크 ID: ${chunk.id || "N/A"}`);
        const labels = chunk.labels && chunk.labels.length ? chunk.labels : [];
        const labelsHtml = labels.length
          ? ` <span class="chunk-labels">${labels.map((l) => `<span class="chunk-label-tag">${escapeHtml(l)}</span>`).join(" ")}</span>`
          : "";
        return `
          <div class="chunk-item">
            <div class="chunk-meta">${metaParts.join(" / ")}${labelsHtml}</div>
            <div class="chunk-content">${escapeHtml(chunk.content || "내용 없음")}</div>
          </div>
        `;
      })
      .join("");
  } else {
    contextChunksDiv.innerHTML = '<p style="color: #999;">사용된 컨텍스트 청크가 없습니다.</p>';
  }
}

/**
 * 문서 목록 표시
 */
function renderContextDocuments(chunks) {
  const contextDocumentsDiv = document.getElementById("context-documents");
  if (!contextDocumentsDiv) return;

  const documentMap = new Map();
  chunks.forEach((chunk) => {
    if (chunk.document && !documentMap.has(chunk.document)) {
      documentMap.set(chunk.document, {
        name: chunk.document,
        project: chunk.project,
        chunks: [],
      });
    }
    if (chunk.document) {
      documentMap.get(chunk.document).chunks.push(chunk);
    }
  });

  if (documentMap.size > 0) {
    contextDocumentsDiv.innerHTML = Array.from(documentMap.values())
      .map((doc) => {
        const docPath = doc.name.startsWith("brain/") ? doc.name : `brain/${doc.name}`;
        return `
          <div class="document-item">
            <div class="doc-info">
              <div class="doc-name">${escapeHtml(doc.name)}</div>
              <div class="doc-meta">
                ${doc.project ? `프로젝트: ${escapeHtml(doc.project)} / ` : ""}
                ${doc.chunks.length}개 청크 사용됨
              </div>
            </div>
            <a href="/document/${encodeURIComponent(docPath)}" class="doc-btn" target="_blank">
              문서 열기 →
            </a>
          </div>
        `;
      })
      .join("");
  } else {
    contextDocumentsDiv.innerHTML = '<p style="color: #999;">사용된 문서가 없습니다.</p>';
  }
}

/**
 * 컨텍스트 표시
 */
function renderContext(chunks) {
  renderContextChunks(chunks);
  renderContextDocuments(chunks);
}

/**
 * Reasoning 단계 표시
 */
function renderSteps(steps) {
  const stepsDiv = document.getElementById("reasoning-steps");
  if (!stepsDiv) return;

  if (steps && steps.length > 0) {
    stepsDiv.innerHTML = `<ol>${steps.map((step) => `<li>${escapeHtml(step || "단계 정보 없음")}</li>`).join("")}</ol>`;
  } else {
    stepsDiv.innerHTML = '<p style="color: #999;">Reasoning 단계 정보가 없습니다.</p>';
  }
}

/**
 * Reasoning 결과 표시 (메인)
 */
function displayResults(result) {
  if (!result) {
    console.error("displayResults: result가 없습니다");
    return;
  }

  const chunks = result.context_chunks || [];
  const mode = (document.getElementById("mode") && document.getElementById("mode").value) || "design_explain";

  renderSummary(result);
  renderModeViz(result, mode);
  renderConclusion(result);
  renderContext(chunks);
  renderSteps(result.reasoning_steps);

  if (result.recommendations) {
    displayRecommendations(result.recommendations);
  } else {
    hideRecommendationsSection();
  }
}

/**
 * Phase 10-2: 모드별 시각화 표시
 */
function renderModeViz(result, mode) {
  const container = document.getElementById("mode-viz-container");
  const titleEl = document.getElementById("mode-viz-title");
  if (!container || !titleEl) return;

  const titles = {
    design_explain: "📐 설계/배경 시각화",
    risk_review: "⚠️ 리스크 매트릭스",
    next_steps: "🚀 다음 단계 로드맵",
    history_trace: "📜 히스토리 타임라인",
  };
  titleEl.textContent = titles[mode] || "시각화";

  let panel = null;
  switch (mode) {
    case "design_explain":
      panel = document.getElementById("viz-design-explain");
      if (panel) {
        renderDesignExplainViz(result, panel);
        panel.style.display = "block";
      }
      break;
    case "risk_review":
      panel = document.getElementById("viz-risk-review");
      if (panel) {
        renderRiskReviewViz(result, panel);
        panel.style.display = "block";
      }
      break;
    case "next_steps":
      panel = document.getElementById("viz-next-steps");
      if (panel) {
        renderNextStepsViz(result, panel);
        panel.style.display = "block";
      }
      break;
    case "history_trace":
      panel = document.getElementById("viz-history-trace");
      if (panel) {
        renderHistoryTraceViz(result, panel);
        panel.style.display = "block";
      }
      break;
    default:
      break;
  }

  if (panel && panel.innerHTML.trim()) {
    container.style.display = "block";
  }
}

/**
 * 10-2-1: design_explain — Mermaid 다이어그램 렌더링
 * Mermaid 10: mermaid.render(id, code)로 SVG 반환 후 삽입 (Phase 10-2)
 */
function renderDesignExplainViz(result, container) {
  const text = [result.answer || "", (result.reasoning_steps || []).join("\n")].join("\n");
  // 블록 추출: ```mermaid ... ``` 또는 ``` mermaid ... ``` (공백 허용), 닫는 ``` 없으면 끝까지
  let mermaidMatch = text.match(/```\s*mermaid\s*([\s\S]*?)```/i);
  if (!mermaidMatch) {
    mermaidMatch = text.match(/```\s*mermaid\s*([\s\S]+)/i);
  }
  if (!mermaidMatch && /flowchart|graph\s+(LR|TD|TB|BT)|sequenceDiagram|classDiagram/.test(text)) {
    var start = text.search(/(?:^|\n)\s*(flowchart|graph\s+(?:LR|TD|TB|BT)|sequenceDiagram|classDiagram)/im);
    if (start >= 0) {
      var rest = text.slice(start).trim();
      var endMatch = rest.match(/\n```\s*$/m);
      var code = endMatch ? rest.slice(0, endMatch.index).trim() : rest.trim();
      if (code.length > 10) mermaidMatch = [null, code];
    }
  }
  if (!mermaidMatch) {
    container.innerHTML =
      '<p class="viz-fallback">Mermaid 다이어그램을 표시하려면 LLM 응답에 <code>```mermaid ... ```</code> 블록을 포함해 주세요.</p>';
    return;
  }
  const mermaidCode = mermaidMatch[1].trim();
  const id = "mermaid-viz-" + Date.now();
  container.innerHTML = '<div class="mermaid-viz-wrapper"><div id="' + id + '" class="mermaid-viz"></div></div>';
  const target = document.getElementById(id);
  if (!target) return;
  if (typeof mermaid !== "undefined") {
    if (typeof mermaid.initialize === "function" && !window.__mermaidReasonInitialized) {
      mermaid.initialize({ startOnLoad: false });
      window.__mermaidReasonInitialized = true;
    }
    if (typeof mermaid.render === "function") {
      mermaid
        .render(id, mermaidCode)
        .then(function (out) {
          if (out && out.svg) {
            target.innerHTML = out.svg;
            if (typeof out.bindFunctions === "function") {
              out.bindFunctions(target);
            }
          } else {
            target.innerHTML = '<pre class="mermaid-code">' + escapeHtml(mermaidCode) + "</pre>";
          }
        })
        .catch(function (err) {
          target.innerHTML = '<p class="viz-error">다이어그램 렌더링 실패: ' + escapeHtml(String(err.message || err)) + "</p>";
        });
    } else {
      target.className = "mermaid-viz mermaid";
      target.textContent = mermaidCode;
      mermaid
        .run({ nodes: [target], suppressErrors: true })
        .catch(function (err) {
          target.innerHTML = '<p class="viz-error">다이어그램 렌더링 실패: ' + escapeHtml(String(err.message || err)) + "</p>";
        });
    }
  } else {
    target.innerHTML = '<pre class="mermaid-code">' + escapeHtml(mermaidCode) + "</pre>";
  }
}

/**
 * 10-2-2: risk_review — 5x5 리스크 매트릭스
 */
function renderRiskReviewViz(result, container) {
  const steps = result.reasoning_steps || [];
  const items = steps.map(function (s, i) {
    return { label: (s || "").substring(0, 60) + ((s || "").length > 60 ? "…" : ""), severity: Math.min(5, (i % 5) + 1), likelihood: Math.min(5, ((i * 2) % 5) + 1) };
  });
  if (items.length === 0 && result.answer) {
    items.push({ label: (result.answer || "").substring(0, 80) + "…", severity: 3, likelihood: 3 });
  }
  const severityLabels = ["1 낮음", "2", "3", "4", "5 높음"];
  const likelihoodLabels = ["1 낮음", "2", "3", "4", "5 높음"];
  let table = '<table class="risk-matrix-table"><thead><tr><th></th>';
  for (let l = 0; l < 5; l++) table += "<th>" + likelihoodLabels[l] + "</th>";
  table += "</tr></thead><tbody>";
  const cellMap = {};
  items.forEach(function (it) {
    const key = (it.severity - 1) * 5 + (it.likelihood - 1);
    if (!cellMap[key]) cellMap[key] = [];
    cellMap[key].push(it.label);
  });
  for (let s = 5; s >= 1; s--) {
    table += "<tr><th>" + severityLabels[s - 1] + "</th>";
    for (let l = 1; l <= 5; l++) {
      const key = (s - 1) * 5 + (l - 1);
      const labels = cellMap[key] || [];
      const riskClass = s >= 4 && l >= 4 ? "high" : s >= 3 && l >= 3 ? "medium" : "low";
      table += '<td class="risk-cell ' + riskClass + '">' + labels.map(function (lb) { return "<span class=\"risk-item\">" + escapeHtml(lb) + "</span>"; }).join("") + "</td>";
    }
    table += "</tr>";
  }
  table += "</tbody></table>";
  container.innerHTML = '<div class="risk-matrix-wrapper"><p class="risk-matrix-caption">심각도(행) × 가능성(열)</p>' + table + "</div>";
}

/**
 * 10-2-3: next_steps — Phase별 로드맵(카드)
 */
function renderNextStepsViz(result, container) {
  const steps = result.reasoning_steps || [];
  if (steps.length === 0 && result.answer) {
    const parts = (result.answer || "").split(/\n+/).filter(Boolean);
    parts.forEach(function (p) {
      if (p.trim()) steps.push(p.trim());
    });
  }
  if (steps.length === 0) {
    container.innerHTML = '<p class="viz-fallback">다음 단계 항목이 없습니다.</p>';
    return;
  }
  let html = '<div class="roadmap-timeline">';
  steps.forEach(function (step, i) {
    html +=
      '<div class="roadmap-item"><div class="roadmap-phase">' +
      (i + 1) +
      '</div><div class="roadmap-content">' +
      escapeHtml(step || "") +
      "</div></div>";
  });
  html += "</div>";
  container.innerHTML = html;
}

/**
 * 10-2-4: history_trace — 수직 타임라인
 */
function renderHistoryTraceViz(result, container) {
  const steps = result.reasoning_steps || [];
  const items = steps.length ? steps : (result.answer || "").split(/\n+/).filter(Boolean);
  if (items.length === 0) {
    container.innerHTML = '<p class="viz-fallback">타임라인 이벤트가 없습니다.</p>';
    return;
  }
  let html = '<div class="history-timeline">';
  items.forEach(function (item, i) {
    html +=
      '<div class="history-timeline-item"><div class="history-timeline-marker"></div><div class="history-timeline-content">' +
      escapeHtml(String(item).trim()) +
      "</div></div>";
  });
  html += "</div>";
  container.innerHTML = html;
}

/**
 * 추천 섹션 숨기기
 */
function hideRecommendationsSection() {
  const section = document.getElementById("recommendations-section");
  if (section) {
    section.style.display = "none";
  }
}

/**
 * 추천 정보 전체 표시
 */
function displayRecommendations(rec) {
  const section = document.getElementById("recommendations-section");
  if (!section) return;
  section.style.display = "block";

  displayRelatedChunks(rec.related_chunks || []);
  displaySuggestedLabels(rec.suggested_labels || []);
  displaySampleQuestions(rec.sample_questions || []);
  displayExploreMore(rec.explore_more || []);

  // 패널 토글 이벤트 (한 번만 바인딩)
  if (!section.dataset.bound) {
    section.dataset.bound = "1";
    section.querySelectorAll(".rec-toggle").forEach((btn) => {
      btn.addEventListener("click", function () {
        section.querySelectorAll(".rec-toggle").forEach((b) => b.classList.remove("active"));
        section.querySelectorAll(".rec-panel").forEach((p) => p.classList.remove("active"));
        this.classList.add("active");
        const panelId = this.getAttribute("data-panel") + "-panel";
        const panel = document.getElementById(panelId);
        if (panel) panel.classList.add("active");
      });
    });
  }
}

/**
 * 관련 청크 추천 카드 표시
 */
function displayRelatedChunks(chunks) {
  const el = document.getElementById("related-chunks");
  if (!el) return;

  if (!chunks.length) {
    el.innerHTML = '<p class="rec-empty">관련 청크 추천이 없습니다.</p>';
    return;
  }

  el.innerHTML = chunks
    .map((c) => `
      <div class="rec-card rec-card-chunk">
        <div class="rec-card-header">
          <span class="rec-card-title">${escapeHtml(c.title || "제목 없음")}</span>
          <span class="rec-card-meta">${escapeHtml(c.document_name || "")} · ${(c.similarity_score * 100).toFixed(0)}%</span>
        </div>
        <div class="rec-card-body">${escapeHtml((c.content_preview || "").substring(0, 150))}${(c.content_preview || "").length > 150 ? "…" : ""}</div>
        <a href="/knowledge-detail?chunk_id=${c.chunk_id}" class="rec-card-link" target="_blank">청크 보기 →</a>
      </div>
    `)
    .join("");
}

/**
 * 추천 라벨 태그 표시
 */
function displaySuggestedLabels(labels) {
  const el = document.getElementById("suggested-labels");
  if (!el) return;

  if (!labels.length) {
    el.innerHTML = '<p class="rec-empty">추천 라벨이 없습니다.</p>';
    return;
  }

  el.innerHTML = labels
    .map((l) => `<span class="label-tag" title="${escapeHtml(l.label_type || "")} · ${(l.confidence * 100).toFixed(0)}%">${escapeHtml(l.name || "")}</span>`)
    .join("");
}

/**
 * 샘플 질문 버튼 그룹 표시
 */
function displaySampleQuestions(questions) {
  const el = document.getElementById("sample-questions");
  if (!el) return;

  if (!questions.length) {
    el.innerHTML = '<p class="rec-empty">샘플 질문이 없습니다.</p>';
    return;
  }

  window.__lastSampleQuestions = questions;

  el.innerHTML = questions
    .map((q, i) => `
      <button type="button" class="sample-question-btn" data-index="${i}" data-mode="${escapeHtml(q.suggested_mode || "design_explain")}">
        ${escapeHtml((q.question || "").substring(0, 60))}${(q.question || "").length > 60 ? "…" : ""}
      </button>
    `)
    .join("");

  el.querySelectorAll(".sample-question-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const idx = parseInt(this.getAttribute("data-index"), 10);
      const item = window.__lastSampleQuestions && window.__lastSampleQuestions[idx];
      if (item) handleSampleQuestionClick(item);
    });
  });
}

/**
 * 샘플 질문 클릭 시 질문 필드에 넣고 모드 선택
 */
function handleSampleQuestionClick(item) {
  const questionEl = document.getElementById("question");
  const modeEl = document.getElementById("mode");
  if (questionEl) questionEl.value = item.question || "";
  if (modeEl && item.suggested_mode) modeEl.value = item.suggested_mode;
}

/**
 * 추가 탐색 제안 표시
 */
function displayExploreMore(items) {
  const el = document.getElementById("explore-more");
  if (!el) return;

  if (!items.length) {
    el.innerHTML = '<p class="rec-empty">추가 탐색 제안이 없습니다.</p>';
    return;
  }

  el.innerHTML = items
    .map((it) => {
      const typeLabel = it.type === "project" ? "프로젝트" : it.type === "label" ? "라벨" : "질문";
      const href = it.type === "project" ? "#" : it.type === "label" ? "/admin/labels" : "#";
      return `
        <div class="explore-item">
          <span class="explore-type">${escapeHtml(typeLabel)}</span>
          <span class="explore-name">${escapeHtml(it.name || "")}</span>
          <span class="explore-desc">${escapeHtml((it.description || "").substring(0, 50))}${(it.description || "").length > 50 ? "…" : ""}</span>
          ${href !== "#" ? `<a href="${href}" class="explore-link">보기 →</a>` : ""}
        </div>
      `;
    })
    .join("");
}
