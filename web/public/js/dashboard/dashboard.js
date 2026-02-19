/**
 * 대시보드 렌더링 — Phase 17-7 리뉴얼
 * 6단 레이아웃: 상태바 → 지식현황 → Reasoning → 바로가기 → 최근문서 → 차트
 */

const DASHBOARD_REFRESH_INTERVAL = 30000;

// Layout 초기화
document.addEventListener('DOMContentLoaded', () => {
  initLayout();
  if (typeof renderHeader === 'function') {
    renderHeader({
      title: '🧠 Personal AI Brain',
      subtitle: '개인 지식 관리 시스템 대시보드',
      currentPath: '/dashboard'
    });
  }
});

/**
 * 1단: 시스템 상태 한줄 바
 */
function renderSystemStatusBar(status, health) {
  const checks = health?.checks || {};

  // PostgreSQL
  const pgOk = status.database?.status === 'connected';
  setDot('indPostgres', pgOk ? 'ok' : 'error');

  // Qdrant
  const qdOk = status.qdrant?.status === 'connected';
  setDot('indQdrant', qdOk ? 'ok' : 'error');

  // Redis
  if (checks.redis === 'ok') setDot('indRedis', 'ok');
  else if (checks.redis && checks.redis.startsWith('skipped')) setDot('indRedis', 'warn');
  else setDot('indRedis', checks.redis ? 'error' : 'warn');

  // Ollama
  const g = status.gpt4all || {};
  const ollamaOk = g.status === 'available' || g.status === 'available_via_host';
  setDot('indOllama', ollamaOk ? 'ok' : (g.status === 'not_installed' ? 'warn' : 'error'));
}

function setDot(id, state) {
  const el = document.getElementById(id);
  if (!el) return;
  const dot = el.querySelector('.dot');
  if (dot) dot.className = 'dot ' + state;
}

/**
 * 2단: 등록 지식 현황 카드
 */
function renderKnowledgeCards(stats) {
  const s = stats.summary || {};
  setText('dashTotalDocs', (s.total_documents || 0).toLocaleString('ko-KR'));
  setText('dashTotalChunks', (s.total_chunks || 0).toLocaleString('ko-KR'));
  setText('dashTotalLabels', (s.total_labels || 0).toLocaleString('ko-KR'));
  setText('dashTotalProjects', (s.total_projects || 0).toLocaleString('ko-KR'));
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

/**
 * 5단: 최근 업데이트 문서 카드뷰
 */
function renderRecentDocsCards(docs) {
  const grid = document.getElementById('recentDocsGrid');
  if (!grid) return;

  if (!docs || docs.length === 0) {
    grid.innerHTML = '<div class="loading">최근 문서가 없습니다.</div>';
    return;
  }

  grid.innerHTML = docs.slice(0, 8).map(doc => {
    const folder = (doc.file_path || '').split('/').slice(0, -1).join('/') || '-';
    return `<div class="rd-card">
      <div class="rd-title">${escapeHtml(doc.name || '-')}</div>
      <div class="rd-folder">📁 ${escapeHtml(folder)}</div>
    </div>`;
  }).join('');
}

// 페이지 로드 시 실행
loadDashboard();

// 자동 새로고침 (30초)
setInterval(loadDashboard, DASHBOARD_REFRESH_INTERVAL);
