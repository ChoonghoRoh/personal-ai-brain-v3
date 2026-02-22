/**
 * 키워드 그룹 매칭 모듈
 * 키워드 선택, 연결, 제거 기능 + 3단 레이아웃 키워드 영역 관리
 */
class KeywordGroupMatching {
  constructor(manager) {
    this.manager = manager;
    this.keywordPage = 1;
    this.keywordPageSize = 20;
    this.keywordTotal = 0;
    this.groupKeywordPage = 1;
    this.groupKeywordPageSize = 20;
    this.groupKeywordTotal = 0;
    this._keywordSearchTimer = null;
  }

  /**
   * 키워드 검색 (디바운스)
   */
  searchKeywords() {
    clearTimeout(this._keywordSearchTimer);
    this._keywordSearchTimer = setTimeout(() => {
      this.keywordPage = 1;
      this.groupKeywordPage = 1;
      this.loadKeywords();
    }, 300);
  }

  /**
   * 키워드 목록 로드 (3단 영역, 검색 + 페이지네이션)
   */
  async loadKeywords() {
    try {
      const q = document.getElementById("keyword-search-input")?.value.trim() || "";
      const offset = (this.keywordPage - 1) * this.keywordPageSize;
      const params = new URLSearchParams({ label_type: "keyword", limit: this.keywordPageSize, offset });
      if (q) params.set("q", q);

      const keywordsList = document.getElementById(this.manager.keywordsListId);
      if (!keywordsList) return;
      keywordsList.innerHTML = "";

      if (this.manager.selectedGroupId) {
        // 그룹 선택 시: 그룹 키워드 전체를 별도 API로 fetch
        const [groupKwResponse, otherKwResponse] = await Promise.all([
          fetch(`/api/labels/groups/${this.manager.selectedGroupId}/keywords`),
          fetch("/api/labels?" + params.toString()),
        ]);

        let allGroupKeywords = await groupKwResponse.json();
        const otherData = await otherKwResponse.json();
        const otherRaw = Array.isArray(otherData) ? otherData : (otherData.items || []);
        const otherTotal = Array.isArray(otherData) ? otherRaw.length : (otherData.total || 0);

        // 검색어가 있으면 그룹 키워드에 client-side 필터 적용
        if (q) {
          const lowerQ = q.toLowerCase();
          allGroupKeywords = allGroupKeywords.filter(kw => kw.name.toLowerCase().includes(lowerQ));
        }

        // 그룹 키워드 client-side 페이징
        this.groupKeywordTotal = allGroupKeywords.length;
        const groupStart = (this.groupKeywordPage - 1) * this.groupKeywordPageSize;
        const groupKeywords = allGroupKeywords.slice(groupStart, groupStart + this.groupKeywordPageSize);

        // 그룹 키워드 ID Set으로 기타 목록에서 중복 제거
        const groupKwIdSet = new Set(allGroupKeywords.map(kw => kw.id));
        const otherKeywords = otherRaw.filter(kw => !groupKwIdSet.has(kw.id));

        if (allGroupKeywords.length > 0) {
          keywordsList.appendChild(this.createKeywordSection("group", groupKeywords, true, this.groupKeywordTotal));
        }

        if (otherKeywords.length > 0) {
          keywordsList.appendChild(this.createKeywordSection("other", otherKeywords, false, otherTotal));
        }

        if (allGroupKeywords.length === 0 && otherKeywords.length === 0) {
          keywordsList.innerHTML = '<div style="padding:20px;color:#9ca3af;text-align:center">키워드가 없습니다</div>';
        }

        // 기타 키워드 total 저장
        this.keywordTotal = otherTotal;
      } else {
        // 그룹 미선택 시: 기존 전역 fetch 유지
        const response = await fetch("/api/labels?" + params.toString());
        const keywordsData = await response.json();
        const keywords = Array.isArray(keywordsData) ? keywordsData : (keywordsData.items || []);
        const total = Array.isArray(keywordsData) ? keywords.length : (keywordsData.total || 0);

        const keywordsContainer = document.createElement("div");
        keywordsContainer.style.cssText = "display: flex; flex-wrap: wrap; gap: 8px";

        keywords.forEach((keyword) => {
          const badge = this.createKeywordBadge(keyword, false);
          keywordsContainer.appendChild(badge);
        });

        keywordsList.appendChild(keywordsContainer);
        this.keywordTotal = total;
      }

      // 그룹 선택 시: 각 섹션 내부에 페이지네이션이 있으므로 전역 페이지네이션 숨김
      const globalPagination = document.getElementById("keywords-pagination");
      if (globalPagination) {
        globalPagination.style.display = this.manager.selectedGroupId ? "none" : "";
      }
      if (!this.manager.selectedGroupId) {
        this.renderKeywordsPagination();
      }
      this.manager.ui.updateMatchingUI();
      this.manager.onKeywordChange();
    } catch (error) {
      console.error("키워드 로드 실패:", error);
      showError("키워드 목록을 불러오는 중 오류가 발생했습니다.");
    }
  }

  /**
   * 키워드 페이지네이션 렌더링
   */
  renderKeywordsPagination() {
    const container = document.getElementById("keywords-pagination");
    if (!container) return;
    container.innerHTML = "";

    const totalPages = Math.ceil(this.keywordTotal / this.keywordPageSize);
    if (totalPages <= 1) return;

    const prevBtn = document.createElement("button");
    prevBtn.className = "pagination-btn";
    prevBtn.textContent = "<";
    prevBtn.disabled = this.keywordPage <= 1;
    prevBtn.onclick = () => { this.keywordPage--; this.loadKeywords(); };
    container.appendChild(prevBtn);

    const startPage = Math.max(1, this.keywordPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);

    for (let i = startPage; i <= endPage; i++) {
      const pageBtn = document.createElement("button");
      pageBtn.className = "pagination-btn" + (i === this.keywordPage ? " active" : "");
      pageBtn.textContent = i;
      pageBtn.onclick = () => { this.keywordPage = i; this.loadKeywords(); };
      container.appendChild(pageBtn);
    }

    const nextBtn = document.createElement("button");
    nextBtn.className = "pagination-btn";
    nextBtn.textContent = ">";
    nextBtn.disabled = this.keywordPage >= totalPages;
    nextBtn.onclick = () => { this.keywordPage++; this.loadKeywords(); };
    container.appendChild(nextBtn);

    const info = document.createElement("span");
    info.className = "pagination-info";
    info.textContent = "(" + this.keywordTotal + "개)";
    container.appendChild(info);
  }

  /**
   * 키워드 섹션 생성
   */
  createKeywordSection(sectionType, keywords, isGroupSection, totalCount) {
    const sectionContainer = document.createElement("div");
    sectionContainer.className = "keyword-section";

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
    keywordsContainer.className = "keyword-section-body";
    keywordsContainer.dataset.section = sectionType;

    keywords.forEach((keyword) => {
      const badge = this.createKeywordBadge(keyword, isGroupSection);
      keywordsContainer.appendChild(badge);
    });

    sectionContainer.appendChild(keywordsContainer);

    // 섹션별 페이지네이션
    const pageSize = isGroupSection ? this.groupKeywordPageSize : this.keywordPageSize;
    const totalPages = Math.ceil((totalCount || 0) / pageSize);
    if (totalPages > 1) {
      const paginationDiv = this._renderSectionPagination(sectionType, isGroupSection, totalPages, totalCount || 0);
      sectionContainer.appendChild(paginationDiv);
    }

    return sectionContainer;
  }

  /**
   * 섹션별 페이지네이션 렌더링
   */
  _renderSectionPagination(sectionType, isGroupSection, totalPages, totalCount) {
    const currentPage = isGroupSection ? this.groupKeywordPage : this.keywordPage;

    const container = document.createElement("div");
    container.className = "groups-pagination";

    const prevBtn = document.createElement("button");
    prevBtn.className = "pagination-btn";
    prevBtn.textContent = "<";
    prevBtn.disabled = currentPage <= 1;
    prevBtn.onclick = () => {
      if (isGroupSection) { this.groupKeywordPage--; }
      else { this.keywordPage--; }
      this.loadKeywords();
    };
    container.appendChild(prevBtn);

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);

    for (let i = startPage; i <= endPage; i++) {
      const pageBtn = document.createElement("button");
      pageBtn.className = "pagination-btn" + (i === currentPage ? " active" : "");
      pageBtn.textContent = i;
      pageBtn.onclick = () => {
        if (isGroupSection) { this.groupKeywordPage = i; }
        else { this.keywordPage = i; }
        this.loadKeywords();
      };
      container.appendChild(pageBtn);
    }

    const nextBtn = document.createElement("button");
    nextBtn.className = "pagination-btn";
    nextBtn.textContent = ">";
    nextBtn.disabled = currentPage >= totalPages;
    nextBtn.onclick = () => {
      if (isGroupSection) { this.groupKeywordPage++; }
      else { this.keywordPage++; }
      this.loadKeywords();
    };
    container.appendChild(nextBtn);

    const info = document.createElement("span");
    info.className = "pagination-info";
    info.textContent = "(" + totalCount + "개)";
    container.appendChild(info);

    return container;
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

    // 트리 선택 상태 동기화
    if (this.manager.treeView) {
      this.manager.treeView.selectedNodeId = this.manager.selectedGroupId;
      // 트리 DOM 하이라이트 직접 갱신 (전체 re-render 없이)
      var allContents = document.querySelectorAll("#groups-tree .tree-node-content");
      allContents.forEach(function (el) { el.classList.remove("selected"); });
      if (this.manager.selectedGroupId) {
        var selectedNode = document.querySelector('#groups-tree .tree-node[data-node-id="' + this.manager.selectedGroupId + '"] > .tree-node-content');
        if (selectedNode) {
          selectedNode.classList.add("selected");
        }
      }
    }

    if (this.manager.selectedGroupId) {
      this.manager.selectedKeywordIds.clear();
      this.manager.selectedRemoveKeywordIds.clear();
      this.manager.selectedKeywordForGroupCheck = null;
      this.groupKeywordPage = 1;
      this.keywordPage = 1;

      // 상세 패널 업데이트 (트리에서 선택 시 crud.groups 없을 수 있음 → API로 조회)
      const groupFromList = this.manager.crud.groups.find(g => g.id === groupId);
      if (groupFromList) {
        this.manager.crud.renderDetailPanel(groupFromList);
      } else {
        fetch("/api/labels/groups/" + groupId)
          .then((res) => (res.ok ? res.json() : Promise.reject(new Error("그룹 조회 실패"))))
          .then((group) => {
            if (this.manager.selectedGroupId === group.id) {
              this.manager.crud.renderDetailPanel(group);
            }
          })
          .catch((err) => {
            console.error("그룹 상세 로드 실패:", err);
            showError(err.message || "그룹 정보를 불러올 수 없습니다.");
          });
      }
    } else {
      // 선택 해제 시 상세 패널 초기화
      const panel = document.getElementById("group-detail-panel");
      if (panel) {
        panel.innerHTML = '<div class="detail-empty-state"><p>좌측에서 그룹을 선택하세요</p></div>';
      }
    }

    // 하단 액션바 그룹 액션 버튼 상태 업데이트
    const groupActionButtons = document.getElementById("group-action-buttons");
    if (groupActionButtons) {
      groupActionButtons.style.display = this.manager.selectedGroupId ? "flex" : "none";
    }

    // 유사 키워드 섹션 상태 업데이트
    const relatedSection = document.getElementById("related-keywords-section");
    if (relatedSection) {
      relatedSection.style.display = this.manager.selectedGroupId ? "block" : "none";
      if (!this.manager.selectedGroupId) {
        document.getElementById("related-keywords-list").innerHTML = "";
        document.getElementById("add-related-btn").style.display = "none";
      }
    }

    this.loadKeywords();
    this.manager.ui.updateMatchingUI();

    // 그룹 선택 시 유사 키워드 자동 로드
    if (this.manager.selectedGroupId) {
      const group = this.manager.crud.groups.find(g => g.id === groupId);
      if (group && group.description) {
        if (typeof searchRelatedKeywords === "function") {
          searchRelatedKeywords();
        }
      }
    }
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
