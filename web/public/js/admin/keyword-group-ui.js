/**
 * 키워드 그룹 UI 업데이트 모듈
 * 매칭 UI, 선택 버튼 업데이트 기능 (3단 레이아웃)
 */
class KeywordGroupUI {
  constructor(manager) {
    this.manager = manager;
  }

  /**
   * 매칭 UI 업데이트
   */
  updateMatchingUI() {
    // 그룹 카드 선택 상태 업데이트
    document.querySelectorAll(".group-card").forEach((card) => {
      if (card.dataset.groupId == this.manager.selectedGroupId) {
        card.classList.add("selected");
      } else {
        card.classList.remove("selected");
      }
    });

    // 키워드 배지 상태 업데이트
    document.querySelectorAll(".keyword-badge").forEach((badge) => {
      const keywordId = parseInt(badge.dataset.keywordId);
      const isInGroup = badge.dataset.isInGroup === "true";

      if (this.manager.selectedGroupId) {
        if (isInGroup && this.manager.selectedRemoveKeywordIds.has(keywordId)) {
          badge.classList.add("remove-selected");
          badge.classList.remove("active", "inactive", "selected");
        } else if (!isInGroup && this.manager.selectedKeywordIds.has(keywordId)) {
          badge.classList.add("selected");
          badge.classList.remove("active", "inactive", "remove-selected");
        } else {
          badge.classList.remove("selected", "remove-selected");
          if (isInGroup) {
            badge.classList.add("active");
            badge.classList.remove("inactive");
          } else {
            badge.classList.add("inactive");
            badge.classList.remove("active");
          }
        }
      } else {
        if (this.manager.selectedKeywordForGroupCheck === keywordId) {
          badge.classList.add("selected");
          badge.classList.remove("active", "inactive", "remove-selected");
        } else {
          badge.classList.remove("selected", "remove-selected");
          badge.classList.add("inactive");
        }
      }
    });

    this.updateSelectAllButtons();

    // 요약 바 업데이트
    const summaryBar = document.getElementById(this.manager.matchingSummaryBarId);
    const summaryText = document.getElementById(this.manager.selectionSummaryId);
    const applyBtn = document.getElementById(this.manager.applyKeywordsBtnId);
    const removeBtn = document.getElementById(this.manager.removeKeywordsBtnId);

    if (summaryBar && summaryText) {
      if (this.manager.selectedGroupId) {
        summaryBar.style.display = "flex";
        const treeNameEl = document.querySelector("#groups-tree .tree-node-content.selected .tree-name");
        const groupName = treeNameEl ? treeNameEl.textContent : `그룹 #${this.manager.selectedGroupId}`;

        const parts = [];
        if (this.manager.selectedKeywordIds.size > 0) {
          parts.push(`연결할 키워드: ${this.manager.selectedKeywordIds.size}개`);
        }
        if (this.manager.selectedRemoveKeywordIds.size > 0) {
          parts.push(`제외할 키워드: ${this.manager.selectedRemoveKeywordIds.size}개`);
        }

        if (parts.length > 0) {
          summaryText.textContent = `선택된 그룹: ${groupName} · ${parts.join(" · ")}`;
        } else {
          summaryText.textContent = `선택된 그룹: ${groupName} · 우측에서 키워드를 선택하세요`;
        }

        if (applyBtn) applyBtn.style.display = this.manager.selectedKeywordIds.size > 0 ? "inline-block" : "none";
        if (removeBtn) removeBtn.style.display = this.manager.selectedRemoveKeywordIds.size > 0 ? "inline-block" : "none";
      } else {
        summaryBar.style.display = "none";
      }
    }
  }

  /**
   * 전체 선택 버튼 업데이트
   */
  updateSelectAllButtons() {
    const groupSection = document.querySelector('div[data-section="group"]');
    if (groupSection) {
      const groupBadges = groupSection.querySelectorAll(".keyword-badge");
      const groupBtn = groupSection.parentElement?.querySelector('button[data-section="group"]');

      if (groupBtn && groupBadges.length > 0) {
        let allSelected = true;
        groupBadges.forEach((badge) => {
          const keywordId = parseInt(badge.dataset.keywordId);
          if (!this.manager.selectedRemoveKeywordIds.has(keywordId)) allSelected = false;
        });
        groupBtn.textContent = allSelected ? "전체 해제" : "전체 선택";
      }
    }

    const otherSection = document.querySelector('div[data-section="other"]');
    if (otherSection) {
      const otherBadges = otherSection.querySelectorAll(".keyword-badge");
      const otherBtn = otherSection.parentElement?.querySelector('button[data-section="other"]');

      if (otherBtn && otherBadges.length > 0) {
        let allSelected = true;
        otherBadges.forEach((badge) => {
          const keywordId = parseInt(badge.dataset.keywordId);
          if (!this.manager.selectedKeywordIds.has(keywordId)) allSelected = false;
        });
        otherBtn.textContent = allSelected ? "전체 해제" : "전체 선택";
      }
    }
  }

  /**
   * 선택 초기화
   */
  clearSelection() {
    this.manager.selectedGroupId = null;
    this.manager.selectedKeywordIds.clear();
    this.manager.selectedRemoveKeywordIds.clear();
    this.manager.selectedKeywordForGroupCheck = null;

    // 상세 패널 초기화 (우측 빈 상태)
    const panel = document.getElementById("group-detail-panel");
    if (panel) {
      panel.innerHTML = "<div class=\"detail-empty-state\"><p>좌측에서 그룹을 선택하세요</p></div>";
    }

    this.updateMatchingUI();
    this.manager.matching.loadKeywords();
  }
}
