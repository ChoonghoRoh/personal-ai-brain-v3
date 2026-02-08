/**
 * 청크 라벨 관리 페이지 (/admin/chunk-labels) 초기화
 */
let labelManager;

document.addEventListener("DOMContentLoaded", function () {
  window.ADMIN_MESSAGES_PERSIST = true;
  initializeAdminPage({
    title: "📝 청크 관리",
    subtitle: "청크별 라벨 추가·제거",
    currentPath: "/admin/chunk-labels",
  });

  labelManager = new LabelManager({
    enablePagination: true,
    enableLabelsPagination: false,
    chunkContentId: "chunk-content-body",
    chunkPaginationHideWhenEmpty: false,
    labelPickerListId: "label-picker-list",
    aiSuggestionsContainerId: "ai-label-suggestions",
    aiSuggestStatusId: "ai-label-suggest-status",
    aiSuggestBtnId: "btn-ai-label-suggest",
    onLabelChange: () => {},
    onChunkChange: () => {},
  });

  window.labelManager = labelManager;

  labelManager.loadChunks();
  labelManager.loadLabelOptions();

  // AI 키워드·라벨 추천 버튼
  const btnAiSuggest = document.getElementById("btn-ai-label-suggest");
  if (btnAiSuggest) {
    btnAiSuggest.addEventListener("click", () => labelManager.fetchAiLabelSuggestions());
  }

  // 라벨 분류 필터 버튼
  document.querySelectorAll(".label-filter-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const type = this.getAttribute("data-type") || "";
      document.querySelectorAll(".label-filter-btn").forEach((b) => b.classList.remove("active"));
      this.classList.add("active");
      labelManager.setLabelPickerFilter(type);
    });
  });
});

function loadChunks() {
  if (labelManager) labelManager.loadChunks();
}
function displayChunks(chunksToDisplay) {
  if (labelManager) labelManager.displayChunks(chunksToDisplay);
}
function searchChunks() {
  if (labelManager) labelManager.searchChunks();
}
function selectChunk(chunkId) {
  if (labelManager) labelManager.selectChunk(chunkId);
}
function addLabelToChunk() {
  if (labelManager) labelManager.addLabelToChunk();
}
function addSelectedLabelsToChunk() {
  if (labelManager) labelManager.addSelectedLabelsToChunk();
}
function selectAllLabelsInPicker() {
  if (labelManager) labelManager.selectAllLabelsInPicker();
}
function selectSimilarLabelsInPicker() {
  if (labelManager) labelManager.selectSimilarLabelsInPicker();
}
function deselectAllLabelsInPicker() {
  if (labelManager) labelManager.deselectAllLabelsInPicker();
}
function removeLabelFromChunk(labelId) {
  if (labelManager) labelManager.removeLabelFromChunk(labelId);
}
