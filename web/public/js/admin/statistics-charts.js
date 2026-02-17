/**
 * Statistics Dashboard - Chart Rendering
 * Phase 16-5-2-5: Chart.js 렌더링 함수 분리
 * 의존성: Chart.js, utils.js (formatNumber)
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
 * Capitalize first letter
 */
function capitalizeFirst(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Format trend date (YYYY-MM-DD -> MM/DD)
 * 차트 X축 라벨 전용 포맷터
 */
function formatTrendDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[1]}/${parts[2]}`;
  }
  return dateStr;
}

/**
 * Update document type chart (doughnut)
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
 * Update label type chart (doughnut)
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
  const labels = trendData.map(d => formatTrendDate(d.date));

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
