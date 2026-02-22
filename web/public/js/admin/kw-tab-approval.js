class ApprovalTab {
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

    this.manager = new ChunkApprovalManager({
      enablePagination: true,
      limit: 20,
      chunkListId: 'kw-approval-chunk-list',
      detailBodyId: 'kw-approval-detail-body',
      detailPlaceholderId: 'kw-approval-detail-placeholder',
      detailContentId: 'kw-approval-detail-content',
      onChunkChange: () => this.afterDisplayChunks(),
    });

    window.approvalManager = this.manager;
    this.overrideManagerMethods();
    this.bindEvents();
    this.isInitialized = true;
  }

  overrideManagerMethods() {
    const originalApprove = this.manager.approveChunk.bind(this.manager);
    const originalReject = this.manager.rejectChunk.bind(this.manager);
    const originalBatchApprove = this.manager.batchApproveAll.bind(this.manager);

    this.manager.approveChunk = async (chunkId) => {
      try {
        await approveChunkApi(chunkId);
        showSuccess("청크가 승인되었습니다.");
        await this.manager.loadPendingChunks();
      } catch (error) {
        console.error("청크 승인 실패:", error);
        showError(error.message || "청크 승인 중 오류가 발생했습니다.");
      }
    };

    this.manager.rejectChunk = async (chunkId) => {
      try {
        await rejectChunkApi(chunkId, null);
        showSuccess("청크가 거절되었습니다.");
        await this.manager.loadPendingChunks();
      } catch (error) {
        console.error("청크 거절 실패:", error);
        showError(error.message || "청크 거절 중 오류가 발생했습니다.");
      }
    };

    this.manager.batchApproveAll = async () => {
      const draftIds = this.manager.pendingChunks.filter((c) => (c.status || "") === "draft").map((c) => c.id);
      if (draftIds.length === 0) {
        showError("승인할 대기 중 청크가 없습니다.");
        return;
      }
      try {
        const data = await batchApproveChunksApi(draftIds);
        showSuccess(data.message || draftIds.length + "개 청크가 승인되었습니다.");
        await this.manager.loadPendingChunks();
      } catch (error) {
        console.error("전체 승인 실패:", error);
        showError(error.message || "전체 승인 중 오류가 발생했습니다.");
      }
    };
  }

  bindEvents() {
    const q = (sel) => this.container.querySelector(sel);

    this.container.querySelectorAll('.status-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const status = btn.getAttribute('data-status');
        this.manager.filterByStatus(status);
        this.selectedChunkIds.clear();
        this.updateBulkToolbar();
      });
    });

    q('#kw-approval-btn-select-all')?.addEventListener('click', () => this.selectAllVisible());
    q('#kw-approval-btn-deselect-all')?.addEventListener('click', () => this.deselectAll());
    q('#kw-approval-btn-approve-selected')?.addEventListener('click', () => this.batchApproveSelected());
    q('#kw-approval-btn-approve-all')?.addEventListener('click', () => this.batchApproveAllDraft());
    q('#kw-approval-btn-approve-and-label')?.addEventListener('click', () => this.approveAllAndGoManage());
  }

  activate() {
    if (!this.isInitialized) return;
    this.manager.loadPendingChunks();
  }

  deactivate() {}

  refresh() {
    this.manager.loadPendingChunks();
  }

  onTabEvent(fromTab, event) {
    if (fromTab === "create" && (event.type === "chunks_created" || event.type === "chunks_quick_approved")) {
      this.refresh();
    }
  }

  afterDisplayChunks() {
    const cards = this.container.querySelectorAll('.approval-chunk-card');
    cards.forEach(card => {
      const chunkId = parseInt(card.getAttribute('data-chunk-id'), 10);
      if (isNaN(chunkId)) return;

      let checkbox = card.querySelector('.kw-bulk-check');
      if (!checkbox) {
        checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'kw-bulk-check';
        checkbox.style.marginRight = '12px';
        checkbox.addEventListener('change', () => this.toggleChunkSelection(chunkId));
        const header = card.querySelector('.chunk-card-header');
        if (header) header.prepend(checkbox);
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
    const card = this.container.querySelector(`.approval-chunk-card[data-chunk-id="${chunkId}"]`);
    if (card) {
      const checkbox = card.querySelector('.kw-bulk-check');
      if (checkbox) checkbox.checked = this.selectedChunkIds.has(chunkId);
    }
  }

  selectAllVisible() {
    const cards = this.container.querySelectorAll('.approval-chunk-card');
    cards.forEach(card => {
      const chunkId = parseInt(card.getAttribute('data-chunk-id'), 10);
      if (!isNaN(chunkId)) this.selectedChunkIds.add(chunkId);
    });
    this.afterDisplayChunks();
  }

  deselectAll() {
    this.selectedChunkIds.clear();
    this.afterDisplayChunks();
  }

  updateBulkToolbar() {
    const toolbar = this.container.querySelector('#kw-approval-bulk-toolbar');
    const countEl = this.container.querySelector('#kw-approval-selected-count');
    const count = this.selectedChunkIds.size;

    if (toolbar) toolbar.style.display = count > 0 ? 'flex' : 'none';
    if (countEl) countEl.textContent = `${count}개 선택`;
  }

  async batchApproveSelected() {
    const ids = Array.from(this.selectedChunkIds);
    if (ids.length === 0) {
      showError('승인할 청크를 선택하세요.');
      return;
    }

    try {
      await batchApproveChunksApi(ids);
      showSuccess(`${ids.length}개 청크가 승인되었습니다.`);
      this.selectedChunkIds.clear();
      await this.manager.loadPendingChunks();
    } catch (e) {
      showError(e.message || '일괄 승인 중 오류');
    }
  }

  async batchApproveAllDraft() {
    const draftIds = this.manager.pendingChunks.filter(c => (c.status || '') === 'draft').map(c => c.id);
    if (draftIds.length === 0) {
      showError('승인할 대기 중 청크가 없습니다.');
      return;
    }

    try {
      await batchApproveChunksApi(draftIds);
      showSuccess(`${draftIds.length}개 청크가 승인되었습니다.`);
      await this.manager.loadPendingChunks();
    } catch (e) {
      showError(e.message || '전체 승인 중 오류');
    }
  }

  async approveAllAndGoManage() {
    const draftIds = this.manager.pendingChunks.filter(c => (c.status || '') === 'draft').map(c => c.id);
    if (draftIds.length === 0) {
      showError('승인할 대기 중 청크가 없습니다.');
      return;
    }

    try {
      await batchApproveChunksApi(draftIds);
      showSuccess(`${draftIds.length}개 청크가 승인되었습니다. 관리 탭으로 이동합니다.`);
      this.workflow.notifyTabChange('approval', { type: 'chunks_approved', count: draftIds.length });
      this.workflow.switchTab('manage');
    } catch (e) {
      showError(e.message || '전체 승인 중 오류');
    }
  }
}
