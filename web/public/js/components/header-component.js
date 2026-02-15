/**
 * 공통 Header 컴포넌트
 * 모든 페이지에서 일관된 헤더와 네비게이션을 제공
 */

// 사용자 메뉴 정의 (좌측)
const USER_MENU = [
  { path: '/dashboard', label: '대시보드', icon: '🎛️' },
  { path: '/search', label: '검색', icon: '🔍' },
  { path: '/knowledge', label: '지식 구조', icon: '📊' },
  { path: '/reason', label: 'Reasoning', icon: '💭' },
  { path: '/ask', label: 'AI 질의', icon: '💬' },
  { path: '/logs', label: '로그', icon: '📋' }
];

// 관리자 메뉴 정의 - 지식 관리 (우측)
const ADMIN_MENU = [
  { path: '/admin/groups', label: '키워드 관리', icon: '📦' },
  { path: '/admin/labels', label: '라벨 관리', icon: '🏷️' },
  { path: '/admin/chunk-create', label: '청크 생성', icon: '➕' },
  { path: '/admin/approval', label: '청크 승인', icon: '✅' },
  { path: '/admin/chunk-labels', label: '청크 관리', icon: '📝' },
  { path: '/admin/statistics', label: '통계', icon: '📈' }
];

// 설정 관리 메뉴 정의 (Phase 11-3)
const SETTINGS_MENU = [
  { path: '/admin/settings/templates', label: '템플릿', icon: '📄' },
  { path: '/admin/settings/presets', label: '프리셋', icon: '⚙️' },
  { path: '/admin/settings/rag-profiles', label: 'RAG 프로필', icon: '🔍' },
  { path: '/admin/settings/policy-sets', label: '정책', icon: '📋' },
  { path: '/admin/settings/audit-logs', label: '변경 이력', icon: '📜' }
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
  
  // 현재 경로에 해당하는 메뉴 라벨 찾기
  // [활성 해석 순서] user → settings → admin
  // 1) USER_MENU: /dashboard는 exact match, 나머지는 startsWith
  // 2) SETTINGS_MENU: startsWith (더 구체적인 /admin/settings/* 경로 먼저 매칭)
  // 3) ADMIN_MENU: startsWith (/admin/* 범용)
  let currentMenuLabel = '';

  // 사용자 메뉴에서 찾기
  const userMenuItem = USER_MENU.find(item => {
    if (item.path === '/dashboard') {
      return currentPath === item.path;
    }
    return currentPath.startsWith(item.path);
  });

  if (userMenuItem) {
    currentMenuLabel = `${userMenuItem.icon} ${userMenuItem.label}`;
  } else {
    // 설정 관리 메뉴에서 찾기 (먼저 확인 - 더 구체적인 경로)
    const settingsMenuItem = SETTINGS_MENU.find(item => {
      return currentPath.startsWith(item.path);
    });

    if (settingsMenuItem) {
      currentMenuLabel = `${settingsMenuItem.icon} ${settingsMenuItem.label}`;
    } else {
      // 관리자 메뉴에서 찾기
      const adminMenuItem = ADMIN_MENU.find(item => {
        return currentPath.startsWith(item.path);
      });

      if (adminMenuItem) {
        currentMenuLabel = `${adminMenuItem.icon} ${adminMenuItem.label}`;
      }
    }
  }
  
  // 사용자 메뉴 HTML 생성 (좌측)
  const userMenuItems = USER_MENU.map(item => {
    const isActive = currentPath === item.path || 
                     (item.path !== '/dashboard' && currentPath.startsWith(item.path));
    const activeClass = isActive ? 'active' : '';
    return `<a href="${item.path}" class="${activeClass}">${item.icon} ${item.label}</a>`;
  }).join('\n          ');
  
  // 관리자 메뉴 HTML 생성 (우측)
  const adminMenuItems = ADMIN_MENU.map(item => {
    const isActive = currentPath === item.path || currentPath.startsWith(item.path);
    const activeClass = isActive ? 'active' : '';
    return `<a href="${item.path}" class="${activeClass}"> ${item.icon} ${item.label}</a>`;
  }).join('\n          ');

  // 설정 관리 메뉴 HTML 생성 (Phase 11-3)
  const settingsMenuItems = SETTINGS_MENU.map(item => {
    const isActive = currentPath.startsWith(item.path);
    const activeClass = isActive ? 'active' : '';
    return `<a href="${item.path}" class="${activeClass}"> ${item.icon} ${item.label}</a>`;
  }).join('\n          ');

  return `
    <header>
      <h1><a href="/dashboard">🧠 Personal AI Brain</a></h1>
      <nav>
        <div class="menu-group">
          <div class="menu-group-title">사용자 메뉴</div>
          <div class="menu-separator">|</div>
          <div class="user-menu">
            ${userMenuItems}
          </div>
        </div>
        <div class="menu-group">
          <div class="menu-group-title">관리자 메뉴</div>
          <div class="menu-separator">|</div>
          <div class="admin-menu">
            ${adminMenuItems}
          </div>
        </div>
        <div class="menu-group">
          <div class="menu-group-title">설정 관리</div>
          <div class="menu-separator">|</div>
          <div class="settings-menu">
            ${settingsMenuItems}
          </div>
        </div>
      </nav>
      <div class="subtitle-divider"></div>
      <div class="subtitle-section"> 
        ${currentMenuLabel ? `<h2>${currentMenuLabel}</h2>` : '<h2></h2>'}
        <div class="subtitle-separator">|</div>
        ${subtitle ? `<p class="subtitle">${subtitle}</p>` : '<p class="subtitle"></p>'}
      </div>
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
    margin-bottom: 15px;
    font-size: 24px;
  }

  header h1 a {
    color: #2563eb;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: opacity 0.2s;
  }

  header h1 a:hover {
    opacity: 0.8;
  }

  header .subtitle-divider {
    border-top: 1px solid #e5e7eb;
    margin-top: 15px;
    margin-bottom: 8px;
  }

  header .subtitle-section {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  header p.subtitle {
    color: #666;
    margin: 0;
    font-size: 14px;
    min-width: 100px;
  }

  header .subtitle-separator {
    color: #e5e7eb;
    font-size: 16px;
    font-weight: 300;
  }

  header .subtitle-section h2 {
    color: #2563eb;
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    flex: 1;
  }

  header nav {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  header nav .menu-group {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  header nav .menu-group-title {
    font-size: 12px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    min-width: 100px;
  }

  header nav .menu-separator {
    color: #e5e7eb;
    font-size: 16px;
    font-weight: 300;
  }

  header nav .user-menu {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    flex: 1;
  }

  header nav .admin-menu {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    flex: 1;
    border-top: 2px solid #e5e7eb;
    padding-top: 15px;
  }

  header nav .settings-menu {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    flex: 1;
    border-top: 2px solid #10b981;
    padding-top: 15px;
  }

  header nav .settings-menu a {
    color: #059669;
  }

  header nav .settings-menu a:hover {
    background: #ecfdf5;
  }

  header nav .settings-menu a.active {
    background: #059669;
    color: white;
  }

  @media (max-width: 768px) {
    header nav .admin-menu,
    header nav .settings-menu {
      width: 100%;
    }
  }

  header nav a {
    padding: 8px 16px;
    text-decoration: none;
    color: #2563eb;
    font-weight: 500;
    border-radius: 6px;
    transition: all 0.2s;
    font-size: 16px;
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
    window.USER_MENU = USER_MENU;
    window.ADMIN_MENU = ADMIN_MENU;
    window.SETTINGS_MENU = SETTINGS_MENU;
  }
}


