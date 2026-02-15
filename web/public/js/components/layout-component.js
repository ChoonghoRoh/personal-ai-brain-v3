/**
 * 공통 Layout 컴포넌트
 * Body와 Container 스타일 및 구조를 공통화
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
  }

  .container {
    max-width: 1440px;
    margin: 0 auto;
    padding: 20px;
  }

  /* 반응형 디자인 */
  @media (max-width: 768px) {
    .container {
      padding: 15px;
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
 * @param {string|HTMLElement} content - 컨테이너 내부 콘텐츠 (HTML string 또는 DOM 요소)
 * @param {object} options - 옵션
 * @param {string} options.className - 추가 클래스명
 * @param {string} options.maxWidth - 최대 너비 (기본: 1200px)
 * @returns {HTMLElement} Container 요소
 */
function createContainer(content = '', options = {}) {
  const className = options.className || '';
  const maxWidth = options.maxWidth || '1200px';

  const container = document.createElement('div');
  container.className = `container ${className}`.trim();
  container.style.maxWidth = maxWidth;

  if (content) {
    if (content instanceof HTMLElement || content instanceof DocumentFragment) {
      container.appendChild(content);
    } else {
      // @trusted: 개발자 제공 HTML 템플릿만 허용. 사용자 입력은 escapeHtml() 처리 필수.
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
  // Layout 스타일 초기화
  initLayoutStyles();

  // 기존 container 찾기
  const existingContainer = document.querySelector('.container');

  if (existingContainer) {
    // 기존 container가 있으면 내용만 업데이트
    if (content instanceof HTMLElement || content instanceof DocumentFragment) {
      existingContainer.replaceChildren(content);
    } else if (typeof content === 'string') {
      // @trusted: 개발자 제공 HTML 템플릿만 허용. 사용자 입력은 escapeHtml() 처리 필수.
      existingContainer.innerHTML = content;
    }

    // 옵션 적용
    if (options.maxWidth) {
      existingContainer.style.maxWidth = options.maxWidth;
    }
    if (options.className) {
      existingContainer.className = `container ${options.className}`.trim();
    }
  } else {
    // 기존 container가 없으면 새로 생성
    const container = createContainer(content, options);
    document.body.appendChild(container);
  }
}

/**
 * 페이지 초기화 (Layout 스타일만 적용)
 */
function initLayout() {
  initLayoutStyles();
}

// 전역으로 export (브라우저 환경)
// 중복 선언 방지: 이미 선언된 경우 재선언하지 않음
if (typeof window !== 'undefined') {
  if (!window.initLayout) {
    window.initLayout = initLayout;
    window.initLayoutStyles = initLayoutStyles;
    window.createContainer = createContainer;
    window.renderContainer = renderContainer;
    window.LAYOUT_STYLES = LAYOUT_STYLES;
  }
}

