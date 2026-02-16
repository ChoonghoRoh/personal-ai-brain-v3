/**
 * 공통 Layout 컴포넌트
 * Phase 14-3: app-layout (LNB + main-content) 그리드 구조
 * Phase 14 QC 4.2: LNB 접기/펼치기 + 모바일 드로어
 */

/**
 * Layout 스타일 CSS
 */
const LAYOUT_STYLES = `
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: #f5f5f5;
    color: #333;
    overflow: hidden;
  }

  /* Phase 14-3: App Layout (LNB + Main Content) */
  .app-layout {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 100vh;
    max-height: 100vh;
    transition: grid-template-columns 0.25s ease;
  }

  /* LNB Sidebar */
  .lnb {
    background: #1e293b;
    color: #e2e8f0;
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    z-index: 100;
    display: flex;
    flex-direction: column;
    transition: width 0.25s ease;
  }

  .lnb::-webkit-scrollbar {
    width: 4px;
  }

  .lnb::-webkit-scrollbar-thumb {
    background: #475569;
    border-radius: 2px;
  }

  /* Main Content Container */
  .container {
    max-width: none;
    padding: 24px 32px;
    overflow-y: auto;
    height: 100vh;
  }

  /* ==============================
   * Desktop LNB Collapse (QC 4.2)
   * ============================== */
  .lnb-collapse-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px 16px;
    margin-top: auto;
    background: #334155;
    color: #94a3b8;
    border: none;
    border-top: 1px solid #475569;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s;
  }

  .lnb-collapse-btn:hover {
    background: #475569;
    color: #f1f5f9;
  }

  .lnb-collapse-btn .collapse-icon {
    transition: transform 0.25s ease;
  }

  /* Collapsed LNB */
  .app-layout.lnb-collapsed {
    grid-template-columns: 60px 1fr;
  }

  .app-layout.lnb-collapsed .lnb {
    overflow: visible;
  }

  .app-layout.lnb-collapsed .lnb-logo span,
  .app-layout.lnb-collapsed .logo-sub,
  .app-layout.lnb-collapsed .lnb-group-title,
  .app-layout.lnb-collapsed .menu-label,
  .app-layout.lnb-collapsed .collapse-label {
    display: none;
  }

  .app-layout.lnb-collapsed .lnb-logo {
    padding: 16px 8px;
    text-align: center;
  }

  .app-layout.lnb-collapsed .lnb-logo a {
    justify-content: center;
  }

  .app-layout.lnb-collapsed .lnb-menu li a {
    justify-content: center;
    padding: 12px 0;
    border-left-width: 0;
  }

  .app-layout.lnb-collapsed .lnb-menu li a .menu-icon {
    font-size: 18px;
    width: auto;
  }

  .app-layout.lnb-collapsed .lnb-menu li a:hover {
    position: relative;
  }

  .app-layout.lnb-collapsed .lnb-collapse-btn {
    padding: 12px 0;
  }

  .app-layout.lnb-collapsed .lnb-collapse-btn .collapse-icon {
    transform: rotate(180deg);
  }

  /* LNB 메뉴 아이템 툴팁 (collapsed 모드) */
  .app-layout.lnb-collapsed .lnb-menu li {
    position: relative;
  }

  .app-layout.lnb-collapsed .lnb-menu li a::after {
    content: attr(data-tooltip);
    position: absolute;
    left: 100%;
    top: 50%;
    transform: translateY(-50%);
    background: #1e293b;
    color: #f1f5f9;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 13px;
    white-space: nowrap;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.15s;
    z-index: 200;
    margin-left: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  }

  .app-layout.lnb-collapsed .lnb-menu li a:hover::after {
    opacity: 1;
  }

  /* ==============================
   * Mobile Toggle (QC 4.2)
   * ============================== */
  .lnb-toggle {
    display: none;
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 1001;
    background: #1e293b;
    color: #f8fafc;
    border: none;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 18px;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  }

  .lnb-toggle:hover {
    background: #334155;
  }

  .lnb-overlay {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  }

  .lnb-overlay.active {
    display: block;
  }

  /* 반응형 디자인 */
  @media (max-width: 1024px) {
    .app-layout {
      grid-template-columns: 220px 1fr;
    }
    .app-layout.lnb-collapsed {
      grid-template-columns: 60px 1fr;
    }
  }

  @media (max-width: 768px) {
    .app-layout {
      grid-template-columns: 1fr;
    }

    .app-layout.lnb-collapsed {
      grid-template-columns: 1fr;
    }

    .lnb {
      display: none;
    }

    .lnb.lnb-open {
      display: flex;
      position: fixed;
      top: 0;
      left: 0;
      width: 260px;
      z-index: 1000;
    }

    .lnb-toggle {
      display: block;
    }

    .lnb-collapse-btn {
      display: none;
    }

    .container {
      padding: 56px 16px 16px;
    }
  }
`;

/**
 * Layout 스타일을 페이지에 추가
 */
function initLayoutStyles() {
  if (!document.getElementById('layout-component-styles')) {
    const style = document.createElement('style');
    style.id = 'layout-component-styles';
    style.textContent = LAYOUT_STYLES;
    document.head.appendChild(style);
  }
}

/**
 * Container를 생성하고 반환
 * @param {string|HTMLElement} content - 컨테이너 내부 콘텐츠
 * @param {object} options - 옵션
 * @returns {HTMLElement} Container 요소
 */
function createContainer(content = '', options = {}) {
  const className = options.className || '';

  const container = document.createElement('div');
  container.className = `container ${className}`.trim();

  if (content) {
    if (content instanceof HTMLElement || content instanceof DocumentFragment) {
      container.appendChild(content);
    } else {
      // @trusted: 개발자 제공 HTML 템플릿만 허용
      container.innerHTML = content;
    }
  }

  return container;
}

/**
 * Body에 Container를 추가
 * @param {string|HTMLElement} content - 컨테이너 내부 콘텐츠
 * @param {object} options - 옵션
 */
function renderContainer(content = '', options = {}) {
  initLayoutStyles();

  const existingContainer = document.querySelector('.container');

  if (existingContainer) {
    if (content instanceof HTMLElement || content instanceof DocumentFragment) {
      existingContainer.replaceChildren(content);
    } else if (typeof content === 'string') {
      // @trusted: 개발자 제공 HTML 템플릿만 허용
      existingContainer.innerHTML = content;
    }

    if (options.className) {
      existingContainer.className = `container ${options.className}`.trim();
    }
  } else {
    const container = createContainer(content, options);
    document.body.appendChild(container);
  }
}

/**
 * 페이지 초기화 — app-layout 래핑 + LNB placeholder 생성 (Phase 14-3)
 * Phase 14 QC 4.2: 토글 버튼, 오버레이, 접기 버튼 추가
 */
function initLayout() {
  initLayoutStyles();

  const container = document.querySelector('.container');
  if (!container || container.closest('.app-layout')) return;

  // app-layout 래퍼 생성
  const appLayout = document.createElement('div');
  appLayout.className = 'app-layout';

  // LNB placeholder
  const lnb = document.createElement('aside');
  lnb.id = 'lnb-sidebar';
  lnb.className = 'lnb';

  // DOM 재구성: body > .app-layout > (.lnb + .container)
  container.parentNode.insertBefore(appLayout, container);
  appLayout.appendChild(lnb);
  appLayout.appendChild(container);

  // --- QC 4.2: 모바일 토글 버튼 ---
  if (!document.getElementById('lnb-toggle-btn')) {
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'lnb-toggle';
    toggleBtn.id = 'lnb-toggle-btn';
    toggleBtn.textContent = '\u2630'; // ☰
    toggleBtn.setAttribute('aria-label', '메뉴 열기/닫기');
    document.body.appendChild(toggleBtn);

    toggleBtn.addEventListener('click', toggleMobileLNB);
  }

  // --- QC 4.2: 모바일 오버레이 ---
  if (!document.getElementById('lnb-overlay')) {
    const overlay = document.createElement('div');
    overlay.className = 'lnb-overlay';
    overlay.id = 'lnb-overlay';
    document.body.appendChild(overlay);

    overlay.addEventListener('click', closeMobileLNB);
  }

  // --- QC 4.2: localStorage 복원 (데스크톱 접기 상태) ---
  if (localStorage.getItem('lnb_collapsed') === 'true') {
    appLayout.classList.add('lnb-collapsed');
  }

  // ESC 키로 모바일 LNB 닫기
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeMobileLNB();
    }
  });
}

/**
 * 모바일 LNB 토글 (QC 4.2)
 */
function toggleMobileLNB() {
  const lnb = document.getElementById('lnb-sidebar');
  const overlay = document.getElementById('lnb-overlay');
  if (lnb) lnb.classList.toggle('lnb-open');
  if (overlay) overlay.classList.toggle('active');
}

/**
 * 모바일 LNB 닫기 (QC 4.2)
 */
function closeMobileLNB() {
  const lnb = document.getElementById('lnb-sidebar');
  const overlay = document.getElementById('lnb-overlay');
  if (lnb) lnb.classList.remove('lnb-open');
  if (overlay) overlay.classList.remove('active');
}

/**
 * 데스크톱 LNB 접기/펼치기 토글 (QC 4.2)
 */
function toggleCollapseLNB() {
  const appLayout = document.querySelector('.app-layout');
  if (!appLayout) return;

  appLayout.classList.toggle('lnb-collapsed');
  const collapsed = appLayout.classList.contains('lnb-collapsed');
  localStorage.setItem('lnb_collapsed', collapsed);
}

// 전역으로 export (브라우저 환경)
if (typeof window !== 'undefined') {
  if (!window.initLayout) {
    window.initLayout = initLayout;
    window.initLayoutStyles = initLayoutStyles;
    window.createContainer = createContainer;
    window.renderContainer = renderContainer;
    window.toggleMobileLNB = toggleMobileLNB;
    window.closeMobileLNB = closeMobileLNB;
    window.toggleCollapseLNB = toggleCollapseLNB;
    window.LAYOUT_STYLES = LAYOUT_STYLES;
  }
}
