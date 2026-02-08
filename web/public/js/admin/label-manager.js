/**
 * 라벨 관리 모듈
 * 라벨 CRUD, 청크-라벨 연결 관리 기능을 제공하는 클래스
 */
class LabelManager {
  constructor(config = {}) {
    // 콜백 함수
    this.onLabelChange = config.onLabelChange || (() => {});
    this.onChunkChange = config.onChunkChange || (() => {});

    // 상태 관리
    this.allLabels = [];
    this.allChunks = [];
    this.selectedChunkId = null;
    this.currentSearchTerm = "";
    this.filteredChunks = [];

    // 페이징 컴포넌트 (청크 목록용)
    this.searchPagination = null;
    if (config.enablePagination) {
      this.searchPagination = new PaginationComponent({
        initialPage: 1,
        initialLimit: 20,
        prefix: "청크",
        hideWhenEmpty: config.chunkPaginationHideWhenEmpty !== false,
        onPageChange: () => this.searchChunks(),
        onLimitChange: () => this.searchChunks(),
      });
    }

    // DOM 요소 ID (기본값)
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

    // 라벨 목록 페이징 (knowledge-admin)
    this.enableLabelsPagination = config.enableLabelsPagination === true;
    this.labelsPage = 1;
    this.labelsLimit = config.labelsInitialLimit || 20;
    this.totalLabels = 0;
    this.labelOptions = []; // 청크 라벨 탭용 드롭다운 전체 목록
    this.labelsPaginationControlsId = config.labelsPaginationControlsId || "labels-pagination-controls";
    this.labelsPaginationInfoId = config.labelsPaginationInfoId || "labels-pagination-info";
    this.labelsItemsPerPageId = config.labelsItemsPerPageId || "labels-items-per-page";
    this.labelsPaginationButtonsId = config.labelsPaginationButtonsId || "labels-pagination-buttons";
    this.labelsFilterTypeId = config.labelsFilterTypeId || "labels-filter-type";
    this.labelsFilterNameId = config.labelsFilterNameId || "labels-filter-name";
    this.labelsFilterApplyId = config.labelsFilterApplyId || "labels-filter-apply";
  }

  /**
   * 라벨 목록 필터 값 반환 (타입, 이름 검색어)
   */
  getLabelsFilterParams() {
    const typeEl = document.getElementById(this.labelsFilterTypeId);
    const nameEl = document.getElementById(this.labelsFilterNameId);
    const labelType = typeEl ? typeEl.value : "";
    const q = nameEl ? nameEl.value.trim() : "";
    return { labelType, q };
  }

  /**
   * 라벨 목록 로드 (페이징 시 limit/offset 사용, 타입/이름 필터 적용)
   */
  async loadLabels(pageOrReset) {
    try {
      const page = typeof pageOrReset === "number" ? pageOrReset : this.labelsPage;
      if (this.enableLabelsPagination) {
        const offset = (page - 1) * this.labelsLimit;
        const { labelType, q } = this.getLabelsFilterParams();
        const params = new URLSearchParams({ limit: this.labelsLimit, offset });
        if (labelType) params.set("label_type", labelType);
        if (q) params.set("q", q);
        const response = await fetch(`/api/labels?${params.toString()}`);
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `서버 오류 (${response.status})`);
        }
        const data = await response.json();
        this.allLabels = data.items || [];
        this.totalLabels = data.total != null ? data.total : 0;
        this.labelsPage = page;
        this.displayLabels();
        this.updateLabelsPaginationUI();
      } else {
        const response = await fetch("/api/labels");
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `서버 오류 (${response.status})`);
        }
        this.allLabels = await response.json();
        this.totalLabels = Array.isArray(this.allLabels) ? this.allLabels.length : 0;
        this.displayLabels();
        this.updateLabelSelect();
      }
      this.onLabelChange();
    } catch (error) {
      console.error("라벨 로드 실패:", error);
      let errorMessage = "라벨 목록을 불러올 수 없습니다.";
      if (error.message && (error.message.includes("Failed to fetch") || error.message.includes("NetworkError"))) {
        errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      if (typeof showError === "function") showError(errorMessage);
    }
  }

  /**
   * 청크 라벨 탭용 라벨 전체 목록 로드 (드롭다운 채우기)
   */
  async loadLabelOptions() {
    try {
      const response = await fetch("/api/labels");
      if (!response.ok) return;
      const data = await response.json();
      this.labelOptions = Array.isArray(data) ? data : (data.items || []);
      this.updateLabelSelect();
    } catch (e) {
      console.warn("라벨 옵션 로드 실패:", e);
      this.labelOptions = [];
    }
  }

  /**
   * 라벨 목록 페이징 UI 갱신
   */
  updateLabelsPaginationUI() {
    const controls = document.getElementById(this.labelsPaginationControlsId);
    const info = document.getElementById(this.labelsPaginationInfoId);
    const buttons = document.getElementById(this.labelsPaginationButtonsId);
    const perPageSelect = document.getElementById(this.labelsItemsPerPageId);
    if (!controls || !info || !buttons) return;

    const total = this.totalLabels;
    const limit = this.labelsLimit;
    const totalPages = Math.max(1, Math.ceil(total / limit));

    // 1개 이상일 때 페이징 UI 항상 고정 표시 (0개일 때만 숨김)
    if (total === 0) {
      controls.style.display = "none";
      return;
    }
    controls.style.display = "block";

    const start = (this.labelsPage - 1) * limit + 1;
    const end = Math.min(this.labelsPage * limit, total);
    info.textContent = `총 ${total.toLocaleString()}개 중 ${start.toLocaleString()}-${end.toLocaleString()}개 표시`;

    if (perPageSelect) {
      perPageSelect.value = limit;
      perPageSelect.onchange = () => {
        this.labelsLimit = parseInt(perPageSelect.value, 10);
        this.labelsPage = 1;
        this.loadLabels(1);
      };
    }

    buttons.innerHTML = "";
    const prev = document.createElement("button");
    prev.type = "button";
    prev.textContent = "◀ 이전";
    prev.disabled = this.labelsPage <= 1;
    prev.className = "btn btn-small";
    prev.style = "padding: 4px 10px; font-size: 12px;";
    prev.onclick = () => {
      if (this.labelsPage > 1) this.loadLabels(this.labelsPage - 1);
    };
    buttons.appendChild(prev);

    const maxButtons = 7;
    let startPage = Math.max(1, this.labelsPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);
    if (endPage - startPage + 1 < maxButtons) startPage = Math.max(1, endPage - maxButtons + 1);

    for (let i = startPage; i <= endPage; i++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = i;
      btn.className = "btn btn-small " + (i === this.labelsPage ? "btn-primary" : "");
      btn.style = "padding: 4px 10px; font-size: 12px; min-width: 32px;";
      btn.onclick = () => this.loadLabels(i);
      buttons.appendChild(btn);
    }

    const next = document.createElement("button");
    next.type = "button";
    next.textContent = "다음 ▶";
    next.disabled = this.labelsPage >= totalPages;
    next.className = "btn btn-small";
    next.style = "padding: 4px 10px; font-size: 12px;";
    next.onclick = () => {
      if (this.labelsPage < totalPages) this.loadLabels(this.labelsPage + 1);
    };
    buttons.appendChild(next);
  }

  /**
   * 라벨 표시
   */
  displayLabels() {
    const tbody = document.getElementById(this.labelsTableId);
    if (!tbody) return;

    if (this.allLabels.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">등록된 라벨이 없습니다.</td></tr>';
      return;
    }

    tbody.innerHTML = this.allLabels
      .map((label) => {
        const typeClass = label.label_type || "default";
        return `
        <tr>
          <td><span class="label-badge ${typeClass}">${escapeHtml(label.name)}</span></td>
          <td>${escapeHtml(label.label_type || "N/A")}</td>
          <td>${escapeHtml(label.description || "-")}</td>
          <td>
            <button class="btn btn-danger btn-small" onclick="window.labelManager.deleteLabel(${label.id})">삭제</button>
          </td>
        </tr>
      `;
      })
      .join("");
  }

  /**
   * 라벨 생성
   */
  async createLabel(event) {
    event.preventDefault();

    const name = document.getElementById(this.labelNameInputId).value.trim();
    const labelType = document.getElementById(this.labelTypeInputId).value;
    const description = document.getElementById(this.labelDescriptionInputId).value.trim();

    try {
      const response = await fetch("/api/labels", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: name,
          label_type: labelType,
          description: description || null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "라벨 생성 실패");
      }

      showSuccess("라벨이 생성되었습니다.");
      document.getElementById(this.labelFormId).reset();
      await this.loadLabels();
    } catch (error) {
      console.error("라벨 생성 실패:", error);
      showError(error.message || "라벨 생성 중 오류가 발생했습니다.");
    }
  }

  /**
   * 라벨 삭제 (영향도 조회 포함)
   */
  async deleteLabel(labelId) {
    try {
      // 영향도 조회
      const impactResponse = await fetch(`/api/labels/${labelId}/impact`);
      if (!impactResponse.ok) {
        throw new Error("영향도 정보를 불러올 수 없습니다.");
      }
      const impact = await impactResponse.json();

      // 영향도 정보를 포함한 확인 다이얼로그
      let message = `다음 라벨을 삭제하시겠습니까?\n\n`;
      message += `라벨: ${escapeHtml(impact.label_name)} (${escapeHtml(impact.label_type)})\n\n`;
      message += `⚠️ 영향도:\n`;
      message += `- 이 라벨이 붙은 청크: ${impact.chunks_count}개\n`;
      if (impact.child_labels_count > 0) {
        message += `- 이 그룹에 속한 키워드: ${impact.child_labels_count}개\n`;
      }
      if (impact.parent_group) {
        message += `- 속한 그룹: ${escapeHtml(impact.parent_group.name)}\n`;
      }
      message += `\n⚠️ 주의: 삭제 후 복구할 수 없습니다.`;

      if (!confirm(message)) {
        return;
      }

      // 삭제 실행
      const response = await fetch(`/api/labels/${labelId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("라벨 삭제 실패");
      }

      showSuccess("라벨이 삭제되었습니다.");
      await this.loadLabels();
    } catch (error) {
      console.error("라벨 삭제 실패:", error);
      showError(error.message || "라벨 삭제 중 오류가 발생했습니다.");
    }
  }

  /**
   * 라벨 선택 드롭다운 업데이트 (청크 라벨 탭: labelOptions, 라벨 탭: allLabels)
   * labelPickerListId가 있으면 배지 토글 목록만 렌더
   */
  updateLabelSelect() {
    if (this.labelPickerListId) {
      this.renderLabelPickerList();
      return;
    }
    const select = document.getElementById(this.addLabelSelectId);
    if (!select) return;

    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    select.innerHTML =
      '<option value="">라벨 선택...</option>' +
      (Array.isArray(list) ? list : []).map((label) => `<option value="${label.id}">${escapeHtml(label.name)} (${escapeHtml(label.label_type || "")})</option>`).join("");
  }

  /**
   * 라벨 분류 필터 설정 (청크 관리 페이지용)
   */
  setLabelPickerFilter(type) {
    this.labelPickerFilterType = type || "";
    this.renderLabelPickerList();
  }

  /**
   * 라벨 배지 토글 목록 렌더 (청크 관리 페이지용, 분류 필터 적용)
   */
  renderLabelPickerList() {
    const container = this.labelPickerListId ? document.getElementById(this.labelPickerListId) : null;
    if (!container) return;

    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    let labels = Array.isArray(list) ? list : [];
    if (this.labelPickerFilterType) {
      labels = labels.filter((l) => (l.label_type || "") === this.labelPickerFilterType);
    }

    if (labels.length === 0) {
      container.innerHTML = '<p class="label-picker-empty">' + (this.labelPickerFilterType ? "해당 분류에 라벨이 없습니다." : "등록된 라벨이 없습니다.") + "</p>";
      return;
    }

    container.innerHTML = labels
      .map((label) => {
        const typeClass = label.label_type || "default";
        const isSelected = this.selectedLabelIdsForAdd.has(label.id);
        const isAlreadyOnChunk = this.currentChunkLabelIds.includes(label.id);
        return `
        <button type="button" class="label-picker-badge label-badge ${typeClass} ${isSelected ? "selected" : ""} ${isAlreadyOnChunk ? "on-chunk" : ""}" data-label-id="${label.id}" title="${isAlreadyOnChunk ? "이미 청크에 추가됨" : "클릭하여 선택/해제"}">
          ${escapeHtml(label.name)}
        </button>
      `;
      })
      .join("");

    container.querySelectorAll(".label-picker-badge").forEach((btn) => {
      btn.addEventListener("click", () => {
        const id = parseInt(btn.getAttribute("data-label-id"), 10);
        if (!isNaN(id)) this.toggleLabelPicker(id);
      });
    });
  }

  /**
   * 배지 목록에서 라벨 토글 (선택/해제)
   */
  toggleLabelPicker(labelId) {
    if (this.selectedLabelIdsForAdd.has(labelId)) {
      this.selectedLabelIdsForAdd.delete(labelId);
    } else {
      this.selectedLabelIdsForAdd.add(labelId);
    }
    this.renderLabelPickerList();
  }

  /**
   * 배지 목록 전체 선택 (현재 필터된 목록 기준)
   */
  selectAllLabelsInPicker() {
    const list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    let labels = Array.isArray(list) ? list : [];
    if (this.labelPickerFilterType) labels = labels.filter((l) => (l.label_type || "") === this.labelPickerFilterType);
    this.selectedLabelIdsForAdd = new Set(labels.map((l) => l.id));
    this.renderLabelPickerList();
  }

  /**
   * 배지 목록 유사선택 (현재 선택된 라벨과 동일한 label_type인 라벨 모두 선택)
   */
  selectSimilarLabelsInPicker() {
    let list = this.labelOptions && this.labelOptions.length ? this.labelOptions : this.allLabels;
    const labels = Array.isArray(list) ? list : [];
    if (this.selectedLabelIdsForAdd.size === 0) {
      if (typeof showError === "function") showError("먼저 유사하게 선택할 라벨을 1개 이상 선택하세요.");
      return;
    }
    const selectedTypes = new Set();
    labels.forEach((l) => {
      if (this.selectedLabelIdsForAdd.has(l.id)) selectedTypes.add(l.label_type || "");
    });
    labels.forEach((l) => {
      if (selectedTypes.has(l.label_type || "")) this.selectedLabelIdsForAdd.add(l.id);
    });
    this.renderLabelPickerList();
  }

  /**
   * 배지 목록 선택 해제
   */
  deselectAllLabelsInPicker() {
    this.selectedLabelIdsForAdd.clear();
    this.renderLabelPickerList();
  }

  /**
   * 선택된 배지 항목을 청크에 일괄 추가
   */
  async addSelectedLabelsToChunk() {
    if (!this.selectedChunkId) {
      showError("먼저 청크를 선택하세요.");
      return;
    }
    const ids = Array.from(this.selectedLabelIdsForAdd);
    if (ids.length === 0) {
      showError("추가할 라벨을 1개 이상 선택하세요.");
      return;
    }

    let success = 0;
    let fail = 0;
    for (const labelId of ids) {
      try {
        const response = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, { method: "POST" });
        if (response.ok) success++;
        else fail++;
      } catch {
        fail++;
      }
    }

    this.selectedLabelIdsForAdd.clear();
    await this.loadChunkLabels(this.selectedChunkId);
    this.renderLabelPickerList();

    if (fail === 0) showSuccess(success + "개 라벨을 추가했습니다.");
    else if (success > 0) showSuccess(success + "개 추가, " + fail + "개 실패(이미 추가됨 등).");
    else showError("라벨 추가에 실패했습니다.");
  }

  /**
   * 청크 내용 기반 AI(LLM) 키워드·라벨 추천 요청
   */
  async fetchAiLabelSuggestions() {
    if (!this.selectedChunkId) {
      showError("먼저 청크를 선택하세요.");
      return;
    }
    const container = this.aiSuggestionsContainerId ? document.getElementById(this.aiSuggestionsContainerId) : null;
    const statusEl = this.aiSuggestStatusId ? document.getElementById(this.aiSuggestStatusId) : null;
    const btnEl = this.aiSuggestBtnId ? document.getElementById(this.aiSuggestBtnId) : null;
    if (container) container.style.display = "none";
    if (statusEl) statusEl.textContent = "LLM 추천 중...";
    if (btnEl) btnEl.disabled = true;
    try {
      const res = await fetch(`/api/knowledge/labels/suggest-llm?chunk_id=${this.selectedChunkId}&limit=10`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "추천 요청 실패");
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

  /**
   * AI 추천 라벨 목록 렌더 (배지 + 추가 버튼) + 새 키워드 (라벨로 등록 버튼)
   */
  renderAiSuggestions(suggestions, newKeywords) {
    const list = Array.isArray(suggestions) ? suggestions : [];
    const container = this.aiSuggestionsContainerId ? document.getElementById(this.aiSuggestionsContainerId) : null;
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
            if (!isNaN(labelId)) this.applyAiSuggestion(labelId, conf);
          });
        });
      }
    }
    const newKwList = Array.isArray(newKeywords) ? newKeywords : [];
    const newKwContainer = this.aiNewKeywordsContainerId ? document.getElementById(this.aiNewKeywordsContainerId) : null;
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
            if (keyword) this.applyNewKeywordAsLabel(keyword);
          });
        });
      }
    }
  }

  /**
   * 새 키워드를 라벨로 생성 후 청크에 연결
   */
  async applyNewKeywordAsLabel(keyword) {
    if (!this.selectedChunkId || !keyword || !String(keyword).trim()) return;
    const kw = String(keyword).trim();
    try {
      const createRes = await fetch("/api/labels", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: kw, label_type: "keyword", description: "" }),
      });
      const createData = await createRes.json();
      if (!createRes.ok) throw new Error(createData.detail || "라벨 생성 실패");
      const labelId = createData.id;
      const linkRes = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, { method: "POST" });
      if (!linkRes.ok) {
        const err = await linkRes.json().catch(() => ({}));
        throw new Error(err.detail || "청크에 라벨 연결 실패");
      }
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

  /**
   * AI 추천 라벨 1건 청크에 추가
   */
  async applyAiSuggestion(labelId, confidence) {
    if (!this.selectedChunkId) return;
    try {
      const res = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, { method: "POST" });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "라벨 추가 실패");
      }
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

  /**
   * 청크 목록 로드
   */
  async loadChunks() {
    try {
      const response = await fetch("/api/knowledge/chunks?limit=1000");
      const data = await response.json();
      // 새로운 API 응답 형식 처리 (하위 호환성 유지)
      this.allChunks = Array.isArray(data) ? data : data.items || data.chunks || [];

      // 검색어가 있으면 검색 결과 페이징, 없으면 전체 목록 페이징 표시
      if (this.currentSearchTerm) {
        this.searchChunks();
      } else {
        this.applyChunkPagination(this.allChunks);
      }
      this.onChunkChange();
    } catch (error) {
      console.error("청크 로드 실패:", error);
      showError("청크 목록을 불러올 수 없습니다.");
      if (this.searchPagination) {
        this.searchPagination.hide();
      }
    }
  }

  /**
   * 청크 표시
   */
  displayChunks(chunksToDisplay = null) {
    const chunks = chunksToDisplay !== null ? chunksToDisplay : this.allChunks;
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;

    if (chunks.length === 0) {
      chunkList.innerHTML = '<div class="loading">청크가 없습니다.</div>';
      if (this.searchPagination) {
        this.searchPagination.hide();
      }
      return;
    }

    chunkList.innerHTML = chunks
      .map((chunk) => {
        const isSelected = this.selectedChunkId === chunk.id;
        return `
        <div class="chunk-item-select ${isSelected ? "selected" : ""}" onclick="window.labelManager.selectChunk(${chunk.id})">
          <div><strong>ID: ${chunk.id}</strong></div>
          <div class="chunk-preview">${escapeHtml((chunk.content || "").substring(0, 100))}...</div>
        </div>
      `;
      })
      .join("");
  }

  /**
   * 청크 검색
   */
  searchChunks() {
    const searchInput = document.getElementById(this.chunkSearchInputId);
    if (!searchInput) return;

    const searchTerm = searchInput.value.toLowerCase();
    this.currentSearchTerm = searchTerm;

    if (!searchTerm) {
      // 검색어가 없으면 전체 목록 페이징 표시
      if (this.searchPagination) {
        this.searchPagination.currentPage = 1;
      }
      this.applyChunkPagination(this.allChunks);
      return;
    }

    // 검색 필터링
    this.filteredChunks = this.allChunks.filter((chunk) => {
      const content = (chunk.content || "").toLowerCase();
      return content.includes(searchTerm);
    });

    this.applyChunkPagination(this.filteredChunks);
  }

  /**
   * 청크 목록 페이징 적용: 목록 슬라이스 후 표시 및 페이징 UI 갱신
   */
  applyChunkPagination(chunkSource) {
    const list = Array.isArray(chunkSource) ? chunkSource : [];
    if (list.length === 0) {
      this.displayChunks([]);
      if (this.searchPagination) {
        this.searchPagination.updateState({ totalCount: 0, totalPages: 0 });
        this.searchPagination.updateUI();
      }
      return;
    }
    if (this.searchPagination) {
      const totalPages = Math.max(1, Math.ceil(list.length / this.searchPagination.limit));
      const safePage = Math.min(Math.max(1, this.searchPagination.currentPage), totalPages);
      this.searchPagination.updateState({
        totalCount: list.length,
        totalPages,
        currentPage: safePage,
      });
      const state = this.searchPagination.getState();
      const startIndex = state.offset;
      const endIndex = startIndex + state.limit;
      const paginatedChunks = list.slice(startIndex, endIndex);
      this.displayChunks(paginatedChunks);
      this.searchPagination.updateUI();
    } else {
      this.displayChunks(list);
    }
  }

  /**
   * 청크 선택 (현재 조회/페이징 상태 유지, 선택만 반영)
   */
  async selectChunk(chunkId) {
    this.selectedChunkId = chunkId;
    // 목록 전체 갱신 없이 현재 페이지·검색 결과만 다시 그리기
    const list = this.currentSearchTerm ? this.filteredChunks : this.allChunks;
    this.applyChunkPagination(list);

    // 선택된 청크 정보 및 내용 표시
    const chunk = this.allChunks.find((c) => c.id === chunkId);
    if (chunk) {
      const currentChunkInfo = document.getElementById(this.currentChunkInfoId);
      if (currentChunkInfo) {
        currentChunkInfo.textContent = `청크 ID: ${chunk.id}`;
        currentChunkInfo.setAttribute("aria-hidden", "false");
      }
      const chunkContentEl = this.chunkContentId ? document.getElementById(this.chunkContentId) : null;
      if (chunkContentEl) {
        chunkContentEl.textContent = chunk.content || "";
        chunkContentEl.style.display = "block";
      }
    } else {
      const currentChunkInfo = document.getElementById(this.currentChunkInfoId);
      if (currentChunkInfo) {
        currentChunkInfo.textContent = "";
        currentChunkInfo.setAttribute("aria-hidden", "true");
      }
      const chunkContentEl = this.chunkContentId ? document.getElementById(this.chunkContentId) : null;
      if (chunkContentEl) {
        chunkContentEl.textContent = "";
        chunkContentEl.style.display = "none";
      }
    }

    // 청크의 현재 라벨 로드
    await this.loadChunkLabels(chunkId);

    // 라벨 관리 섹션 표시 (chunk-labels 페이지 등 우측 패널 항상 노출 시 사용)
    const chunkLabelsSection = document.getElementById(this.chunkLabelsSectionId);
    if (chunkLabelsSection && chunkLabelsSection.style) {
      chunkLabelsSection.style.display = "block";
    }
  }

  /**
   * 청크의 라벨 로드
   */
  async loadChunkLabels(chunkId) {
    try {
      const response = await fetch(`/api/labels/chunks/${chunkId}/labels`);
      const chunkLabels = await response.json();
      this.currentChunkLabelIds = (chunkLabels || []).map((l) => l.id);

      const currentLabelsDiv = document.getElementById(this.currentLabelsId);
      if (!currentLabelsDiv) return;

      if (chunkLabels.length === 0) {
        currentLabelsDiv.innerHTML = '<p style="color: #999; font-size: 12px;">라벨이 없습니다.</p>';
      } else {
        currentLabelsDiv.innerHTML = chunkLabels
          .map((label) => {
            const typeClass = label.label_type || "default";
            return `
            <span class="label-badge ${typeClass}">
              ${escapeHtml(label.name)}
              <button onclick="window.labelManager.removeLabelFromChunk(${label.id})" style="margin-left: 5px; background: none; border: none; color: inherit; cursor: pointer; font-weight: bold;">×</button>
            </span>
          `;
          })
          .join("");
      }
      if (this.labelPickerListId) this.renderLabelPickerList();
    } catch (error) {
      console.error("청크 라벨 로드 실패:", error);
    }
  }

  /**
   * 청크에 라벨 추가
   */
  async addLabelToChunk() {
    if (!this.selectedChunkId) {
      showError("먼저 청크를 선택하세요.");
      return;
    }

    const select = document.getElementById(this.addLabelSelectId);
    if (!select) return;

    const labelId = parseInt(select.value);
    if (!labelId) {
      showError("라벨을 선택하세요.");
      return;
    }

    try {
      const response = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "라벨 추가 실패");
      }

      showSuccess("라벨이 추가되었습니다.");
      await this.loadChunkLabels(this.selectedChunkId);
      select.value = "";
    } catch (error) {
      console.error("라벨 추가 실패:", error);
      showError(error.message || "라벨 추가 중 오류가 발생했습니다.");
    }
  }

  /**
   * 청크에서 라벨 제거
   */
  async removeLabelFromChunk(labelId) {
    if (!this.selectedChunkId) {
      return;
    }

    if (!confirm("이 라벨을 제거하시겠습니까?")) {
      return;
    }

    try {
      const response = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("라벨 제거 실패");
      }

      showSuccess("라벨이 제거되었습니다.");
      await this.loadChunkLabels(this.selectedChunkId);
    } catch (error) {
      console.error("라벨 제거 실패:", error);
      showError("라벨 제거 중 오류가 발생했습니다.");
    }
  }

  /**
   * 라벨 제안 적용 (knowledge-admin.js 전용)
   */
  async applyLabelSuggestion(chunkId, labelId, confidence) {
    try {
      const response = await fetch(`/api/knowledge/labels/suggest/${chunkId}/apply/${labelId}?confidence=${confidence}`, {
        method: "POST",
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "라벨 적용 실패");
      }

      showSuccess("라벨이 적용되었습니다.");
      return true;
    } catch (error) {
      console.error("라벨 적용 실패:", error);
      showError(error.message || "라벨 적용 중 오류가 발생했습니다.");
      return false;
    }
  }
}
