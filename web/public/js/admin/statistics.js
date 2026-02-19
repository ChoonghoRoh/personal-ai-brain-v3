/**
 * Statistics Dashboard JavaScript
 * Phase 9-4-2: 통계/분석 대시보드
 * Chart 렌더링은 statistics-charts.js 참조
 */

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
  initializeAdminPage({
    title: '📈 통계 대시보드',
    subtitle: '시스템 현황 및 사용량 통계'
  });
  loadAllStatistics();
});

/**
 * Load all statistics
 */
async function loadAllStatistics() {
  try {
    showLoading();

    // Load all data in parallel
    const [summary, knowledge, usage, system, trends, health] = await Promise.all([
      fetchStatistics('/api/system/statistics'),
      fetchStatistics('/api/system/statistics/knowledge'),
      fetchStatistics('/api/system/statistics/usage'),
      fetchStatistics('/api/system/statistics/system'),
      fetchStatistics(`/api/system/statistics/trends?days=${document.getElementById('trendDays')?.value || 7}`),
      fetchStatistics('/health/ready').catch(() => ({ status: 'unknown', checks: {} }))
    ]);

    // Update summary cards
    updateSummaryCards(summary);

    // Update charts (statistics-charts.js)
    updateDocTypeChart(summary.documents?.by_type || {});
    updateChunkStatusChart(summary.chunks?.by_status || {});
    updateLabelTypeChart(summary.labels?.by_type || {});
    updateTrendsChart(trends);

    // Update tables
    updateTopLabelsTable(summary.labels?.top_used || knowledge.labels?.top_used || []);
    updateProjectsTable(knowledge);

    // Update system status
    updateSystemStatus(system, health);

  } catch (error) {
    console.error('Statistics load error:', error);
    showStatError('통계 데이터를 불러오는 중 오류가 발생했습니다.');
  }
}

/**
 * Fetch statistics from API
 */
async function fetchStatistics(endpoint) {
  const response = await fetch(endpoint);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

/**
 * Update summary cards
 */
function updateSummaryCards(data) {
  const summary = data.summary || {};

  // Documents
  document.getElementById('totalDocuments').textContent = formatStatNumber(summary.total_documents || 0);
  document.getElementById('recentDocuments').textContent = `최근 7일: +${data.documents?.recent_7d || 0}`;

  // Chunks
  document.getElementById('totalChunks').textContent = formatStatNumber(summary.total_chunks || 0);
  document.getElementById('approvedChunks').textContent = `승인됨: ${formatStatNumber(summary.approved_chunks || 0)}`;

  // Labels
  document.getElementById('totalLabels').textContent = formatStatNumber(summary.total_labels || 0);
  document.getElementById('totalProjects').textContent = `프로젝트: ${summary.total_projects || 0}`;

  // Usage
  document.getElementById('todayUsage').textContent = formatStatNumber(data.usage?.reasoning_today || 0);
  document.getElementById('totalReasoning').textContent = `총 추론: ${formatStatNumber(data.usage?.reasoning_total || 0)}`;
}

/**
 * Update top labels table
 */
function updateTopLabelsTable(labels) {
  const tbody = document.getElementById('topLabelsBody');

  if (!labels || labels.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="loading">데이터 없음</td></tr>';
    return;
  }

  tbody.innerHTML = labels.map((label, index) => `
    <tr>
      <td>${index + 1}</td>
      <td>${escapeHtml(label.name)}</td>
      <td>${escapeHtml(label.type || '-')}</td>
      <td>${formatStatNumber(label.usage_count || 0)}</td>
    </tr>
  `).join('');
}

/**
 * Update projects table
 */
function updateProjectsTable(data) {
  const tbody = document.getElementById('projectsBody');

  const docsByProject = data.documents?.by_project || [];
  const chunksByProject = data.chunks?.by_project || [];

  // Merge data
  const projectMap = new Map();

  docsByProject.forEach(p => {
    projectMap.set(p.project_id, {
      name: p.project_name || 'Unknown',
      documents: p.count || 0,
      chunks: 0
    });
  });

  chunksByProject.forEach(p => {
    if (projectMap.has(p.project_id)) {
      projectMap.get(p.project_id).chunks = p.count || 0;
    } else {
      projectMap.set(p.project_id, {
        name: p.project_name || 'Unknown',
        documents: 0,
        chunks: p.count || 0
      });
    }
  });

  const projects = Array.from(projectMap.values());

  if (projects.length === 0) {
    tbody.innerHTML = '<tr><td colspan="3" class="loading">데이터 없음</td></tr>';
    return;
  }

  tbody.innerHTML = projects.map(p => `
    <tr>
      <td>${escapeHtml(p.name)}</td>
      <td>${formatStatNumber(p.documents)}</td>
      <td>${formatStatNumber(p.chunks)}</td>
    </tr>
  `).join('');
}

/**
 * Update system status
 */
function updateSystemStatus(data, health) {
  const checks = health?.checks || {};

  // Database status
  const dbTables = data.database?.tables || {};
  const totalRecords = data.database?.total_records || 0;
  const dbEl = document.getElementById('dbStatus');
  if (checks.postgres === 'ok') {
    dbEl.textContent = `OK (${Object.keys(dbTables).length} 테이블)`;
    dbEl.classList.add('success');
  } else if (checks.postgres) {
    dbEl.textContent = 'Error';
    dbEl.classList.add('error');
  } else {
    dbEl.textContent = `${Object.keys(dbTables).length} 테이블`;
    dbEl.classList.add('success');
  }

  // Qdrant status
  const qdrant = data.qdrant || {};
  const qdrantEl = document.getElementById('qdrantStatus');
  if (checks.qdrant === 'ok') {
    qdrantEl.textContent = `OK (${formatStatNumber(qdrant.vectors_count || 0)} 벡터)`;
    qdrantEl.classList.add('success');
  } else if (qdrant.error || (checks.qdrant && checks.qdrant !== 'ok')) {
    qdrantEl.textContent = 'Error';
    qdrantEl.classList.add('error');
  } else {
    qdrantEl.textContent = formatStatNumber(qdrant.vectors_count || 0) + ' 벡터';
    qdrantEl.classList.add('success');
  }

  // Redis status
  const redisEl = document.getElementById('redisStatus');
  if (redisEl) {
    if (checks.redis === 'ok') {
      redisEl.textContent = 'OK';
      redisEl.classList.add('success');
    } else if (checks.redis && checks.redis.startsWith('skipped')) {
      redisEl.textContent = '미설정';
      redisEl.classList.add('warning');
    } else if (checks.redis) {
      redisEl.textContent = 'Error';
      redisEl.classList.add('error');
    }
  }

  // Ollama LLM status
  const ollamaEl = document.getElementById('ollamaStatus');
  if (ollamaEl) {
    const ollama = data.ollama || {};
    if (ollama.status === 'available' || ollama.status === 'connected') {
      ollamaEl.textContent = `OK (${ollama.model_name || 'model'})`;
      ollamaEl.classList.add('success');
    } else if (ollama.status === 'not_installed') {
      ollamaEl.textContent = '미설치';
      ollamaEl.classList.add('warning');
    } else if (ollama.status === 'error') {
      ollamaEl.textContent = 'Error';
      ollamaEl.classList.add('error');
    } else {
      ollamaEl.textContent = '-';
    }
  }

  // Total records
  document.getElementById('totalRecords').textContent = formatStatNumber(totalRecords);
}

/**
 * Show loading state
 */
function showLoading() {
  document.getElementById('totalDocuments').textContent = '...';
  document.getElementById('totalChunks').textContent = '...';
  document.getElementById('totalLabels').textContent = '...';
  document.getElementById('todayUsage').textContent = '...';
}

/**
 * Show error message (statistics 전용)
 */
function showStatError(message) {
  console.error(message);
}

/**
 * Format number with commas (statistics 전용: toLocaleString)
 */
function formatStatNumber(num) {
  return num.toLocaleString('ko-KR');
}

// ==================== Phase 17-5: 카드 클릭 필터링 ====================

var _currentCategory = null;
var _currentPage = 1;
var _pageSize = 20;
var _searchTimer = null;

// 카드 클릭 이벤트 바인딩
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.summary-card').forEach(function (card) {
    card.style.cursor = 'pointer';
    card.addEventListener('click', function () {
      var category = this.getAttribute('data-category');
      if (category) activateCategory(category);
    });
  });

  // 검색 debounce
  var searchInput = document.getElementById('filteredSearchInput');
  if (searchInput) {
    searchInput.addEventListener('input', function () {
      if (_searchTimer) clearTimeout(_searchTimer);
      _searchTimer = setTimeout(function () { applyFilters(); }, 300);
    });
  }

  // 유형 필터 변경
  var typeFilter = document.getElementById('filteredTypeFilter');
  if (typeFilter) {
    typeFilter.addEventListener('change', function () { applyFilters(); });
  }
});

function activateCategory(category) {
  _currentCategory = category;
  _currentPage = 1;

  // 카드 active 상태
  document.querySelectorAll('.summary-card').forEach(function (c) { c.classList.remove('active'); });
  var activeCard = document.querySelector('.summary-card[data-category="' + category + '"]');
  if (activeCard) activeCard.classList.add('active');

  // 탭 active
  document.querySelectorAll('.filtered-list-tabs .tab-btn').forEach(function (btn) {
    btn.classList.toggle('active', btn.getAttribute('data-category') === category);
  });

  // 필터 옵션 업데이트
  updateFilterOptions(category);

  // 섹션 표시 + 스크롤
  var section = document.getElementById('filtered-list-section');
  if (section) {
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  loadFilteredList(category, 1);
}

function switchCategory(category) {
  activateCategory(category);
}

function closeFilteredList() {
  var section = document.getElementById('filtered-list-section');
  if (section) section.style.display = 'none';
  document.querySelectorAll('.summary-card').forEach(function (c) { c.classList.remove('active'); });
  _currentCategory = null;
}

function updateFilterOptions(category) {
  var select = document.getElementById('filteredTypeFilter');
  if (!select) return;
  var options = '<option value="">전체</option>';
  if (category === 'documents') {
    options += '<option value="md">.md</option><option value="txt">.txt</option><option value="pdf">.pdf</option><option value="json">.json</option>';
  } else if (category === 'chunks') {
    options += '<option value="approved">승인</option><option value="pending">대기</option><option value="rejected">거부</option>';
  } else if (category === 'labels') {
    options += '<option value="keyword">keyword</option><option value="category">category</option><option value="project">project</option>';
  } else if (category === 'usage') {
    options += '<option value="design_explain">설계 설명</option><option value="risk_review">리스크 분석</option><option value="next_steps">다음 단계</option><option value="history_trace">히스토리 추적</option>';
  }
  select.innerHTML = options;

  // 검색 초기화
  var searchInput = document.getElementById('filteredSearchInput');
  if (searchInput) searchInput.value = '';
  var sortOrder = document.getElementById('filteredSortOrder');
  if (sortOrder) sortOrder.value = 'desc';
}

async function loadFilteredList(category, page) {
  if (!category) return;
  _currentCategory = category;
  _currentPage = page || 1;

  var searchInput = document.getElementById('filteredSearchInput');
  var typeFilter = document.getElementById('filteredTypeFilter');
  var sortOrder = document.getElementById('filteredSortOrder');
  var q = searchInput ? searchInput.value.trim() : '';
  var filterVal = typeFilter ? typeFilter.value : '';
  var sort = sortOrder ? sortOrder.value : 'desc';

  var url = '/api/system/statistics/' + category + '/list?page=' + _currentPage + '&size=' + _pageSize + '&sort_order=' + sort;
  if (q) url += '&q=' + encodeURIComponent(q);

  if (category === 'documents' && filterVal) url += '&type=' + encodeURIComponent(filterVal);
  else if (category === 'chunks' && filterVal) url += '&status=' + encodeURIComponent(filterVal);
  else if (category === 'labels' && filterVal) url += '&label_type=' + encodeURIComponent(filterVal);
  else if (category === 'usage' && filterVal) url += '&mode=' + encodeURIComponent(filterVal);

  var tbody = document.getElementById('filteredTableBody');
  if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="loading">로딩 중...</td></tr>';

  try {
    var resp = await fetch(url);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    var data = await resp.json();
    renderFilteredTable(category, data);
    renderFilteredPagination(data.total, data.page, data.total_pages);
  } catch (e) {
    console.error('필터 목록 로드 실패:', e);
    if (tbody) tbody.innerHTML = '<tr><td colspan="5" class="loading">로드 실패</td></tr>';
  }
}

function applyFilters() {
  if (_currentCategory) loadFilteredList(_currentCategory, 1);
}

function resetFilters() {
  var searchInput = document.getElementById('filteredSearchInput');
  var typeFilter = document.getElementById('filteredTypeFilter');
  var sortOrder = document.getElementById('filteredSortOrder');
  if (searchInput) searchInput.value = '';
  if (typeFilter) typeFilter.value = '';
  if (sortOrder) sortOrder.value = 'desc';
  if (_currentCategory) loadFilteredList(_currentCategory, 1);
}

function renderFilteredTable(category, data) {
  var thead = document.getElementById('filteredTableHead');
  var tbody = document.getElementById('filteredTableBody');
  if (!thead || !tbody) return;

  var items = data.items || [];

  // 카테고리별 헤더
  if (category === 'documents') {
    thead.innerHTML = '<tr><th>#</th><th>파일명</th><th>유형</th><th>경로</th><th>생성일</th></tr>';
    tbody.innerHTML = items.length === 0
      ? '<tr><td colspan="5" class="loading">데이터 없음</td></tr>'
      : items.map(function (d, i) {
          var date = d.created_at ? new Date(d.created_at).toLocaleDateString('ko-KR') : '-';
          return '<tr><td>' + ((_currentPage - 1) * _pageSize + i + 1) + '</td>'
            + '<td>' + escapeHtml(d.file_name || '-') + '</td>'
            + '<td>' + escapeHtml(d.file_type || '-') + '</td>'
            + '<td title="' + escapeHtml(d.file_path || '') + '">' + escapeHtml((d.file_path || '').split('/').pop() || '-') + '</td>'
            + '<td>' + date + '</td></tr>';
        }).join('');
  } else if (category === 'chunks') {
    thead.innerHTML = '<tr><th>#</th><th>내용</th><th>상태</th><th>문서 ID</th><th>생성일</th></tr>';
    tbody.innerHTML = items.length === 0
      ? '<tr><td colspan="5" class="loading">데이터 없음</td></tr>'
      : items.map(function (c, i) {
          var date = c.created_at ? new Date(c.created_at).toLocaleDateString('ko-KR') : '-';
          var statusClass = c.status === 'approved' ? 'success' : (c.status === 'pending' ? 'warning' : '');
          return '<tr><td>' + ((_currentPage - 1) * _pageSize + i + 1) + '</td>'
            + '<td>' + escapeHtml(c.content || '-') + '</td>'
            + '<td><span class="status-badge ' + statusClass + '">' + escapeHtml(c.status || '-') + '</span></td>'
            + '<td>' + (c.document_id || '-') + '</td>'
            + '<td>' + date + '</td></tr>';
        }).join('');
  } else if (category === 'labels') {
    thead.innerHTML = '<tr><th>#</th><th>이름</th><th>유형</th><th>사용 횟수</th></tr>';
    tbody.innerHTML = items.length === 0
      ? '<tr><td colspan="4" class="loading">데이터 없음</td></tr>'
      : items.map(function (l, i) {
          return '<tr><td>' + ((_currentPage - 1) * _pageSize + i + 1) + '</td>'
            + '<td>' + escapeHtml(l.name || '-') + '</td>'
            + '<td>' + escapeHtml(l.label_type || '-') + '</td>'
            + '<td>' + formatStatNumber(l.usage_count || 0) + '</td></tr>';
        }).join('');
  } else if (category === 'usage') {
    thead.innerHTML = '<tr><th>#</th><th>질문</th><th>모드</th><th>요약</th><th>생성일</th></tr>';
    tbody.innerHTML = items.length === 0
      ? '<tr><td colspan="5" class="loading">데이터 없음</td></tr>'
      : items.map(function (r, i) {
          var date = r.created_at ? new Date(r.created_at).toLocaleDateString('ko-KR') : '-';
          return '<tr><td>' + ((_currentPage - 1) * _pageSize + i + 1) + '</td>'
            + '<td>' + escapeHtml(r.question || '-') + '</td>'
            + '<td>' + escapeHtml(r.mode || '-') + '</td>'
            + '<td>' + escapeHtml(r.summary || '-') + '</td>'
            + '<td>' + date + '</td></tr>';
        }).join('');
  }
}

function renderFilteredPagination(total, currentPage, totalPages) {
  var container = document.getElementById('filteredPagination');
  if (!container) return;
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  var html = '<div class="pagination-controls">';
  html += '<button class="btn btn-sm pagination-btn" onclick="loadFilteredList(\'' + _currentCategory + '\',' + (currentPage - 1) + ')"' + (currentPage <= 1 ? ' disabled' : '') + '>&laquo; 이전</button>';
  html += '<span class="pagination-info">' + currentPage + ' / ' + totalPages + ' (총 ' + formatStatNumber(total) + '건)</span>';
  html += '<button class="btn btn-sm pagination-btn" onclick="loadFilteredList(\'' + _currentCategory + '\',' + (currentPage + 1) + ')"' + (currentPage >= totalPages ? ' disabled' : '') + '>다음 &raquo;</button>';
  html += '</div>';
  container.innerHTML = html;
}
