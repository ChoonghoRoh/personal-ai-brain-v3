/**
 * 공통 페이징 컴포넌트
 * 여러 페이지에서 재사용 가능한 페이징 UI 및 로직
 */

class PaginationComponent {
  constructor(config) {
    // 필수 설정
    this.onPageChange = config.onPageChange; // 페이지 변경 시 호출할 함수
    this.onLimitChange = config.onLimitChange || this.onPageChange; // limit 변경 시 호출할 함수
    
    // 선택적 설정
    this.prefix = config.prefix || ""; // 페이지 정보 메시지 접두사 (예: "검색 결과")
    this.hideWhenEmpty = config.hideWhenEmpty !== false; // 총 개수가 limit보다 작을 때 숨김 (기본: true)
    
    // DOM 요소 ID (기본값)
    this.controlsId = config.controlsId || "pagination-controls";
    this.infoId = config.infoId || "pagination-info";
    this.buttonsId = config.buttonsId || "pagination-buttons";
    this.itemsPerPageId = config.itemsPerPageId || "items-per-page";
    
    // 페이징 상태
    this.currentPage = config.initialPage || 1;
    this.limit = config.initialLimit || 20;
    this.totalCount = 0;
    this.totalPages = 0;
    
    // 최대 표시할 페이지 버튼 수
    this.maxButtons = config.maxButtons || 7;
  }

  /**
   * 페이징 상태 업데이트
   */
  updateState(data) {
    this.totalCount = data.total_count || data.totalCount || 0;
    this.totalPages = data.total_pages || data.totalPages || Math.ceil(this.totalCount / this.limit);
    this.currentPage = data.current_page || data.currentPage || this.currentPage;
    
    // limit이 응답에 포함된 경우 업데이트
    if (data.limit !== undefined) {
      this.limit = data.limit;
    }
  }

  /**
   * 페이징 UI 업데이트
   */
  updateUI() {
    const paginationControls = document.getElementById(this.controlsId);
    const paginationInfo = document.getElementById(this.infoId);
    const paginationButtons = document.getElementById(this.buttonsId);
    const itemsPerPageSelect = document.getElementById(this.itemsPerPageId);

    if (!paginationControls || !paginationInfo || !paginationButtons || !itemsPerPageSelect) {
      console.warn("페이징 컨트롤 요소를 찾을 수 없습니다.");
      return;
    }

    // 총 개수가 limit보다 작으면 페이징 UI 숨기기
    if (this.hideWhenEmpty && this.totalCount <= this.limit) {
      paginationControls.style.display = "none";
      return;
    }

    // 페이징 UI 표시
    paginationControls.style.display = "block";

    // 페이지당 항목 수 설정
    itemsPerPageSelect.value = this.limit;

    // 페이지 정보 표시
    const startItem = (this.currentPage - 1) * this.limit + 1;
    const endItem = Math.min(this.currentPage * this.limit, this.totalCount);
    const prefixText = this.prefix ? `${this.prefix} ` : "";
    paginationInfo.textContent = `${prefixText}${this.totalCount.toLocaleString()}개 중 ${startItem.toLocaleString()}-${endItem.toLocaleString()}개 표시`;

    // 페이지 버튼 생성
    paginationButtons.innerHTML = "";

    // 이전 버튼
    const prevButton = this.createNavButton("◀ 이전", this.currentPage === 1, () => {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.onPageChange();
      }
    });
    paginationButtons.appendChild(prevButton);

    // 페이지 번호 버튼
    const { startPage, endPage } = this.calculatePageRange();
    
    // 첫 페이지 버튼
    if (startPage > 1) {
      paginationButtons.appendChild(this.createPageButton(1));
      if (startPage > 2) {
        paginationButtons.appendChild(this.createEllipsis());
      }
    }

    // 페이지 번호 버튼들
    for (let i = startPage; i <= endPage; i++) {
      paginationButtons.appendChild(this.createPageButton(i));
    }

    // 마지막 페이지 버튼
    if (endPage < this.totalPages) {
      if (endPage < this.totalPages - 1) {
        paginationButtons.appendChild(this.createEllipsis());
      }
      paginationButtons.appendChild(this.createPageButton(this.totalPages));
    }

    // 다음 버튼
    const nextButton = this.createNavButton("다음 ▶", this.currentPage === this.totalPages, () => {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.onPageChange();
      }
    });
    paginationButtons.appendChild(nextButton);

    // 페이지당 항목 수 변경 이벤트
    itemsPerPageSelect.onchange = () => {
      this.limit = parseInt(itemsPerPageSelect.value);
      this.currentPage = 1; // 페이지당 항목 수 변경 시 첫 페이지로
      this.onLimitChange();
    };
  }

  /**
   * 페이지 범위 계산
   */
  calculatePageRange() {
    let startPage = Math.max(1, this.currentPage - Math.floor(this.maxButtons / 2));
    let endPage = Math.min(this.totalPages, startPage + this.maxButtons - 1);
    
    // 끝 페이지가 조정되면 시작 페이지도 조정
    if (endPage - startPage < this.maxButtons - 1) {
      startPage = Math.max(1, endPage - this.maxButtons + 1);
    }
    
    return { startPage, endPage };
  }

  /**
   * 페이지 버튼 생성
   */
  createPageButton(pageNum) {
    const button = document.createElement("button");
    button.textContent = pageNum;
    const isActive = pageNum === this.currentPage;
    button.style.cssText = `padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: ${isActive ? "#2563eb" : "white"}; color: ${isActive ? "white" : "#374151"}; cursor: pointer; font-size: 14px; min-width: 40px;`;
    
    if (isActive) {
      button.style.fontWeight = "bold";
    }
    
    button.addEventListener("click", () => {
      this.currentPage = pageNum;
      this.onPageChange();
    });
    
    return button;
  }

  /**
   * 네비게이션 버튼 생성 (이전/다음)
   */
  createNavButton(text, disabled, onClick) {
    const button = document.createElement("button");
    button.textContent = text;
    button.disabled = disabled;
    button.style.cssText = "padding: 6px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 14px;";
    if (disabled) {
      button.style.opacity = "0.5";
      button.style.cursor = "not-allowed";
    }
    button.addEventListener("click", onClick);
    return button;
  }

  /**
   * 생략 표시 생성
   */
  createEllipsis() {
    const ellipsis = document.createElement("span");
    ellipsis.textContent = "...";
    ellipsis.style.cssText = "padding: 6px; color: #6b7280;";
    return ellipsis;
  }

  /**
   * 페이징 UI 숨기기
   */
  hide() {
    const paginationControls = document.getElementById(this.controlsId);
    if (paginationControls) {
      paginationControls.style.display = "none";
    }
  }

  /**
   * 페이징 상태 가져오기
   */
  getState() {
    return {
      currentPage: this.currentPage,
      limit: this.limit,
      totalCount: this.totalCount,
      totalPages: this.totalPages,
      offset: (this.currentPage - 1) * this.limit
    };
  }

  /**
   * 페이징 상태 설정
   */
  setState(state) {
    if (state.currentPage !== undefined) this.currentPage = state.currentPage;
    if (state.limit !== undefined) this.limit = state.limit;
    if (state.totalCount !== undefined) this.totalCount = state.totalCount;
    if (state.totalPages !== undefined) this.totalPages = state.totalPages;
  }
}
