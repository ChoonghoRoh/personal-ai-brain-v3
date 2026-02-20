/**
 * 키워드 그룹 매칭 모듈
 * 키워드 선택, 연결, 제거 기능 + 3단 레이아웃 키워드 영역 관리
 */
class KeywordGroupMatching {
  constructor(manager) {
    this.manager = manager;
  }

  /**
   * 키워드 목록 로드 (3단 영역)
   */
  async loadKeywords() {
    try {
      const [keywordsResponse, groupsResponse] = await Promise.all([
        fetch("/api/labels?label_type=keyword"),
        fetch("/api/labels/groups"),
      ]);

      const keywords = await keywordsResponse.json();
      const groups = await groupsResponse.json();

      const keywordsList = document.getElementById(this.manager.keywordsListId);
      if (!keywordsList) return;
      keywordsList.innerHTML = "";

      let groupKeywords = [];
      let otherKeywords = [];

      if (this.manager.selectedGroupId) {
        keywords.forEach((keyword) => {
          if (keyword.parent_label_id === this.manager.selectedGroupId) {
            groupKeywords.push(keyword);
          } else {
            otherKeywords.push(keyword);
          }
        });

        if (groupKeywords.length > 0) {
          const sectionContainer = this.createKeywordSection("group", groupKeywords, true);
          keywordsList.appendChild(sectionContainer);
        }

        if (otherKeywords.length > 0) {
          const sectionContainer = this.createKeywordSection("other", otherKeywords, false);
          keywordsList.appendChild(sectionContainer);
        }

        if (groupKeywords.length === 0 && otherKeywords.length === 0) {
          keywordsList.innerHTML = '<div style="padding:20px;color:#9ca3af;text-align:center">키워드가 없습니다</div>';
        }
      } else {
        const keywordsContainer = document.createElement("div");
        keywordsContainer.style.cssText = "display: flex; flex-wrap: wrap; gap: 8px";

        keywords.forEach((keyword) => {
          const badge = this.createKeywordBadge(keyword, false);
          keywordsContainer.appendChild(badge);
        });

        keywordsList.appendChild(keywordsContainer);
      }

      this.manager.ui.updateMatchingUI();
      this.manager.onKeywordChange();
    } catch (error) {
      console.error("키워드 로드 실패:", error);
      showError("키워드 목록을 불러오는 중 오류가 발생했습니다.");
    }
  }

  /**
   * 키워드 섹션 생성
   */
  createKeywordSection(sectionType, keywords, isGroupSection) {
    const sectionContainer = document.createElement("div");
    sectionContainer.style.cssText = "width: 100%; margin-bottom: 15px";

    const sectionHeader = document.createElement("div");
    sectionHeader.style.cssText = "display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px";

    const sectionTitle = document.createElement("div");
    sectionTitle.style.cssText = `font-weight: 600; color: ${isGroupSection ? "#2563eb" : "#6b7280"}; font-size: 14px`;
    sectionTitle.textContent = isGroupSection ? "그룹 키워드" : "그룹 외 키워드";

    const selectAllBtn = document.createElement("button");
    selectAllBtn.className = "btn btn-small";
    selectAllBtn.style.cssText = "padding: 4px 8px; font-size: 11px; background: #f3f4f6; color: #333";
    selectAllBtn.dataset.section = sectionType;
    selectAllBtn.textContent = "전체 선택";
    selectAllBtn.onclick = () => this.selectAllKeywordsInSection(isGroupSection);

    sectionHeader.appendChild(sectionTitle);
    sectionHeader.appendChild(selectAllBtn);
    sectionContainer.appendChild(sectionHeader);

    const keywordsContainer = document.createElement("div");
    keywordsContainer.style.cssText = "display: flex; flex-wrap: wrap; gap: 8px";
    keywordsContainer.dataset.section = sectionType;

    keywords.forEach((keyword) => {
      const badge = this.createKeywordBadge(keyword, isGroupSection);
      keywordsContainer.appendChild(badge);
    });

    sectionContainer.appendChild(keywordsContainer);
    return sectionContainer;
  }

  /**
   * 키워드 배지 생성
   */
  createKeywordBadge(keyword, isInGroup) {
    const badge = document.createElement("span");
    badge.className = isInGroup ? "keyword-badge active" : "keyword-badge inactive";
    badge.dataset.keywordId = keyword.id;
    badge.dataset.isInGroup = isInGroup;
    badge.dataset.parentGroupId = keyword.parent_label_id || "";
    badge.textContent = keyword.name;
    badge.style.cursor = "pointer";

    badge.onclick = () => {
      if (this.manager.selectedGroupId) {
        if (isInGroup) {
          this.toggleRemoveKeywordSelection(keyword.id);
        } else {
          this.toggleKeywordSelection(keyword.id);
        }
      } else {
        this.toggleKeywordSelectionForGroupCheck(keyword.id);
      }
    };

    return badge;
  }

  /**
   * 그룹 선택 — 3단 레이아웃: 상세 패널 + 키워드 목록 갱신
   */
  selectGroup(groupId) {
    // 토글: 같은 그룹 다시 클릭하면 선택 해제
    this.manager.selectedGroupId = this.manager.selectedGroupId === groupId ? null : groupId;

    if (this.manager.selectedGroupId) {
      this.manager.selectedKeywordIds.clear();
      this.manager.selectedRemoveKeywordIds.clear();
      this.manager.selectedKeywordForGroupCheck = null;

      // 상세 패널 업데이트
      const group = this.manager.crud.groups.find(g => g.id === groupId);
      if (group) {
        this.manager.crud.renderDetailPanel(group);
      }
    } else {
      // 선택 해제 시 상세 패널 초기화
      const panel = document.getElementById("group-detail-panel");
      if (panel) {
        panel.innerHTML = '<div class="detail-empty-state"><p>좌측에서 그룹을 선택하세요</p></div>';
      }
    }

    // LLM 추천 버튼 상태 업데이트
    const llmSuggestBtn = document.getElementById("llm-suggest-btn");
    if (llmSuggestBtn) {
      llmSuggestBtn.disabled = !this.manager.selectedGroupId;
    }

    // 하단 액션바 그룹 액션 버튼 상태 업데이트
    const groupActionButtons = document.getElementById("group-action-buttons");
    if (groupActionButtons) {
      groupActionButtons.style.display = this.manager.selectedGroupId ? "flex" : "none";
    }

    // 연관 키워드 섹션 상태 업데이트
    const relatedSection = document.getElementById("related-keywords-section");
    if (relatedSection) {
      relatedSection.style.display = this.manager.selectedGroupId ? "block" : "none";
      // 그룹 변경 시 연관 키워드 초기화
      if (!this.manager.selectedGroupId) {
        document.getElementById("related-keyword-search").value = "";
        document.getElementById("related-keywords-list").innerHTML = "";
        document.getElementById("add-related-btn").style.display = "none";
      }
    }

    this.loadKeywords();
    this.manager.ui.updateMatchingUI();
  }

  /**
   * 키워드 선택 토글 (그룹 외 키워드)
   */
  toggleKeywordSelection(keywordId) {
    if (!this.manager.selectedGroupId) {
      showError("먼저 좌측에서 그룹을 선택해주세요.");
      return;
    }
    if (this.manager.selectedKeywordIds.has(keywordId)) {
      this.manager.selectedKeywordIds.delete(keywordId);
    } else {
      this.manager.selectedKeywordIds.add(keywordId);
    }
    this.manager.ui.updateMatchingUI();
  }

  /**
   * 키워드 제외 선택 토글 (그룹 키워드)
   */
  toggleRemoveKeywordSelection(keywordId) {
    if (!this.manager.selectedGroupId) {
      showError("먼저 좌측에서 그룹을 선택해주세요.");
      return;
    }
    if (this.manager.selectedRemoveKeywordIds.has(keywordId)) {
      this.manager.selectedRemoveKeywordIds.delete(keywordId);
    } else {
      this.manager.selectedRemoveKeywordIds.add(keywordId);
    }
    this.manager.ui.updateMatchingUI();
  }

  /**
   * 그룹 미선택 시 키워드 선택 토글
   */
  toggleKeywordSelectionForGroupCheck(keywordId) {
    if (this.manager.selectedKeywordForGroupCheck === keywordId) {
      this.manager.selectedKeywordForGroupCheck = null;
    } else {
      this.manager.selectedKeywordForGroupCheck = keywordId;
    }
    this.manager.ui.updateMatchingUI();
  }

  /**
   * 섹션 전체 선택/해제
   */
  selectAllKeywordsInSection(isGroupSection) {
    if (!this.manager.selectedGroupId) {
      showError("먼저 좌측에서 그룹을 선택해주세요.");
      return;
    }

    const sectionContainer = document.querySelector(`div[data-section="${isGroupSection ? "group" : "other"}"]`);
    if (!sectionContainer) return;

    const sectionBadges = sectionContainer.querySelectorAll(".keyword-badge");
    let hasUnselected = false;

    sectionBadges.forEach((badge) => {
      const keywordId = parseInt(badge.dataset.keywordId);
      if (isGroupSection) {
        if (!this.manager.selectedRemoveKeywordIds.has(keywordId)) hasUnselected = true;
      } else {
        if (!this.manager.selectedKeywordIds.has(keywordId)) hasUnselected = true;
      }
    });

    sectionBadges.forEach((badge) => {
      const keywordId = parseInt(badge.dataset.keywordId);
      if (hasUnselected) {
        if (isGroupSection) this.manager.selectedRemoveKeywordIds.add(keywordId);
        else this.manager.selectedKeywordIds.add(keywordId);
      } else {
        if (isGroupSection) this.manager.selectedRemoveKeywordIds.delete(keywordId);
        else this.manager.selectedKeywordIds.delete(keywordId);
      }
    });

    this.manager.ui.updateMatchingUI();
    this.manager.ui.updateSelectAllButtons();
  }

  /**
   * 그룹에 키워드 연결
   */
  async applyGroupKeywords() {
    if (!this.manager.selectedGroupId || this.manager.selectedKeywordIds.size === 0) {
      showError("그룹과 키워드를 선택해주세요.");
      return;
    }

    try {
      const response = await fetch(`/api/labels/groups/${this.manager.selectedGroupId}/keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword_ids: Array.from(this.manager.selectedKeywordIds) }),
      });

      if (!response.ok) throw new Error("키워드 연결 실패");

      showSuccess(`${this.manager.selectedKeywordIds.size}개의 키워드가 그룹에 연결되었습니다.`);
      this.manager.selectedKeywordIds.clear();
      this.manager.ui.updateMatchingUI();
      await this.manager.crud.loadGroups();
      await this.loadKeywords();
    } catch (error) {
      console.error("키워드 연결 실패:", error);
      showError("키워드 연결 중 오류가 발생했습니다.");
    }
  }

  /**
   * 그룹에서 키워드 제거
   */
  async removeGroupKeywords() {
    if (!this.manager.selectedGroupId || this.manager.selectedRemoveKeywordIds.size === 0) {
      showError("제외할 키워드를 선택해주세요.");
      return;
    }

    try {
      const removePromises = Array.from(this.manager.selectedRemoveKeywordIds).map((keywordId) =>
        fetch(`/api/labels/groups/${this.manager.selectedGroupId}/keywords/${keywordId}`, { method: "DELETE" })
      );

      const results = await Promise.all(removePromises);
      const failed = results.filter((r) => !r.ok);

      if (failed.length > 0) throw new Error("일부 키워드 제외 실패");

      showSuccess(`${this.manager.selectedRemoveKeywordIds.size}개의 키워드가 그룹에서 제외되었습니다.`);
      this.manager.selectedRemoveKeywordIds.clear();
      this.manager.ui.updateMatchingUI();
      await this.manager.crud.loadGroups();
      await this.loadKeywords();
    } catch (error) {
      console.error("키워드 제외 실패:", error);
      showError("키워드 제외 중 오류가 발생했습니다.");
    }
  }

  /**
   * 그룹에 키워드 추가 (이름 기반)
   */
  async addKeywordsToGroup(groupId, keywordNames) {
    try {
      const cleanedKeywords = cleanArray(keywordNames);
      if (cleanedKeywords.length === 0) {
        showError("추가할 키워드가 없습니다.");
        return;
      }

      const response = await fetch(`/api/labels/groups/${groupId}/keywords`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword_names: cleanedKeywords }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "키워드 추가 실패");
      }

      const result = await response.json();
      let message = `${result.added_count || cleanedKeywords.length}개의 키워드가 그룹에 추가되었습니다.`;
      if (result.skipped_count > 0) {
        message += ` (${result.skipped_count}개는 이미 그룹에 속함)`;
      }

      if (result.errors && result.errors.length > 0) {
        console.warn("키워드 추가 경고:", result.errors);
        showError(`일부 키워드 추가 실패 (${result.error_count}개)`);
      } else {
        showSuccess(message);
      }

      await this.manager.crud.loadGroups();
      await this.loadKeywords();
    } catch (error) {
      console.error("키워드 추가 실패:", error);
      throw error;
    }
  }
}
