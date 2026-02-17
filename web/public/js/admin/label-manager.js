/**
 * 라벨 관리 모듈
 * 라벨 CRUD, 청크-라벨 연결 관리 기능을 제공하는 클래스
 * API 호출은 label-manager-api.js 전역 함수 사용
 */
class LabelManager {
  constructor(config = {}) {
    this.onLabelChange = config.onLabelChange || (() => {});
    this.onChunkChange = config.onChunkChange || (() => {});
    this.allLabels = [];
    this.allChunks = [];
    this.selectedChunkId = null;
    this.currentSearchTerm = "";
    this.filteredChunks = [];
    this.searchPagination = null;
    if (config.enablePagination) {
      this.searchPagination = new PaginationComponent({
        initialPage: 1, initialLimit: 20, prefix: "청크",
        hideWhenEmpty: config.chunkPaginationHideWhenEmpty !== false,
        onPageChange: () => this.searchChunks(),
        onLimitChange: () => this.searchChunks(),
      });
    }
    this.labelsTableId = config.labelsTableId || "labels-table";
    this.labelNameInputId = config.labelNameInputId || "label-name";
    this.labelTypeInputId = config.labelTypeInputId || "label-type";
    this.labelDescriptionInputId = config.labelDescriptionInputId || "label-description";
    this.labelFormId = config.labelFormId || "label-form";
    this.addLabelSelectId = config.addLabelSelectId || "add-label-select";
    this.chunkListId = config.chunkListId || "chunk-list";
    this.chunkSearchInputId = config.chunkSearchInputId || "chunk-search";
    this.currentChunkInfoId = config.currentChunkInfoId || "current-chunk-info";
    this.currentLabelsId = config.currentLabelsId || "current-labels";
    this.chunkLabelsSectionId = config.chunkLabelsSectionId || "chunk-labels-section";
    this.chunkContentId = config.chunkContentId || null;
    this.labelPickerListId = config.labelPickerListId || null;
    this.selectedLabelIdsForAdd = new Set();
    this.currentChunkLabelIds = [];
    this.labelPickerFilterType = "";
    this.aiSuggestionsContainerId = config.aiSuggestionsContainerId || null;
    this.aiSuggestStatusId = config.aiSuggestStatusId || null;
    this.aiSuggestBtnId = config.aiSuggestBtnId || null;
    this.aiNewKeywordsContainerId = config.aiNewKeywordsContainerId || "ai-new-keywords";
    this.aiNewKeywordsWrapId = config.aiNewKeywordsWrapId || "ai-new-keywords-wrap";
    this.lastAiSuggestions = [];
    this.lastAiNewKeywords = [];
    this.enableLabelsPagination = config.enableLabelsPagination === true;
    this.labelsPage = 1;
    this.labelsLimit = config.labelsInitialLimit || 20;
    this.totalLabels = 0;
    this.labelOptions = [];
    this.labelsPaginationControlsId = config.labelsPaginationControlsId || "labels-pagination-controls";
    this.labelsPaginationInfoId = config.labelsPaginationInfoId || "labels-pagination-info";
    this.labelsItemsPerPageId = config.labelsItemsPerPageId || "labels-items-per-page";
    this.labelsPaginationButtonsId = config.labelsPaginationButtonsId || "labels-pagination-buttons";
    this.labelsFilterTypeId = config.labelsFilterTypeId || "labels-filter-type";
    this.labelsFilterNameId = config.labelsFilterNameId || "labels-filter-name";
    this.labelsFilterApplyId = config.labelsFilterApplyId || "labels-filter-apply";
  }

  getLabelsFilterParams() {
    const typeEl = document.getElementById(this.labelsFilterTypeId);
    const nameEl = document.getElementById(this.labelsFilterNameId);
    return { labelType: typeEl ? typeEl.value : "", q: nameEl ? nameEl.value.trim() : "" };
  }

  async loadLabels(pageOrReset) {
    try {
      const page = typeof pageOrReset === "number" ? pageOrReset : this.labelsPage;
      if (this.enableLabelsPagination) {
        const offset = (page - 1) * this.labelsLimit;
        const { labelType, q } = this.getLabelsFilterParams();
        const data = await fetchLabelsPaged(this.labelsLimit, offset, labelType, q);
        this.allLabels = data.items || [];
        this.totalLabels = data.total != null ? data.total : 0;
        this.labelsPage = page;
        this.displayLabels();
        this.updateLabelsPaginationUI();
      } else {
        this.allLabels = await fetchLabelsAll();
        this.totalLabels = Array.isArray(this.allLabels) ? this.allLabels.length : 0;
        this.displayLabels();
        this.updateLabelSelect();
      }
      this.onLabelChange();
    } catch (error) {
      console.error("라벨 로드 실패:", error);
      let msg = "라벨 목록을 불러올 수 없습니다.";
      if (error.message && (error.message.includes("Failed to fetch") || error.message.includes("NetworkError"))) {
        msg = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) { msg = error.message; }
      if (typeof showError === "function") showError(msg);
    }
  }

  async loadLabelOptions() {
    try {
      const data = await fetchLabelsAll();
      this.labelOptions = Array.isArray(data) ? data : (data.items || []);
      this.updateLabelSelect();
    } catch (e) {
      console.warn("라벨 옵션 로드 실패:", e);
      this.labelOptions = [];
    }
  }

  updateLabelsPaginationUI() {
    renderLabelsPaginationUI({
      page: this.labelsPage, limit: this.labelsLimit, total: this.totalLabels,
      controlsId: this.labelsPaginationControlsId, infoId: this.labelsPaginationInfoId,
      buttonsId: this.labelsPaginationButtonsId, perPageId: this.labelsItemsPerPageId,
      onPageChange: (p) => this.loadLabels(p),
      onLimitChange: (val) => { this.labelsLimit = val; this.labelsPage = 1; this.loadLabels(1); },
    });
  }

  displayLabels() {
    const tbody = document.getElementById(this.labelsTableId);
    if (!tbody) return;
    if (this.allLabels.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">등록된 라벨이 없습니다.</td></tr>';
      return;
    }
    tbody.innerHTML = this.allLabels.map((label) => {
      const typeClass = label.label_type || "default";
      return `<tr>
        <td><span class="label-badge ${typeClass}">${escapeHtml(label.name)}</span></td>
        <td>${escapeHtml(label.label_type || "N/A")}</td>
        <td>${escapeHtml(label.description || "-")}</td>
        <td><button class="btn btn-danger btn-small" onclick="window.labelManager.deleteLabel(${label.id})">삭제</button></td>
      </tr>`;
    }).join("");
  }

  async createLabel(event) {
    event.preventDefault();
    const name = document.getElementById(this.labelNameInputId).value.trim();
    const labelType = document.getElementById(this.labelTypeInputId).value;
    const description = document.getElementById(this.labelDescriptionInputId).value.trim();
    try {
      await createLabelApi(name, labelType, description);
      showSuccess("라벨이 생성되었습니다.");
      document.getElementById(this.labelFormId).reset();
      await this.loadLabels();
    } catch (error) {
      console.error("라벨 생성 실패:", error);
      showError(error.message || "라벨 생성 중 오류가 발생했습니다.");
    }
  }

  async deleteLabel(labelId) {
    try {
      const impact = await fetchLabelImpact(labelId);
      let message = `다음 라벨을 삭제하시겠습니까?\n\n`;
      message += `라벨: ${escapeHtml(impact.label_name)} (${escapeHtml(impact.label_type)})\n\n⚠️ 영향도:\n`;
      message += `- 이 라벨이 붙은 청크: ${impact.chunks_count}개\n`;
      if (impact.child_labels_count > 0) message += `- 이 그룹에 속한 키워드: ${impact.child_labels_count}개\n`;
      if (impact.parent_group) message += `- 속한 그룹: ${escapeHtml(impact.parent_group.name)}\n`;
      message += `\n⚠️ 주의: 삭제 후 복구할 수 없습니다.`;
      if (!confirm(message)) return;
      await deleteLabelApi(labelId);
      showSuccess("라벨이 삭제되었습니다.");
      await this.loadLabels();
    } catch (error) {
      console.error("라벨 삭제 실패:", error);
      showError(error.message || "라벨 삭제 중 오류가 발생했습니다.");
    }
  }

  updateLabelSelect() {
    if (this.labelPickerListId) { this.renderLabelPickerList(); return; }
    const select = document.getElementById(this.addLabelSelectId);
    if (!select) return;
    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    select.innerHTML = '<option value="">라벨 선택...</option>' +
      (Array.isArray(list) ? list : []).map((label) => `<option value="${label.id}">${escapeHtml(label.name)} (${escapeHtml(label.label_type || "")})</option>`).join("");
  }

  setLabelPickerFilter(type) { this.labelPickerFilterType = type || ""; this.renderLabelPickerList(); }

  renderLabelPickerList() {
    const container = this.labelPickerListId ? document.getElementById(this.labelPickerListId) : null;
    if (!container) return;
    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    let labels = Array.isArray(list) ? list : [];
    if (this.labelPickerFilterType) labels = labels.filter((l) => (l.label_type || "") === this.labelPickerFilterType);
    if (labels.length === 0) {
      container.innerHTML = '<p class="label-picker-empty">' + (this.labelPickerFilterType ? "해당 분류에 라벨이 없습니다." : "등록된 라벨이 없습니다.") + "</p>";
      return;
    }
    container.innerHTML = labels.map((label) => {
      const typeClass = label.label_type || "default";
      const isSelected = this.selectedLabelIdsForAdd.has(label.id);
      const isAlreadyOnChunk = this.currentChunkLabelIds.includes(label.id);
      return `<button type="button" class="label-picker-badge label-badge ${typeClass} ${isSelected ? "selected" : ""} ${isAlreadyOnChunk ? "on-chunk" : ""}" data-label-id="${label.id}" title="${isAlreadyOnChunk ? "이미 청크에 추가됨" : "클릭하여 선택/해제"}">${escapeHtml(label.name)}</button>`;
    }).join("");
    container.querySelectorAll(".label-picker-badge").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-label-id"), 10);
        if (!isNaN(id)) this.toggleLabelPicker(id);
      });
    });
  }

  toggleLabelPicker(labelId) {
    if (this.selectedLabelIdsForAdd.has(labelId)) this.selectedLabelIdsForAdd.delete(labelId);
    else this.selectedLabelIdsForAdd.add(labelId);
    this.renderLabelPickerList();
  }

  selectAllLabelsInPicker() {
    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    let labels = Array.isArray(list) ? list : [];
    if (this.labelPickerFilterType) labels = labels.filter((l) => (l.label_type || "") === this.labelPickerFilterType);
    this.selectedLabelIdsForAdd = new Set(labels.map((l) => l.id));
    this.renderLabelPickerList();
  }

  selectSimilarLabelsInPicker() {
    let list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    const labels = Array.isArray(list) ? list : [];
    if (this.selectedLabelIdsForAdd.size === 0) {
      if (typeof showError === "function") showError("먼저 유사하게 선택할 라벨을 1개 이상 선택하세요.");
      return;
    }
    const selectedTypes = new Set();
    labels.forEach((l) => { if (this.selectedLabelIdsForAdd.has(l.id)) selectedTypes.add(l.label_type || ""); });
    labels.forEach((l) => { if (selectedTypes.has(l.label_type || "")) this.selectedLabelIdsForAdd.add(l.id); });
    this.renderLabelPickerList();
  }

  deselectAllLabelsInPicker() { this.selectedLabelIdsForAdd.clear(); this.renderLabelPickerList(); }

  async addSelectedLabelsToChunk() {
    if (!this.selectedChunkId) { showError("먼저 청크를 선택하세요."); return; }
    const ids = Array.from(this.selectedLabelIdsForAdd);
    if (ids.length === 0) { showError("추가할 라벨을 1개 이상 선택하세요."); return; }
    const { success, fail } = await batchAddLabelsToChunkApi(this.selectedChunkId, ids);
    this.selectedLabelIdsForAdd.clear();
    await this.loadChunkLabels(this.selectedChunkId);
    this.renderLabelPickerList();
    if (fail === 0) showSuccess(success + "개 라벨을 추가했습니다.");
    else if (success > 0) showSuccess(success + "개 추가, " + fail + "개 실패(이미 추가됨 등).");
    else showError("라벨 추가에 실패했습니다.");
  }

  async fetchAiLabelSuggestions() {
    if (!this.selectedChunkId) { showError("먼저 청크를 선택하세요."); return; }
    const container = this.aiSuggestionsContainerId ? document.getElementById(this.aiSuggestionsContainerId) : null;
    const statusEl = this.aiSuggestStatusId ? document.getElementById(this.aiSuggestStatusId) : null;
    const btnEl = this.aiSuggestBtnId ? document.getElementById(this.aiSuggestBtnId) : null;
    if (container) container.style.display = "none";
    if (statusEl) statusEl.textContent = "LLM 추천 중...";
    if (btnEl) btnEl.disabled = true;
    try {
      const data = await fetchAiSuggestionsApi(this.selectedChunkId, 10);
      this.lastAiSuggestions = data.suggestions || [];
      this.lastAiNewKeywords = data.new_keywords || [];
      this.renderAiSuggestions(this.lastAiSuggestions, this.lastAiNewKeywords);
      if (container) container.style.display = this.lastAiSuggestions.length ? "block" : "none";
      const newWrap = this.aiNewKeywordsWrapId ? document.getElementById(this.aiNewKeywordsWrapId) : null;
      if (newWrap) newWrap.style.display = this.lastAiNewKeywords.length ? "block" : "none";
      const ollamaOk = data.ollama_feedback && data.ollama_feedback.available;
      const noResults = !this.lastAiSuggestions.length && !this.lastAiNewKeywords.length;
      if (statusEl) {
        if (noResults) statusEl.textContent = data.message || (ollamaOk ? "추천 결과가 없습니다." : (data.ollama_feedback && data.ollama_feedback.message) || "추천 결과가 없습니다.");
        else if (!ollamaOk && data.ollama_feedback && data.ollama_feedback.message) statusEl.textContent = "(참고: " + data.ollama_feedback.message + ")";
        else statusEl.textContent = "";
      }
    } catch (e) {
      console.error("AI 라벨 추천 실패:", e);
      showError(e.message || "AI 추천을 불러오지 못했습니다. LLM 서버(Ollama)가 실행 중인지 확인하세요.");
      if (statusEl) statusEl.textContent = "";
    } finally {
      if (btnEl) btnEl.disabled = false;
    }
  }

  renderAiSuggestions(suggestions, newKeywords) {
    renderAiSuggestionsUI(
      suggestions, newKeywords,
      this.aiSuggestionsContainerId, this.aiNewKeywordsContainerId,
      (labelId, conf) => this.applyAiSuggestion(labelId, conf),
      (keyword) => this.applyNewKeywordAsLabel(keyword)
    );
  }

  async applyNewKeywordAsLabel(keyword) {
    if (!this.selectedChunkId || !keyword || !String(keyword).trim()) return;
    const kw = String(keyword).trim();
    try {
      const labelId = await createAndLinkKeywordLabel(this.selectedChunkId, kw);
      showSuccess('키워드 "' + kw + '"를 라벨로 등록하고 청크에 추가했습니다.');
      this.currentChunkLabelIds.push(labelId);
      await this.loadChunkLabels(this.selectedChunkId);
      this.lastAiNewKeywords = this.lastAiNewKeywords.filter((k) => String(k).trim() !== kw);
      this.renderAiSuggestions(this.lastAiSuggestions, this.lastAiNewKeywords);
      const newWrap = this.aiNewKeywordsWrapId ? document.getElementById(this.aiNewKeywordsWrapId) : null;
      if (newWrap) newWrap.style.display = this.lastAiNewKeywords.length ? "block" : "none";
      this.loadLabelOptions();
      this.renderLabelPickerList();
    } catch (e) {
      console.error("새 키워드 라벨 등록 실패:", e);
      showError(e.message || "라벨 등록에 실패했습니다.");
    }
  }

  async applyAiSuggestion(labelId, confidence) {
    if (!this.selectedChunkId) return;
    try {
      await applyAiSuggestionLabelApi(this.selectedChunkId, labelId);
      showSuccess("라벨을 추가했습니다.");
      this.currentChunkLabelIds.push(labelId);
      await this.loadChunkLabels(this.selectedChunkId);
      this.lastAiSuggestions = this.lastAiSuggestions.filter((s) => s.label_id !== labelId);
      this.renderAiSuggestions(this.lastAiSuggestions, this.lastAiNewKeywords);
      const container = this.aiSuggestionsContainerId ? document.getElementById(this.aiSuggestionsContainerId) : null;
      if (container) container.style.display = this.lastAiSuggestions.length ? "block" : "none";
    } catch (e) {
      console.error("AI 추천 라벨 적용 실패:", e);
      showError(e.message || "라벨 추가에 실패했습니다.");
    }
  }

  async loadChunks() {
    try {
      this.allChunks = await fetchChunksApi(1000);
      if (this.currentSearchTerm) this.searchChunks();
      else this.applyChunkPagination(this.allChunks);
      this.onChunkChange();
    } catch (error) {
      console.error("청크 로드 실패:", error);
      showError("청크 목록을 불러올 수 없습니다.");
      if (this.searchPagination) this.searchPagination.hide();
    }
  }

  displayChunks(chunksToDisplay = null) {
    const chunks = chunksToDisplay !== null ? chunksToDisplay : this.allChunks;
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;
    if (chunks.length === 0) {
      chunkList.innerHTML = '<div class="loading">청크가 없습니다.</div>';
      if (this.searchPagination) this.searchPagination.hide();
      return;
    }
    chunkList.innerHTML = chunks.map((chunk) => {
      const isSelected = this.selectedChunkId === chunk.id;
      return `<div class="chunk-item-select ${isSelected ? "selected" : ""}" onclick="window.labelManager.selectChunk(${chunk.id})">
        <div><strong>ID: ${chunk.id}</strong></div>
        <div class="chunk-preview">${escapeHtml((chunk.content || "").substring(0, 100))}...</div>
      </div>`;
    }).join("");
  }

  searchChunks() {
    const searchInput = document.getElementById(this.chunkSearchInputId);
    if (!searchInput) return;
    const searchTerm = searchInput.value.toLowerCase();
    this.currentSearchTerm = searchTerm;
    if (!searchTerm) {
      if (this.searchPagination) this.searchPagination.currentPage = 1;
      this.applyChunkPagination(this.allChunks);
      return;
    }
    this.filteredChunks = this.allChunks.filter((chunk) => (chunk.content || "").toLowerCase().includes(searchTerm));
    this.applyChunkPagination(this.filteredChunks);
  }

  applyChunkPagination(chunkSource) {
    const list = Array.isArray(chunkSource) ? chunkSource : [];
    if (list.length === 0) {
      this.displayChunks([]);
      if (this.searchPagination) { this.searchPagination.updateState({ totalCount: 0, totalPages: 0 }); this.searchPagination.updateUI(); }
      return;
    }
    if (this.searchPagination) {
      const totalPages = Math.max(1, Math.ceil(list.length / this.searchPagination.limit));
      const safePage = Math.min(Math.max(1, this.searchPagination.currentPage), totalPages);
      this.searchPagination.updateState({ totalCount: list.length, totalPages, currentPage: safePage });
      const state = this.searchPagination.getState();
      this.displayChunks(list.slice(state.offset, state.offset + state.limit));
      this.searchPagination.updateUI();
    } else {
      this.displayChunks(list);
    }
  }

  async selectChunk(chunkId) {
    this.selectedChunkId = chunkId;
    const list = this.currentSearchTerm ? this.filteredChunks : this.allChunks;
    this.applyChunkPagination(list);
    const chunk = this.allChunks.find((c) => c.id === chunkId);
    const currentChunkInfo = document.getElementById(this.currentChunkInfoId);
    const chunkContentEl = this.chunkContentId ? document.getElementById(this.chunkContentId) : null;
    if (chunk) {
      if (currentChunkInfo) { currentChunkInfo.textContent = `청크 ID: ${chunk.id}`; currentChunkInfo.setAttribute("aria-hidden", "false"); }
      if (chunkContentEl) { chunkContentEl.textContent = chunk.content || ""; chunkContentEl.style.display = "block"; }
    } else {
      if (currentChunkInfo) { currentChunkInfo.textContent = ""; currentChunkInfo.setAttribute("aria-hidden", "true"); }
      if (chunkContentEl) { chunkContentEl.textContent = ""; chunkContentEl.style.display = "none"; }
    }
    await this.loadChunkLabels(chunkId);
    const chunkLabelsSection = document.getElementById(this.chunkLabelsSectionId);
    if (chunkLabelsSection && chunkLabelsSection.style) chunkLabelsSection.style.display = "block";
  }

  async loadChunkLabels(chunkId) {
    try {
      const chunkLabels = await fetchChunkLabelsApi(chunkId);
      this.currentChunkLabelIds = (chunkLabels || []).map((l) => l.id);
      const currentLabelsDiv = document.getElementById(this.currentLabelsId);
      if (!currentLabelsDiv) return;
      if (chunkLabels.length === 0) {
        currentLabelsDiv.innerHTML = '<p style="color: #999; font-size: 12px;">라벨이 없습니다.</p>';
      } else {
        currentLabelsDiv.innerHTML = chunkLabels.map((label) => {
          const typeClass = label.label_type || "default";
          return `<span class="label-badge ${typeClass}">${escapeHtml(label.name)}<button onclick="window.labelManager.removeLabelFromChunk(${label.id})" style="margin-left: 5px; background: none; border: none; color: inherit; cursor: pointer; font-weight: bold;">×</button></span>`;
        }).join("");
      }
      if (this.labelPickerListId) this.renderLabelPickerList();
    } catch (error) {
      console.error("청크 라벨 로드 실패:", error);
    }
  }

  async addLabelToChunk() {
    if (!this.selectedChunkId) { showError("먼저 청크를 선택하세요."); return; }
    const select = document.getElementById(this.addLabelSelectId);
    if (!select) return;
    const labelId = parseInt(select.value);
    if (!labelId) { showError("라벨을 선택하세요."); return; }
    try {
      await addChunkLabelApi(this.selectedChunkId, labelId);
      showSuccess("라벨이 추가되었습니다.");
      await this.loadChunkLabels(this.selectedChunkId);
      select.value = "";
    } catch (error) {
      console.error("라벨 추가 실패:", error);
      showError(error.message || "라벨 추가 중 오류가 발생했습니다.");
    }
  }

  async removeLabelFromChunk(labelId) {
    if (!this.selectedChunkId) return;
    if (!confirm("이 라벨을 제거하시겠습니까?")) return;
    try {
      await removeChunkLabelApi(this.selectedChunkId, labelId);
      showSuccess("라벨이 제거되었습니다.");
      await this.loadChunkLabels(this.selectedChunkId);
    } catch (error) {
      console.error("라벨 제거 실패:", error);
      showError("라벨 제거 중 오류가 발생했습니다.");
    }
  }

  async applyLabelSuggestion(chunkId, labelId, confidence) {
    try {
      await applyLabelSuggestionApi(chunkId, labelId, confidence);
      showSuccess("라벨이 적용되었습니다.");
      return true;
    } catch (error) {
      console.error("라벨 적용 실패:", error);
      showError(error.message || "라벨 적용 중 오류가 발생했습니다.");
      return false;
    }
  }
}
