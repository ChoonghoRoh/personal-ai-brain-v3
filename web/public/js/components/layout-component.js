/**
 * 공통 Layout 컴포넌트
 * Phase 14-3: app-layout (LNB + main-content) 그리드 구조
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

  /* 반응형 디자인 */
  @media (max-width: 1024px) {
    .app-layout {
      grid-template-columns: 220px 1fr;
    }
  }

  @media (max-width: 768px) {
    .app-layout {
      grid-template-columns: 1fr;
    }

    .lnb {
      display: none;
    }

    .lnb.lnb-open {
      display: block;
      position: fixed;
      top: 0;
      left: 0;
      width: 260px;
      z-index: 1000;
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

    .container {
      padding: 16px;
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
}

// 전역으로 export (브라우저 환경)
if (typeof window !== 'undefined') {
  if (!window.initLayout) {
    window.initLayout = initLayout;
    window.initLayoutStyles = initLayoutStyles;
    window.createContainer = createContainer;
    window.renderContainer = renderContainer;
    window.LAYOUT_STYLES = LAYOUT_STYLES;
  }
}
