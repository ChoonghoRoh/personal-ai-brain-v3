/**
 * 대시보드 API — Phase 17-7 리뉴얼
 * 4개 API 병렬 호출 → 렌더 함수 위임
 */

async function loadDashboard() {
  try {
    const [status, health, stats, trends] = await Promise.all([
      fetch('/api/system/status').then(r => r.json()),
      fetch('/health/ready').then(r => r.json()).catch(() => ({ status: 'unknown', checks: {} })),
      fetch('/api/system/statistics').then(r => r.json()),
      fetch('/api/system/statistics/trends?days=7').then(r => r.json())
    ]);

    renderSystemStatusBar(status, health);
    renderKnowledgeCards(stats);
    renderRecentDocsCards(status.recent_documents || []);

    // 차트: statistics-charts.js 재사용
    if (typeof updateDocTypeChart === 'function') {
      updateDocTypeChart(stats.documents?.by_type || {});
    }
    if (typeof updateTrendsChart === 'function') {
      updateTrendsChart(trends);
    }
  } catch (error) {
    console.error('Dashboard load error:', error);
  }
}
