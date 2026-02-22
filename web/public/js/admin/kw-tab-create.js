class CreateTab {
  constructor() {
    this.container = null;
    this.workflow = null;
    this.isInitialized = false;
    this.tempChunks = [];
    this.currentStep = 1;
    this.selectedFilePath = "";
    this.selectedFileName = "";
    this.allFileItems = [];
    this.filePage = 1;
    this.FILE_PAGE_SIZE = 15;
  }

  init(container, workflow) {
    this.container = container;
    this.workflow = workflow;
    this.bindEvents();
    this.isInitialized = true;
  }

  bindEvents() {
    const q = (sel) => this.container.querySelector(sel);

    q("#kw-create-btn-file-prev")?.addEventListener("click", () => this.prevFilePage());
    q("#kw-create-btn-file-next")?.addEventListener("click", () => this.nextFilePage());
    q("#kw-create-btn-run-split")?.addEventListener("click", () => this.runSplit());
    q("#kw-create-btn-select-all")?.addEventListener("click", () => this.selectAllTemp());
    q("#kw-create-btn-select-none")?.addEventListener("click", () => this.selectNoneTemp());
    q("#kw-create-btn-merge-selected")?.addEventListener("click", () => this.mergeSelectedChunks());
    q("#kw-create-btn-merge-by-heading")?.addEventListener("click", () => this.mergeByHeading());
    q("#kw-create-btn-back-to-step1")?.addEventListener("click", () => this.showStep(1));
    q("#kw-create-btn-back-to-step2")?.addEventListener("click", () => this.showStep(2));
    q("#kw-create-btn-go-step3")?.addEventListener("click", () => this.goToStep3());
    q("#kw-create-btn-register")?.addEventListener("click", () => this.registerSelected());
    q("#kw-create-btn-quick-approve")?.addEventListener("click", () => this.quickApproveAndRegister());

    q("#kw-create-doc-target-new")?.addEventListener("change", () => this.toggleDocTarget());
    q("#kw-create-doc-target-existing")?.addEventListener("change", () => this.toggleDocTarget());
  }

  activate() {
    if (!this.isInitialized) return;
    this.loadStorageFileList();
  }

  deactivate() {}
  refresh() { this.loadStorageFileList(); }
  onTabEvent(fromTab, event) {}

  async loadStorageFileList() {
    const listEl = this.container.querySelector("#kw-create-file-list");
    if (!listEl) return;
    try {
      const res = await fetch("/api/documents");
      const list = await res.json();
      this.allFileItems = Array.isArray(list) ? list : [];
      this.filePage = 1;
      if (this.allFileItems.length === 0) {
        listEl.innerHTML = '<div class="chunk-create-empty">brain/, docs/에 .md 파일이 없습니다.</div>';
        this.hideFilePagination();
        return;
      }
      this.renderFileListPage();
      this.showFilePagination();
    } catch (e) {
      console.warn("스토리지 파일 목록 로드 실패:", e);
      listEl.innerHTML = '<div class="chunk-create-empty">파일 목록을 불러올 수 없습니다.</div>';
      this.hideFilePagination();
    }
  }

  getFilePageCount() {
    return Math.max(1, Math.ceil(this.allFileItems.length / this.FILE_PAGE_SIZE));
  }

  getFilePageItems() {
    const start = (this.filePage - 1) * this.FILE_PAGE_SIZE;
    return this.allFileItems.slice(start, start + this.FILE_PAGE_SIZE);
  }

  renderFileListPage() {
    const listEl = this.container.querySelector("#kw-create-file-list");
    if (!listEl) return;
    const items = this.getFilePageItems();
    const totalPages = this.getFilePageCount();

    listEl.innerHTML = items.map((f) => {
      const path = f.file_path || f.id || "";
      const name = f.name || f.file_path || "";
      const isSelected = path === this.selectedFilePath;
      return `<button type="button" class="chunk-create-file-item ${isSelected ? "selected" : ""}" data-path="${escapeHtml(path)}" data-name="${escapeHtml(name)}">${escapeHtml(f.file_path || f.name || "")}</button>`;
    }).join("");

    listEl.querySelectorAll(".chunk-create-file-item").forEach((btn) => {
      btn.addEventListener("click", () => {
        const path = btn.getAttribute("data-path");
        const name = btn.getAttribute("data-name");
        if (path) this.loadFileContent(path, name);
      });
    });

    const infoEl = this.container.querySelector("#kw-create-file-page-info");
    if (infoEl) infoEl.textContent = this.filePage + " / " + totalPages;

    const prevBtn = this.container.querySelector("#kw-create-btn-file-prev");
    const nextBtn = this.container.querySelector("#kw-create-btn-file-next");
    if (prevBtn) prevBtn.disabled = this.filePage <= 1;
    if (nextBtn) nextBtn.disabled = this.filePage >= totalPages;
  }

  showFilePagination() {
    const el = this.container.querySelector("#kw-create-file-list-pagination");
    if (el) el.style.display = this.allFileItems.length > this.FILE_PAGE_SIZE ? "flex" : "none";
  }

  hideFilePagination() {
    const el = this.container.querySelector("#kw-create-file-list-pagination");
    if (el) el.style.display = "none";
  }

  prevFilePage() {
    if (this.filePage > 1) {
      this.filePage--;
      this.renderFileListPage();
    }
  }

  nextFilePage() {
    if (this.filePage < this.getFilePageCount()) {
      this.filePage++;
      this.renderFileListPage();
    }
  }

  encodePath(path) {
    return path.split("/").map(encodeURIComponent).join("/");
  }

  async loadFileContent(filePath, fileName) {
    this.selectedFilePath = filePath;
    this.selectedFileName = fileName || filePath.split("/").pop() || "note.md";
    const sourceEl = this.container.querySelector("#kw-create-source-text");
    const contentGroup = this.container.querySelector("#kw-create-source-content-group");
    const emptyEl = this.container.querySelector("#kw-create-step1-empty");
    if (!contentGroup) return;
    try {
      const url = "/api/documents/" + this.encodePath(filePath);
      const res = await fetch(url);
      if (!res.ok) throw new Error("파일을 불러올 수 없습니다.");
      const data = await res.json();
      const content = data.content != null ? data.content : "";
      if (sourceEl) sourceEl.textContent = content;
      contentGroup.style.display = "block";
      if (emptyEl) emptyEl.style.display = "none";
      showSuccess("파일 내용을 불러왔습니다. 분할 방식을 선택하고 자동 생성을 누르세요.", { persist: true });
      this.renderFileListPage();
    } catch (e) {
      showError(e.message || "파일 내용을 불러오는 데 실패했습니다.");
    }
  }

  showStep(step) {
    this.currentStep = step;
    [1, 2, 3].forEach((n) => {
      const panel = this.container.querySelector(`#kw-create-step${n}-panel`);
      if (panel) {
        panel.style.display = n === step ? "block" : "none";
        panel.classList.toggle("active", n === step);
      }
    });
    this.container.querySelectorAll(".chunk-create-tab").forEach((tab) => {
      const n = parseInt(tab.getAttribute("data-step"), 10);
      tab.classList.toggle("active", n === step);
      tab.setAttribute("aria-selected", n === step ? "true" : "false");
    });
  }

  splitByMode(text, mode) {
    const t = (text || "").trim();
    if (!t) return [];
    if (mode === "line") return t.split(/\n/).map((s) => s.trim()).filter(Boolean);
    if (mode === "heading") return t.split(/(?=^#{1,6}\s)/m).map((s) => s.trim()).filter(Boolean);
    return t.split(/\n\n+/).map((s) => s.trim()).filter(Boolean);
  }

  runSplit() {
    const sourceEl = this.container.querySelector("#kw-create-source-text");
    const modeEl = this.container.querySelector("#kw-create-split-mode");
    const text = sourceEl ? sourceEl.textContent || "" : "";
    const mode = modeEl ? modeEl.value : "paragraph";

    const parts = this.splitByMode(text, mode);
    if (parts.length === 0) {
      showError("입력된 텍스트가 없거나 분할 결과가 없습니다.");
      return;
    }

    this.tempChunks = parts.map((content, i) => ({ index: i, content, selected: true }));
    this.showStep(2);
    this.renderTempList();
    this.updateSelectedCount();
  }

  renderTempList() {
    const listEl = this.container.querySelector("#kw-create-temp-chunk-list");
    if (!listEl) return;

    if (this.tempChunks.length === 0) {
      listEl.innerHTML = '<div class="chunk-create-empty">청크가 없습니다. 1단계에서 스토리지 파일을 선택하고 자동 생성을 실행하세요.</div>';
      return;
    }

    listEl.innerHTML = this.tempChunks.map((c, i) => `
      <label class="chunk-create-temp-item">
        <input type="checkbox" class="chunk-temp-check" data-index="${i}" ${c.selected ? "checked" : ""} />
        <span class="chunk-temp-preview">${escapeHtml((c.content || "").substring(0, 200))}${(c.content || "").length > 200 ? "…" : ""}</span>
      </label>
    `).join("");

    listEl.querySelectorAll(".chunk-temp-check").forEach((cb) => {
      cb.addEventListener("change", () => {
        const idx = parseInt(cb.getAttribute("data-index"), 10);
        if (!isNaN(idx) && this.tempChunks[idx]) this.tempChunks[idx].selected = cb.checked;
        this.updateSelectedCount();
      });
    });
  }

  updateSelectedCount() {
    const count = this.tempChunks.filter((c) => c.selected).length;
    const el = this.container.querySelector("#kw-create-temp-selected-count");
    if (el) el.textContent = count + "개 선택";
  }

  selectAllTemp() {
    this.tempChunks.forEach((c) => (c.selected = true));
    this.renderTempList();
    this.updateSelectedCount();
  }

  selectNoneTemp() {
    this.tempChunks.forEach((c) => (c.selected = false));
    this.renderTempList();
    this.updateSelectedCount();
  }

  mergeSelectedChunks() {
    const indices = this.tempChunks.map((c, i) => (c.selected ? i : -1)).filter((i) => i >= 0).sort((a, b) => a - b);
    if (indices.length < 2) {
      showError("병합하려면 2개 이상의 청크를 선택하세요.");
      return;
    }
    const contents = indices.map((i) => (this.tempChunks[i].content || "").trim()).filter(Boolean);
    const mergedContent = contents.join("\n\n");
    const newChunk = { index: 0, content: mergedContent, selected: true };
    const newList = [];
    for (let i = 0; i < this.tempChunks.length; i++) {
      if (indices.includes(i)) {
        if (i === indices[0]) newList.push(newChunk);
        continue;
      }
      newList.push({ index: newList.length, content: this.tempChunks[i].content, selected: this.tempChunks[i].selected });
    }
    this.tempChunks = newList.map((c, i) => ({ ...c, index: i }));
    showSuccess("선택한 " + indices.length + "개 청크를 1개로 병합했습니다.");
    this.renderTempList();
    this.updateSelectedCount();
  }

  mergeByHeading() {
    const levelEl = this.container.querySelector("#kw-create-merge-heading-level");
    const lv = parseInt(levelEl ? levelEl.value : "", 10);
    if (!lv || lv < 1 || lv > 3) {
      showError("헤딩 레벨(1~3)을 선택하세요.");
      return;
    }
    const prefix = "#".repeat(lv);
    const headingRe = new RegExp("^" + prefix + "\\s");
    const groups = [];
    let current = [];
    for (let i = 0; i < this.tempChunks.length; i++) {
      const content = this.tempChunks[i].content || "";
      const firstLine = (content.split("\n")[0] || "").trim();
      const isHeading = headingRe.test(firstLine);
      if (isHeading && current.length > 0) {
        groups.push(current);
        current = [];
      }
      current.push(content);
    }
    if (current.length > 0) groups.push(current);
    const merged = groups.map((contents) => contents.join("\n\n").trim()).filter(Boolean);
    this.tempChunks = merged.map((content, i) => ({ index: i, content, selected: true }));
    showSuccess('"' + prefix + '" 기준으로 ' + groups.length + "개 그룹으로 병합했습니다.");
    this.renderTempList();
    this.updateSelectedCount();
  }

  goToStep3() {
    const selected = this.tempChunks.filter((c) => c.selected);
    if (selected.length === 0) {
      showError("등록할 청크를 1개 이상 선택하세요.");
      return;
    }
    this.showStep(3);
    if (this.selectedFilePath) {
      const pathEl = this.container.querySelector("#kw-create-new-doc-file-path");
      const nameEl = this.container.querySelector("#kw-create-new-doc-file-name");
      if (pathEl) pathEl.value = this.selectedFilePath;
      if (nameEl) nameEl.value = this.selectedFileName;
    }
    const useExisting = this.container.querySelector("#kw-create-doc-target-existing")?.checked;
    if (useExisting) this.loadExistingDocuments();
  }

  toggleDocTarget() {
    const isNew = this.container.querySelector("#kw-create-doc-target-new")?.checked;
    const newFields = this.container.querySelector("#kw-create-doc-target-new-fields");
    const existingFields = this.container.querySelector("#kw-create-doc-target-existing-fields");
    if (newFields) newFields.style.display = isNew ? "block" : "none";
    if (existingFields) existingFields.style.display = isNew ? "none" : "block";
    if (!isNew) this.loadExistingDocuments();
  }

  async loadExistingDocuments() {
    const select = this.container.querySelector("#kw-create-existing-doc-select");
    if (!select) return;
    try {
      const res = await fetch("/api/knowledge/documents");
      const list = await res.json();
      const items = Array.isArray(list) ? list : list.items || [];
      select.innerHTML = '<option value="">문서를 선택하세요...</option>' + items.map((d) => `<option value="${d.id}">${escapeHtml(d.file_name || d.file_path || "문서 " + d.id)}</option>`).join("");
    } catch (e) {
      console.warn("문서 목록 로드 실패:", e);
      select.innerHTML = '<option value="">문서 목록을 불러올 수 없습니다.</option>';
    }
  }

  async registerSelected() {
    const createdIds = await this.registerChunksInternal();
    if (createdIds.length > 0) {
      this.workflow.notifyTabChange("create", { type: "chunks_created", ids: createdIds });
      this.workflow.switchTab("approval");
    }
  }

  async quickApproveAndRegister() {
    const createdIds = await this.registerChunksInternal();
    if (createdIds.length === 0) return;

    try {
      await batchApproveChunksApi(createdIds);
      showSuccess(`${createdIds.length}개 청크가 등록 + 승인되었습니다.`);
      this.workflow.notifyTabChange("create", { type: "chunks_quick_approved", ids: createdIds });
      this.workflow.switchTab("manage");
    } catch (e) {
      showError("등록은 완료, 승인 중 오류: " + (e.message || "알 수 없는 오류"));
    }
  }

  async registerChunksInternal() {
    const selected = this.tempChunks.filter((c) => c.selected);
    if (selected.length === 0) {
      showError("등록할 청크를 선택하세요.");
      return [];
    }

    const useExisting = this.container.querySelector("#kw-create-doc-target-existing")?.checked;
    let documentId = null;

    if (useExisting) {
      const select = this.container.querySelector("#kw-create-existing-doc-select");
      documentId = select ? parseInt(select.value, 10) : NaN;
      if (!documentId) {
        showError("기존 문서를 선택하세요.");
        return [];
      }
    } else {
      const filePath = this.container.querySelector("#kw-create-new-doc-file-path")?.value || "";
      const fileName = this.container.querySelector("#kw-create-new-doc-file-name")?.value || "";
      if (!filePath.trim() || !fileName.trim()) {
        showError("새 문서의 파일 경로와 파일 이름을 입력하세요.");
        return [];
      }
      try {
        const res = await fetch("/api/knowledge/documents", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ file_path: filePath.trim(), file_name: fileName.trim(), file_type: "md", size: 0, project_id: null }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "문서 생성 실패");
        }
        const data = await res.json();
        documentId = data.document && data.document.id;
        if (!documentId) throw new Error("문서 ID를 받지 못했습니다.");
      } catch (e) {
        showError(e.message || "문서 생성 중 오류가 발생했습니다.");
        return [];
      }
    }

    let startIndex = 0;
    if (useExisting && documentId) {
      try {
        const chunksRes = await fetch("/api/knowledge/chunks?document_id=" + documentId + "&limit=1000");
        const chunksData = await chunksRes.json();
        const chunks = Array.isArray(chunksData) ? chunksData : chunksData.items || chunksData.chunks || [];
        const maxIdx = chunks.length ? Math.max(...chunks.map((c) => c.chunk_index != null ? c.chunk_index : -1)) : -1;
        startIndex = maxIdx + 1;
      } catch (_) {}
    }

    const createdIds = [];
    for (let i = 0; i < selected.length; i++) {
      const chunk = selected[i];
      const chunkIndex = startIndex + i;
      try {
        const res = await fetch("/api/knowledge/chunks?include_suggestions=false", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ document_id: documentId, content: chunk.content, chunk_index: chunkIndex, title: null, title_source: "manual" }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.chunk && data.chunk.id) createdIds.push(data.chunk.id);
        }
      } catch (_) {}
    }

    showSuccess("청크 " + createdIds.length + "개를 등록했습니다.");
    if (createdIds.length === selected.length) {
      this.tempChunks = this.tempChunks.filter((c) => !c.selected);
      this.selectedFilePath = "";
      this.selectedFileName = "";
      this.showStep(1);
      const textarea = this.container.querySelector("#kw-create-source-text");
      if (textarea) textarea.textContent = "";
      const contentGroup = this.container.querySelector("#kw-create-source-content-group");
      if (contentGroup) contentGroup.style.display = "none";
      const emptyEl = this.container.querySelector("#kw-create-step1-empty");
      if (emptyEl) emptyEl.style.display = "block";
      this.renderFileListPage();
    }

    return createdIds;
  }
}
