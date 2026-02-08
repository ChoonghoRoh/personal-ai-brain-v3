// 키워드 그룹 관리자 인스턴스
let groupManager;

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializeAdminPage({
    title: "📦 키워드 그룹 관리",
    subtitle: "키워드 그룹 생성 및 관리",
    currentPath: "/admin/groups",
  });

  // 키워드 그룹 관리자 초기화
  groupManager = new KeywordGroupManager({
    onGroupChange: () => {
      // 그룹 변경 시 추가 처리 (필요시)
    },
    onKeywordChange: () => {
      // 키워드 변경 시 추가 처리 (필요시)
    },
  });

  // 전역 함수로 노출 (하위 호환성)
  window.groupManager = groupManager;

  // 초기 데이터 로드
  groupManager.loadGroups();
  groupManager.loadKeywords();

  // 키워드 추천용 LLM 모델 목록 로드 (공통 모듈 사용, exaone 제외)
  if (typeof loadOllamaModelOptions === "function") {
    loadOllamaModelOptions("keyword-suggestion-model");
  }
});

// 전역 함수 래퍼 (하위 호환성)
function loadGroups() {
  if (groupManager) groupManager.loadGroups();
}

function loadKeywords() {
  if (groupManager) groupManager.loadKeywords();
}

function selectGroup(groupId) {
  if (groupManager) groupManager.selectGroup(groupId);
}

function toggleKeywordSelection(keywordId) {
  if (groupManager) groupManager.toggleKeywordSelection(keywordId);
}

function toggleRemoveKeywordSelection(keywordId) {
  if (groupManager) groupManager.toggleRemoveKeywordSelection(keywordId);
}

function toggleKeywordSelectionForGroupCheck(keywordId) {
  if (groupManager) groupManager.toggleKeywordSelectionForGroupCheck(keywordId);
}

function selectAllKeywordsInSection(isGroupSection) {
  if (groupManager) groupManager.selectAllKeywordsInSection(isGroupSection);
}

function updateMatchingUI() {
  if (groupManager) groupManager.updateMatchingUI();
}

function clearSelection() {
  if (groupManager) groupManager.clearSelection();
}

function applyGroupKeywords() {
  if (groupManager) groupManager.applyGroupKeywords();
}

function removeGroupKeywords() {
  if (groupManager) groupManager.removeGroupKeywords();
}

function searchGroupsAndKeywords() {
  if (groupManager) groupManager.searchGroupsAndKeywords();
}

function showCreateGroupModal() {
  if (groupManager) groupManager.showCreateGroupModal();
}

function showEditGroupModal(groupId) {
  if (groupManager) groupManager.showEditGroupModal(groupId);
}

function closeCreateGroupModal() {
  if (groupManager) groupManager.closeCreateGroupModal();
}

function handleCreateGroup(event) {
  if (groupManager) groupManager.handleCreateGroup(event);
}

function clearSuggestedKeywords() {
  if (groupManager) groupManager.clearSuggestedKeywords();
}

function suggestKeywordsFromDescription() {
  if (groupManager) groupManager.suggestKeywordsFromDescription();
}

function toggleSuggestedKeyword(keyword, chip) {
  if (groupManager) groupManager.toggleSuggestedKeyword(keyword, chip);
}

function removeSuggestedKeyword(keyword, chip) {
  if (groupManager) groupManager.removeSuggestedKeyword(keyword, chip);
}
