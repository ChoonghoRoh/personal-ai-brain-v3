/**
 * 키워드 그룹 검색 모듈
 * 그룹/키워드 검색 기능 (3단 레이아웃 + 페이지네이션 연동)
 */
class KeywordGroupSearch {
  constructor(manager) {
    this.manager = manager;
    this._debounceTimer = null;
  }

  /**
   * 그룹/키워드 검색 (디바운스 적용)
   */
  searchGroupsAndKeywords() {
    clearTimeout(this._debounceTimer);
    this._debounceTimer = setTimeout(() => {
      // 검색어가 변경되면 그룹 목록을 1페이지부터 다시 로드
      this.manager.crud.loadGroups(1);

      // 트리 뷰 활성화 시 하이라이트
      if (typeof isTreeViewActive === "function" && isTreeViewActive() && this.manager.treeView) {
        var query = document.getElementById(this.manager.searchInputId)?.value.trim() || "";
        if (query) {
          this.manager.treeView.highlightSearchResults(query);
        } else {
          this.manager.treeView.clearHighlight();
        }
      }
    }, 300);
  }
}
