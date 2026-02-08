/**
 * 청크 승인 관리 모듈
 * 청크 승인/거절, 상태 필터링, 상세 보기 기능을 제공하는 클래스
 */
class ChunkApprovalManager {
  constructor(config = {}) {
    // 콜백 함수
    this.onChunkChange = config.onChunkChange || (() => {});

    // 상태 관리
    this.currentStatusFilter = "draft";
    this.pendingChunks = [];

    // 페이징 컴포넌트
    this.pagination = null;
    if (config.enablePagination) {
      this.pagination = new PaginationComponent({
        initialPage: 1,
        initialLimit: config.limit || 20,
        onPageChange: () => this.loadPendingChunks(),
        onLimitChange: () => this.loadPendingChunks(),
      });
    }

    // DOM 요소 ID (기본값) — 우측 청크 상세 패널 사용 (모달 제거)
    this.chunkListId = config.chunkListId || "approval-chunk-list";
    this.detailBodyId = config.detailBodyId || "approval-detail-body";
    this.detailPlaceholderId = config.detailPlaceholderId || "approval-detail-placeholder";
    this.detailContentId = config.detailContentId || "approval-detail-content";
    this.selectedChunkId = null;
    this.lastNewKeywords = [];
    this.lastAiSuggestions = [];
  }

  /**
   * 상태 필터 변경
   */
  async filterByStatus(status) {
    this.currentStatusFilter = status;

    if (this.pagination) {
      this.pagination.currentPage = 1; // 필터 변경 시 첫 페이지로
    }

    // 필터 버튼 활성화 상태 업데이트
    document.querySelectorAll(".status-filter-btn").forEach((btn) => {
      if (btn.dataset.status === status) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    });

    // 청크 목록 다시 로드
    await this.loadPendingChunks();
  }

  /**
   * 승인 대기 청크 로드
   */
  async loadPendingChunks() {
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;

    chunkList.innerHTML = '<div class="loading">청크 목록을 불러오는 중...</div>';

    try {
      let url = `/api/approval/chunks/pending?status=${this.currentStatusFilter}`;

      if (this.pagination) {
        const state = this.pagination.getState();
        url += `&limit=${state.limit}&offset=${state.offset}`;
      } else {
        url += `&limit=50`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error("청크 목록을 불러올 수 없습니다.");
      }

      const data = await response.json();

      // 새로운 API 응답 형식 처리 (하위 호환성 유지)
      this.pendingChunks = data.items || data;

      // 페이징 상태 업데이트
      if (this.pagination) {
        this.pagination.updateState(data);
        this.pagination.updateUI();
      }

      this.displayPendingChunks();
      if (this.selectedChunkId) {
        this.showChunkDetail(this.selectedChunkId);
      } else {
        this.clearChunkDetail();
      }
      this.onChunkChange();
    } catch (error) {
      console.error("승인 대기 청크 로드 실패:", error);
      chunkList.innerHTML = '<div class="error">청크 목록을 불러올 수 없습니다.</div>';
      if (this.pagination) {
        this.pagination.hide();
      }
    }
  }

  /**
   * 승인 대기 청크 표시
   */
  displayPendingChunks() {
    const chunkList = document.getElementById(this.chunkListId);
    if (!chunkList) return;

    if (this.pendingChunks.length === 0) {
      chunkList.innerHTML = '<div class="loading">해당 상태의 청크가 없습니다.</div>';
      if (this.pagination) {
        this.pagination.hide();
      }
      return;
    }

    const selectedId = this.selectedChunkId;
    chunkList.innerHTML = this.pendingChunks
      .map((chunk) => {
        const statusClass = chunk.status || "draft";
        const statusText =
          {
            draft: "📝 대기 중",
            approved: "✅ 승인됨",
            rejected: "❌ 거절됨",
          }[statusClass] || "📝 대기 중";
        const selectedClass = chunk.id === selectedId ? " selected" : "";

        return `
          <div class="approval-chunk-card ${statusClass}${selectedClass}" data-chunk-id="${chunk.id}" onclick="window.approvalManager.showChunkDetail(${chunk.id})">
            <div class="chunk-card-header">
              <div>
                <div class="chunk-card-meta">
                  청크 ID: ${chunk.id} | 문서 ID: ${chunk.document_id} | 인덱스: ${chunk.chunk_index}
                </div>
                <div class="chunk-card-content">${escapeHtml(chunk.content)}</div>
              </div>
              <span class="chunk-card-status ${statusClass}">${statusText}</span>
            </div>
            <div class="chunk-card-actions">
              ${
                statusClass === "draft"
                  ? `
                <button class="btn btn-success btn-small" onclick="event.stopPropagation(); window.approvalManager.approveChunk(${chunk.id})">✅ 승인</button>
                <button class="btn btn-danger btn-small" onclick="event.stopPropagation(); window.approvalManager.rejectChunk(${chunk.id})">❌ 거절</button>
              `
                  : ""
              }
              <button class="btn btn-primary btn-small" onclick="event.stopPropagation(); window.approvalManager.showChunkDetail(${chunk.id})">상세 보기</button>
            </div>
          </div>
        `;
      })
      .join("");
  }

  /**
   * 청크 승인
   */
  async approveChunk(chunkId) {
    if (!confirm("이 청크를 승인하시겠습니까?")) {
      return;
    }

    try {
      const response = await fetch(`/api/approval/chunks/${chunkId}/approve`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          approved_by: "admin",
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "청크 승인 실패");
      }

      showSuccess("청크가 승인되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("청크 승인 실패:", error);
      showError(error.message || "청크 승인 중 오류가 발생했습니다.");
    }
  }

  /**
   * 현재 목록(현재 페이지)의 대기 중 청크 전체 승인
   */
  async batchApproveAll() {
    const draftIds = this.pendingChunks.filter((c) => (c.status || "") === "draft").map((c) => c.id);
    if (draftIds.length === 0) {
      if (typeof showError === "function") showError("승인할 대기 중 청크가 없습니다.");
      return;
    }
    if (!confirm("현재 목록의 대기 중 청크 " + draftIds.length + "개를 모두 승인하시겠습니까?")) {
      return;
    }
    try {
      const response = await fetch("/api/approval/chunks/batch/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chunk_ids: draftIds, approved_by: "admin" }),
      });
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "일괄 승인 실패");
      }
      const data = await response.json();
      if (typeof showSuccess === "function") showSuccess(data.message || draftIds.length + "개 청크가 승인되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("전체 승인 실패:", error);
      if (typeof showError === "function") showError(error.message || "전체 승인 중 오류가 발생했습니다.");
    }
  }

  /**
   * 청크 거절
   */
  async rejectChunk(chunkId) {
    const reason = prompt("거절 사유를 입력하세요 (선택사항):");

    if (reason === null) {
      return; // 취소
    }

    try {
      const response = await fetch(`/api/approval/chunks/${chunkId}/reject`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          reason: reason || null,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "청크 거절 실패");
      }

      showSuccess("청크가 거절되었습니다.");
      await this.loadPendingChunks();
    } catch (error) {
      console.error("청크 거절 실패:", error);
      showError(error.message || "청크 거절 중 오류가 발생했습니다.");
    }
  }

  /**
   * 청크 상세 보기 — 우측 패널에 렌더 (모달 제거)
   */
  async showChunkDetail(chunkId) {
    const placeholder = document.getElementById(this.detailPlaceholderId);
    const contentEl = document.getElementById(this.detailContentId);
    const body = document.getElementById(this.detailBodyId);

    if (!contentEl || !body) return;

    this.selectedChunkId = chunkId;
    if (placeholder) placeholder.style.display = "none";
    contentEl.style.display = "block";
    contentEl.innerHTML = '<div class="loading">청크 정보를 불러오는 중...</div>';

    this.updateSelectedCard();

    try {
      const chunkResponse = await fetch(`/api/knowledge/chunks/${chunkId}`);
      if (!chunkResponse.ok) {
        throw new Error("청크 정보를 불러올 수 없습니다.");
      }
      const chunk = await chunkResponse.json();

      let relationSuggestions = [];
      try {
        const relationResponse = await fetch(`/api/knowledge/relations/suggest?chunk_id=${chunkId}&limit=5`);
        if (relationResponse.ok) {
          const relationData = await relationResponse.json();
          relationSuggestions = relationData.suggestions || [];
        }
      } catch (e) {
        console.error("관계 추천 로드 실패:", e);
      }

      contentEl.innerHTML = `
        <div class="chunk-detail-section">
          <h4>청크 내용</h4>
          <div class="chunk-content-body">${escapeHtml(chunk.content || "내용 없음")}</div>
          <div class="chunk-content-ai-row approval-ai-row">
            <button type="button" class="btn btn-primary btn-small" id="approval-ai-btn" onclick="window.approvalManager.fetchAiLabelSuggestions()">AI 키워드·라벨 추천</button>
            <span id="approval-ai-status" class="ai-suggest-status"></span>
          </div>
          <div id="approval-ai-suggestions" class="ai-label-suggestions" style="display: none"></div>
          <div id="approval-ai-new-keywords-wrap" class="ai-new-keywords-wrap" style="display: none">
            <h5 class="ai-new-keywords-title">새 키워드 (라벨로 등록 가능)</h5>
            <div id="approval-ai-new-keywords" class="ai-new-keywords"></div>
          </div>
        </div>
        <div class="chunk-detail-section">
          <h4>현재 라벨</h4>
          <div class="current-labels">
            ${
              chunk.labels && chunk.labels.length > 0
                ? chunk.labels
                    .map(
                      (label) =>
                        `<span class="label-badge ${(label.label_type || "default").replace(/\s+/g, "_")}">${escapeHtml(label.name)}</span>`
                    )
                    .join("")
                : '<p style="color: #9ca3af; font-size: 13px;">라벨이 없습니다.</p>'
            }
          </div>
        </div>
        ${
          relationSuggestions.length > 0
            ? `
        <div class="chunk-detail-section">
          <h4>🔗 AI 유사 청크 추천</h4>
          <div class="suggestion-block">
            ${relationSuggestions
              .map(
                (s) => `
              <div class="similar-chunk-item" onclick="window.approvalManager.showChunkDetail(${s.target_chunk_id})">
                <div style="font-weight: 600; margin-bottom: 5px;">청크 ID: ${s.target_chunk_id}</div>
                <div style="font-size: 12px; color: #666; margin-bottom: 5px;">${escapeHtml(s.target_content_preview)}</div>
                <div style="font-size: 11px; color: #999;">유사도: ${(s.score * 100).toFixed(0)}%</div>
              </div>
            `
              )
              .join("")}
          </div>
        </div>
        `
            : ""
        }
        <div class="chunk-detail-section">
          <h4>작업</h4>
          <div class="chunk-detail-actions">
            ${
              chunk.status === "draft"
                ? `
              <button class="btn btn-success" onclick="window.approvalManager.approveChunk(${chunkId})">✅ 승인</button>
              <button class="btn btn-danger" onclick="window.approvalManager.rejectChunk(${chunkId})">❌ 거절</button>
            `
                : ""
            }
            <button class="btn btn-small" style="background: #e5e7eb; color: #333" onclick="window.approvalManager.clearChunkDetail()">선택 해제</button>
          </div>
        </div>
      `;
    } catch (error) {
      console.error("청크 상세 로드 실패:", error);
      let errorMessage = "청크 정보를 불러올 수 없습니다.";
      if (error.message.includes("Failed to fetch") || error.message.includes("NetworkError")) {
        errorMessage = "네트워크 오류가 발생했습니다. 인터넷 연결을 확인하세요.";
      } else if (error.message) {
        errorMessage = error.message;
      }
      contentEl.innerHTML = `<div class="error">${escapeHtml(errorMessage)}</div>`;
    }
  }

  /**
   * 청크 내용 기반 AI 키워드·라벨 추천 요청 (청크 관리와 동일: 버튼 클릭 시 호출)
   */
  async fetchAiLabelSuggestions() {
    if (!this.selectedChunkId) {
      showError("먼저 청크를 선택하세요.");
      return;
    }
    const btnEl = document.getElementById("approval-ai-btn");
    const statusEl = document.getElementById("approval-ai-status");
    const suggestionsEl = document.getElementById("approval-ai-suggestions");
    const newWrapEl = document.getElementById("approval-ai-new-keywords-wrap");
    if (suggestionsEl) suggestionsEl.style.display = "none";
    if (newWrapEl) newWrapEl.style.display = "none";
    if (statusEl) statusEl.textContent = "LLM 추천 중...";
    if (btnEl) btnEl.disabled = true;
    try {
      const res = await fetch(`/api/knowledge/labels/suggest-llm?chunk_id=${this.selectedChunkId}&limit=10`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "추천 요청 실패");
      this.lastAiSuggestions = data.suggestions || [];
      this.lastNewKeywords = data.new_keywords || [];
      this.renderAiSuggestionsIntoApproval(this.lastAiSuggestions, this.lastNewKeywords);
      if (suggestionsEl) suggestionsEl.style.display = this.lastAiSuggestions.length ? "block" : "none";
      if (newWrapEl) newWrapEl.style.display = this.lastNewKeywords.length ? "block" : "none";
      const hasAny = this.lastAiSuggestions.length || this.lastNewKeywords.length;
      if (statusEl) {
        if (hasAny) statusEl.textContent = "";
        else statusEl.textContent = data.message || (data.ollama_feedback && !data.ollama_feedback.available && data.ollama_feedback.message) || "추천 결과가 없습니다.";
      }
    } catch (e) {
      console.error("AI 라벨 추천 실패:", e);
      showError(e.message || "AI 추천을 불러오지 못했습니다. LLM 서버(Ollama)가 실행 중인지 확인하세요.");
      if (statusEl) statusEl.textContent = "";
    } finally {
      if (btnEl) btnEl.disabled = false;
    }
  }

  /**
   * AI 추천 결과를 승인 상세 패널에 렌더 (청크 관리와 동일 UI: 배지 + 추가 / 새 키워드 + 라벨로 등록)
   */
  renderAiSuggestionsIntoApproval(suggestions, newKeywords) {
    const suggestionsEl = document.getElementById("approval-ai-suggestions");
    const newKwEl = document.getElementById("approval-ai-new-keywords");
    const list = Array.isArray(suggestions) ? suggestions : [];
    const newKwList = Array.isArray(newKeywords) ? newKeywords : [];
    if (suggestionsEl) {
      if (list.length === 0) {
        suggestionsEl.innerHTML = "";
      } else {
        suggestionsEl.innerHTML = list
          .map((s) => {
            const typeClass = (s.label_type || "default").replace(/\s+/g, "_");
            const conf = s.confidence != null ? Math.round(s.confidence * 100) : "";
            return `
            <span class="ai-suggestion-item label-badge ${typeClass}">
              ${escapeHtml(s.name || s.label_name || "")}
              ${conf ? `<span class="ai-suggestion-conf">${conf}%</span>` : ""}
              <button type="button" class="btn btn-small ai-suggestion-apply" data-label-id="${s.label_id}" data-conf="${s.confidence != null ? s.confidence : 0.8}">추가</button>
            </span>
          `;
          })
          .join("");
        suggestionsEl.querySelectorAll(".ai-suggestion-apply").forEach((btn) => {
          btn.addEventListener("click", () => {
            const labelId = parseInt(btn.getAttribute("data-label-id"), 10);
            const conf = parseFloat(btn.getAttribute("data-conf")) || 0.8;
            if (!isNaN(labelId)) this.applyLabelSuggestion(this.selectedChunkId, labelId, conf);
          });
        });
      }
    }
    if (newKwEl) {
      if (newKwList.length === 0) {
        newKwEl.innerHTML = "";
      } else {
        newKwEl.innerHTML = newKwList
          .map(
            (kw, i) =>
              `<span class="ai-new-keyword-item">${escapeHtml(kw)}<button type="button" class="btn btn-small ai-new-keyword-apply" data-idx="${i}">라벨로 등록</button></span>`
          )
          .join("");
        newKwEl.querySelectorAll(".ai-new-keyword-apply").forEach((btn) => {
          btn.addEventListener("click", () => {
            const idx = parseInt(btn.getAttribute("data-idx"), 10);
            const keyword = !isNaN(idx) && newKwList[idx] !== undefined ? newKwList[idx] : null;
            if (keyword) this.applyNewKeywordAsLabel(keyword);
          });
        });
      }
    }
  }

  /**
   * 좌측 목록에서 선택된 카드 강조
   */
  updateSelectedCard() {
    const list = document.getElementById(this.chunkListId);
    if (!list) return;
    list.querySelectorAll(".approval-chunk-card").forEach((card) => {
      const id = parseInt(card.getAttribute("data-chunk-id"), 10);
      if (id === this.selectedChunkId) {
        card.classList.add("selected");
      } else {
        card.classList.remove("selected");
      }
    });
  }

  /**
   * 청크 상세 패널 비우기 (선택 해제)
   */
  clearChunkDetail() {
    this.selectedChunkId = null;
    const placeholder = document.getElementById(this.detailPlaceholderId);
    const contentEl = document.getElementById(this.detailContentId);
    if (placeholder) placeholder.style.display = "block";
    if (contentEl) {
      contentEl.style.display = "none";
      contentEl.innerHTML = "";
    }
    this.updateSelectedCard();
  }

  /**
   * @deprecated 모달 제거로 clearChunkDetail 사용
   */
  closeChunkDetail() {
    this.clearChunkDetail();
  }

  /**
   * 라벨 추천 적용 (LabelManager와 연동)
   */
  async applyLabelSuggestion(chunkId, labelId, confidence) {
    // LabelManager가 있으면 사용, 없으면 직접 호출
    if (window.labelsTabManager && typeof window.labelsTabManager.applyLabelSuggestion === "function") {
      const success = await window.labelsTabManager.applyLabelSuggestion(chunkId, labelId, confidence);
      if (success) {
        this.showChunkDetail(chunkId); // 상세 정보 새로고침
      }
    } else {
      // 폴백: 직접 API 호출
      try {
        const response = await fetch(`/api/knowledge/labels/suggest/${chunkId}/apply/${labelId}?confidence=${confidence}`, {
          method: "POST",
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "라벨 적용 실패");
        }

        showSuccess("라벨이 적용되었습니다.");
        this.showChunkDetail(chunkId); // 상세 정보 새로고침
      } catch (error) {
        console.error("라벨 적용 실패:", error);
        showError(error.message || "라벨 적용 중 오류가 발생했습니다.");
      }
    }
  }

  /**
   * 새 키워드 인덱스로 라벨 등록 (onclick에서 호출)
   */
  applyNewKeywordAsLabelByIndex(index) {
    const kw = Array.isArray(this.lastNewKeywords) && this.lastNewKeywords[index] !== undefined ? this.lastNewKeywords[index] : null;
    if (kw) this.applyNewKeywordAsLabel(kw);
  }

  /**
   * 새 키워드를 라벨로 생성 후 현재 청크에 연결 (청크 관리와 동일 로직)
   */
  async applyNewKeywordAsLabel(keyword) {
    if (!this.selectedChunkId || !keyword || !String(keyword).trim()) return;
    const kw = String(keyword).trim();
    try {
      const createRes = await fetch("/api/labels", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: kw, label_type: "keyword", description: "" }),
      });
      const createData = await createRes.json();
      if (!createRes.ok) throw new Error(createData.detail || "라벨 생성 실패");
      const labelId = createData.id;
      const linkRes = await fetch(`/api/labels/chunks/${this.selectedChunkId}/labels/${labelId}`, { method: "POST" });
      if (!linkRes.ok) {
        const err = await linkRes.json().catch(() => ({}));
        throw new Error(err.detail || "청크에 라벨 연결 실패");
      }
      showSuccess('키워드 "' + kw + '"를 라벨로 등록하고 청크에 추가했습니다.');
      this.showChunkDetail(this.selectedChunkId);
    } catch (e) {
      console.error("새 키워드 라벨 등록 실패:", e);
      showError(e.message || "라벨 등록에 실패했습니다.");
    }
  }
}
