/**
 * 공통 Header 컴포넌트
 * 모든 페이지에서 일관된 헤더와 네비게이션을 제공
 */

// 네비게이션 메뉴 정의
const NAV_MENU = [
  { path: '/dashboard', label: '대시보드', icon: '🧠' },
  { path: '/search', label: '검색', icon: '🔍' },
  { path: '/knowledge', label: '지식 구조', icon: '📊' },
  { path: '/reason', label: 'Reasoning', icon: '🧠' },
  { path: '/knowledge-admin', label: '지식 관리', icon: '⚙️' },
  { path: '/ask', label: 'AI 질의', icon: '💬' },
  { path: '/logs', label: '로그', icon: '📋' }
];

/**
 * Header HTML 생성
 * @param {object} options - 헤더 옵션
 * @param {string} options.title - 페이지 제목
 * @param {string} options.subtitle - 페이지 부제목
 * @param {string} options.currentPath - 현재 경로 (활성 메뉴 하이라이트용)
 * @returns {string} Header HTML
 */
function createHeader(options = {}) {
  const title = options.title || 'Personal AI Brain';
  const subtitle = options.subtitle || '';
  const currentPath = options.currentPath || window.location.pathname;
  
  // 네비게이션 메뉴 HTML 생성
  const navItems = NAV_MENU.map(item => {
    const isActive = currentPath === item.path || 
                     (item.path !== '/dashboard' && currentPath.startsWith(item.path));
    const activeClass = isActive ? 'active' : '';
    return `<a href="${item.path}" class="${activeClass}">${item.icon} ${item.label}</a>`;
  }).join('\n          ');
  
  return `
    <header>
      <h1>${title}</h1>
      ${subtitle ? `<p>${subtitle}</p>` : ''}
      <nav>
        ${navItems}
      </nav>
    </header>
  `;
}

/**
 * Header 스타일 CSS
 */
const HEADER_STYLES = `
  header {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  header h1 {
    color: #2563eb;
    margin-bottom: 10px;
    font-size: 24px;
  }

  header p {
    color: #666;
    margin-bottom: 15px;
    font-size: 14px;
  }

  header nav {
    margin-top: 15px;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }

  header nav a {
    padding: 8px 16px;
    text-decoration: none;
    color: #2563eb;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.2s;
    font-size: 14px;
  }

  header nav a:hover {
    background: #eff6ff;
    text-decoration: none;
  }

  header nav a.active {
    background: #2563eb;
    color: white;
  }
`;

/**
 * Header를 페이지에 렌더링
 * @param {object} options - 헤더 옵션
 * @param {string} options.containerSelector - 헤더를 삽입할 컨테이너 선택자 (기본: '.container')
 * @param {string} options.insertPosition - 삽입 위치 ('beforebegin' | 'afterbegin' | 'beforeend' | 'afterend', 기본: 'afterbegin')
 */
function renderHeader(options = {}) {
  const containerSelector = options.containerSelector || '.container';
  const insertPosition = options.insertPosition || 'afterbegin';
  
  // 스타일 추가 (이미 추가되어 있지 않은 경우)
  if (!document.getElementById('header-component-styles')) {
    const style = document.createElement('style');
    style.id = 'header-component-styles';
    style.textContent = HEADER_STYLES;
    document.head.appendChild(style);
  }
  
  // Header HTML 생성
  const headerHTML = createHeader(options);
  
  // 컨테이너 찾기
  const container = document.querySelector(containerSelector);
  if (!container) {
    console.error(`Header 컴포넌트: 컨테이너를 찾을 수 없습니다: ${containerSelector}`);
    return;
  }
  
  // 기존 header 제거 (있다면)
  const existingHeader = container.querySelector('header');
  if (existingHeader) {
    existingHeader.remove();
  }
  
  // Header 삽입
  if (insertPosition === 'afterbegin') {
    container.insertAdjacentHTML('afterbegin', headerHTML);
  } else if (insertPosition === 'beforebegin') {
    container.insertAdjacentHTML('beforebegin', headerHTML);
  } else if (insertPosition === 'beforeend') {
    container.insertAdjacentHTML('beforeend', headerHTML);
  } else if (insertPosition === 'afterend') {
    container.insertAdjacentHTML('afterend', headerHTML);
  }
}

// 전역으로 export (브라우저 환경)
// 중복 선언 방지: 이미 선언된 경우 재선언하지 않음
if (typeof window !== 'undefined') {
  if (!window.renderHeader) {
    window.createHeader = createHeader;
    window.renderHeader = renderHeader;
    window.NAV_MENU = NAV_MENU;
  }
}

