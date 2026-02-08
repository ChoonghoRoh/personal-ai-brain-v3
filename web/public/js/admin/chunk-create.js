/**
 * 청크 생성 페이지 (/admin/chunk-create)
 * 문서 스토리지(brain/, docs/) 기준: 1. 파일 선택 → 2. 분할·선택 → 3. 등록
 * 레이아웃: 상단 탭(1,2,3) + 하단 단계별 좌/우 영역
 */
(function () {
  let tempChunks = [];
  let currentStep = 1;
  let selectedFilePath = "";
  let selectedFileName = "";
  let allFileItems = [];
  let filePage = 1;
  const FILE_PAGE_SIZE = 15;

  function getEl(id) {
    return document.getElementById(id);
  }

  function encodePath(path) {
    return path.split("/").map(encodeURIComponent).join("/");
  }

  async function loadStorageFileList() {
    const listEl = getEl("storage-file-list");
    if (!listEl) return;
    try {
      const res = await fetch("/api/documents");
      const list = await res.json();
      allFileItems = Array.isArray(list) ? list : [];
      filePage = 1;
      if (allFileItems.length === 0) {
        listEl.innerHTML = '<div class="chunk-create-empty">brain/, docs/에 .md 파일이 없습니다.</div>';
        hideFilePagination();
        return;
      }
      renderFileListPage();
      showFilePagination();
    } catch (e) {
      console.warn("스토리지 파일 목록 로드 실패:", e);
      listEl.innerHTML = '<div class="chunk-create-empty">파일 목록을 불러올 수 없습니다.</div>';
      hideFilePagination();
    }
  }

  function getFilePageCount() {
    return Math.max(1, Math.ceil(allFileItems.length / FILE_PAGE_SIZE));
  }

  function getFilePageItems() {
    const start = (filePage - 1) * FILE_PAGE_SIZE;
    return allFileItems.slice(start, start + FILE_PAGE_SIZE);
  }

  function renderFileListPage() {
    const listEl = getEl("storage-file-list");
    if (!listEl) return;
    const items = getFilePageItems();
    const totalPages = getFilePageCount();

    listEl.innerHTML = items
      .map(
        (f) => {
          const path = f.file_path || f.id || "";
          const name = f.name || f.file_path || "";
          const isSelected = path === selectedFilePath;
          return `
        <button type="button" class="chunk-create-file-item ${isSelected ? "selected" : ""}" data-path="${escapeHtml(path)}" data-name="${escapeHtml(name)}">
          ${escapeHtml(f.file_path || f.name || "")}
        </button>
      `;
        }
      )
      .join("");

    listEl.querySelectorAll(".chunk-create-file-item").forEach((btn) => {
      btn.addEventListener("click", function () {
        const path = this.getAttribute("data-path");
        const name = this.getAttribute("data-name");
        if (path) loadFileContent(path, name);
      });
    });

    const infoEl = getEl("file-page-info");
    if (infoEl) infoEl.textContent = filePage + " / " + totalPages;

    const prevBtn = getEl("btn-file-prev");
    const nextBtn = getEl("btn-file-next");
    if (prevBtn) prevBtn.disabled = filePage <= 1;
    if (nextBtn) nextBtn.disabled = filePage >= totalPages;
  }

  function showFilePagination() {
    const paginationEl = getEl("file-list-pagination");
    if (paginationEl) paginationEl.style.display = allFileItems.length > FILE_PAGE_SIZE ? "flex" : "none";
  }

  function hideFilePagination() {
    const paginationEl = getEl("file-list-pagination");
    if (paginationEl) paginationEl.style.display = "none";
  }

  async function loadFileContent(filePath, fileName) {
    selectedFilePath = filePath;
    selectedFileName = fileName || filePath.split("/").pop() || "note.md";
    const sourceEl = getEl("chunk-source-text");
    const contentGroup = getEl("source-content-group");
    const emptyEl = getEl("step1-empty");
    if (!contentGroup) return;
    try {
      const url = "/api/documents/" + encodePath(filePath);
      const res = await fetch(url);
      if (!res.ok) throw new Error("파일을 불러올 수 없습니다.");
      const data = await res.json();
      const content = data.content != null ? data.content : "";
      if (sourceEl) sourceEl.textContent = content;
      contentGroup.style.display = "block";
      if (emptyEl) emptyEl.style.display = "none";
      if (typeof showSuccess === "function") showSuccess("파일 내용을 불러왔습니다. 분할 방식을 선택하고 자동 생성을 누르세요.", { persist: true });
      renderFileListPage();
    } catch (e) {
      if (typeof showError === "function") showError(e.message || "파일 내용을 불러오는 데 실패했습니다.");
    }
  }

  function showStep(step) {
    currentStep = step;
    [1, 2, 3].forEach((n) => {
      const panel = getEl("step" + n + "-panel");
      if (panel) panel.style.display = n === step ? "block" : "none";
      if (panel) panel.classList.toggle("active", n === step);
    });
    document.querySelectorAll(".chunk-create-tab").forEach((tab) => {
      const n = parseInt(tab.getAttribute("data-step"), 10);
      tab.classList.toggle("active", n === step);
      tab.setAttribute("aria-selected", n === step ? "true" : "false");
    });
  }

  function splitByMode(text, mode) {
    const t = (text || "").trim();
    if (!t) return [];
    if (mode === "line") {
      return t.split(/\n/).map((s) => s.trim()).filter(Boolean);
    }
    if (mode === "heading") {
      const parts = t.split(/(?=^#{1,6}\s)/m);
      return parts.map((s) => s.trim()).filter(Boolean);
    }
    return t.split(/\n\n+/).map((s) => s.trim()).filter(Boolean);
  }

  function runSplit() {
    const sourceEl = getEl("chunk-source-text");
    const modeEl = getEl("split-mode");
    const text = sourceEl ? (sourceEl.textContent || "") : "";
    const mode = modeEl ? modeEl.value : "paragraph";

    const parts = splitByMode(text, mode);
    if (parts.length === 0) {
      if (typeof showError === "function") showError("입력된 텍스트가 없거나 분할 결과가 없습니다.");
      return;
    }

    tempChunks = parts.map((content, i) => ({
      index: i,
      content: content,
      selected: true,
    }));
    showStep(2);
    renderTempList();
    updateSelectedCount();
  }

  function renderTempList() {
    const listEl = getEl("temp-chunk-list");
    if (!listEl) return;

    if (tempChunks.length === 0) {
      listEl.innerHTML = '<div class="chunk-create-empty">청크가 없습니다. 1단계에서 스토리지 파일을 선택하고 자동 생성을 실행하세요.</div>';
      return;
    }

    listEl.innerHTML = tempChunks
      .map(
        (c, i) => `
      <label class="chunk-create-temp-item">
        <input type="checkbox" class="chunk-temp-check" data-index="${i}" ${c.selected ? "checked" : ""} />
        <span class="chunk-temp-preview">${escapeHtml((c.content || "").substring(0, 200))}${(c.content || "").length > 200 ? "…" : ""}</span>
      </label>
    `
      )
      .join("");

    listEl.querySelectorAll(".chunk-temp-check").forEach((cb) => {
      cb.addEventListener("change", function () {
        const idx = parseInt(this.getAttribute("data-index"), 10);
        if (!isNaN(idx) && tempChunks[idx]) tempChunks[idx].selected = this.checked;
        updateSelectedCount();
      });
    });
  }

  function updateSelectedCount() {
    const count = tempChunks.filter((c) => c.selected).length;
    const el = getEl("temp-selected-count");
    if (el) el.textContent = count + "개 선택";
  }

  function selectAllTemp() {
    tempChunks.forEach((c) => (c.selected = true));
    renderTempList();
    updateSelectedCount();
  }

  function selectNoneTemp() {
    tempChunks.forEach((c) => (c.selected = false));
    renderTempList();
    updateSelectedCount();
  }

  function goBackToStep1() {
    showStep(1);
  }

  function goBackToStep2() {
    showStep(2);
  }

  function mergeSelectedChunks() {
    const indices = tempChunks
      .map((c, i) => (c.selected ? i : -1))
      .filter((i) => i >= 0)
      .sort((a, b) => a - b);
    if (indices.length < 2) {
      if (typeof showError === "function") showError("병합하려면 2개 이상의 청크를 선택하세요.");
      return;
    }
    const contents = indices.map((i) => (tempChunks[i].content || "").trim()).filter(Boolean);
    const mergedContent = contents.join("\n\n");
    const newChunk = { index: 0, content: mergedContent, selected: true };
    const newList = [];
    for (let i = 0; i < tempChunks.length; i++) {
      if (indices.includes(i)) {
        if (i === indices[0]) newList.push(newChunk);
        continue;
      }
      newList.push({ index: newList.length, content: tempChunks[i].content, selected: tempChunks[i].selected });
    }
    tempChunks = newList.map((c, i) => ({ ...c, index: i }));
    if (typeof showSuccess === "function") showSuccess("선택한 " + indices.length + "개 청크를 1개로 병합했습니다.");
    renderTempList();
    updateSelectedCount();
  }

  function mergeByHeadingLevel(level) {
    const lv = parseInt(level, 10);
    if (!lv || lv < 1 || lv > 3) {
      if (typeof showError === "function") showError("헤딩 레벨(1~3)을 선택하세요.");
      return;
    }
    const prefix = "#".repeat(lv);
    const headingRe = new RegExp("^" + prefix + "\\s");
    const groups = [];
    let current = [];
    for (let i = 0; i < tempChunks.length; i++) {
      const content = tempChunks[i].content || "";
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
    tempChunks = merged.map((content, i) => ({ index: i, content: content, selected: true }));
    if (typeof showSuccess === "function") showSuccess('"' + prefix + '" 기준으로 ' + groups.length + "개 그룹으로 병합했습니다.");
    renderTempList();
    updateSelectedCount();
  }

  function goToStep3() {
    const selected = tempChunks.filter((c) => c.selected);
    if (selected.length === 0) {
      if (typeof showError === "function") showError("등록할 청크를 1개 이상 선택하세요.");
      return;
    }
    showStep(3);
    if (selectedFilePath) {
      const pathEl = getEl("new-doc-file-path");
      const nameEl = getEl("new-doc-file-name");
      if (pathEl) pathEl.value = selectedFilePath;
      if (nameEl) nameEl.value = selectedFileName;
    }
    const useExisting = getEl("doc-target-existing") && getEl("doc-target-existing").checked;
    if (useExisting) loadExistingDocuments();
  }

  function toggleDocTarget() {
    const isNew = getEl("doc-target-new") && getEl("doc-target-new").checked;
    const newFields = getEl("doc-target-new-fields");
    const existingFields = getEl("doc-target-existing-fields");
    if (newFields) newFields.style.display = isNew ? "block" : "none";
    if (existingFields) existingFields.style.display = isNew ? "none" : "block";
    if (!isNew) loadExistingDocuments();
  }

  async function loadExistingDocuments() {
    const select = getEl("existing-doc-select");
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

  async function registerSelected() {
    const selected = tempChunks.filter((c) => c.selected);
    if (selected.length === 0) {
      if (typeof showError === "function") showError("등록할 청크를 선택하세요.");
      return;
    }

    const useExisting = getEl("doc-target-existing") && getEl("doc-target-existing").checked;
    let documentId = null;

    if (useExisting) {
      const select = getEl("existing-doc-select");
      documentId = select ? parseInt(select.value, 10) : NaN;
      if (!documentId) {
        if (typeof showError === "function") showError("기존 문서를 선택하세요.");
        return;
      }
    } else {
      const filePath = (getEl("new-doc-file-path") && getEl("new-doc-file-path").value) || "";
      const fileName = (getEl("new-doc-file-name") && getEl("new-doc-file-name").value) || "";
      if (!filePath.trim() || !fileName.trim()) {
        if (typeof showError === "function") showError("새 문서의 파일 경로와 파일 이름을 입력하세요.");
        return;
      }
      try {
        const res = await fetch("/api/knowledge/documents", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            file_path: filePath.trim(),
            file_name: fileName.trim(),
            file_type: "md",
            size: 0,
            project_id: null,
          }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "문서 생성 실패");
        }
        const data = await res.json();
        documentId = data.document && data.document.id;
        if (!documentId) throw new Error("문서 ID를 받지 못했습니다.");
      } catch (e) {
        if (typeof showError === "function") showError(e.message || "문서 생성 중 오류가 발생했습니다.");
        return;
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

    let success = 0;
    for (let i = 0; i < selected.length; i++) {
      const chunk = selected[i];
      const chunkIndex = startIndex + i;
      try {
        const res = await fetch("/api/knowledge/chunks?include_suggestions=false", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            document_id: documentId,
            content: chunk.content,
            chunk_index: chunkIndex,
            title: null,
            title_source: "manual",
          }),
        });
        if (res.ok) success++;
      } catch (_) {}
    }

    if (typeof showSuccess === "function") showSuccess("청크 " + success + "개를 등록했습니다.");
    if (success === selected.length) {
      tempChunks = tempChunks.filter((c) => !c.selected);
      selectedFilePath = "";
      selectedFileName = "";
      showStep(1);
      const textarea = getEl("chunk-source-text");
      if (textarea) textarea.value = "";
      const contentGroup = getEl("source-content-group");
      if (contentGroup) contentGroup.style.display = "none";
      const emptyEl = getEl("step1-empty");
      if (emptyEl) emptyEl.style.display = "block";
      renderFileListPage();
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    initializeAdminPage({
      title: "➕ 청크 생성",
      subtitle: "문서 스토리지(brain/, docs/) → 분할 → 등록",
      currentPath: "/admin/chunk-create",
    });

    loadStorageFileList();

    document.querySelectorAll(".chunk-create-tab").forEach((tab) => {
      tab.addEventListener("click", function () {
        const step = parseInt(this.getAttribute("data-step"), 10);
        if (!isNaN(step)) showStep(step);
      });
    });

    getEl("btn-file-prev") && getEl("btn-file-prev").addEventListener("click", function () {
      if (filePage > 1) {
        filePage--;
        renderFileListPage();
      }
    });
    getEl("btn-file-next") && getEl("btn-file-next").addEventListener("click", function () {
      if (filePage < getFilePageCount()) {
        filePage++;
        renderFileListPage();
      }
    });

    getEl("btn-run-split").addEventListener("click", runSplit);
    getEl("btn-select-all").addEventListener("click", selectAllTemp);
    getEl("btn-select-none").addEventListener("click", selectNoneTemp);
    getEl("btn-merge-selected").addEventListener("click", mergeSelectedChunks);
    getEl("btn-merge-by-heading").addEventListener("click", function () {
      const level = getEl("merge-heading-level") && getEl("merge-heading-level").value;
      mergeByHeadingLevel(level);
    });
    getEl("btn-back-to-step1").addEventListener("click", goBackToStep1);
    getEl("btn-back-to-step2").addEventListener("click", goBackToStep2);
    getEl("btn-go-step3").addEventListener("click", goToStep3);
    getEl("btn-register-chunks").addEventListener("click", registerSelected);

    const newRadio = getEl("doc-target-new");
    const existingRadio = getEl("doc-target-existing");
    if (newRadio) newRadio.addEventListener("change", toggleDocTarget);
    if (existingRadio) existingRadio.addEventListener("change", toggleDocTarget);

    toggleDocTarget();
  });
})();
