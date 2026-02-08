/**
 * Knowledge Admin 페이지
 * 탭 기반 관리 인터페이스로 라벨, 키워드 그룹, 청크 승인 기능을 제공합니다.
 */

// 탭별 관리자 인스턴스 (지연 초기화)
let groupsTabManager = null;
let labelsTabManager = null;
let approvalTabManager = null;

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  // 공통 관리자 페이지 초기화
  initializeAdminPage({
    title: "⚙️ Knowledge Admin",
    subtitle: "지식 구조 관리",
    currentPath: "/knowledge-admin",
  });

  // 라벨 탭 관리자 초기화 (라벨 목록 페이징 활성화)
  labelsTabManager = new LabelManager({
    enablePagination: false,
    enableLabelsPagination: true,
    labelsInitialLimit: 20,
    onLabelChange: () => {},
    onChunkChange: () => {},
  });
  window.labelsTabManager = labelsTabManager;
  window.labelManager = labelsTabManager;

  // 라벨 탭이 기본이므로 초기 로드
  labelsTabManager.loadLabels(1);

  // 청크 승인 탭 관리자 초기화
  approvalTabManager = new ChunkApprovalManager({
    enablePagination: false,
    onChunkChange: () => {},
  });
  window.approvalTabManager = approvalTabManager;
});

// ========== 탭 전환 ==========

/**
 * 탭 전환 처리
 * @param {string} tab - 탭 이름 ('labels', 'chunklabels', 'groups', 'approval')
 */
function switchTab(tab) {
  // 탭 버튼 활성화
  document.querySelectorAll(".tab-nav-btn").forEach((btn) => btn.classList.remove("active"));
  const tabBtn = document.getElementById(`tab-${tab}`);
  if (tabBtn) tabBtn.classList.add("active");

  // 탭 컨텐츠 표시/숨김
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.style.display = "none";
  });
  const tabContent = document.getElementById(`tab-content-${tab}`);
  if (tabContent) {
    tabContent.style.display = "block";
  }

  // 탭별 데이터 로드
  switch (tab) {
    case "groups":
      if (!groupsTabManager) {
        groupsTabManager = new KeywordGroupManager({
          onGroupChange: () => {},
          onKeywordChange: () => {},
        });
        window.groupsTabManager = groupsTabManager;
      }
      groupsTabManager.loadGroups();
      groupsTabManager.loadKeywords();
      break;

    case "labels":
      if (labelsTabManager) {
        labelsTabManager.loadLabels(1);
      }
      break;

    case "chunklabels":
      if (labelsTabManager) {
        labelsTabManager.loadChunks();
        labelsTabManager.loadLabelOptions();
      }
      break;

    case "approval":
      if (approvalTabManager) {
        approvalTabManager.loadPendingChunks();
      }
      break;
  }
}

// ========== 전역 함수 래퍼 (하위 호환성) ==========
// HTML에서 직접 호출되는 함수들을 위한 래퍼 함수들

// 청크 승인 관리 함수
async function filterByStatus(status) {
  if (approvalTabManager) await approvalTabManager.filterByStatus(status);
}
async function loadPendingChunks() {
  if (approvalTabManager) await approvalTabManager.loadPendingChunks();
}
function displayPendingChunks() {
  if (approvalTabManager) approvalTabManager.displayPendingChunks();
}
async function approveChunk(chunkId) {
  if (approvalTabManager) await approvalTabManager.approveChunk(chunkId);
}
async function rejectChunk(chunkId) {
  if (approvalTabManager) await approvalTabManager.rejectChunk(chunkId);
}
async function showChunkDetail(chunkId) {
  if (approvalTabManager) await approvalTabManager.showChunkDetail(chunkId);
}
function closeChunkDetail() {
  if (approvalTabManager) approvalTabManager.closeChunkDetail();
}
async function applyLabelSuggestion(chunkId, labelId, confidence) {
  if (approvalTabManager) await approvalTabManager.applyLabelSuggestion(chunkId, labelId, confidence);
}

// 라벨 관리 함수
async function loadLabels() {
  if (labelsTabManager) await labelsTabManager.loadLabels();
}
function displayLabels() {
  if (labelsTabManager) labelsTabManager.displayLabels();
}
async function createLabel(event) {
  if (labelsTabManager) await labelsTabManager.createLabel(event);
}
async function deleteLabel(labelId) {
  if (labelsTabManager) await labelsTabManager.deleteLabel(labelId);
}
function updateLabelSelect() {
  if (labelsTabManager) labelsTabManager.updateLabelSelect();
}
async function loadChunks() {
  if (labelsTabManager) await labelsTabManager.loadChunks();
}
function displayChunks(filteredChunks) {
  if (labelsTabManager) labelsTabManager.displayChunks(filteredChunks);
}
function searchChunks() {
  if (labelsTabManager) labelsTabManager.searchChunks();
}
async function selectChunk(chunkId) {
  if (labelsTabManager) await labelsTabManager.selectChunk(chunkId);
}
async function loadChunkLabels(chunkId) {
  if (labelsTabManager) await labelsTabManager.loadChunkLabels(chunkId);
}
async function addLabelToChunk() {
  if (labelsTabManager) await labelsTabManager.addLabelToChunk();
}
async function removeLabelFromChunk(labelId) {
  if (labelsTabManager) await labelsTabManager.removeLabelFromChunk(labelId);
}

// 키워드 그룹 관리 함수
function loadGroups() {
  if (groupsTabManager) groupsTabManager.loadGroups();
}
function loadKeywords() {
  if (groupsTabManager) groupsTabManager.loadKeywords();
}
function selectGroup(groupId) {
  if (groupsTabManager) groupsTabManager.selectGroup(groupId);
}
function toggleKeywordSelection(keywordId) {
  if (groupsTabManager) groupsTabManager.toggleKeywordSelection(keywordId);
}
function updateMatchingUI() {
  if (groupsTabManager) groupsTabManager.updateMatchingUI();
}
function clearSelection() {
  if (groupsTabManager) groupsTabManager.clearSelection();
}
function applyGroupKeywords() {
  if (groupsTabManager) groupsTabManager.applyGroupKeywords();
}
function searchGroupsAndKeywords() {
  if (groupsTabManager) groupsTabManager.searchGroupsAndKeywords();
}
function showCreateGroupModal() {
  if (groupsTabManager) groupsTabManager.showCreateGroupModal();
}
function showEditGroupModal(groupId) {
  if (groupsTabManager) groupsTabManager.showEditGroupModal(groupId);
}
function closeCreateGroupModal() {
  if (groupsTabManager) groupsTabManager.closeCreateGroupModal();
}
function handleCreateGroup(event) {
  if (groupsTabManager) groupsTabManager.handleCreateGroup(event);
}
function clearSuggestedKeywords() {
  if (groupsTabManager) groupsTabManager.clearSuggestedKeywords();
}
function suggestKeywordsFromDescription() {
  if (groupsTabManager) groupsTabManager.suggestKeywordsFromDescription();
}
function toggleSuggestedKeyword(keyword, chip) {
  if (groupsTabManager) groupsTabManager.toggleSuggestedKeyword(keyword, chip);
}
function removeSuggestedKeyword(keyword, chip) {
  if (groupsTabManager) groupsTabManager.removeSuggestedKeyword(keyword, chip);
}
