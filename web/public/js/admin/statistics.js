/**
 * Statistics Dashboard JavaScript
 * Phase 9-4-2: 통계/분석 대시보드
 */

// Chart instances (for cleanup on refresh)
let docTypeChart = null;
let chunkStatusChart = null;
let labelTypeChart = null;
let trendsChart = null;

// Color palette for charts
const CHART_COLORS = {
  primary: ['#4e79a7', '#f28e2c', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#af7aa1', '#ff9da7', '#9c755f', '#bab0ab'],
  status: {
    approved: '#28a745',
    pending: '#ffc107',
    rejected: '#dc3545',
    unknown: '#6c757d'
  }
};

/**
 * Initialize page
 */
document.addEventListener('DOMContentLoaded', () => {
  renderHeader();
  loadAllStatistics();
});

/**
 * Load all statistics
 */
async function loadAllStatistics() {
  try {
    showLoading();

    // Load all data in parallel
    const [summary, knowledge, usage, system, trends] = await Promise.all([
      fetchStatistics('/api/system/statistics'),
      fetchStatistics('/api/system/statistics/knowledge'),
      fetchStatistics('/api/system/statistics/usage'),
      fetchStatistics('/api/system/statistics/system'),
      fetchStatistics(`/api/system/statistics/trends?days=${document.getElementById('trendDays')?.value || 7}`)
    ]);

    // Update summary cards
    updateSummaryCards(summary);

    // Update charts
    updateDocTypeChart(summary.documents?.by_type || {});
    updateChunkStatusChart(summary.chunks?.by_status || {});
    updateLabelTypeChart(summary.labels?.by_type || {});
    updateTrendsChart(trends);

    // Update tables
    updateTopLabelsTable(summary.labels?.top_used || knowledge.labels?.top_used || []);
    updateProjectsTable(knowledge);

    // Update system status
    updateSystemStatus(system);

  } catch (error) {
    console.error('Statistics load error:', error);
    showError('통계 데이터를 불러오는 중 오류가 발생했습니다.');
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
  document.getElementById('totalDocuments').textContent = formatNumber(summary.total_documents || 0);
  document.getElementById('recentDocuments').textContent = `최근 7일: +${data.documents?.recent_7d || 0}`;

  // Chunks
  document.getElementById('totalChunks').textContent = formatNumber(summary.total_chunks || 0);
  document.getElementById('approvedChunks').textContent = `승인됨: ${formatNumber(summary.approved_chunks || 0)}`;

  // Labels
  document.getElementById('totalLabels').textContent = formatNumber(summary.total_labels || 0);
  document.getElementById('totalProjects').textContent = `프로젝트: ${summary.total_projects || 0}`;

  // Usage
  document.getElementById('todayUsage').textContent = formatNumber(data.usage?.reasoning_today || 0);
  document.getElementById('totalReasoning').textContent = `총 추론: ${formatNumber(data.usage?.reasoning_total || 0)}`;
}

/**
 * Update document type chart (pie)
 */
function updateDocTypeChart(data) {
  const ctx = document.getElementById('docTypeChart').getContext('2d');

  // Destroy existing chart
  if (docTypeChart) {
    docTypeChart.destroy();
  }

  const labels = Object.keys(data);
  const values = Object.values(data);

  if (labels.length === 0) {
    labels.push('데이터 없음');
    values.push(1);
  }

  docTypeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.toUpperCase()),
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS.primary.slice(0, labels.length),
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            usePointStyle: true
          }
        }
      }
    }
  });
}

/**
 * Update chunk status chart (bar)
 */
function updateChunkStatusChart(data) {
  const ctx = document.getElementById('chunkStatusChart').getContext('2d');

  // Destroy existing chart
  if (chunkStatusChart) {
    chunkStatusChart.destroy();
  }

  const labels = Object.keys(data);
  const values = Object.values(data);
  const colors = labels.map(l => CHART_COLORS.status[l] || CHART_COLORS.status.unknown);

  chunkStatusChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels.map(capitalizeFirst),
      datasets: [{
        label: '청크 수',
        data: values,
        backgroundColor: colors,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: Math.ceil(Math.max(...values, 1) / 5)
          }
        }
      }
    }
  });
}

/**
 * Update label type chart (pie)
 */
function updateLabelTypeChart(data) {
  const ctx = document.getElementById('labelTypeChart').getContext('2d');

  // Destroy existing chart
  if (labelTypeChart) {
    labelTypeChart.destroy();
  }

  const labels = Object.keys(data);
  const values = Object.values(data);

  if (labels.length === 0) {
    labels.push('데이터 없음');
    values.push(1);
  }

  labelTypeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.map(capitalizeFirst),
      datasets: [{
        data: values,
        backgroundColor: CHART_COLORS.primary.slice(0, labels.length),
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            usePointStyle: true
          }
        }
      }
    }
  });
}

/**
 * Update trends chart (line)
 */
function updateTrendsChart(data) {
  const ctx = document.getElementById('trendsChart').getContext('2d');

  // Destroy existing chart
  if (trendsChart) {
    trendsChart.destroy();
  }

  const trendData = data.data || [];
  const labels = trendData.map(d => formatDate(d.date));

  trendsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: '문서',
          data: trendData.map(d => d.documents || 0),
          borderColor: CHART_COLORS.primary[0],
          backgroundColor: CHART_COLORS.primary[0] + '20',
          fill: true,
          tension: 0.3
        },
        {
          label: '청크',
          data: trendData.map(d => d.chunks || 0),
          borderColor: CHART_COLORS.primary[1],
          backgroundColor: CHART_COLORS.primary[1] + '20',
          fill: true,
          tension: 0.3
        },
        {
          label: '추론',
          data: trendData.map(d => d.reasoning || 0),
          borderColor: CHART_COLORS.primary[2],
          backgroundColor: CHART_COLORS.primary[2] + '20',
          fill: true,
          tension: 0.3
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
}

/**
 * Load trends with selected days
 */
async function loadTrends() {
  try {
    const days = document.getElementById('trendDays').value;
    const trends = await fetchStatistics(`/api/system/statistics/trends?days=${days}`);
    updateTrendsChart(trends);
  } catch (error) {
    console.error('Trends load error:', error);
  }
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
      <td>${formatNumber(label.usage_count || 0)}</td>
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
      <td>${formatNumber(p.documents)}</td>
      <td>${formatNumber(p.chunks)}</td>
    </tr>
  `).join('');
}

/**
 * Update system status
 */
function updateSystemStatus(data) {
  // Database status
  const dbTables = data.database?.tables || {};
  const totalRecords = data.database?.total_records || 0;
  document.getElementById('dbStatus').textContent = `${Object.keys(dbTables).length} 테이블`;
  document.getElementById('dbStatus').classList.add('success');

  // Qdrant status
  const qdrant = data.qdrant || {};
  if (qdrant.error) {
    document.getElementById('qdrantStatus').textContent = '연결 실패';
    document.getElementById('qdrantStatus').classList.add('error');
  } else {
    document.getElementById('qdrantStatus').textContent = formatNumber(qdrant.vectors_count || 0) + ' 벡터';
    document.getElementById('qdrantStatus').classList.add('success');
  }

  // Total records
  document.getElementById('totalRecords').textContent = formatNumber(totalRecords);
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
 * Show error message
 */
function showError(message) {
  console.error(message);
  // Could add a toast notification here
}

/**
 * Format number with commas
 */
function formatNumber(num) {
  return num.toLocaleString('ko-KR');
}

/**
 * Format date (YYYY-MM-DD -> MM/DD)
 */
function formatDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[1]}/${parts[2]}`;
  }
  return dateStr;
}

/**
 * Capitalize first letter
 */
function capitalizeFirst(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Escape HTML
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
