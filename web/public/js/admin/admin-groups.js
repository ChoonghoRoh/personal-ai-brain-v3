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

  // 트리 단일 진입: 트리 로드 후 키워드 목록 로드
  groupManager.treeView.loadTree();
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
function switchTab(tabName) { if (typeof switchView === "function") switchView(tabName); }
function searchKeywords() { if (groupManager) groupManager.searchKeywords(); }

function applyTreeMaxDepth() {
  if (!groupManager || !groupManager.treeView) return;
  groupManager.treeView.loadTree();
}

function deleteCurrentGroup() {
  if (!groupManager) return;

  const selectedGroupId = groupManager.selectedGroupId;
  if (!selectedGroupId) {
    showError("삭제할 그룹을 선택해주세요.");
    return;
  }

  groupManager.deleteGroup(selectedGroupId);
}

let selectedRelatedKeywords = new Set();

async function searchRelatedKeywords() {
  if (!groupManager) return;

  const selectedGroupId = groupManager.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  const query = "";
  const errorDiv = document.getElementById("related-keywords-error");
  const listContainer = document.getElementById("related-keywords-list");
  const addBtn = document.getElementById("add-related-btn");

  if (errorDiv) errorDiv.style.display = "none";
  listContainer.innerHTML = "";
  addBtn.style.display = "none";
  selectedRelatedKeywords.clear();

  try {
    const url = "/api/labels/groups/" + selectedGroupId + "/related-keywords" + (query ? "?q=" + encodeURIComponent(query) + "&limit=20" : "?limit=20");
    const response = await fetch(url);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "연관 키워드 조회 실패");
    }

    const data = await response.json();
    const relatedKeywords = data.items || [];

    if (relatedKeywords.length === 0) {
      listContainer.innerHTML = '<div style="padding: 12px; text-align: center; color: #9ca3af; font-size: 12px">유사 키워드가 없습니다</div>';
      return;
    }

    relatedKeywords.forEach((item) => {
      const itemSpan = document.createElement("span");
      itemSpan.className = "keyword-badge inactive";
      itemSpan.dataset.keywordName = item.name;

      const scorePercent = Math.round(item.similarity_score * 100);
      itemSpan.innerHTML =
        escapeHtml(item.name) +
        ' <span class="similarity-badge">' +
        scorePercent +
        "%</span>";

      itemSpan.onclick = () => {
        if (selectedRelatedKeywords.has(item.name)) {
          selectedRelatedKeywords.delete(item.name);
          itemSpan.classList.remove("selected");
          itemSpan.classList.add("inactive");
        } else {
          selectedRelatedKeywords.add(item.name);
          itemSpan.classList.add("selected");
          itemSpan.classList.remove("inactive");
        }
        addBtn.style.display = selectedRelatedKeywords.size > 0 ? "block" : "none";
      };

      listContainer.appendChild(itemSpan);
    });
  } catch (error) {
    console.error("연관 키워드 조회 실패:", error);
    if (errorDiv) {
      errorDiv.textContent = esc(error.message) || "연관 키워드 조회 중 오류가 발생했습니다.";
      errorDiv.style.display = "block";
    } else {
      showError(error.message || "연관 키워드 조회 중 오류가 발생했습니다.");
    }
  }
}

async function addSelectedRelatedKeywords() {
  if (!groupManager) return;

  const selectedKeywords = Array.from(selectedRelatedKeywords);
  if (selectedKeywords.length === 0) {
    showError("추가할 연관 키워드를 선택해주세요.");
    return;
  }

  const selectedGroupId = groupManager.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  try {
    await groupManager.matching.addKeywordsToGroup(selectedGroupId, selectedKeywords);
    selectedRelatedKeywords.clear();
    document.getElementById("related-keywords-list").innerHTML = "";
    document.getElementById("add-related-btn").style.display = "none";
    groupManager.matching.loadKeywords();
    showSuccess(selectedKeywords.length + "개의 연관 키워드가 추가되었습니다.");
  } catch (error) {
    console.error("연관 키워드 추가 실패:", error);
    showError("연관 키워드 추가 중 오류가 발생했습니다.");
  }
}
