/**
 * 키워드 그룹 관리 모듈 (메인 클래스)
 * 3단 레이아웃: 그룹 목록 | 상세/편집 | 키워드 목록
 */
class KeywordGroupManager {
  constructor(config = {}) {
    // 콜백 함수
    this.onGroupChange = config.onGroupChange || (() => {});
    this.onKeywordChange = config.onKeywordChange || (() => {});

    // 상태 관리
    this.selectedGroupId = null;
    this.selectedKeywordIds = new Set();
    this.selectedRemoveKeywordIds = new Set();
    this.selectedKeywordForGroupCheck = null;
    this.selectedSuggestedKeywords = new Set();
    this.editingGroupId = null;

    // DOM 요소 ID
    this.groupsListId = config.groupsListId || "groups-list";
    this.keywordsListId = config.keywordsListId || "keywords-list";
    this.searchInputId = config.searchInputId || "group-search-input";
    this.suggestedKeywordsContainerId = config.suggestedKeywordsContainerId || "suggested-keywords-container";
    this.suggestedKeywordsListId = config.suggestedKeywordsListId || "suggested-keywords-list";
    this.suggestionErrorId = config.suggestionErrorId || "keyword-suggestion-error";
    this.suggestionSuccessId = config.suggestionSuccessId || "keyword-suggestion-success";
    this.suggestionModelSelectId = config.suggestionModelSelectId || "keyword-suggestion-model";
    this.matchingSummaryBarId = config.matchingSummaryBarId || "matching-summary-bar";
    this.selectionSummaryId = config.selectionSummaryId || "selection-summary";
    this.applyKeywordsBtnId = config.applyKeywordsBtnId || "apply-keywords-btn";
    this.removeKeywordsBtnId = config.removeKeywordsBtnId || "remove-keywords-btn";
    this.groupNameInputId = config.groupNameInputId || "group-name-input";
    this.groupDescriptionInputId = config.groupDescriptionInputId || "group-description-input";
    this.groupColorInputId = config.groupColorInputId || "group-color-input";

    // 기능별 모듈 인스턴스 생성
    this.crud = new KeywordGroupCRUD(this);
    this.matching = new KeywordGroupMatching(this);
    this.ui = new KeywordGroupUI(this);
    this.suggestion = new KeywordGroupSuggestion(this);
    this.search = new KeywordGroupSearch(this);
  }

  // ========== 그룹 CRUD 메서드 위임 ==========
  async loadGroups(page) { return this.crud.loadGroups(page); }
  createGroupCard(group) { return this.crud.createGroupCard(group); }
  async loadGroupKeywordsCount(groupId) { return this.crud.loadGroupKeywordsCount(groupId); }
  showCreateGroupModal() { return this.crud.showCreateGroupModal(); }
  async showEditGroupModal(groupId) { return this.crud.showEditGroupModal(groupId); }
  async showEditGroupInline(groupId) { return this.crud.showEditGroupInline(groupId); }
  closeCreateGroupModal() { return this.crud.closeCreateGroupModal(); }
  cancelEditInline() { return this.crud.cancelEditInline(); }
  async saveEditInline() { return this.crud.saveEditInline(); }
  async handleCreateGroup(event) { return this.crud.handleCreateGroup(event); }
  async createGroup(name, description, color) { return this.crud.createGroup(name, description, color); }
  async updateGroup(groupId, name, description, color) { return this.crud.updateGroup(groupId, name, description, color); }
  async deleteGroup(groupId) { return this.crud.deleteGroup(groupId); }

  // ========== 키워드 매칭 메서드 위임 ==========
  async loadKeywords() { return this.matching.loadKeywords(); }
  createKeywordSection(sectionType, keywords, isGroupSection) { return this.matching.createKeywordSection(sectionType, keywords, isGroupSection); }
  createKeywordBadge(keyword, isInGroup) { return this.matching.createKeywordBadge(keyword, isInGroup); }
  selectGroup(groupId) { return this.matching.selectGroup(groupId); }
  toggleKeywordSelection(keywordId) { return this.matching.toggleKeywordSelection(keywordId); }
  toggleRemoveKeywordSelection(keywordId) { return this.matching.toggleRemoveKeywordSelection(keywordId); }
  toggleKeywordSelectionForGroupCheck(keywordId) { return this.matching.toggleKeywordSelectionForGroupCheck(keywordId); }
  selectAllKeywordsInSection(isGroupSection) { return this.matching.selectAllKeywordsInSection(isGroupSection); }
  async applyGroupKeywords() { return this.matching.applyGroupKeywords(); }
  async removeGroupKeywords() { return this.matching.removeGroupKeywords(); }
  async addKeywordsToGroup(groupId, keywordNames) { return this.matching.addKeywordsToGroup(groupId, keywordNames); }

  // ========== UI 업데이트 메서드 위임 ==========
  updateMatchingUI() { return this.ui.updateMatchingUI(); }
  updateSelectAllButtons() { return this.ui.updateSelectAllButtons(); }
  clearSelection() { return this.ui.clearSelection(); }

  // ========== 키워드 추천 메서드 위임 ==========
  clearSuggestedKeywords() { return this.suggestion.clearSuggestedKeywords(); }
  async suggestKeywordsFromDescription() { return this.suggestion.suggestKeywordsFromDescription(); }
  createSuggestedKeywordChip(keyword, isSimilar) { return this.suggestion.createSuggestedKeywordChip(keyword, isSimilar); }
  toggleSuggestedKeyword(keyword, chip) { return this.suggestion.toggleSuggestedKeyword(keyword, chip); }
  removeSuggestedKeyword(keyword, chip) { return this.suggestion.removeSuggestedKeyword(keyword, chip); }

  // ========== 검색 메서드 위임 ==========
  searchGroupsAndKeywords() { return this.search.searchGroupsAndKeywords(); }
}
