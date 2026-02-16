/**
 * Settings Management Common JS (Phase 11-3)
 * Shared utilities for Template, Preset, RAG Profile, Policy Set pages
 */

// API Base URL
const ADMIN_API_BASE = '/api/admin';

/**
 * Generic API call wrapper
 */
async function adminApiCall(endpoint, options = {}) {
  const url = `${ADMIN_API_BASE}${endpoint}`;
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  // JWT 토큰 첨부 (Phase 14 QC 4.1)
  const token = localStorage.getItem('auth_token');
  if (token) {
    defaultHeaders['Authorization'] = 'Bearer ' + token;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) {
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Show success message
 */
function showSuccess(message) {
  const el = document.getElementById('success-message');
  if (el) {
    el.textContent = message;
    el.style.display = 'block';
    setTimeout(() => {
      el.style.display = 'none';
    }, 3000);
  }
}

/**
 * Show error message
 */
function showError(message) {
  const el = document.getElementById('error-message');
  if (el) {
    el.textContent = message;
    el.style.display = 'block';
    setTimeout(() => {
      el.style.display = 'none';
    }, 5000);
  }
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format date for input[type="datetime-local"]
 */
function formatDateForInput(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toISOString().slice(0, 16);
}

/**
 * Create status badge HTML
 */
function createStatusBadge(status) {
  const statusClass = status === 'published' ? 'published' : 'draft';
  return `<span class="status-badge ${statusClass}">${status}</span>`;
}

/**
 * Create active badge HTML
 */
function createActiveBadge(isActive) {
  const statusClass = isActive ? 'active' : 'inactive';
  const label = isActive ? 'Active' : 'Inactive';
  return `<span class="status-badge ${statusClass}">${label}</span>`;
}

/**
 * Create action badge HTML for audit logs
 */
function createActionBadge(action) {
  return `<span class="action-badge ${action}">${action}</span>`;
}

/**
 * Truncate text with ellipsis
 */
function truncateText(text, maxLength = 50) {
  if (!text) return '';
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

/**
 * Extract template variables from content
 */
function extractVariables(content) {
  if (!content) return [];
  const regex = /\{\{(\w+)\}\}/g;
  const variables = [];
  let match;
  while ((match = regex.exec(content)) !== null) {
    if (!variables.includes(match[1])) {
      variables.push(match[1]);
    }
  }
  return variables;
}

/**
 * Render variables as tags
 */
function renderVariableTags(variables) {
  if (!variables || variables.length === 0) {
    return '<span class="hint">No variables detected</span>';
  }
  return variables.map(v => `<span class="variable-tag">{{${v}}}</span>`).join('');
}

/**
 * Build query string from object
 */
function buildQueryString(params) {
  const filtered = Object.entries(params)
    .filter(([_, v]) => v !== '' && v !== null && v !== undefined)
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
  return filtered.length > 0 ? '?' + filtered.join('&') : '';
}

/**
 * Simple pagination renderer
 */
function renderPagination(containerId, currentPage, totalPages, onPageChange) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = '';

  if (totalPages <= 1) {
    container.parentElement.style.display = 'none';
    return;
  }

  container.parentElement.style.display = 'block';

  // Previous button
  const prevBtn = document.createElement('button');
  prevBtn.className = 'btn btn-outline btn-small';
  prevBtn.textContent = 'Prev';
  prevBtn.disabled = currentPage <= 1;
  prevBtn.onclick = () => onPageChange(currentPage - 1);
  container.appendChild(prevBtn);

  // Page numbers
  const maxVisiblePages = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
  let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

  if (endPage - startPage < maxVisiblePages - 1) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1);
  }

  if (startPage > 1) {
    const firstBtn = document.createElement('button');
    firstBtn.className = 'btn btn-outline btn-small';
    firstBtn.textContent = '1';
    firstBtn.onclick = () => onPageChange(1);
    container.appendChild(firstBtn);

    if (startPage > 2) {
      const ellipsis = document.createElement('span');
      ellipsis.textContent = '...';
      ellipsis.style.padding = '0 8px';
      container.appendChild(ellipsis);
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    const btn = document.createElement('button');
    btn.className = `btn btn-small ${i === currentPage ? 'btn-primary' : 'btn-outline'}`;
    btn.textContent = i.toString();
    btn.onclick = () => onPageChange(i);
    container.appendChild(btn);
  }

  if (endPage < totalPages) {
    if (endPage < totalPages - 1) {
      const ellipsis = document.createElement('span');
      ellipsis.textContent = '...';
      ellipsis.style.padding = '0 8px';
      container.appendChild(ellipsis);
    }

    const lastBtn = document.createElement('button');
    lastBtn.className = 'btn btn-outline btn-small';
    lastBtn.textContent = totalPages.toString();
    lastBtn.onclick = () => onPageChange(totalPages);
    container.appendChild(lastBtn);
  }

  // Next button
  const nextBtn = document.createElement('button');
  nextBtn.className = 'btn btn-outline btn-small';
  nextBtn.textContent = 'Next';
  nextBtn.disabled = currentPage >= totalPages;
  nextBtn.onclick = () => onPageChange(currentPage + 1);
  container.appendChild(nextBtn);
}

/**
 * Update pagination info text
 */
function updatePaginationInfo(infoId, currentPage, itemsPerPage, total) {
  const infoEl = document.getElementById(infoId);
  if (infoEl) {
    const start = (currentPage - 1) * itemsPerPage + 1;
    const end = Math.min(currentPage * itemsPerPage, total);
    infoEl.textContent = `Showing ${start}-${end} of ${total}`;
  }
}

/**
 * Confirm dialog
 */
function confirmAction(message) {
  return window.confirm(message);
}

/**
 * Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Export for global use
if (typeof window !== 'undefined') {
  window.adminApiCall = adminApiCall;
  window.showSuccess = showSuccess;
  window.showError = showError;
  window.formatDate = formatDate;
  window.formatDateForInput = formatDateForInput;
  window.createStatusBadge = createStatusBadge;
  window.createActiveBadge = createActiveBadge;
  window.createActionBadge = createActionBadge;
  window.truncateText = truncateText;
  window.extractVariables = extractVariables;
  window.renderVariableTags = renderVariableTags;
  window.buildQueryString = buildQueryString;
  window.renderPagination = renderPagination;
  window.updatePaginationInfo = updatePaginationInfo;
  window.confirmAction = confirmAction;
  window.debounce = debounce;
}
