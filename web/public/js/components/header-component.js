/**
 * 공통 Header + LNB 컴포넌트
 * Phase 14-3: 좌측 LNB 네비게이션 + 심플 상단 헤더
 * Phase 14-1: 역할 기반 메뉴 표시/숨김
 */

// 역할 계층 (Phase 14-1)
const ROLE_HIERARCHY = {
  'user': 0,
  'admin_knowledge': 1,
  'admin_system': 2,
};

// 메뉴 그룹별 필요 최소 역할 (Phase 14-1)
const MENU_REQUIRED_ROLE = {
  'user-menu': 'user',
  'admin-menu': 'admin_knowledge',
  'system-menu': 'admin_system',
  'settings-menu': 'admin_system',
};

// 캐시된 사용자 역할 (Phase 14-1)
let _cachedUserRole = null;

// 사용자 메뉴 정의
const USER_MENU = [
  { path: '/dashboard', label: '대시보드', icon: '🎛️' },
  { path: '/search', label: '검색', icon: '🔍' },
  { path: '/knowledge', label: '지식 구조', icon: '📊' },
  { path: '/reason', label: 'Reasoning', icon: '💭' },
  { path: '/ask', label: 'AI 질의', icon: '💬' },
  { path: '/logs', label: '로그', icon: '📋' }
];

// 관리자 메뉴 - 지식 관리
const ADMIN_MENU = [
  { path: '/admin/groups', label: '키워드 관리', icon: '📦' },
  { path: '/admin/labels', label: '라벨 관리', icon: '🏷️' },
  { path: '/admin/chunk-create', label: '청크 생성', icon: '➕' },
  { path: '/admin/approval', label: '청크 승인', icon: '✅' },
  { path: '/admin/chunk-labels', label: '청크 관리', icon: '📝' },
  { path: '/admin/knowledge-files', label: '파일관리', icon: '📁' },
  { path: '/admin/ai-automation', label: 'AI 자동화', icon: '🤖' },
  { path: '/knowledge-graph', label: '지식 그래프', icon: '🕸️' },
  { path: '/admin/statistics', label: '통계', icon: '📈' }
];

// 시스템 관리 메뉴 (Phase 15-5-3)
const SYSTEM_MENU = [
  { path: '/admin/users', label: '사용자 관리', icon: '👥' }
];

// 설정 관리 메뉴 (Phase 11-3)
const SETTINGS_MENU = [
  { path: '/admin/settings/templates', label: '템플릿', icon: '📄' },
  { path: '/admin/settings/presets', label: '프리셋', icon: '⚙️' },
  { path: '/admin/settings/rag-profiles', label: 'RAG 프로필', icon: '🔍' },
  { path: '/admin/settings/policy-sets', label: '정책', icon: '📋' },
  { path: '/admin/settings/audit-logs', label: '변경 이력', icon: '📜' }
];

// ============================================
// LNB (Left Navigation Bar) — Phase 14-3
// ============================================

const LNB_STYLES = `
  /* LNB Logo */
  .lnb-logo {
    padding: 20px 16px;
    border-bottom: 1px solid #334155;
  }

  .lnb-logo a {
    color: #f8fafc;
    text-decoration: none;
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: opacity 0.2s;
  }

  .lnb-logo a:hover {
    opacity: 0.85;
  }

  .lnb-logo .logo-sub {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 400;
    margin-top: 4px;
  }

  /* LNB Menu Groups */
  .lnb-group {
    padding: 12px 0;
    border-bottom: 1px solid #334155;
  }

  .lnb-group:last-child {
    border-bottom: none;
  }

  .lnb-group-title {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding: 0 16px 8px;
  }

  .lnb-menu {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .lnb-menu li a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 9px 16px;
    color: #cbd5e1;
    text-decoration: none;
    font-size: 14px;
    transition: all 0.15s;
    border-left: 3px solid transparent;
  }

  .lnb-menu li a:hover {
    background: #334155;
    color: #f1f5f9;
  }

  .lnb-menu li a.active {
    background: #1e40af;
    color: #ffffff;
    border-left-color: #60a5fa;
    font-weight: 600;
  }

  .lnb-menu li a .menu-icon {
    font-size: 16px;
    width: 22px;
    text-align: center;
    flex-shrink: 0;
  }

  /* Settings group styling */
  .lnb-group.settings-group .lnb-group-title {
    color: #34d399;
  }

  .lnb-group.settings-group .lnb-menu li a.active {
    background: #065f46;
    border-left-color: #34d399;
  }

  .lnb-group.settings-group .lnb-menu li a:hover {
    background: #1e3a3a;
  }

  /* Mobile toggle button */
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
  }

  @media (max-width: 768px) {
    .lnb-toggle {
      display: block;
    }
  }
`;

/**
 * LNB HTML 생성
 * @param {string} currentPath - 현재 경로
 * @returns {string} LNB HTML
 */
function createLNB(currentPath) {
  currentPath = currentPath || window.location.pathname;

  function menuItems(items, groupClass) {
    return items.map(item => {
      let isActive = false;
      if (item.path === '/dashboard') {
        isActive = currentPath === item.path || currentPath === '/';
      } else {
        isActive = currentPath.startsWith(item.path);
      }
      const activeClass = isActive ? 'active' : '';
      return `<li><a href="${item.path}" class="${activeClass}" data-tooltip="${item.label}"><span class="menu-icon">${item.icon}</span><span class="menu-label">${item.label}</span></a></li>`;
    }).join('\n');
  }

  return `
    <div class="lnb-logo">
      <a href="/dashboard">
        <span>Personal AI Brain</span>
      </a>
      <div class="logo-sub">Knowledge Management System</div>
    </div>
    <div class="lnb-group" data-menu-group="user-menu">
      <div class="lnb-group-title">사용자 메뉴</div>
      <ul class="lnb-menu user-menu">
        ${menuItems(USER_MENU, 'user-menu')}
      </ul>
    </div>
    <div class="lnb-group" data-menu-group="admin-menu">
      <div class="lnb-group-title">지식 관리</div>
      <ul class="lnb-menu admin-menu">
        ${menuItems(ADMIN_MENU, 'admin-menu')}
      </ul>
    </div>
    <div class="lnb-group system-group" data-menu-group="system-menu">
      <div class="lnb-group-title">시스템 관리</div>
      <ul class="lnb-menu system-menu">
        ${menuItems(SYSTEM_MENU, 'system-menu')}
      </ul>
    </div>
    <div class="lnb-group settings-group" data-menu-group="settings-menu">
      <div class="lnb-group-title">설정 관리</div>
      <ul class="lnb-menu settings-menu">
        ${menuItems(SETTINGS_MENU, 'settings-menu')}
      </ul>
    </div>
    <button class="lnb-collapse-btn" onclick="toggleCollapseLNB()" aria-label="메뉴 접기/펼치기">
      <span class="collapse-icon">\u25C0</span>
      <span class="collapse-label">메뉴 접기</span>
    </button>
  `;
}

/**
 * LNB를 #lnb-sidebar에 렌더링 (Phase 14-3)
 * @param {string} currentPath - 현재 경로
 */
function renderLNB(currentPath) {
  // LNB 스타일 추가
  if (!document.getElementById('lnb-component-styles')) {
    const style = document.createElement('style');
    style.id = 'lnb-component-styles';
    style.textContent = LNB_STYLES;
    document.head.appendChild(style);
  }

  const lnbEl = document.getElementById('lnb-sidebar');
  if (!lnbEl) return;

  // @trusted: 개발자 정의 메뉴 배열만 사용
  lnbEl.innerHTML = createLNB(currentPath);

  // 역할 기반 메뉴 필터링
  fetchUserRole().then(role => applyMenuPermissions(role));
}

// ============================================
// Header (Top Bar) — Phase 14-3 (심플 버전)
// ============================================

const HEADER_STYLES = `
  .top-bar {
    background: white;
    padding: 16px 0;
    margin-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .top-bar h2 {
    color: #1e293b;
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }

  .top-bar .top-bar-separator {
    color: #d1d5db;
    font-size: 16px;
    font-weight: 300;
  }

  .top-bar p.subtitle {
    color: #6b7280;
    margin: 0;
    font-size: 14px;
  }
`;

/**
 * Header HTML 생성 (심플 상단 바 — Phase 14-3)
 * @param {object} options - 헤더 옵션
 * @returns {string} Header HTML
 */
function createHeader(options = {}) {
  const subtitle = options.subtitle || '';
  const currentPath = options.currentPath || window.location.pathname;

  // 현재 경로에 해당하는 메뉴 라벨 찾기
  let currentMenuLabel = '';

  const userMenuItem = USER_MENU.find(item => {
    if (item.path === '/dashboard') {
      return currentPath === item.path || currentPath === '/';
    }
    return currentPath.startsWith(item.path);
  });

  if (userMenuItem) {
    currentMenuLabel = `${userMenuItem.icon} ${userMenuItem.label}`;
  } else {
    const settingsMenuItem = SETTINGS_MENU.find(item => currentPath.startsWith(item.path));
    if (settingsMenuItem) {
      currentMenuLabel = `${settingsMenuItem.icon} ${settingsMenuItem.label}`;
    } else {
      const adminMenuItem = ADMIN_MENU.find(item => currentPath.startsWith(item.path));
      if (adminMenuItem) {
        currentMenuLabel = `${adminMenuItem.icon} ${adminMenuItem.label}`;
      }
    }
  }

  return `
    <div class="top-bar">
      ${currentMenuLabel ? `<h2>${currentMenuLabel}</h2>` : '<h2></h2>'}
      ${subtitle ? `<div class="top-bar-separator">|</div><p class="subtitle">${subtitle}</p>` : ''}
    </div>
  `;
}

/**
 * Header + LNB를 페이지에 렌더링 (Phase 14-3)
 * @param {object} options - 옵션
 */
function renderHeader(options = {}) {
  const containerSelector = options.containerSelector || '.container';

  // Header 스타일 추가
  if (!document.getElementById('header-component-styles')) {
    const style = document.createElement('style');
    style.id = 'header-component-styles';
    style.textContent = HEADER_STYLES;
    document.head.appendChild(style);
  }

  // Header HTML 생성 (심플 상단 바)
  const headerHTML = createHeader(options);

  // 컨테이너에 Header 삽입
  const container = document.querySelector(containerSelector);
  if (container) {
    // 기존 header 또는 top-bar 제거
    const existing = container.querySelector('header, .top-bar');
    if (existing) existing.remove();

    container.insertAdjacentHTML('afterbegin', headerHTML);
  }

  // LNB 렌더링
  renderLNB(options.currentPath);
}

// ============================================
// 역할 기반 필터링 (Phase 14-1)
// ============================================

/**
 * 사용자 역할 조회 (캐시 지원, 인증 리다이렉트 포함)
 * Phase 14 QC 4.1: auth_enabled 시 비인증 admin 접근 → /login 리다이렉트
 * @returns {Promise<string>} 사용자 역할
 */
async function fetchUserRole() {
  if (_cachedUserRole !== null) return _cachedUserRole;

  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const res = await fetch('/api/auth/me', { headers });
    if (res.ok) {
      const data = await res.json();

      // Phase 15-6-3: 비인증 시 보호 페이지 접근 → 로그인 리다이렉트
      if (data.auth_enabled && !data.authenticated) {
        const path = window.location.pathname;
        // 공개 페이지: /, /login, /dashboard 외 모든 페이지는 보호 대상
        const publicPaths = ['/', '/login', '/dashboard'];
        if (!publicPaths.includes(path)) {
          window.location.href = '/login?return_to=' + encodeURIComponent(path);
          return 'user';
        }
      }

      _cachedUserRole = data.role || 'user';
    } else {
      _cachedUserRole = 'user';
    }
  } catch (e) {
    console.warn('사용자 역할 조회 실패, 기본 role=user 적용:', e);
    _cachedUserRole = 'user';
  }

  return _cachedUserRole;
}

/**
 * 역할 기반 메뉴 그룹 표시/숨김 (Phase 14-1, Phase 14-3 LNB 대응)
 * @param {string} userRole - 사용자 역할
 */
function applyMenuPermissions(userRole) {
  const roleLevel = ROLE_HIERARCHY[userRole] ?? 0;

  Object.entries(MENU_REQUIRED_ROLE).forEach(([menuClass, requiredRole]) => {
    const requiredLevel = ROLE_HIERARCHY[requiredRole] ?? 0;

    // LNB에서 메뉴 그룹 찾기 (Phase 14-3)
    const lnbGroup = document.querySelector(`.lnb-group[data-menu-group="${menuClass}"]`);
    if (lnbGroup && roleLevel < requiredLevel) {
      lnbGroup.style.display = 'none';
    }
  });
}

// 전역으로 export (브라우저 환경)
if (typeof window !== 'undefined') {
  if (!window.renderHeader) {
    window.createHeader = createHeader;
    window.renderHeader = renderHeader;
    window.renderLNB = renderLNB;
    window.createLNB = createLNB;
    window.fetchUserRole = fetchUserRole;
    window.applyMenuPermissions = applyMenuPermissions;
    window.USER_MENU = USER_MENU;
    window.ADMIN_MENU = ADMIN_MENU;
    window.SETTINGS_MENU = SETTINGS_MENU;
    window.ROLE_HIERARCHY = ROLE_HIERARCHY;
    window.MENU_REQUIRED_ROLE = MENU_REQUIRED_ROLE;
  }
}
