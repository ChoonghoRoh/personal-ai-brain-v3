/**
 * 키워드 그룹 CRUD 모듈
 * 그룹 생성, 읽기, 수정, 삭제 기능 + 3단 레이아웃 상세 패널 관리
 */
class KeywordGroupCRUD {
  constructor(manager) {
    this.manager = manager;
    this.currentPage = 1;
    this.pageSize = 20;
    this.totalGroups = 0;
    this.groups = []; // 현재 페이지 그룹 목록 캐시
  }

  /**
   * 그룹 목록 로드 (페이지네이션)
   */
  async loadGroups(page) {
    if (page !== undefined) this.currentPage = page;

    try {
      const q = document.getElementById(this.manager.searchInputId)?.value.trim() || "";
      const params = new URLSearchParams({
        page: this.currentPage,
        size: this.pageSize,
      });
      if (q) params.set("q", q);

      const response = await fetch(`/api/labels/groups?${params}`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
        throw new Error(errorData.detail || `서버 오류 (${response.status})`);
      }

      const data = await response.json();

      // 페이지네이션 모드 응답
      if (data.items) {
        this.groups = data.items;
        this.totalGroups = data.total;
      } else {
        // 레거시 배열 응답
        this.groups = data;
        this.totalGroups = data.length;
      }

      this.renderGroupsList();
      this.renderPagination();
      this.manager.onGroupChange();

      // 최초 로드 시 첫 번째 그룹 자동 선택
      if (!this.manager.selectedGroupId && this.groups.length > 0) {
        this.manager.matching.selectGroup(this.groups[0].id);
      } else if (this.manager.selectedGroupId) {
        // 현재 선택된 그룹이 이 페이지에 있으면 상세 다시 렌더링
        const exists = this.groups.find(g => g.id === this.manager.selectedGroupId);
        if (exists) {
          this.renderDetailPanel(exists);
        }
      }
    } catch (error) {
      console.error("그룹 로드 실패:", error);
      showError(error.message || "그룹 목록을 불러오는 중 오류가 발생했습니다.");
    }
  }

  /**
   * 그룹 목록 렌더링
   */
  renderGroupsList() {
    const groupsList = document.getElementById(this.manager.groupsListId);
    if (!groupsList) return;
    groupsList.innerHTML = "";

    if (this.groups.length === 0) {
      groupsList.innerHTML = '<div class="detail-empty-state"><p>그룹이 없습니다</p></div>';
      return;
    }

    this.groups.forEach((group) => {
      const card = this.createGroupCard(group);
      groupsList.appendChild(card);
      this.loadGroupKeywordsCount(group.id);
    });
  }

  /**
   * 페이지네이션 렌더링
   */
  renderPagination() {
    const container = document.getElementById("groups-pagination");
    if (!container) return;
    container.innerHTML = "";

    const totalPages = Math.ceil(this.totalGroups / this.pageSize);
    if (totalPages <= 1) return;

    // 이전 버튼
    const prevBtn = document.createElement("button");
    prevBtn.className = "pagination-btn";
    prevBtn.textContent = "<";
    prevBtn.disabled = this.currentPage <= 1;
    prevBtn.onclick = () => this.loadGroups(this.currentPage - 1);
    container.appendChild(prevBtn);

    // 페이지 번호
    const startPage = Math.max(1, this.currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);

    for (let i = startPage; i <= endPage; i++) {
      const pageBtn = document.createElement("button");
      pageBtn.className = `pagination-btn${i === this.currentPage ? " active" : ""}`;
      pageBtn.textContent = i;
      pageBtn.onclick = () => this.loadGroups(i);
      container.appendChild(pageBtn);
    }

    // 다음 버튼
    const nextBtn = document.createElement("button");
    nextBtn.className = "pagination-btn";
    nextBtn.textContent = ">";
    nextBtn.disabled = this.currentPage >= totalPages;
    nextBtn.onclick = () => this.loadGroups(this.currentPage + 1);
    container.appendChild(nextBtn);

    // 총 개수 표시
    const info = document.createElement("span");
    info.className = "pagination-info";
    info.textContent = `(${this.totalGroups}개)`;
    container.appendChild(info);
  }

  /**
   * 그룹 카드 생성 (간소화 — 수정/삭제 버튼은 상세 패널로 이동)
   */
  createGroupCard(group) {
    const card = document.createElement("div");
    card.className = "group-card";
    card.dataset.groupId = group.id;
    if (group.color) {
      card.style.borderLeftColor = group.color;
    }
    if (this.manager.selectedGroupId === group.id) {
      card.classList.add("selected");
    }
    card.onclick = () => this.manager.matching.selectGroup(group.id);

    card.innerHTML = `
      <div class="group-card-name">${escapeHtml(group.name)}</div>
      ${group.description ? `<div class="group-card-description">${escapeHtml(group.description)}</div>` : ""}
      <div class="group-card-keywords-count">키워드: <span id="group-${group.id}-count">0</span>개</div>
    `;

    return card;
  }

  /**
   * 그룹 키워드 수 로드
   */
  async loadGroupKeywordsCount(groupId) {
    try {
      const response = await fetch(`/api/labels/groups/${groupId}/keywords`);
      if (!response.ok) return;
      const keywords = await response.json();
      const countElement = document.getElementById(`group-${groupId}-count`);
      if (countElement) countElement.textContent = keywords.length;
    } catch (error) {
      console.warn("그룹 키워드 수 로드 실패:", error);
    }
  }

  // ============================
  // 상세 패널 (2단) — 편집 모드 직접 표시
  // ============================

  /** 상세 패널 렌더링 (편집 폼 직접 표시) */
  renderDetailPanel(group) {
    const panel = document.getElementById("group-detail-panel");
    if (!panel) return;
    this.manager.editingGroupId = group.id;
    panel.innerHTML = this._buildEditFormHTML(group, false);
    if (typeof loadOllamaModelOptions === "function") {
      loadOllamaModelOptions("keyword-suggestion-model");
    }
  }

  /** 레거시 호환: showEditGroupInline은 이제 renderDetailPanel을 호출 */
  async showEditGroupInline(groupId) {
    try {
      const response = await fetch(`/api/labels/groups/${groupId}`);
      if (!response.ok) throw new Error("그룹 정보를 불러올 수 없습니다.");
      const group = await response.json();
      this.renderDetailPanel(group);
      document.getElementById("group-name-input")?.focus();
    } catch (error) {
      console.error("편집 모드 전환 실패:", error);
      showError(error.message);
    }
  }

  /** 새 그룹 생성 모드 */
  showCreateGroupModal() {
    this.manager.editingGroupId = null;
    this.manager.selectedSuggestedKeywords.clear();
    this.manager.selectedGroupId = null;
    this.manager.ui.updateMatchingUI();

    const panel = document.getElementById("group-detail-panel");
    if (!panel) return;

    panel.innerHTML = this._buildEditFormHTML(null, true);
    if (typeof loadOllamaModelOptions === "function") {
      loadOllamaModelOptions("keyword-suggestion-model");
    }
    document.getElementById("group-name-input")?.focus();
  }

  /** 편집/생성 폼 HTML 생성 */
  _buildEditFormHTML(group, isNew) {
    const title = isNew ? '<div style="font-weight:600;color:#2563eb;margin-bottom:12px;font-size:15px">새 키워드 그룹 생성</div>' : '';
    const nameVal = isNew ? '' : escapeHtml(group.name);
    const descVal = isNew ? '' : (group.description ? escapeHtml(group.description) : '');
    const colorVal = isNew ? '#4F46E5' : (group.color || '#4F46E5');
    const colorInputVal = isNew ? '' : (group.color ? escapeHtml(group.color) : '');
    const saveBtn = isNew ? '생성' : '저장';
    const deleteBtn = isNew ? '' : '<button type="button" class="btn btn-danger btn-small" onclick="window.groupManager.deleteGroup(' + group.id + ')">삭제</button>';

    return `
      <div class="detail-edit-mode">
        ${title}
        <div class="form-group">
          <label>그룹 이름 *</label>
          <input type="text" id="group-name-input" value="${nameVal}" required placeholder="예: AI 인프라" />
        </div>
        <div class="form-group">
          <label>설명</label>
          <textarea id="group-description-input" rows="3" placeholder="그룹에 대한 설명을 입력하세요">${descVal}</textarea>
          <button type="button" class="btn btn-small btn-suggest" style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 13px; border: none; cursor: pointer; box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3); margin-top: 8px;" onclick="suggestKeywordsFromDescription()">AI 키워드 추천</button>
          <div id="keyword-suggestion-error" style="display:none"></div>
          <div id="keyword-suggestion-success" style="display:none"></div>
          <div class="detail-suggestion-area">
            <div class="form-group">
              <label style="font-size:12px;color:#666">LLM 모델</label>
              <select id="keyword-suggestion-model" style="min-width:180px;padding:6px 10px;font-size:13px;border-radius:6px;border:1px solid #e5e7eb">
                <option value="">기본 (env)</option>
              </select>
            </div>
            <div id="suggested-keywords-container" style="display:none;margin-top:8px;padding:10px;background:#f9fafb;border-radius:6px;border:1px solid #e5e7eb">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="font-size:12px;color:#666;font-weight:500">추천 키워드:</div>
                <button type="button" class="btn btn-small" style="padding:4px 8px;font-size:11px;background:#fee2e2;color:#991b1b" onclick="clearSuggestedKeywords()">전체삭제</button>
              </div>
              <div id="suggested-keywords-list" style="display:flex;flex-wrap:wrap;gap:6px"></div>
            </div>
          </div>
        </div>
        <div class="form-group">
          <label>색상 코드</label>
          <div style="display: flex; align-items: center; gap: 8px">
            <input type="color" id="group-color-picker" value="${colorVal}" style="width: 40px; height: 36px; border: 1px solid #e5e7eb; border-radius: 6px; cursor: pointer; padding: 2px" onchange="document.getElementById('group-color-input').value = this.value" />
            <input type="text" id="group-color-input" value="${colorInputVal}" placeholder="#4F46E5" pattern="^#[0-9A-Fa-f]{6}$" style="flex: 1" oninput="try{document.getElementById('group-color-picker').value = this.value}catch(e){}" />
          </div>
          <small style="color:#666;font-size:12px;display:block;margin-top:4px">16진수 색상 코드 (예: #4F46E5)</small>
        </div>
        <div class="detail-edit-actions">
          <button type="button" class="btn btn-secondary-light btn-small" onclick="window.groupManager.cancelEditInline()">취소</button>
          ${deleteBtn}
          <button type="button" class="btn btn-primary btn-small" onclick="window.groupManager.saveEditInline()">${saveBtn}</button>
        </div>
      </div>
    `;
  }

  /** 편집/생성 취소 */
  cancelEditInline() {
    this.manager.editingGroupId = null;
    this.manager.selectedSuggestedKeywords.clear();

    if (this.manager.selectedGroupId) {
      const group = this.groups.find(g => g.id === this.manager.selectedGroupId);
      if (group) {
        this.renderDetailPanel(group);
        return;
      }
    }

    const panel = document.getElementById("group-detail-panel");
    if (panel) {
      panel.innerHTML = '<div class="detail-empty-state"><p>좌측에서 그룹을 선택하세요</p></div>';
    }
  }

  /**
   * 인라인 저장 (생성 또는 수정)
   */
  async saveEditInline() {
    const name = document.getElementById("group-name-input")?.value.trim();
    const description = document.getElementById("group-description-input")?.value.trim();
    const color = document.getElementById("group-color-input")?.value.trim();

    if (!name) {
      showError("그룹 이름을 입력해주세요.");
      return;
    }

    let validColor = null;
    if (color) {
      if (!validateColorCode(color)) {
        showError("올바른 색상 코드 형식이 아닙니다. (예: #4F46E5)");
        return;
      }
      validColor = color;
    }

    if (this.manager.editingGroupId) {
      // 수정
      await this.updateGroup(this.manager.editingGroupId, name, description || null, validColor);
      // 추천 키워드 추가
      const suggestedKeywords = Array.from(this.manager.selectedSuggestedKeywords);
      if (suggestedKeywords.length > 0) {
        try {
          await this.manager.matching.addKeywordsToGroup(this.manager.editingGroupId, suggestedKeywords);
          showSuccess(`그룹이 수정되었고 ${suggestedKeywords.length}개의 키워드가 추가되었습니다.`);
        } catch (keywordError) {
          console.error("키워드 추가 실패:", keywordError);
          showError("키워드 추가 중 오류가 발생했습니다: " + (keywordError.message || "알 수 없는 오류"));
        }
      }
      this.manager.editingGroupId = null;
    } else {
      // 생성
      await this.createGroup(name, description || null, validColor);
    }
  }

  /**
   * 그룹 생성
   */
  async createGroup(name, description, color) {
    try {
      const response = await fetch("/api/labels/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description: description || null, color: color || null }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "그룹 생성 실패");
      }

      const result = await response.json();

      const suggestedKeywords = Array.from(this.manager.selectedSuggestedKeywords);
      if (suggestedKeywords.length > 0 && result.id) {
        try {
          await this.manager.matching.addKeywordsToGroup(result.id, suggestedKeywords);
          showSuccess(`그룹이 생성되었고 ${suggestedKeywords.length}개의 키워드가 자동으로 연결되었습니다.`);
        } catch (keywordError) {
          console.error("키워드 자동 연결 실패:", keywordError);
          showSuccess("그룹이 생성되었습니다. (키워드 자동 연결 실패)");
        }
      } else {
        showSuccess("그룹이 생성되었습니다.");
      }

      this.manager.selectedSuggestedKeywords.clear();
      // 생성된 그룹 자동 선택
      this.manager.selectedGroupId = result.id;
      await this.loadGroups();
      // 트리 동기화
      if (this.manager && this.manager.treeView) {
        await this.manager.treeView.loadTree();
      }
      await this.manager.matching.loadKeywords();
    } catch (error) {
      console.error("그룹 생성 실패:", error);
      showError(error.message || "그룹 생성 중 오류가 발생했습니다.");
    }
  }

  /**
   * 그룹 수정
   */
  async updateGroup(groupId, name, description, color) {
    try {
      const response = await fetch(`/api/labels/groups/${groupId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description: description || null, color: color || null }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "그룹 수정 실패");
      }

      showSuccess("그룹이 수정되었습니다.");
      await this.loadGroups();
      // 트리 동기화
      if (this.manager && this.manager.treeView) {
        await this.manager.treeView.loadTree();
      }
    } catch (error) {
      console.error("그룹 수정 실패:", error);
      showError(error.message || "그룹 수정 중 오류가 발생했습니다.");
    }
  }

  /**
   * 그룹 삭제 (영향도 조회 포함)
   */
  async deleteGroup(groupId) {
    try {
      const impactResponse = await fetch(`/api/labels/groups/${groupId}/impact`);
      if (!impactResponse.ok) throw new Error("영향도 정보를 불러올 수 없습니다.");
      const impact = await impactResponse.json();

      let message = `다음 키워드 그룹을 삭제하시겠습니까?\n\n`;
      message += `그룹: ${impact.group_name}\n\n`;
      message += `영향도:\n`;
      message += `- 이 그룹에 속한 키워드: ${impact.keywords_count}개\n`;
      if (impact.chunks_count > 0) {
        message += `- 이 그룹의 키워드가 붙은 청크: ${impact.chunks_count}개 (간접 영향)\n`;
      }
      message += `\n주의: 그룹에 속한 키워드는 그룹에서 해제됩니다.\n삭제 후 복구할 수 없습니다.`;

      if (!confirm(message)) return;

      const response = await fetch(`/api/labels/groups/${groupId}`, { method: "DELETE" });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "그룹 삭제 실패");
      }

      showSuccess("그룹이 삭제되었습니다.");
      this.manager.selectedGroupId = null;
      this.manager.editingGroupId = null;

      // 상세 패널 초기화
      const panel = document.getElementById("group-detail-panel");
      if (panel) {
        panel.innerHTML = '<div class="detail-empty-state"><p>좌측에서 그룹을 선택하세요</p></div>';
      }

      await this.loadGroups();
      // 트리 동기화
      if (this.manager && this.manager.treeView) {
        await this.manager.treeView.loadTree();
      }
      await this.manager.matching.loadKeywords();
    } catch (error) {
      console.error("그룹 삭제 실패:", error);
      showError(error.message || "그룹 삭제 중 오류가 발생했습니다.");
    }
  }

  // ========== 레거시 호환 (모달) ==========
  // 모달은 더 이상 사용하지 않지만 기존 글로벌 함수가 호출할 수 있으므로 인라인으로 전환
  closeCreateGroupModal() {
    this.cancelEditInline();
  }

  showEditGroupModal(groupId) {
    return this.showEditGroupInline(groupId);
  }

  async handleCreateGroup(event) {
    if (event) event.preventDefault();
    return this.saveEditInline();
  }
}
