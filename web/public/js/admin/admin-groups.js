// 키워드 그룹 관리자 인스턴스
let groupManager;

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializeAdminPage({
    title: "키워드 그룹 관리",
    subtitle: "키워드 그룹 생성 및 관리",
    currentPath: "/admin/groups",
  });

  // 키워드 그룹 관리자 초기화
  groupManager = new KeywordGroupManager({
    onGroupChange: () => {},
    onKeywordChange: () => {},
  });

  // 전역 함수로 노출
  window.groupManager = groupManager;

  // 초기 데이터 로드 (페이지네이션 모드)
  groupManager.loadGroups(1);
  groupManager.loadKeywords();
});

// 전역 함수 래퍼 (하위 호환성)
function loadGroups() { if (groupManager) groupManager.loadGroups(); }
function loadKeywords() { if (groupManager) groupManager.loadKeywords(); }
function selectGroup(groupId) { if (groupManager) groupManager.selectGroup(groupId); }
function toggleKeywordSelection(keywordId) { if (groupManager) groupManager.toggleKeywordSelection(keywordId); }
function toggleRemoveKeywordSelection(keywordId) { if (groupManager) groupManager.toggleRemoveKeywordSelection(keywordId); }
function toggleKeywordSelectionForGroupCheck(keywordId) { if (groupManager) groupManager.toggleKeywordSelectionForGroupCheck(keywordId); }
function selectAllKeywordsInSection(isGroupSection) { if (groupManager) groupManager.selectAllKeywordsInSection(isGroupSection); }
function updateMatchingUI() { if (groupManager) groupManager.updateMatchingUI(); }
function clearSelection() { if (groupManager) groupManager.clearSelection(); }
function applyGroupKeywords() { if (groupManager) groupManager.applyGroupKeywords(); }
function removeGroupKeywords() { if (groupManager) groupManager.removeGroupKeywords(); }
function searchGroupsAndKeywords() { if (groupManager) groupManager.searchGroupsAndKeywords(); }
function showCreateGroupModal() { if (groupManager) groupManager.showCreateGroupModal(); }
function showEditGroupModal(groupId) { if (groupManager) groupManager.showEditGroupModal(groupId); }
function closeCreateGroupModal() { if (groupManager) groupManager.closeCreateGroupModal(); }
function handleCreateGroup(event) { if (groupManager) groupManager.handleCreateGroup(event); }
function clearSuggestedKeywords() { if (groupManager) groupManager.clearSuggestedKeywords(); }
function suggestKeywordsFromDescription() { if (groupManager) groupManager.suggestKeywordsFromDescription(); }
function toggleSuggestedKeyword(keyword, chip) { if (groupManager) groupManager.toggleSuggestedKeyword(keyword, chip); }
function removeSuggestedKeyword(keyword, chip) { if (groupManager) groupManager.removeSuggestedKeyword(keyword, chip); }
