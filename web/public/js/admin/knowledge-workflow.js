/**
 * 지식 워크플로우 메인 컨트롤러
 * 탭 기반 통합 페이지 (생성/승인/관리)
 */

class KnowledgeWorkflow {
  constructor() {
    this.tabs = new Map();
    this.currentTab = "create";
    this.tabButtons = document.querySelectorAll(".kw-tab");
    this.tabPanels = document.querySelectorAll(".kw-tab-panel");

    this.bindEvents();
    this.syncFromUrl();
  }

  /**
   * 이벤트 바인딩
   */
  bindEvents() {
    // 탭 버튼 클릭
    this.tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const tabName = btn.getAttribute("data-tab");
        if (tabName) {
          this.switchTab(tabName);
        }
      });
    });

    // 브라우저 뒤로가기 핸들링
    window.addEventListener("popstate", (event) => {
      this.handlePopState(event);
    });
  }

  /**
   * 탭 모듈 등록
   * @param {string} name - 탭 이름 (create, approval, manage)
   * @param {object} instance - 탭 인스턴스 (init, activate, deactivate, refresh, onTabEvent 구현)
   */
  registerTab(name, instance) {
    this.tabs.set(name, instance);

    const container = document.getElementById(`tab-${name}`);
    if (container && instance.init) {
      instance.init(container, this);
    }
  }

  /**
   * 탭 전환
   * @param {string} tabName - 전환할 탭 이름
   */
  switchTab(tabName) {
    if (this.currentTab === tabName) return;

    const fromTab = this.currentTab;

    // 이전 탭 비활성화
    const prevTab = this.tabs.get(fromTab);
    if (prevTab && prevTab.deactivate) {
      prevTab.deactivate();
    }

    // UI 업데이트
    this.tabButtons.forEach((btn) => {
      const btnTab = btn.getAttribute("data-tab");
      if (btnTab === tabName) {
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
      } else {
        btn.classList.remove("active");
        btn.setAttribute("aria-selected", "false");
      }
    });

    this.tabPanels.forEach((panel) => {
      const panelTab = panel.getAttribute("data-tab");
      if (panelTab === tabName) {
        panel.classList.add("active");
        panel.style.display = "";
      } else {
        panel.classList.remove("active");
        panel.style.display = "none";
      }
    });

    this.currentTab = tabName;

    // 새 탭 활성화
    const newTab = this.tabs.get(tabName);
    if (newTab && newTab.activate) {
      newTab.activate();
    }

    // URL 쿼리 업데이트 (history.pushState)
    const url = new URL(window.location.href);
    url.searchParams.set("tab", tabName);
    window.history.pushState({ tab: tabName }, "", url.toString());
  }

  /**
   * URL 쿼리에서 탭 상태 동기화
   */
  syncFromUrl() {
    const url = new URL(window.location.href);
    const tabParam = url.searchParams.get("tab");

    if (tabParam && ["create", "approval", "manage"].includes(tabParam)) {
      this.switchTab(tabParam);
    } else {
      // 기본 탭: create
      this.switchTab("create");
    }
  }

  /**
   * 브라우저 뒤로가기 핸들링
   * @param {PopStateEvent} event
   */
  handlePopState(event) {
    if (event.state && event.state.tab) {
      const tabName = event.state.tab;
      if (tabName !== this.currentTab) {
        // URL 변경 없이 탭만 전환
        const fromTab = this.currentTab;

        const prevTab = this.tabs.get(fromTab);
        if (prevTab && prevTab.deactivate) {
          prevTab.deactivate();
        }

        this.tabButtons.forEach((btn) => {
          const btnTab = btn.getAttribute("data-tab");
          if (btnTab === tabName) {
            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");
          } else {
            btn.classList.remove("active");
            btn.setAttribute("aria-selected", "false");
          }
        });

        this.tabPanels.forEach((panel) => {
          const panelTab = panel.getAttribute("data-tab");
          if (panelTab === tabName) {
            panel.classList.add("active");
            panel.style.display = "";
          } else {
            panel.classList.remove("active");
            panel.style.display = "none";
          }
        });

        this.currentTab = tabName;

        const newTab = this.tabs.get(tabName);
        if (newTab && newTab.activate) {
          newTab.activate();
        }
      }
    } else {
      this.syncFromUrl();
    }
  }

  /**
   * 탭 간 이벤트 전달
   * @param {string} fromTab - 이벤트를 발생시킨 탭
   * @param {object} event - 전달할 이벤트 데이터
   */
  notifyTabChange(fromTab, event) {
    this.tabs.forEach((tab, name) => {
      if (name !== fromTab && tab.onTabEvent) {
        tab.onTabEvent(fromTab, event);
      }
    });
  }

  /**
   * 현재 활성 탭 반환
   * @returns {string}
   */
  getCurrentTab() {
    return this.currentTab;
  }

  /**
   * 특정 탭 인스턴스 반환
   * @param {string} name
   * @returns {object|undefined}
   */
  getTab(name) {
    return this.tabs.get(name);
  }
}

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  initializeAdminPage({
    title: "🔄 지식 워크플로우",
    subtitle: "청크 생성 → 승인 → 관리 통합",
    currentPath: "/admin/knowledge-workflow",
  });

  const workflow = new KnowledgeWorkflow();

  // 각 탭 모듈 인스턴스 생성 및 등록
  const createTab = new CreateTab();
  const approvalTab = new ApprovalTab();
  const manageTab = new ManageTab();

  workflow.registerTab("create", createTab);
  workflow.registerTab("approval", approvalTab);
  workflow.registerTab("manage", manageTab);

  // 전역 노출 (디버깅용)
  window.workflow = workflow;
});
