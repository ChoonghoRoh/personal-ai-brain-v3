/**
 * 키워드 그룹 CRUD 모듈
 * 그룹 생성, 읽기, 수정, 삭제 기능을 제공하는 클래스
 */
class KeywordGroupCRUD {
  constructor(manager) {
    this.manager = manager; // KeywordGroupManager 인스턴스 참조
  }

  /**
   * 그룹 목록 로드
   */
  async loadGroups() {
    try {
      const response = await fetch("/api/labels/groups");
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(errorData.detail || `서버 오류 (${response.status})`);
      }
      
      const groups = await response.json();

      const groupsList = document.getElementById(this.manager.groupsListId);
      if (!groupsList) return;
      groupsList.innerHTML = "";

      groups.forEach((group) => {
        const card = this.createGroupCard(group);
        groupsList.appendChild(card);
        this.loadGroupKeywordsCount(group.id);
      });

      this.manager.onGroupChange();
    } catch (error) {
      console.error("그룹 로드 실패:", error);
      
      // 네트워크 오류와 API 오류 구분
      let errorMessage = "그룹 목록을 불러오는 중 오류가 발생했습니다.";
      if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showError(errorMessage);
    }
  }

  /**
   * 그룹 카드 생성
   */
  createGroupCard(group) {
    const card = document.createElement("div");
    card.className = "group-card";
    card.dataset.groupId = group.id;
    if (group.color) {
      card.style.borderLeftColor = group.color;
    }
    card.onclick = () => this.manager.matching.selectGroup(group.id);

    card.innerHTML = `
      <div class="group-card-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px">
        <div style="flex: 1; min-width: 0">
          <div class="group-card-name" style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 600; color: #1f2937; margin-bottom: 4px">${
            escapeHtml(group.name)
          }</div>
          ${
            group.description
              ? `<div class="group-card-description" style="font-size: 13px; color: #6b7280; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">${escapeHtml(group.description)}</div>`
              : ""
          }
        </div>
        <div style="display: flex; gap: 5px; align-items: center; flex-shrink: 0; margin-left: 10px">
          <button class="btn btn-small" style="padding: 8px 16px; font-size: 22px; background: #f3f4f6; color: #333; line-height: 1" onclick="event.stopPropagation(); window.groupManager.showEditGroupModal(${
            group.id
          })" title="수정">
            ✏️
          </button>
          <button class="btn btn-small" style="padding: 8px 16px; font-size: 22px; background: #fee2e2; color: #991b1b; line-height: 1" onclick="event.stopPropagation(); window.groupManager.deleteGroup(${
            group.id
          })" title="삭제">
            🗑️
          </button>
        </div>
      </div>
      <div class="group-card-keywords-count" style="font-size: 12px; color: #9ca3af">키워드: <span id="group-${group.id}-count">0</span>개</div>
    `;

    return card;
  }

  /**
   * 그룹 키워드 수 로드
   */
  async loadGroupKeywordsCount(groupId) {
    try {
      const response = await fetch(`/api/labels/groups/${groupId}/keywords`);
      
      if (!response.ok) {
        // 키워드 수 로드는 실패해도 전체 기능에 영향을 주지 않으므로 조용히 실패
        console.warn(`그룹 ${groupId}의 키워드 수를 불러올 수 없습니다: ${response.status}`);
        return;
      }
      
      const keywords = await response.json();
      const countElement = document.getElementById(`group-${groupId}-count`);
      if (countElement) {
        countElement.textContent = keywords.length;
      }
    } catch (error) {
      // 키워드 수 로드는 실패해도 전체 기능에 영향을 주지 않으므로 조용히 실패
      console.warn("그룹 키워드 수 로드 실패:", error);
    }
  }

  /**
   * 그룹 생성 모달 표시
   */
  showCreateGroupModal() {
    this.manager.editingGroupId = null;
    const modal = document.getElementById(this.manager.modalId);
    const title = document.getElementById(this.manager.modalTitleId);
    const submitBtn = document.getElementById(this.manager.modalSubmitBtnId);

    if (modal) {
      modal.style.display = "flex";
      title.textContent = "새 키워드 그룹 생성";
      submitBtn.textContent = "생성";

      document.getElementById("create-group-form").reset();
      document.getElementById(this.manager.suggestedKeywordsContainerId).style.display = "none";
      this.manager.selectedSuggestedKeywords.clear();

      const errorDiv = document.getElementById(this.manager.suggestionErrorId);
      const successDiv = document.getElementById(this.manager.suggestionSuccessId);
      if (errorDiv) {
        errorDiv.style.display = "none";
        errorDiv.textContent = "";
      }
      if (successDiv) {
        successDiv.style.display = "none";
        successDiv.textContent = "";
      }

      document.getElementById(this.manager.groupNameInputId).focus();

      modal.onclick = (e) => {
        if (e.target === modal) {
          this.closeCreateGroupModal();
        }
      };
    }
  }

  /**
   * 그룹 수정 모달 표시
   */
  async showEditGroupModal(groupId) {
    try {
      const response = await fetch(`/api/labels/groups/${groupId}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
        throw new Error(errorData.detail || `서버 오류 (${response.status})`);
      }

      const group = await response.json();
      this.manager.editingGroupId = groupId;

      const modal = document.getElementById(this.manager.modalId);
      const title = document.getElementById(this.manager.modalTitleId);
      const submitBtn = document.getElementById(this.manager.modalSubmitBtnId);

      modal.style.display = "flex";
      title.textContent = "키워드 그룹 수정";
      submitBtn.textContent = "수정";

      document.getElementById(this.manager.groupNameInputId).value = group.name || "";
      document.getElementById(this.manager.groupDescriptionInputId).value = group.description || "";
      document.getElementById(this.manager.groupColorInputId).value = group.color || "";
      document.getElementById(this.manager.suggestedKeywordsContainerId).style.display = "none";
      this.manager.selectedSuggestedKeywords.clear();

      const errorDiv = document.getElementById(this.manager.suggestionErrorId);
      const successDiv = document.getElementById(this.manager.suggestionSuccessId);
      if (errorDiv) {
        errorDiv.style.display = "none";
        errorDiv.textContent = "";
      }
      if (successDiv) {
        successDiv.style.display = "none";
        successDiv.textContent = "";
      }

      modal.onclick = (e) => {
        if (e.target === modal) {
          this.closeCreateGroupModal();
        }
      };
    } catch (error) {
      console.error("그룹 정보 로드 실패:", error);
      
      // 네트워크 오류와 API 오류 구분
      let errorMessage = "그룹 정보를 불러오는 중 오류가 발생했습니다.";
      if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      showError(errorMessage);
    }
  }

  /**
   * 그룹 생성 모달 닫기
   */
  closeCreateGroupModal() {
    const modal = document.getElementById(this.manager.modalId);
    if (modal) {
      modal.style.display = "none";
    }
  }

  /**
   * 그룹 생성/수정 처리
   */
  async handleCreateGroup(event) {
    event.preventDefault();

    const name = document.getElementById(this.manager.groupNameInputId).value.trim();
    const description = document.getElementById(this.manager.groupDescriptionInputId).value.trim();
    const color = document.getElementById(this.manager.groupColorInputId).value.trim();

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
      await this.updateGroup(this.manager.editingGroupId, name, description || null, validColor);
      // 문제 2: 수정 시에도 선택된 키워드 추가
      const suggestedKeywords = Array.from(this.manager.selectedSuggestedKeywords);
      if (suggestedKeywords.length > 0) {
        try {
          await this.manager.matching.addKeywordsToGroup(this.manager.editingGroupId, suggestedKeywords);
          showSuccess(`그룹이 수정되었고 ${suggestedKeywords.length}개의 키워드가 추가되었습니다.`);
        } catch (keywordError) {
          console.error("키워드 추가 실패:", keywordError);
          showSuccess("그룹이 수정되었습니다. (키워드 추가 실패)");
        }
      }
    } else {
      await this.createGroup(name, description || null, validColor);
    }
    this.closeCreateGroupModal();
  }

  /**
   * 그룹 생성
   */
  async createGroup(name, description, color) {
    try {
      const payload = {
        name: name,
        description: description || null,
        color: color || null,
      };

      const response = await fetch("/api/labels/groups", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
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

      await this.loadGroups();
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
      const payload = {
        name: name,
        description: description || null,
        color: color || null,
      };

      const response = await fetch(`/api/labels/groups/${groupId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "그룹 수정 실패");
      }

      showSuccess("그룹이 수정되었습니다.");
      await this.loadGroups();
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
      if (!impactResponse.ok) {
        throw new Error("영향도 정보를 불러올 수 없습니다.");
      }
      const impact = await impactResponse.json();

      let message = `다음 키워드 그룹을 삭제하시겠습니까?\n\n`;
      message += `그룹: ${escapeHtml(impact.group_name)}\n\n`;
      message += `⚠️ 영향도:\n`;
      message += `- 이 그룹에 속한 키워드: ${impact.keywords_count}개\n`;
      if (impact.chunks_count > 0) {
        message += `- 이 그룹의 키워드가 붙은 청크: ${impact.chunks_count}개 (간접 영향)\n`;
      }
      message += `\n⚠️ 주의사항:\n`;
      message += `- 그룹에 속한 키워드는 그룹에서 해제됩니다 (키워드 자체는 삭제되지 않음)\n`;
      message += `- 삭제 후 복구할 수 없습니다.`;

      if (!confirm(message)) {
        return;
      }

      const response = await fetch(`/api/labels/groups/${groupId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "그룹 삭제 실패");
      }

      showSuccess("그룹이 삭제되었습니다.");
      await this.loadGroups();
      await this.manager.matching.loadKeywords();
    } catch (error) {
      console.error("그룹 삭제 실패:", error);
      showError(error.message || "그룹 삭제 중 오류가 발생했습니다.");
    }
  }
}
