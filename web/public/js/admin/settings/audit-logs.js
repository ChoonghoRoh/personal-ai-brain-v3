/**
 * Audit Log Viewer Page JS (Phase 11-3)
 */

// State
let currentPage = 1;
let itemsPerPage = 50;
let totalItems = 0;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initEventListeners();
  loadAuditLogs();
});

function initHeader() {
  if (typeof renderHeader === 'function') {
    renderHeader({
      subtitle: 'Admin Audit Log Viewer',
      currentPath: '/admin/settings/audit-logs'
    });
  }
}

function initEventListeners() {
  // Refresh
  document.getElementById('refresh-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadAuditLogs();
  });

  // Filter apply
  document.getElementById('filter-apply-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadAuditLogs();
  });

  // Filter clear
  document.getElementById('filter-clear-btn')?.addEventListener('click', clearFilters);

  // Items per page change
  document.getElementById('items-per-page')?.addEventListener('change', (e) => {
    itemsPerPage = parseInt(e.target.value) || 50;
    currentPage = 1;
    loadAuditLogs();
  });
}

function clearFilters() {
  document.getElementById('filter-table').value = '';
  document.getElementById('filter-action').value = '';
  document.getElementById('filter-changed-by').value = '';
  document.getElementById('filter-from-date').value = '';
  document.getElementById('filter-to-date').value = '';
  currentPage = 1;
  loadAuditLogs();
}

async function loadAuditLogs() {
  const tableBody = document.getElementById('audit-table');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="7" class="loading">Loading...</td></tr>';

  try {
    const params = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      table_name: document.getElementById('filter-table')?.value || '',
      action: document.getElementById('filter-action')?.value || '',
      changed_by: document.getElementById('filter-changed-by')?.value || '',
      from_date: document.getElementById('filter-from-date')?.value || '',
      to_date: document.getElementById('filter-to-date')?.value || '',
    };

    const queryString = buildQueryString(params);
    const data = await adminApiCall(`/audit-logs${queryString}`);

    totalItems = data.total || 0;
    const logs = data.items || [];

    if (logs.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="7" class="loading">No audit logs found</td></tr>';
      document.getElementById('pagination-controls').style.display = 'none';
      return;
    }

    tableBody.innerHTML = logs.map(log => `
      <tr>
        <td>${formatDate(log.created_at)}</td>
        <td>${log.table_name}</td>
        <td>${createActionBadge(log.action)}</td>
        <td>${truncateText(log.record_id, 12)}</td>
        <td>${log.changed_by || '-'}</td>
        <td>${truncateText(log.change_reason, 30) || '-'}</td>
        <td>
          <button class="btn btn-outline btn-small detail-btn" onclick="showDetail('${log.id}')">
            View
          </button>
        </td>
      </tr>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    document.getElementById('pagination-controls').style.display = 'block';
    updatePaginationInfo('pagination-info', currentPage, itemsPerPage, totalItems);
    renderPagination('pagination-buttons', currentPage, totalPages, (page) => {
      currentPage = page;
      loadAuditLogs();
    });

  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="7" class="loading">Error loading audit logs</td></tr>';
    showError('Failed to load audit logs: ' + error.message);
  }
}

async function showDetail(logId) {
  try {
    const log = await adminApiCall(`/audit-logs/${logId}`);

    // Populate basic info
    document.getElementById('detail-basic').innerHTML = `
      <table class="table">
        <tr><th>Timestamp</th><td>${formatDate(log.created_at)}</td></tr>
        <tr><th>Table</th><td>${log.table_name}</td></tr>
        <tr><th>Action</th><td>${createActionBadge(log.action)}</td></tr>
        <tr><th>Record ID</th><td><code>${log.record_id}</code></td></tr>
        <tr><th>Changed By</th><td>${log.changed_by || '-'}</td></tr>
        <tr><th>Reason</th><td>${log.change_reason || '-'}</td></tr>
      </table>
    `;

    // Populate old values
    document.getElementById('detail-old-values').textContent =
      log.old_values ? JSON.stringify(log.old_values, null, 2) : '(empty)';

    // Populate new values
    document.getElementById('detail-new-values').textContent =
      log.new_values ? JSON.stringify(log.new_values, null, 2) : '(empty)';

    // Show modal
    document.getElementById('detail-modal').style.display = 'flex';

  } catch (error) {
    showError('Failed to load audit log detail: ' + error.message);
  }
}

function closeDetailModal() {
  document.getElementById('detail-modal').style.display = 'none';
}

// Close modal on outside click
document.addEventListener('click', (e) => {
  const modal = document.getElementById('detail-modal');
  if (e.target === modal) {
    closeDetailModal();
  }
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeDetailModal();
  }
});

// Export for global use
if (typeof window !== 'undefined') {
  window.showDetail = showDetail;
  window.closeDetailModal = closeDetailModal;
}
