/**
 * 청크 승인 관리 모듈
 * 청크 승인/거절, 상태 필터링, 상세 보기 기능을 제공하는 클래스
 * API 호출은 chunk-approval-api.js 전역 함수 사용
 */
class ChunkApprovalManager {
  constructor(config = {}) {
    this.onChunkChange = config.onChunkChange || (() => {});
    this.currentStatusFilter = "draft";
    this.pendingChunks = [];
    this.pagination = null;
    if (config.enablePagination) {
      this.pagination = new PaginationComponent({
        initialPage: 1, initialLimit: config.limit || 20,
        onPageChange: () => this.loadPendingChunks(),
        onLimitChange: () => this.loadPendingChunks(),
      });
    }
    this.chunkListId = config.chunkListId || "approval-chunk-list";
    this.detailBodyId = config.detailBodyId || "approval-detail-body";
    this.detailPlaceholderId = config.detailPlaceholderId || "approval-detail-placeholder";
    this.detailContentId = config.detailContentId || "approval-detail-content";
    this.selectedChunkId = null;
    this.lastNewKeywords = [];
    this.lastAiSuggestions = [];
  }

  async filterByStatus(status) {
    this.currentStatusFilter = status;
    if (this.pagination) this.pagination.currentPage = 1;
    document.querySelectorAll(".status-filter-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.status === status);
    });
    await this.loadPendingChunks();
  }

  async loadPendingChunks() {
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;
    chunkList.innerHTML = '<div class="loading">청크 목록을 불러오는 중...</div>';
    try {
      const limit = this.pagination ? this.pagination.getState().limit : null;
      const offset = this.pagination ? this.pagination.getState().offset : 0;
      const data = await fetchPendingChunksApi(this.currentStatusFilter, limit, offset);
      this.pendingChunks = data.items || data;
      if (this.pagination) { this.pagination.updateState(data); this.pagination.updateUI(); }
      this.displayPendingChunks();
      if (this.selectedChunkId) this.showChunkDetail(this.selectedChunkId);
      else this.clearChunkDetail();
      this.onChunkChange();
    } catch (error) {
      console.error("승인 대기 청크 로드 실패:", error);
      chunkList.innerHTML = '<div class="error">청크 목록을 불러올 수 없습니다.</div>';
      if (this.pagination) this.pagination.hide();
    }
  }

  displayPendingChunks() {
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;
    if (this.pendingChunks.length === 0) {
      chunkList.innerHTML = '<div class="loading">해당 상태의 청크가 없습니다.</div>';
      if (this.pagination) this.pagination.hide();
      return;
    }
    const selectedId = this.selectedChunkId;
    chunkList.innerHTML = this.pendingChunks.map((chunk) => {
      const statusClass = chunk.status || "draft";
      const statusText = { draft: "📝 대기 중", approved: "✅ 승인됨", rejected: "❌ 거절됨" }[statusClass] || "📝 대기 중";
      const selectedClass = chunk.id === selectedId ? " selected" : "";
      return `
        <div class="approval-chunk-card ${statusClass}${selectedClass}" data-chunk-id="${chunk.id}" onclick="window.approvalManager.showChunkDetail(${chunk.id})">
          <div class="chunk-card-header">
            <div>
              <div class="chunk-card-meta">청크 ID: ${chunk.id} | 문서 ID: ${chunk.document_id} | 인덱스: ${chunk.chunk_index}</div>
              <div class="chunk-card-content">${escapeHtml(chunk.content)}</div>
            </div>
            <span class="chunk-card-status ${statusClass}">${statusText}</span>
          </div>
          <div class="chunk-card-actions">
            ${statusClass === "draft" ? `
              <button class="btn btn-success btn-small" onclick="event.stopPropagation(); window.approvalManager.approveChunk(${chunk.id})">✅ 승인</button>
              <button class="btn btn-danger btn-small" onclick="event.stopPropagation(); window.approvalManager.rejectChunk(${chunk.id})">❌ 거절</button>
            ` : ""}
            <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); window.approvalManager.showChunkDetail(${chunk.id})">상세 보기</button>
          </div>
        </div>
      `;
    }).join("");
  }

  async approveChunk(chunkId) {
    if (!confirm("이 청크를 승인하시겠습니까?")) return;
    try {
      await approveChunkApi(chunkId);
      showSuccess("청크가 승인되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("청크 승인 실패:", error);
      showError(error.message || "청크 승인 중 오류가 발생했습니다.");
    }
  }

  async batchApproveAll() {
    const draftIds = this.pendingChunks.filter((c) => (c.status || "") === "draft").map((c) => c.id);
    if (draftIds.length === 0) { if (typeof showError === "function") showError("승인할 대기 중 청크가 없습니다."); return; }
    if (!confirm("현재 목록의 대기 중 청크 " + draftIds.length + "개를 모두 승인하시겠습니까?")) return;
    try {
      const data = await batchApproveChunksApi(draftIds);
      if (typeof showSuccess === "function") showSuccess(data.message || draftIds.length + "개 청크가 승인되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("전체 승인 실패:", error);
      if (typeof showError === "function") showError(error.message || "전체 승인 중 오류가 발생했습니다.");
    }
  }

  async rejectChunk(chunkId) {
    const reason = prompt("거절 사유를 입력하세요 (선택사항):");
    if (reason === null) return;
    try {
      await rejectChunkApi(chunkId, reason);
      showSuccess("청크가 거절되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("청크 거절 실패:", error);
      showError(error.message || "청크 거절 중 오류가 발생했습니다.");
    }
  }

  async showChunkDetail(chunkId) {
    const placeholder = document.getElementById(this.detailPlaceholderId);
    const contentEl = document.getElementById(this.detailContentId);
    const body = document.getElementById(this.detailBodyId);
    if (!contentEl || !body) return;

    this.selectedChunkId = chunkId;
    if (placeholder) placeholder.style.display = "none";
    contentEl.style.display = "block";
    contentEl.innerHTML = '<div class="loading">청크 정보를 불러오는 중...</div>';
    this.updateSelectedCard();

    try {
      const chunk = await fetchChunkDetailApi(chunkId);
      const relationSuggestions = await fetchRelationSuggestionsApi(chunkId);

      contentEl.innerHTML = `
        <div class="chunk-detail-section">
          <h4>청크 내용</h4>
          <div class="chunk-content-body">${escapeHtml(chunk.content || "내용 없음")}</div>
          <div class="chunk-content-ai-row approval-ai-row">
            <button type="button" class="btn btn-primary btn-small" id="approval-ai-btn" onclick="window.approvalManager.fetchAiLabelSuggestions()">AI 키워드·라벨 추천</button>
            <span id="approval-ai-status" class="ai-suggest-status"></span>
          </div>
          <div id="approval-ai-suggestions" class="ai-label-suggestions" style="display: none"></div>
          <div id="approval-ai-new-keywords-wrap" class="ai-new-keywords-wrap" style="display: none">
            <h5 class="ai-new-keywords-title">새 키워드 (라벨로 등록 가능)</h5>
            <div id="approval-ai-new-keywords" class="ai-new-keywords"></div>
          </div>
        </div>
        <div class="chunk-detail-section">
          <h4>현재 라벨</h4>
          <div class="current-labels">
            ${chunk.labels && chunk.labels.length > 0
              ? chunk.labels.map((label) => `<span class="label-badge ${(label.label_type || "default").replace(/\s+/g, "_")}">${escapeHtml(label.name)}</span>`).join("")
              : '<p style="color: #9ca3af; font-size: 13px;">라벨이 없습니다.</p>'}
          </div>
        </div>
        ${relationSuggestions.length > 0 ? `
        <div class="chunk-detail-section">
          <h4>🔗 AI 유사 청크 추천</h4>
          <div class="suggestion-block">
            ${relationSuggestions.map((s) => `
              <div class="similar-chunk-item" onclick="window.approvalManager.showChunkDetail(${s.target_chunk_id})">
                <div style="font-weight: 600; margin-bottom: 5px;">청크 ID: ${s.target_chunk_id}</div>
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">${escapeHtml(s.target_content_preview)}</div>
                <div style="font-size: 11px; color: #999;">유사도: ${(s.score * 100).toFixed(0)}%</div>
              </div>
            `).join("")}
          </div>
        </div>` : ""}
        <div class="chunk-detail-section">
          <h4>작업</h4>
          <div class="chunk-detail-actions">
            ${chunk.status === "draft" ? `
              <button class="btn btn-success" onclick="window.approvalManager.approveChunk(${chunkId})">✅ 승인</button>
              <button class="btn btn-danger" onclick="window.approvalManager.rejectChunk(${chunkId})">❌ 거절</button>
            ` : ""}
            <button class="btn btn-small" style="background: #e5e7eb; color: #333" onclick="window.approvalManager.clearChunkDetail()">선택 해제</button>
          </div>
        </div>
      `;
    } catch (error) {
      console.error("청크 상세 로드 실패:", error);
      let errorMessage = "청크 정보를 불러올 수 없습니다.";
      if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) { errorMessage = error.message; }
      contentEl.innerHTML = `<div class="error">${escapeHtml(errorMessage)}</div>`;
    }
  }

  async fetchAiLabelSuggestions() {
    if (!this.selectedChunkId) { showError("먼저 청크를 선택하세요."); return; }
    const btnEl = document.getElementById("approval-ai-btn");
    const statusEl = document.getElementById("approval-ai-status");
    const suggestionsEl = document.getElementById("approval-ai-suggestions");
    const newWrapEl = document.getElementById("approval-ai-new-keywords-wrap");
    if (suggestionsEl) suggestionsEl.style.display = "none";
    if (newWrapEl) newWrapEl.style.display = "none";
    if (statusEl) statusEl.textContent = "LLM 추천 중...";
    if (btnEl) btnEl.disabled = true;
    try {
      const data = await fetchApprovalAiSuggestionsApi(this.selectedChunkId);
      this.lastAiSuggestions = data.suggestions || [];
      this.lastNewKeywords = data.new_keywords || [];
      this.renderAiSuggestionsIntoApproval(this.lastAiSuggestions, this.lastNewKeywords);
      if (suggestionsEl) suggestionsEl.style.display = this.lastAiSuggestions.length ? "block" : "none";
      if (newWrapEl) newWrapEl.style.display = this.lastNewKeywords.length ? "block" : "none";
      const hasAny = this.lastAiSuggestions.length || this.lastNewKeywords.length;
      if (statusEl) {
        if (hasAny) statusEl.textContent = "";
        else statusEl.textContent = data.message || (data.ollama_feedback && !data.ollama_feedback.available && data.ollama_feedback.message) || "추천 결과가 없습니다.";
      }
    } catch (e) {
      console.error("AI 라벨 추천 실패:", e);
      showError(e.message || "AI 추천을 불러오지 못했습니다.");
      if (statusEl) statusEl.textContent = "";
    } finally {
      if (btnEl) btnEl.disabled = false;
    }
  }

  renderAiSuggestionsIntoApproval(suggestions, newKeywords) {
    const suggestionsEl = document.getElementById("approval-ai-suggestions");
    const newKwEl = document.getElementById("approval-ai-new-keywords");
    const list = Array.isArray(suggestions) ? suggestions : [];
    const newKwList = Array.isArray(newKeywords) ? newKeywords : [];
    if (suggestionsEl) {
      if (list.length === 0) { suggestionsEl.innerHTML = ""; } else {
        suggestionsEl.innerHTML = list.map((s) => {
          const typeClass = (s.label_type || "default").replace(/\s+/g, "_");
          const conf = s.confidence != null ? Math.round(s.confidence * 100) : "";
          return `<span class="ai-suggestion-item label-badge ${typeClass}">${escapeHtml(s.name || s.label_name || "")}${conf ? `<span class="ai-suggestion-conf">${conf}%</span>` : ""}<button type="button" class="btn btn-small ai-suggestion-apply" data-label-id="${s.label_id}" data-conf="${s.confidence != null ? s.confidence : 0.8}">추가</button></span>`;
        }).join("");
        suggestionsEl.querySelectorAll(".ai-suggestion-apply").forEach((btn) => {
          btn.addEventListener("click", () => {
            const labelId = parseInt(btn.getAttribute("data-label-id"), 10);
            const conf = parseFloat(btn.getAttribute("data-conf")) || 0.8;
            if (!isNaN(labelId)) this.applyLabelSuggestion(this.selectedChunkId, labelId, conf);
          });
        });
      }
    }
    if (newKwEl) {
      if (newKwList.length === 0) { newKwEl.innerHTML = ""; } else {
        newKwEl.innerHTML = newKwList.map((kw, i) => `<span class="ai-new-keyword-item">${escapeHtml(kw)}<button type="button" class="btn btn-small ai-new-keyword-apply" data-idx="${i}">라벨로 등록</button></span>`).join("");
        newKwEl.querySelectorAll(".ai-new-keyword-apply").forEach((btn) => {
          btn.addEventListener("click", () => {
            const idx = parseInt(btn.getAttribute("data-idx"), 10);
            const keyword = !isNaN(idx) && newKwList[idx] !== undefined ? newKwList[idx] : null;
            if (keyword) this.applyNewKeywordAsLabel(keyword);
          });
        });
      }
    }
  }

  updateSelectedCard() {
    const list = document.getElementById(this.chunkListId);
    if (!list) return;
    list.querySelectorAll(".approval-chunk-card").forEach((card) => {
      const id = parseInt(card.getAttribute("data-chunk-id"), 10);
      card.classList.toggle("selected", id === this.selectedChunkId);
    });
  }

  clearChunkDetail() {
    this.selectedChunkId = null;
    const placeholder = document.getElementById(this.detailPlaceholderId);
    const contentEl = document.getElementById(this.detailContentId);
    if (placeholder) placeholder.style.display = "block";
    if (contentEl) { contentEl.style.display = "none"; contentEl.innerHTML = ""; }
    this.updateSelectedCard();
  }

  closeChunkDetail() { this.clearChunkDetail(); }

  async applyLabelSuggestion(chunkId, labelId, confidence) {
    if (window.labelsTabManager && typeof window.labelsTabManager.applyLabelSuggestion === "function") {
      const success = await window.labelsTabManager.applyLabelSuggestion(chunkId, labelId, confidence);
      if (success) this.showChunkDetail(chunkId);
    } else {
      try {
        await applyApprovalLabelSuggestionApi(chunkId, labelId, confidence);
        showSuccess("라벨이 적용되었습니다.");
        this.showChunkDetail(chunkId);
      } catch (error) {
        console.error("라벨 적용 실패:", error);
        showError(error.message || "라벨 적용 중 오류가 발생했습니다.");
      }
    }
  }

  applyNewKeywordAsLabelByIndex(index) {
    const kw = Array.isArray(this.lastNewKeywords) && this.lastNewKeywords[index] !== undefined ? this.lastNewKeywords[index] : null;
    if (kw) this.applyNewKeywordAsLabel(kw);
  }

  async applyNewKeywordAsLabel(keyword) {
    if (!this.selectedChunkId || !keyword || !String(keyword).trim()) return;
    const kw = String(keyword).trim();
    try {
      await createApprovalKeywordLabelApi(this.selectedChunkId, kw);
      showSuccess('키워드 "' + kw + '"를 라벨로 등록하고 청크에 추가했습니다.');
      this.showChunkDetail(this.selectedChunkId);
    } catch (e) {
      console.error("새 키워드 라벨 등록 실패:", e);
      showError(e.message || "라벨 등록에 실패했습니다.");
    }
  }
}
