class ManageTab {
  constructor() {
    this.container = null;
    this.workflow = null;
    this.manager = null;
    this.selectedChunkIds = new Set();
    this.isInitialized = false;
  }

  init(container, workflow) {
    this.container = container;
    this.workflow = workflow;

    this.manager = new LabelManager({
      enablePagination: true,
      enableLabelsPagination: false,
      chunkListId: 'kw-manage-chunk-list',
      chunkSearchInputId: 'kw-manage-chunk-search',
      currentChunkInfoId: 'kw-manage-current-chunk-info',
      currentLabelsId: 'kw-manage-current-labels',
      chunkLabelsSectionId: 'kw-manage-labels-section',
      chunkContentId: 'kw-manage-chunk-content',
      labelPickerListId: 'kw-manage-label-picker-list',
      aiSuggestionsContainerId: 'kw-manage-ai-suggestions',
      aiSuggestStatusId: 'kw-manage-ai-status',
      aiSuggestBtnId: 'kw-manage-btn-ai-suggest',
      aiNewKeywordsContainerId: 'kw-manage-ai-new-keywords',
      aiNewKeywordsWrapId: 'kw-manage-ai-new-keywords-wrap',
      chunkPaginationHideWhenEmpty: false,
      onLabelChange: () => {},
      onChunkChange: () => this.afterDisplayChunks(),
    });

    window.labelManager = this.manager;
    this.overrideManagerMethods();
    this.bindEvents();
    this.isInitialized = true;
  }

  overrideManagerMethods() {
    const originalRemove = this.manager.removeLabelFromChunk.bind(this.manager);
    this.manager.removeLabelFromChunk = async (labelId) => {
      if (!this.manager.selectedChunkId) return;
      try {
        await removeChunkLabelApi(this.manager.selectedChunkId, labelId);
        showSuccess("라벨이 제거되었습니다.");
        await this.manager.loadChunkLabels(this.manager.selectedChunkId);
      } catch (error) {
        console.error("라벨 제거 실패:", error);
        showError("라벨 제거 중 오류가 발생했습니다.");
      }
    };
  }

  bindEvents() {
    const q = (sel) => this.container.querySelector(sel);

    q('#kw-manage-chunk-search')?.addEventListener('keyup', () => this.manager.searchChunks());
    q('#kw-manage-btn-select-all-chunks')?.addEventListener('click', () => this.selectAllVisible());
    q('#kw-manage-btn-deselect-all-chunks')?.addEventListener('click', () => this.deselectAll());
    q('#kw-manage-btn-bulk-add-labels')?.addEventListener('click', () => this.batchAddLabelsToSelected());
    q('#kw-manage-btn-ai-suggest')?.addEventListener('click', () => this.manager.fetchAiLabelSuggestions());

    this.container.querySelectorAll('.label-filter-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const type = this.getAttribute('data-type') || '';
        document.querySelectorAll('.label-filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        window.labelManager.setLabelPickerFilter(type);
      });
    });
  }

  activate() {
    if (!this.isInitialized) return;
    this.manager.loadChunks();
    this.manager.loadLabelOptions();
  }

  deactivate() {}

  refresh() {
    this.manager.loadChunks();
    this.manager.loadLabelOptions();
  }

  onTabEvent(fromTab, event) {
    if (fromTab === "approval" && event.type === "chunks_approved") {
      this.refresh();
    }
    if (fromTab === "create" && (event.type === "chunks_created" || event.type === "chunks_quick_approved")) {
      this.refresh();
    }
  }

  afterDisplayChunks() {
    const items = this.container.querySelectorAll('.chunk-item-select');
    items.forEach(item => {
      const chunkIdMatch = item.getAttribute('onclick')?.match(/selectChunk\((\d+)\)/);
      const chunkId = chunkIdMatch ? parseInt(chunkIdMatch[1], 10) : NaN;
      if (isNaN(chunkId)) return;

      let checkbox = item.querySelector('.kw-bulk-check');
      if (!checkbox) {
        checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'kw-bulk-check';
        checkbox.style.marginRight = '12px';
        checkbox.addEventListener('change', (e) => {
          e.stopPropagation();
          this.toggleChunkSelection(chunkId);
        });
        item.prepend(checkbox);
      }
      checkbox.checked = this.selectedChunkIds.has(chunkId);
    });
    this.updateBulkToolbar();
  }

  toggleChunkSelection(chunkId) {
    if (this.selectedChunkIds.has(chunkId)) {
      this.selectedChunkIds.delete(chunkId);
    } else {
      this.selectedChunkIds.add(chunkId);
    }
    this.updateBulkToolbar();
    const item = this.container.querySelector(`.chunk-item-select[onclick*="selectChunk(${chunkId})"]`);
    if (item) {
      const checkbox = item.querySelector('.kw-bulk-check');
      if (checkbox) checkbox.checked = this.selectedChunkIds.has(chunkId);
    }
  }

  selectAllVisible() {
    const items = this.container.querySelectorAll('.chunk-item-select');
    items.forEach(item => {
      const chunkIdMatch = item.getAttribute('onclick')?.match(/selectChunk\((\d+)\)/);
      const chunkId = chunkIdMatch ? parseInt(chunkIdMatch[1], 10) : NaN;
      if (!isNaN(chunkId)) this.selectedChunkIds.add(chunkId);
    });
    this.afterDisplayChunks();
  }

  deselectAll() {
    this.selectedChunkIds.clear();
    this.afterDisplayChunks();
  }

  updateBulkToolbar() {
    const toolbar = this.container.querySelector('#kw-manage-bulk-toolbar');
    const countEl = this.container.querySelector('#kw-manage-selected-count');
    const count = this.selectedChunkIds.size;

    if (toolbar) toolbar.style.display = count > 0 ? 'flex' : 'none';
    if (countEl) countEl.textContent = `${count}개 선택`;
  }

  async batchAddLabelsToSelected() {
    const chunkIds = Array.from(this.selectedChunkIds);
    const labelIds = Array.from(this.manager.selectedLabelIdsForAdd);

    if (chunkIds.length === 0) {
      showError('청크를 1개 이상 선택하세요.');
      return;
    }
    if (labelIds.length === 0) {
      showError('추가할 라벨을 1개 이상 선택하세요.');
      return;
    }

    const statusEl = this.container.querySelector('#kw-manage-bulk-status');
    let totalSuccess = 0;
    let totalFail = 0;

    for (let i = 0; i < chunkIds.length; i++) {
      if (statusEl) statusEl.textContent = `${i + 1}/${chunkIds.length} 처리 중...`;
      const { success, fail } = await batchAddLabelsToChunkApi(chunkIds[i], labelIds);
      totalSuccess += success;
      totalFail += fail;
    }

    if (statusEl) statusEl.textContent = '';
    showSuccess(`${totalSuccess}개 라벨 추가 완료` + (totalFail > 0 ? `, ${totalFail}개 실패` : ''));
    this.manager.selectedLabelIdsForAdd.clear();
    this.selectedChunkIds.clear();
    this.refresh();
  }
}
