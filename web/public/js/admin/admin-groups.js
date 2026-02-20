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
function switchTab(tabName) { if (groupManager) groupManager.treeView.switchView(tabName); }
async function suggestKeywordsForSelectedGroup() {
  if (!groupManager) return;

  const selectedGroupId = groupManager.crud.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  // 현재 선택된 그룹의 description을 가져와서 추천 실행
  const descriptionEl = document.querySelector("#group-detail-panel .detail-field-value[data-field='description']");
  if (!descriptionEl || !descriptionEl.textContent.trim() || descriptionEl.classList.contains("empty")) {
    showError("그룹 설명이 없어서 LLM 추천을 실행할 수 없습니다.");
    return;
  }

  const description = descriptionEl.textContent.trim();
  const btn = document.getElementById("llm-suggest-btn");
  const errorDiv = document.getElementById("llm-suggestion-error");
  const successDiv = document.getElementById("llm-suggestion-success");
  const section = document.getElementById("llm-suggestion-section");
  const keywordsList = document.getElementById("llm-suggested-keywords-list");

  if (errorDiv) errorDiv.style.display = "none";
  if (successDiv) successDiv.style.display = "none";

  btn.disabled = true;
  btn.textContent = "⏳ 추천 중...";

  try {
    const response = await fetch("/api/labels/groups/suggest-keywords", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description: description, group_id: selectedGroupId }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "키워드 추천 실패");
    }

    const data = await response.json();
    const suggestions = data.suggestions || [];
    let newKeywords = data.new_keywords || [];

    // new_keywords 정제
    newKeywords = groupManager.suggestion.extractKeywordsOnly(newKeywords);

    const totalCount = suggestions.length + newKeywords.length;

    if (totalCount === 0) {
      if (errorDiv) {
        errorDiv.textContent = "추천할 키워드를 찾을 수 없습니다.";
        errorDiv.style.display = "block";
      }
      return;
    }

    // 추천 결과 렌더링
    keywordsList.innerHTML = "";
    groupManager.selectedSuggestedKeywords.clear();

    suggestions.forEach((item) => {
      const chip = groupManager.suggestion.createSuggestedKeywordChip(item.name, true, item.confidence);
      keywordsList.appendChild(chip);
    });

    newKeywords.forEach((keyword) => {
      const chip = groupManager.suggestion.createSuggestedKeywordChip(keyword, false, null, true);
      keywordsList.appendChild(chip);
    });

    section.style.display = "block";

    if (successDiv) {
      const ollamaOk = data.ollama_feedback && data.ollama_feedback.available;
      const methodLabel = ollamaOk ? "Ollama(로컬 LLM)" : "Fallback (Ollama 미실행)";
      successDiv.textContent = esc(totalCount) + "개의 키워드가 추천되었습니다. [" + esc(methodLabel) + "]";
      successDiv.style.display = "block";
    }
  } catch (error) {
    console.error("키워드 추천 실패:", error);
    if (errorDiv) {
      errorDiv.textContent = esc(error.message) || "키워드 추천 중 오류가 발생했습니다.";
      errorDiv.style.display = "block";
    } else {
      showError(error.message || "키워드 추천 중 오류가 발생했습니다.");
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "🤖 LLM 추천";
  }
}

function addSelectedSuggestedKeywords() {
  if (!groupManager) return;

  const selectedKeywords = Array.from(groupManager.selectedSuggestedKeywords);
  if (selectedKeywords.length === 0) {
    showError("추가할 키워드를 선택해주세요.");
    return;
  }

  const selectedGroupId = groupManager.crud.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  groupManager.matching.addKeywordsToGroup(selectedGroupId, selectedKeywords).then(() => {
    groupManager.selectedSuggestedKeywords.clear();
    document.getElementById("llm-suggestion-section").style.display = "none";
    groupManager.matching.loadKeywords();
  });
}

function deleteCurrentGroup() {
  if (!groupManager) return;

  const selectedGroupId = groupManager.crud.selectedGroupId;
  if (!selectedGroupId) {
    showError("삭제할 그룹을 선택해주세요.");
    return;
  }

  groupManager.deleteGroup(selectedGroupId);
}

let selectedRelatedKeywords = new Set();

async function searchRelatedKeywords() {
  if (!groupManager) return;

  const selectedGroupId = groupManager.crud.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  const query = document.getElementById("related-keyword-search").value.trim();
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
    const relatedKeywords = data.related_keywords || [];

    if (relatedKeywords.length === 0) {
      listContainer.innerHTML = '<div style="padding: 12px; text-align: center; color: #9ca3af; font-size: 12px">연관 키워드가 없습니다</div>';
      return;
    }

    relatedKeywords.forEach((item) => {
      const itemDiv = document.createElement("div");
      itemDiv.className = "related-keyword-item";
      itemDiv.dataset.keywordName = item.keyword_name;

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.onchange = (e) => {
        if (e.target.checked) {
          selectedRelatedKeywords.add(item.keyword_name);
          itemDiv.classList.add("selected");
        } else {
          selectedRelatedKeywords.delete(item.keyword_name);
          itemDiv.classList.remove("selected");
        }
        addBtn.style.display = selectedRelatedKeywords.size > 0 ? "block" : "none";
      };

      const nameSpan = document.createElement("span");
      nameSpan.className = "keyword-name";
      nameSpan.textContent = item.keyword_name;

      const badgeSpan = document.createElement("span");
      badgeSpan.className = "similarity-badge";
      badgeSpan.textContent = Math.round(item.similarity * 100) + "%";

      itemDiv.appendChild(checkbox);
      itemDiv.appendChild(nameSpan);
      itemDiv.appendChild(badgeSpan);

      itemDiv.onclick = (e) => {
        if (e.target !== checkbox) {
          checkbox.checked = !checkbox.checked;
          checkbox.dispatchEvent(new Event("change"));
        }
      };

      listContainer.appendChild(itemDiv);
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

  const selectedGroupId = groupManager.crud.selectedGroupId;
  if (!selectedGroupId) {
    showError("그룹을 먼저 선택해주세요.");
    return;
  }

  try {
    await groupManager.matching.addKeywordsToGroup(selectedGroupId, selectedKeywords);
    selectedRelatedKeywords.clear();
    document.getElementById("related-keywords-list").innerHTML = "";
    document.getElementById("add-related-btn").style.display = "none";
    document.getElementById("related-keyword-search").value = "";
    groupManager.matching.loadKeywords();
    showSuccess(selectedKeywords.length + "개의 연관 키워드가 추가되었습니다.");
  } catch (error) {
    console.error("연관 키워드 추가 실패:", error);
    showError("연관 키워드 추가 중 오류가 발생했습니다.");
  }
}
