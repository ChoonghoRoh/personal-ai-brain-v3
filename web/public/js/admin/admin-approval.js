// 청크 승인 관리자 인스턴스
let approvalManager;

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializeAdminPage({
    title: "✅ 청크 승인 센터",
    subtitle: "청크 승인 및 거절 관리",
    currentPath: "/admin/approval",
  });

  // 청크 승인 관리자 초기화 (페이징 활성화)
  approvalManager = new ChunkApprovalManager({
    enablePagination: true,
    limit: 20,
    onChunkChange: () => {
      // 청크 변경 시 추가 처리 (필요시)
    },
  });

  // 전역 함수로 노출 (하위 호환성)
  window.approvalManager = approvalManager;

  // 초기 데이터 로드
  approvalManager.loadPendingChunks();

  const btnApproveAll = document.getElementById("btn-approve-all");
  if (btnApproveAll) {
    btnApproveAll.addEventListener("click", function () {
      if (approvalManager) approvalManager.batchApproveAll();
    });
  }
});

// 전역 함수 래퍼 (하위 호환성)
async function filterByStatus(status) {
  if (approvalManager) await approvalManager.filterByStatus(status);
}

async function loadPendingChunks() {
  if (approvalManager) await approvalManager.loadPendingChunks();
}

function displayPendingChunks() {
  if (approvalManager) approvalManager.displayPendingChunks();
}

async function approveChunk(chunkId) {
  if (approvalManager) await approvalManager.approveChunk(chunkId);
}

async function approveAllChunks() {
  if (approvalManager) await approvalManager.batchApproveAll();
}

async function rejectChunk(chunkId) {
  if (approvalManager) await approvalManager.rejectChunk(chunkId);
}

async function showChunkDetail(chunkId) {
  if (approvalManager) await approvalManager.showChunkDetail(chunkId);
}

function closeChunkDetail() {
  if (approvalManager) approvalManager.closeChunkDetail();
}

function clearChunkDetail() {
  if (approvalManager) approvalManager.clearChunkDetail();
}

async function applyLabelSuggestion(chunkId, labelId, confidence) {
  if (approvalManager) await approvalManager.applyLabelSuggestion(chunkId, labelId, confidence);
}
