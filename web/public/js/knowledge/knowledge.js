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
 * Knowledge Studio 메인 모듈
 * 지식 청크 탐색 및 관리 기능을 제공
 */

// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🧠 Knowledge Studio",
      subtitle: "지식 구조 탐색 및 관리",
      currentPath: "/knowledge",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

let selectedLabelId = null;
let selectedDocumentId = null;

// 페이징 컴포넌트
let pagination;

// URL 파라미터 확인
const urlParams = new URLSearchParams(window.location.search);
const documentIdParam = urlParams.get("document_id");
if (documentIdParam) {
  selectedDocumentId = parseInt(documentIdParam);
}
const pageParam = urlParams.get("page");
const limitParam = urlParams.get("limit");

// 페이징 컴포넌트 초기화
pagination = new PaginationComponent({
  initialPage: pageParam ? parseInt(pageParam) : 1,
  initialLimit: limitParam ? parseInt(limitParam) : 20,
  onPageChange: () => {
    updateURL();
    loadChunks();
  },
  onLimitChange: () => {
    updateURL();
    loadChunks();
  }
});

/**
 * 라벨 목록 로드
 * API에서 라벨 목록을 가져와서 표시
 */
async function loadLabels() {
  try {
    const response = await fetch("/api/labels");
    const labels = await response.json();

    const labelList = document.getElementById("label-list");
    const allItem = labelList.querySelector('[data-label-id=""]');
    labelList.innerHTML = "";

    // 전체 항목에 onclick 이벤트 추가
    if (allItem) {
      allItem.onclick = () => selectLabel(null);
      labelList.appendChild(allItem);
    } else {
      // 전체 항목이 없으면 새로 생성
      const newAllItem = document.createElement("li");
      newAllItem.className = "label-item active";
      newAllItem.setAttribute("data-label-id", "");
      newAllItem.onclick = () => selectLabel(null);
      newAllItem.innerHTML = '<div class="label-name">전체</div>';
      labelList.appendChild(newAllItem);
    }

    labels.forEach((label) => {
      const li = document.createElement("li");
      li.className = "label-item";
      li.setAttribute("data-label-id", label.id);
      li.onclick = () => selectLabel(label.id);
      li.innerHTML = `
        <div class="label-name">${escapeHtml(label.name)}</div>
        <div class="label-type">${escapeHtml(label.label_type)}</div>
      `;
      labelList.appendChild(li);
    });
  } catch (error) {
    console.error("라벨 로드 실패:", error);
  }
}

/**
 * 라벨 선택
 * 선택된 라벨에 따라 청크 목록을 필터링
 * @param {number|null} labelId - 라벨 ID (null이면 전체 선택)
 */
function selectLabel(labelId) {
  // null, undefined, 빈 문자열 모두 전체 선택으로 처리
  selectedLabelId = labelId || null;

  // UI 업데이트
  document.querySelectorAll(".label-item").forEach((item) => {
    item.classList.remove("active");
  });

  // 전체 선택인 경우 빈 문자열로 찾기
  const targetId = selectedLabelId || "";
  const targetItem = document.querySelector(`[data-label-id="${targetId}"]`);
  if (targetItem) {
    targetItem.classList.add("active");
  }

  // 청크 목록 로드 (페이지 1로 리셋)
  pagination.currentPage = 1;
  loadChunks();
}

/**
 * 청크 API URL 구성
 * @returns {string} API URL
 */
function buildChunksUrl() {
  const state = pagination.getState();
  const offset = state.offset;

  let url = "/api/knowledge/chunks?";
  const params = [];
  if (selectedLabelId) {
    params.push(`label_id=${selectedLabelId}`);
  }
  if (selectedDocumentId) {
    params.push(`document_id=${selectedDocumentId}`);
  }
  params.push(`limit=${state.limit}`);
  params.push(`offset=${offset}`);
  url += params.join("&");

  return url;
}

/**
 * 청크 데이터 가져오기
 * @returns {Promise<Object>} 청크 데이터
 */
async function fetchChunks() {
  const url = buildChunksUrl();
  const response = await fetch(url);

  // HTTP 오류 처리
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
    throw new Error(errorData.detail || `서버 오류 (${response.status})`);
  }

  const data = await response.json();
  return data;
}

/**
 * 빈 상태 표시
 */
function renderEmptyState() {
  const chunkList = document.getElementById("chunk-list");
  chunkList.innerHTML = `
    <div class="empty-state">
      <h3>📭 청크가 없습니다</h3>
      <p>선택한 조건에 해당하는 지식 청크가 없습니다.</p>
      <p style="margin-top: 10px; font-size: 12px; color: #999;">
        ${selectedLabelId ? "다른 라벨을 선택하거나 " : ""}전체 보기를 선택해보세요.
      </p>
    </div>
  `;
  pagination.hide();
}

/**
 * 청크 카드 HTML 생성
 * @param {Object} chunk - 청크 객체
 * @returns {string} 청크 카드 HTML
 */
function renderChunkCard(chunk) {
  return `
    <div class="chunk-card" data-chunk-id="${chunk.id}">
      <div class="chunk-header">
        <div>
          <div class="chunk-meta">
            ${chunk.project_name ? `<strong>${escapeHtml(chunk.project_name)}</strong> / ` : ""}
            ${escapeHtml(chunk.document_name || "알 수 없음")} (청크 #${chunk.chunk_index})
          </div>
          <div class="chunk-title ${!chunk.title ? "no-title" : ""}">
            ${escapeHtml(chunk.title || "제목 없음")}
            ${
              chunk.title && chunk.title_source
                ? `<div class="chunk-title-source">출처: ${
                    chunk.title_source === "heading"
                      ? "헤딩"
                      : chunk.title_source === "ai_extracted"
                      ? "AI 추출"
                      : chunk.title_source === "manual"
                      ? "수동 입력"
                      : escapeHtml(chunk.title_source)
                  }</div>`
                : ""
            }
          </div>
          <div class="chunk-content">${escapeHtml(chunk.content.substring(0, 200))}${chunk.content.length > 200 ? "..." : ""}</div>
        </div>
      </div>
      <div class="chunk-footer">
        <div class="chunk-labels">
          ${
            chunk.labels && chunk.labels.length > 0
              ? chunk.labels.map((label) => `<span class="label-badge">${escapeHtml(label.name)}</span>`).join("")
              : '<span style="color: #999; font-size: 12px;">라벨 없음</span>'
          }
        </div>
        <div>
          관계: ${chunk.outgoing_relations_count || 0}개 출발 / ${chunk.incoming_relations_count || 0}개 도착
        </div>
      </div>
    </div>
  `;
}

/**
 * 청크 목록 렌더링
 * @param {Array} chunks - 청크 배열
 */
function renderChunkList(chunks) {
  const chunkList = document.getElementById("chunk-list");
  chunkList.innerHTML = chunks.map((chunk) => renderChunkCard(chunk)).join("");
}

/**
 * 청크 카드 이벤트 리스너 설정
 */
function setupChunkEventListeners() {
  const chunkList = document.getElementById("chunk-list");
  chunkList.querySelectorAll(".chunk-card").forEach((card) => {
    card.addEventListener("click", function () {
      const chunkId = parseInt(this.getAttribute("data-chunk-id"));
      if (chunkId) {
        window.location.href = `/knowledge-detail?id=${chunkId}`;
      }
    });
  });
}

/**
 * 에러 상태 표시
 * @param {Error} error - 에러 객체
 */
function renderErrorState(error) {
  const chunkList = document.getElementById("chunk-list");

  // 네트워크 오류와 API 오류 구분
  let errorMessage = "청크를 불러올 수 없습니다.";
  if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
    errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
  } else if (error.message) {
    errorMessage = error.message;
  }

  chunkList.innerHTML = `
    <div class="empty-state" style="color: #dc2626;">
      <h3>❌ 오류 발생</h3>
      <p>${escapeHtml(errorMessage)}</p>
      <button onclick="loadChunks()" style="margin-top: 15px; padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer;">
        다시 시도
      </button>
    </div>
  `;
  pagination.hide();
}

/**
 * 청크 목록 로드 (메인 함수)
 */
async function loadChunks() {
  showLoading("chunk-list", "⏳ 청크 목록을 불러오는 중...");

  try {
    // 청크 데이터 가져오기
    const data = await fetchChunks();

    // 새로운 API 응답 형식 확인 (items 속성 존재 여부)
    const chunks = data.items || data; // 하위 호환성 유지

    // 페이징 상태 업데이트
    pagination.updateState(data);

    // 빈 데이터 처리
    if (!chunks || chunks.length === 0) {
      renderEmptyState();
      return;
    }

    // 청크 목록 렌더링
    renderChunkList(chunks);

    // 청크 카드 이벤트 리스너 설정
    setupChunkEventListeners();

    // 페이징 UI 업데이트
    pagination.updateUI();
  } catch (error) {
    console.error("청크 로드 실패:", error);
    renderErrorState(error);
  }
}

/**
 * URL 업데이트 (페이지 상태 유지)
 * 현재 페이징 상태를 URL에 반영하여 북마크 및 새로고침 시 상태 유지
 */
function updateURL() {
  const state = pagination.getState();
  const url = new URL(window.location);
  url.searchParams.set("page", state.currentPage.toString());
  url.searchParams.set("limit", state.limit.toString());
  if (selectedDocumentId) {
    url.searchParams.set("document_id", selectedDocumentId.toString());
  }
  window.history.pushState({}, "", url);
}

/**
 * Reasoning 시작
 * 선택된 청크를 시드로 사용하여 Reasoning Lab으로 이동
 * @param {number} chunkId - 청크 ID
 */
function startReasoning(chunkId) {
  window.location.href = `/reason?seed_chunk=${chunkId}`;
}

// 초기화
loadLabels();
loadChunks();
