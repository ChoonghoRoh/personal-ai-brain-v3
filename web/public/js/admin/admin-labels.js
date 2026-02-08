// 라벨 관리자 인스턴스
let labelManager;

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializeAdminPage({
    title: "🏷️ 라벨 관리",
    subtitle: "라벨 생성 및 관리",
    currentPath: "/admin/labels",
  });

  // 라벨 관리자 초기화 (라벨 목록 페이징 활성화, 청크 UI 없음)
  labelManager = new LabelManager({
    enablePagination: true,
    enableLabelsPagination: true,
    labelsInitialLimit: 20,
    onLabelChange: () => {},
    onChunkChange: () => {},
  });

  window.labelManager = labelManager;

  labelManager.loadLabels();

  // 라벨 목록 필터: 조회 버튼
  const filterApply = document.getElementById("labels-filter-apply");
  if (filterApply) {
    filterApply.addEventListener("click", () => labelManager.loadLabels(1));
  }
  // 이름 입력창에서 Enter 시 조회
  const filterName = document.getElementById("labels-filter-name");
  if (filterName) {
    filterName.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        labelManager.loadLabels(1);
      }
    });
  }
  // 타입 변경 시 즉시 조회 (선택: 변경 시마다 reload)
  const filterType = document.getElementById("labels-filter-type");
  if (filterType) {
    filterType.addEventListener("change", () => labelManager.loadLabels(1));
  }
});

// 전역 함수 래퍼 (하위 호환성)
function loadLabels() {
  if (labelManager) labelManager.loadLabels();
}

function displayLabels() {
  if (labelManager) labelManager.displayLabels();
}

function createLabel(event) {
  if (labelManager) labelManager.createLabel(event);
}

function deleteLabel(labelId) {
  if (labelManager) labelManager.deleteLabel(labelId);
}
function updateLabelSelect() {
  if (labelManager) labelManager.updateLabelSelect();
}

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

function loadChunkLabels(chunkId) {
  if (labelManager) labelManager.loadChunkLabels(chunkId);
}

function addLabelToChunk() {
  if (labelManager) labelManager.addLabelToChunk();
}

function removeLabelFromChunk(labelId) {
  if (labelManager) labelManager.removeLabelFromChunk(labelId);
}

