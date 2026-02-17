/**
 * 라벨 관리 API 모듈
 * LabelManager 클래스에서 사용하는 API fetch 함수들
 * Traditional script 패턴 (전역 함수)
 */

/**
 * 라벨 목록 로드 (페이징)
 * @param {number} limit - 페이지 크기
 * @param {number} offset - 오프셋
 * @param {string} labelType - 라벨 타입 필터
 * @param {string} q - 이름 검색어
 * @returns {Promise<{items: Array, total: number}>}
 */
async function fetchLabelsPaged(limit, offset, labelType, q) {
  const params = new URLSearchParams({ limit, offset });
  if (labelType) params.set("label_type", labelType);
  if (q) params.set("q", q);
  const response = await fetch(`/api/labels?${params.toString()}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `서버 오류 (${response.status})`);
  }
  return response.json();
}

/**
 * 라벨 전체 목록 로드
 * @returns {Promise<Array>}
 */
async function fetchLabelsAll() {
  const response = await fetch("/api/labels");
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `서버 오류 (${response.status})`);
  }
  return response.json();
}

/**
 * 라벨 생성
 * @returns {Promise<Object>} 생성된 라벨
 */
async function createLabelApi(name, labelType, description) {
  const response = await fetch("/api/labels", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, label_type: labelType, description: description || null }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "라벨 생성 실패");
  }
  return response.json();
}

/**
 * 라벨 영향도 조회
 * @returns {Promise<Object>} 영향도 정보
 */
async function fetchLabelImpact(labelId) {
  const response = await fetch(`/api/labels/${labelId}/impact`);
  if (!response.ok) throw new Error("영향도 정보를 불러올 수 없습니다.");
  return response.json();
}

/**
 * 라벨 삭제
 */
async function deleteLabelApi(labelId) {
  const response = await fetch(`/api/labels/${labelId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("라벨 삭제 실패");
}

/**
 * 청크 목록 로드
 * @returns {Promise<Array>}
 */
async function fetchChunksApi(limit = 1000) {
  const response = await fetch(`/api/knowledge/chunks?limit=${limit}`);
  const data = await response.json();
  return Array.isArray(data) ? data : data.items || data.chunks || [];
}

/**
 * 청크의 라벨 목록 로드
 * @returns {Promise<Array>}
 */
async function fetchChunkLabelsApi(chunkId) {
  const response = await fetch(`/api/labels/chunks/${chunkId}/labels`);
  return response.json();
}

/**
 * 청크에 라벨 추가
 */
async function addChunkLabelApi(chunkId, labelId) {
  const response = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "POST" });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "라벨 추가 실패");
  }
}

/**
 * 청크에서 라벨 제거
 */
async function removeChunkLabelApi(chunkId, labelId) {
  const response = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "DELETE" });
  if (!response.ok) throw new Error("라벨 제거 실패");
}

/**
 * 청크에 라벨 일괄 추가 (성공/실패 수 반환)
 * @returns {Promise<{success: number, fail: number}>}
 */
async function batchAddLabelsToChunkApi(chunkId, labelIds) {
  let success = 0;
  let fail = 0;
  for (const labelId of labelIds) {
    try {
      const response = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "POST" });
      if (response.ok) success++;
      else fail++;
    } catch {
      fail++;
    }
  }
  return { success, fail };
}

/**
 * AI(LLM) 키워드·라벨 추천 요청
 * @returns {Promise<Object>} { suggestions, new_keywords, ollama_feedback, message }
 */
async function fetchAiSuggestionsApi(chunkId, limit = 10) {
  const response = await fetch(`/api/knowledge/labels/suggest-llm?chunk_id=${chunkId}&limit=${limit}`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "추천 요청 실패");
  return data;
}

/**
 * 새 키워드를 라벨로 생성 후 청크에 연결
 * @returns {Promise<number>} 생성된 라벨 ID
 */
async function createAndLinkKeywordLabel(chunkId, keyword) {
  const createRes = await fetch("/api/labels", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: keyword, label_type: "keyword", description: "" }),
  });
  const createData = await createRes.json();
  if (!createRes.ok) throw new Error(createData.detail || "라벨 생성 실패");
  const labelId = createData.id;
  const linkRes = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "POST" });
  if (!linkRes.ok) {
    const err = await linkRes.json().catch(() => ({}));
    throw new Error(err.detail || "청크에 라벨 연결 실패");
  }
  return labelId;
}

/**
 * 라벨 제안 적용 (knowledge-admin.js 전용)
 * @returns {Promise<Object>}
 */
async function applyLabelSuggestionApi(chunkId, labelId, confidence) {
  const response = await fetch(`/api/knowledge/labels/suggest/${chunkId}/apply/${labelId}?confidence=${confidence}`, {
    method: "POST",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "라벨 적용 실패");
  }
  return response.json();
}

/**
 * AI 추천 라벨 1건 청크에 추가 (직접 라벨 연결)
 */
async function applyAiSuggestionLabelApi(chunkId, labelId) {
  const res = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "라벨 추가 실패");
  }
}

/**
 * AI 추천 라벨 목록 렌더 (배지 + 추가 버튼) + 새 키워드 (라벨로 등록 버튼)
 * @param {Array} suggestions - 추천 라벨 목록
 * @param {Array} newKeywords - 새 키워드 목록
 * @param {string} containerId - 추천 라벨 컨테이너 ID
 * @param {string} newKwContainerId - 새 키워드 컨테이너 ID
 * @param {function} onApply - 라벨 적용 콜백 (labelId, confidence)
 * @param {function} onNewKeyword - 새 키워드 적용 콜백 (keyword)
 */
function renderAiSuggestionsUI(suggestions, newKeywords, containerId, newKwContainerId, onApply, onNewKeyword) {
  const list = Array.isArray(suggestions) ? suggestions : [];
  const container = containerId ? document.getElementById(containerId) : null;
  if (container) {
    if (list.length === 0) {
      container.innerHTML = "";
    } else {
      container.innerHTML = list
        .map((s) => {
          const typeClass = (s.label_type || "default").replace(/\s+/g, "_");
          const conf = s.confidence != null ? Math.round(s.confidence * 100) : "";
          return `
            <span class="ai-suggestion-item label-badge ${typeClass}">
              ${escapeHtml(s.name)}
              ${conf ? `<span class="ai-suggestion-conf">${conf}%</span>` : ""}
              <button type="button" class="btn btn-small ai-suggestion-apply" data-label-id="${s.label_id}" data-conf="${s.confidence != null ? s.confidence : 0.8}">추가</button>
            </span>
          `;
        })
        .join("");
      container.querySelectorAll(".ai-suggestion-apply").forEach((btn) => {
        btn.addEventListener("click", () => {
          const labelId = parseInt(btn.getAttribute("data-label-id"), 10);
          const conf = parseFloat(btn.getAttribute("data-conf")) || 0.8;
          if (!isNaN(labelId) && onApply) onApply(labelId, conf);
        });
      });
    }
  }
  const newKwList = Array.isArray(newKeywords) ? newKeywords : [];
  const newKwContainer = newKwContainerId ? document.getElementById(newKwContainerId) : null;
  if (newKwContainer) {
    if (newKwList.length === 0) {
      newKwContainer.innerHTML = "";
    } else {
      newKwContainer.innerHTML = newKwList
        .map((kw, i) => `<span class="ai-new-keyword-item">${escapeHtml(kw)}<button type="button" class="btn btn-small ai-new-keyword-apply" data-keyword-index="${i}">라벨로 등록</button></span>`)
        .join("");
      newKwContainer.querySelectorAll(".ai-new-keyword-apply").forEach((btn) => {
        btn.addEventListener("click", () => {
          const idx = parseInt(btn.getAttribute("data-keyword-index"), 10);
          const keyword = !isNaN(idx) && newKwList[idx] !== undefined ? newKwList[idx] : null;
          if (keyword && onNewKeyword) onNewKeyword(keyword);
        });
      });
    }
  }
}

/**
 * 라벨 목록 페이징 UI 렌더
 * @param {Object} opts - { page, limit, total, controlsId, infoId, buttonsId, perPageId, onPageChange, onLimitChange }
 */
function renderLabelsPaginationUI(opts) {
  const controls = document.getElementById(opts.controlsId);
  const info = document.getElementById(opts.infoId);
  const buttons = document.getElementById(opts.buttonsId);
  const perPageSelect = opts.perPageId ? document.getElementById(opts.perPageId) : null;
  if (!controls || !info || !buttons) return;

  const total = opts.total;
  const limit = opts.limit;
  const page = opts.page;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  if (total === 0) {
    controls.style.display = "none";
    return;
  }
  controls.style.display = "block";

  const start = (page - 1) * limit + 1;
  const end = Math.min(page * limit, total);
  info.textContent = `총 ${total.toLocaleString()}개 중 ${start.toLocaleString()}-${end.toLocaleString()}개 표시`;

  if (perPageSelect) {
    perPageSelect.value = limit;
    perPageSelect.onchange = () => {
      if (opts.onLimitChange) opts.onLimitChange(parseInt(perPageSelect.value, 10));
    };
  }

  buttons.innerHTML = "";
  const prev = document.createElement("button");
  prev.type = "button";
  prev.textContent = "◀ 이전";
  prev.disabled = page <= 1;
  prev.className = "btn btn-small";
  prev.style = "padding: 4px 10px; font-size: 12px;";
  prev.onclick = () => { if (opts.onPageChange && page > 1) opts.onPageChange(page - 1); };
  buttons.appendChild(prev);

  const maxButtons = 7;
  let startPage = Math.max(1, page - Math.floor(maxButtons / 2));
  let endPage = Math.min(totalPages, startPage + maxButtons - 1);
  if (endPage - startPage + 1 < maxButtons) startPage = Math.max(1, endPage - maxButtons + 1);

  for (let i = startPage; i <= endPage; i++) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = i;
    btn.className = "btn btn-small " + (i === page ? "btn-primary" : "");
    btn.style = "padding: 4px 10px; font-size: 12px; min-width: 32px;";
    btn.onclick = () => { if (opts.onPageChange) opts.onPageChange(i); };
    buttons.appendChild(btn);
  }

  const next = document.createElement("button");
  next.type = "button";
  next.textContent = "다음 ▶";
  next.disabled = page >= totalPages;
  next.className = "btn btn-small";
  next.style = "padding: 4px 10px; font-size: 12px;";
  next.onclick = () => { if (opts.onPageChange && page < totalPages) opts.onPageChange(page + 1); };
  buttons.appendChild(next);
}
