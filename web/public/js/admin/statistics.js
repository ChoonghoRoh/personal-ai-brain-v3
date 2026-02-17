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
