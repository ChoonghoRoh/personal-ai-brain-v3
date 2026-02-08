/**
 * 키워드 그룹 검색 모듈
 * 그룹/키워드 검색 기능을 제공하는 클래스
 */
class KeywordGroupSearch {
  constructor(manager) {
    this.manager = manager; // KeywordGroupManager 인스턴스 참조
  }

  /**
   * 그룹/키워드 검색
   */
  searchGroupsAndKeywords() {
    const searchTerm = document.getElementById(this.manager.searchInputId)?.value.toLowerCase() || "";
    document.querySelectorAll(".group-card, .keyword-badge").forEach((card) => {
      const text = card.textContent.toLowerCase();
      card.style.display = text.includes(searchTerm) ? "inline-flex" : "none";
    });
  }
}
