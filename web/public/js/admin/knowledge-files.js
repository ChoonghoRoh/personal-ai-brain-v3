// 파일관리 JS 모듈 (ESM)
// Phase 15-9: 트리뷰 + 2탭 구조 리디자인

/**
 * XSS 방지를 위한 HTML 이스케이프
 * @param {string} str - 이스케이프할 문자열
 * @returns {string} 이스케이프된 문자열
 */
function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * 바이트 크기를 읽기 쉬운 형식으로 변환
 * @param {number} bytes - 바이트 크기
 * @returns {string} 포맷된 문자열
 */
function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return (bytes / Math.pow(1024, i)).toFixed(2) + ' ' + units[i];
}

/**
 * ISO 날짜를 로컬 형식으로 변환
 * @param {string} isoDate - ISO 날짜 문자열
 * @returns {string} 포맷된 날짜 문자열
 */
function formatDate(isoDate) {
  if (!isoDate) return '-';
  const date = new Date(isoDate);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// showError, showSuccess는 admin-common.js에서 제공

/**
 * Authorization 헤더 생성 (토큰 있으면 추가)
 * @returns {object} 헤더 객체
 */
function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('auth_token');
  if (token) {
    headers['Authorization'] = 'Bearer ' + token;
  }
  return headers;
}

/**
 * 폴더 경로 로드
 */
async function loadFolderConfig() {
  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const res = await fetch('/api/knowledge/folder-config', { headers });
    if (!res.ok) {
      throw new Error('폴더 경로를 불러올 수 없습니다.');
    }

    const data = await res.json();
    const input = document.getElementById('folder-path-input');
    if (input) {
      input.value = data.folder_path || '';
    }
  } catch (error) {
    console.error('폴더 경로 로드 실패:', error);
    showError(error.message);
  }
}

/**
 * 폴더 경로 변경 UI 표시
 */
function showEditFolderUI() {
  const display = document.querySelector('.folder-display');
  const edit = document.querySelector('.folder-edit');
  const currentPath = document.getElementById('folder-path-input').value;

  if (display) display.style.display = 'none';
  if (edit) {
    edit.style.display = 'block';
    const editInput = document.getElementById('folder-path-edit-input');
    if (editInput) editInput.value = currentPath;
  }
}

/**
 * 폴더 경로 변경 UI 숨기기
 */
function hideEditFolderUI() {
  const display = document.querySelector('.folder-display');
  const edit = document.querySelector('.folder-edit');

  if (display) display.style.display = 'block';
  if (edit) edit.style.display = 'none';
}

/**
 * 폴더 경로 저장
 */
async function saveFolderConfig() {
  const editInput = document.getElementById('folder-path-edit-input');
  const newPath = editInput ? editInput.value.trim() : '';

  if (!newPath) {
    showError('폴더 경로를 입력하세요.');
    return;
  }

  try {
    const headers = getAuthHeaders();
    const res = await fetch('/api/knowledge/folder-config', {
      method: 'PUT',
      headers,
      body: JSON.stringify({ folder_path: newPath })
    });

    if (!res.ok) {
      throw new Error('폴더 경로 저장에 실패했습니다.');
    }

    showSuccess('폴더 경로가 변경되었습니다.');
    await loadFolderConfig();
    hideEditFolderUI();
    await loadFileList();
  } catch (error) {
    console.error('폴더 경로 저장 실패:', error);
    showError(error.message);
  }
}

/** 현재 페이지 (0-based) */
let _currentPage = 0;

/**
 * 파일 목록 로드
 * @param {number} [page] - 이동할 페이지 (0-based). 생략 시 현재 페이지 유지
 */
async function loadFileList(page) {
  const tbody = document.getElementById('files-table-body');
  if (!tbody) return;

  // 페이지 리셋: 필터 변경 등 인자 없이 호출 시 첫 페이지로
  if (typeof page === 'number') {
    _currentPage = page;
  } else {
    _currentPage = 0;
  }

  tbody.innerHTML = '<tr><td colspan="8" class="loading">파일 목록을 불러오는 중...</td></tr>';

  try {
    const maxDepth = document.getElementById('files-max-depth')?.value || '3';
    const limit = parseInt(document.getElementById('files-limit')?.value || '100', 10);
    const offset = _currentPage * limit;

    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const url = `/api/knowledge/folder-files?max_depth=${maxDepth}&limit=${limit}&offset=${offset}`;
    const res = await fetch(url, { headers });

    if (!res.ok) {
      throw new Error('파일 목록을 불러올 수 없습니다.');
    }

    const data = await res.json();
    renderFileList(data.items || [], data.total_count || 0, limit, offset);
  } catch (error) {
    console.error('파일 목록 로드 실패:', error);
    showError(error.message);
    tbody.innerHTML = '<tr><td colspan="8" class="error-cell">파일 목록을 불러오는 데 실패했습니다.</td></tr>';
  }
}

/**
 * 파일 목록 테이블 렌더링
 * @param {Array} items - 파일 목록 배열
 * @param {number} totalCount - 전체 파일 수
 * @param {number} limit - 페이지 크기
 * @param {number} offset - 현재 오프셋
 */
function renderFileList(items, totalCount, limit, offset) {
  const tbody = document.getElementById('files-table-body');
  const paginationInfo = document.getElementById('files-pagination-info');

  if (!tbody) return;

  if (items.length === 0 && _currentPage === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty-cell">파일이 없습니다.</td></tr>';
    if (paginationInfo) paginationInfo.innerHTML = '';
    return;
  }

  const rows = items.map(item => {
    const fileName = esc(item.file_name || '');
    const size = formatFileSize(item.size || 0);
    const updatedAt = formatDate(item.updated_at);
    const docId = item.document_id ? esc(String(item.document_id)) : '-';
    const chunkCount = item.chunk_count !== undefined && item.chunk_count !== null ? item.chunk_count : 0;
    const status = esc(item.status || 'unknown');

    let statusBadge = '';
    if (status === 'indexed') {
      statusBadge = '<span class="status-badge status-indexed">인덱싱됨</span>';
    } else if (status === 'pending') {
      statusBadge = '<span class="status-badge status-pending">대기중</span>';
    } else if (status === 'not_indexed') {
      statusBadge = '<span class="status-badge status-not-indexed">미인덱싱</span>';
    } else {
      statusBadge = `<span class="status-badge status-unknown">${status}</span>`;
    }

    // Phase 15-3: 체크박스 + 개별 Reasoning 링크
    const canReason = item.document_id && chunkCount > 0 && (status === 'indexed' || status === 'synced');
    const checkboxHtml = `<input type="checkbox" class="file-select-cb" data-doc-id="${item.document_id || ''}" data-file-name="${esc(item.file_name || '')}">`;
    let actionHtml = '';
    if (canReason) {
      actionHtml = '<a href="/reason?document_id=' + encodeURIComponent(item.document_id) +
        '" class="btn-reasoning" title="이 문서로 Reasoning 실행">🧠 Reasoning</a>';
    }

    return `
      <tr>
        <td class="td-checkbox">${checkboxHtml}</td>
        <td title="${esc(item.relative_path || '')}">${fileName}</td>
        <td>${size}</td>
        <td>${updatedAt}</td>
        <td>${docId}</td>
        <td>${chunkCount}</td>
        <td>${statusBadge}</td>
        <td>${actionHtml}</td>
      </tr>
    `;
  }).join('');

  tbody.innerHTML = rows;

  // 페이지네이션 렌더링
  if (paginationInfo && limit && totalCount !== undefined) {
    const totalPages = Math.max(1, Math.ceil(totalCount / limit));
    const currentPage = _currentPage + 1; // 1-based 표시
    const startIdx = offset + 1;
    const endIdx = Math.min(offset + items.length, totalCount);

    let html = '<div class="pg-controls">';
    html += `<span class="pg-info">${totalCount}개 중 ${startIdx}-${endIdx}</span>`;
    html += '<div class="pg-buttons">';
    html += `<button class="pg-btn" data-page="0" ${_currentPage === 0 ? 'disabled' : ''}>«</button>`;
    html += `<button class="pg-btn" data-page="${_currentPage - 1}" ${_currentPage === 0 ? 'disabled' : ''}>‹</button>`;

    // 페이지 번호 (최대 5개)
    let startPage = Math.max(0, _currentPage - 2);
    let endPage = Math.min(totalPages - 1, startPage + 4);
    startPage = Math.max(0, endPage - 4);

    for (let i = startPage; i <= endPage; i++) {
      const active = i === _currentPage ? ' pg-active' : '';
      html += `<button class="pg-btn pg-num${active}" data-page="${i}">${i + 1}</button>`;
    }

    html += `<button class="pg-btn" data-page="${_currentPage + 1}" ${_currentPage >= totalPages - 1 ? 'disabled' : ''}>›</button>`;
    html += `<button class="pg-btn" data-page="${totalPages - 1}" ${_currentPage >= totalPages - 1 ? 'disabled' : ''}>»</button>`;
    html += '</div></div>';

    paginationInfo.innerHTML = html;

    // 페이지 버튼 이벤트
    paginationInfo.querySelectorAll('.pg-btn:not([disabled])').forEach(btn => {
      btn.addEventListener('click', () => {
        loadFileList(parseInt(btn.dataset.page, 10));
      });
    });
  }
}

/**
 * 파일 선택 버튼 핸들러
 */
function handleSelectFile() {
  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    fileInput.click();
  }
}

/**
 * 파일 선택 후 업로드 UI 표시
 */
function handleFileSelected(event) {
  const files = event.target.files;
  if (files && files.length > 0) {
    const uploadPathInput = document.querySelector('.upload-path-input');
    if (uploadPathInput) {
      uploadPathInput.style.display = 'block';
    }
  }
}

/**
 * 파일 업로드 취소
 */
function handleCancelUpload() {
  const fileInput = document.getElementById('file-input');
  const uploadPathInput = document.querySelector('.upload-path-input');
  const relativePathInput = document.getElementById('upload-relative-path');

  if (fileInput) fileInput.value = '';
  if (uploadPathInput) uploadPathInput.style.display = 'none';
  if (relativePathInput) relativePathInput.value = '';
}

/**
 * 파일 업로드
 */
async function handleUpload() {
  const fileInput = document.getElementById('file-input');
  const relativePathInput = document.getElementById('upload-relative-path');

  if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
    showError('파일을 선택하세요.');
    return;
  }

  const file = fileInput.files[0];
  const relativePath = relativePathInput ? relativePathInput.value.trim() : '';

  const formData = new FormData();
  formData.append('file', file);
  if (relativePath) {
    formData.append('relative_path', relativePath);
  }

  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const res = await fetch('/api/knowledge/upload', {
      method: 'POST',
      headers,
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || '파일 업로드에 실패했습니다.');
    }

    showSuccess('파일이 업로드되었습니다.');
    handleCancelUpload();
    await loadFileList();
  } catch (error) {
    console.error('파일 업로드 실패:', error);
    showError(error.message);
  }
}

/**
 * 드래그앤드롭 핸들러
 */
function setupDragAndDrop() {
  const dropzone = document.getElementById('upload-dropzone');
  if (!dropzone) return;

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.files = files;
        handleFileSelected({ target: fileInput });
      }
    }
  });

  dropzone.addEventListener('click', (e) => {
    // 버튼 클릭이 아닌 경우만 파일 선택 다이얼로그 열기
    if (e.target === dropzone || e.target.classList.contains('upload-icon') || e.target.tagName === 'P') {
      handleSelectFile();
    }
  });
}

/**
 * 동기화 실행
 */
async function handleSync() {
  const deleteMissingCheckbox = document.getElementById('sync-delete-missing');
  const deleteMissing = deleteMissingCheckbox ? deleteMissingCheckbox.checked : false;

  const maxDepth = document.getElementById('files-max-depth')?.value || '3';

  const syncBtn = document.getElementById('sync-btn');
  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.textContent = '동기화 중...';
  }

  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const url = `/api/knowledge/sync?max_depth=${maxDepth}&delete_missing=${deleteMissing}`;
    const res = await fetch(url, {
      method: 'POST',
      headers
    });

    if (!res.ok) {
      throw new Error('동기화에 실패했습니다.');
    }

    const data = await res.json();
    renderSyncResult(data);
    showSuccess('동기화가 완료되었습니다.');
    await loadFileList();
  } catch (error) {
    console.error('동기화 실패:', error);
    showError(error.message);
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.textContent = '동기화 실행';
    }
  }
}

/**
 * 동기화 결과 렌더링
 * @param {object} result - 동기화 결과
 */
function renderSyncResult(result) {
  const syncResultEl = document.getElementById('sync-result');
  if (!syncResultEl) return;

  const addedCount = result.added_count || 0;
  const missingCount = result.missing_count || 0;
  const unchangedCount = result.unchanged_count || 0;

  let html = '<div class="sync-summary">';
  html += `<p><strong>추가:</strong> ${addedCount}개</p>`;
  html += `<p><strong>누락:</strong> ${missingCount}개</p>`;
  html += `<p><strong>변경없음:</strong> ${unchangedCount}개</p>`;
  html += '</div>';

  if (result.added_files && result.added_files.length > 0) {
    html += '<div class="sync-details"><strong>추가된 파일:</strong><ul>';
    result.added_files.slice(0, 10).forEach(f => {
      html += `<li>${esc(f)}</li>`;
    });
    if (result.added_files.length > 10) {
      html += `<li>... 외 ${result.added_files.length - 10}개</li>`;
    }
    html += '</ul></div>';
  }

  if (result.missing_files && result.missing_files.length > 0) {
    html += '<div class="sync-details"><strong>누락된 파일:</strong><ul>';
    result.missing_files.slice(0, 10).forEach(f => {
      html += `<li>${esc(f)}</li>`;
    });
    if (result.missing_files.length > 10) {
      html += `<li>... 외 ${result.missing_files.length - 10}개</li>`;
    }
    html += '</ul></div>';
  }

  syncResultEl.innerHTML = html;
  syncResultEl.style.display = 'block';
}

// ============================================
// Phase 15-9: 탭 전환
// ============================================

/**
 * 탭 전환
 * @param {string} tabName - 탭 이름 ("file-list" | "upload-sync")
 */
function switchTab(tabName) {
  // 탭 버튼 활성화
  document.querySelectorAll('.kf-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });
  // 탭 패널 활성화
  document.querySelectorAll('.kf-tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.dataset.tabPanel === tabName);
  });
}

// ============================================
// Phase 15-9: 트리뷰 로직
// ============================================

/** 현재 선택된 트리 폴더 경로 */
let _selectedTreePath = null;

/**
 * 트리뷰 노드 데이터 로드
 * @param {string} path - 상대 경로
 * @returns {Promise<Array>}
 */
async function loadTreeNode(path) {
  const headers = {};
  const token = localStorage.getItem('auth_token');
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const url = `/api/knowledge/browse-directory?path=${encodeURIComponent(path)}&show_files=false`;
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error('디렉토리 탐색 실패');
  return await res.json();
}

/**
 * 트리뷰 노드 렌더링
 * @param {HTMLElement} parentEl - 부모 DOM 엘리먼트
 * @param {Array} items - 디렉토리 항목 리스트
 * @param {number} depth - 트리 깊이
 */
function renderTreeNodes(parentEl, items, depth) {
  items.forEach(item => {
    if (item.type !== 'dir') return;

    const node = document.createElement('div');
    node.className = 'kf-tree-node';

    const indent = 12 + depth * 16;
    const hasChildren = item.children_count > 0;
    const arrowClass = hasChildren ? 'kf-tree-arrow' : 'kf-tree-arrow empty';

    const folder = document.createElement('div');
    folder.className = 'kf-tree-folder';
    folder.style.paddingLeft = indent + 'px';
    folder.dataset.path = item.path;
    folder.innerHTML =
      `<span class="${arrowClass}">&#9654;</span>` +
      `<span class="kf-tree-icon">📁</span>` +
      `<span class="kf-tree-name" title="${esc(item.path)}">${esc(item.name)}</span>`;

    const childrenContainer = document.createElement('div');
    childrenContainer.className = 'kf-tree-children';

    // 폴더 클릭 → 선택 + 토글
    folder.addEventListener('click', async (e) => {
      e.stopPropagation();
      // 선택 표시
      selectTreeFolder(item.path, folder);

      // 하위 로드 (lazy)
      if (hasChildren && !childrenContainer.dataset.loaded) {
        try {
          const data = await loadTreeNode(item.path);
          renderTreeNodes(childrenContainer, data.items, depth + 1);
          childrenContainer.dataset.loaded = 'true';
        } catch (err) {
          console.error('트리 노드 로드 실패:', err);
        }
      }

      // 펼침/접힘 토글
      if (hasChildren) {
        const arrow = folder.querySelector('.kf-tree-arrow');
        const isExpanded = childrenContainer.classList.contains('expanded');
        childrenContainer.classList.toggle('expanded');
        if (arrow) arrow.classList.toggle('expanded');
      }
    });

    node.appendChild(folder);
    node.appendChild(childrenContainer);
    parentEl.appendChild(node);
  });
}

/**
 * 트리 폴더 선택 처리
 * @param {string} folderPath - 선택된 폴더의 상대 경로
 * @param {HTMLElement} folderEl - 선택된 폴더 DOM 엘리먼트
 */
async function selectTreeFolder(folderPath, folderEl) {
  // 이전 선택 해제
  document.querySelectorAll('.kf-tree-folder.selected').forEach(el => {
    el.classList.remove('selected');
  });
  folderEl.classList.add('selected');
  _selectedTreePath = folderPath;

  // 현재 폴더 배지 업데이트
  const badge = document.getElementById('current-folder-display');
  if (badge) badge.textContent = folderPath || '(프로젝트 루트)';

  // PUT /api/knowledge/folder-config 호출하여 폴더 경로 설정
  try {
    const headers = getAuthHeaders();
    await fetch('/api/knowledge/folder-config', {
      method: 'PUT',
      headers,
      body: JSON.stringify({ folder_path: folderPath })
    });

    // 탭2의 폴더 경로 입력창도 업데이트
    const folderInput = document.getElementById('folder-path-input');
    if (folderInput) folderInput.value = folderPath;

    // 파일 목록 갱신
    await loadFileList();
  } catch (err) {
    console.error('폴더 선택 실패:', err);
  }
}

/**
 * 트리뷰 초기화 (루트 로드)
 */
async function initTreeView() {
  const treeBody = document.getElementById('kf-tree-body');
  if (!treeBody) return;

  try {
    const data = await loadTreeNode('');
    treeBody.innerHTML = '';
    renderTreeNodes(treeBody, data.items, 0);
  } catch (err) {
    console.error('트리뷰 초기화 실패:', err);
    treeBody.innerHTML = '<div class="kf-tree-loading">폴더를 불러올 수 없습니다.</div>';
  }
}

/**
 * 페이지 초기화
 */
document.addEventListener('DOMContentLoaded', async function () {
  // Header 초기화
  if (typeof initializeAdminPage === 'function') {
    initializeAdminPage({
      title: '📁 파일관리',
      subtitle: '지식 폴더 파일 관리',
      currentPath: '/admin/knowledge-files',
    });
  }

  // 탭 전환 이벤트
  document.querySelectorAll('.kf-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
  });

  // 폴더 경로 로드
  await loadFolderConfig();

  // 트리뷰 초기화 + 파일 목록 로드 (병렬)
  await Promise.all([initTreeView(), loadFileList()]);

  // 현재 폴더 배지 초기값
  const folderInput = document.getElementById('folder-path-input');
  const badge = document.getElementById('current-folder-display');
  if (badge && folderInput) badge.textContent = folderInput.value || '(미설정)';

  // 이벤트 리스너 등록
  const changeFolderBtn = document.getElementById('change-folder-btn');
  if (changeFolderBtn) {
    changeFolderBtn.addEventListener('click', showEditFolderUI);
  }

  const saveFolderBtn = document.getElementById('save-folder-btn');
  if (saveFolderBtn) {
    saveFolderBtn.addEventListener('click', saveFolderConfig);
  }

  const cancelFolderBtn = document.getElementById('cancel-folder-btn');
  if (cancelFolderBtn) {
    cancelFolderBtn.addEventListener('click', hideEditFolderUI);
  }

  const refreshFilesBtn = document.getElementById('refresh-files-btn');
  if (refreshFilesBtn) {
    refreshFilesBtn.addEventListener('click', loadFileList);
  }

  const maxDepthSelect = document.getElementById('files-max-depth');
  if (maxDepthSelect) {
    maxDepthSelect.addEventListener('change', loadFileList);
  }

  const limitSelect = document.getElementById('files-limit');
  if (limitSelect) {
    limitSelect.addEventListener('change', loadFileList);
  }

  const selectFileBtn = document.getElementById('select-file-btn');
  if (selectFileBtn) {
    selectFileBtn.addEventListener('click', handleSelectFile);
  }

  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    fileInput.addEventListener('change', handleFileSelected);
  }

  const uploadBtn = document.getElementById('upload-btn');
  if (uploadBtn) {
    uploadBtn.addEventListener('click', handleUpload);
  }

  const cancelUploadBtn = document.getElementById('cancel-upload-btn');
  if (cancelUploadBtn) {
    cancelUploadBtn.addEventListener('click', handleCancelUpload);
  }

  const syncBtn = document.getElementById('sync-btn');
  if (syncBtn) {
    syncBtn.addEventListener('click', handleSync);
  }

  // Phase 15-3: 벌크 Reasoning 버튼
  const bulkReasonBtn = document.getElementById('bulk-reasoning-btn');
  if (bulkReasonBtn) {
    bulkReasonBtn.addEventListener('click', showReasoningModeModal);
  }

  // Phase 15-3: 전체 선택 체크박스
  const selectAllCb = document.getElementById('select-all-files');
  if (selectAllCb) {
    selectAllCb.addEventListener('change', function() {
      document.querySelectorAll('.file-select-cb').forEach(cb => {
        cb.checked = this.checked;
      });
      updateBulkReasoningBtn();
    });
  }

  // Phase 15-3: 개별 체크박스 변경 감지 (이벤트 위임)
  const filesTableBody = document.getElementById('files-table-body');
  if (filesTableBody) {
    filesTableBody.addEventListener('change', function(e) {
      if (e.target.classList.contains('file-select-cb')) {
        updateBulkReasoningBtn();
      }
    });
  }

  // 드래그앤드롭 설정
  setupDragAndDrop();
});

// ============================================
// Phase 15-3: 벌크 Reasoning 기능
// ============================================

/**
 * 선택된 문서 ID 목록 반환
 */
function getSelectedDocumentIds() {
  const checkboxes = document.querySelectorAll('.file-select-cb:checked');
  return Array.from(checkboxes).map(cb => parseInt(cb.dataset.docId, 10)).filter(id => !isNaN(id) && id > 0);
}

/**
 * 선택된 체크박스 수 반환
 */
function getSelectedCount() {
  return document.querySelectorAll('.file-select-cb:checked').length;
}

/**
 * 벌크 Reasoning 버튼 활성/비활성 업데이트
 */
function updateBulkReasoningBtn() {
  const btn = document.getElementById('bulk-reasoning-btn');
  if (!btn) return;
  const checkedCount = getSelectedCount();
  btn.disabled = checkedCount === 0;
  btn.textContent = checkedCount > 0
    ? `선택 문서 Reasoning (${checkedCount})`
    : '선택 문서 Reasoning';
}

/**
 * Reasoning 모드 선택 모달 표시
 */
function showReasoningModeModal() {
  const checkedCount = getSelectedCount();
  if (checkedCount === 0) {
    if (typeof showError === 'function') showError('Reasoning을 실행할 문서를 선택해주세요.');
    return;
  }

  const docIds = getSelectedDocumentIds();
  if (docIds.length === 0) {
    if (typeof showError === 'function') showError('선택한 파일이 아직 동기화되지 않았습니다. 먼저 "업로드 / 동기화" 탭에서 동기화를 실행하세요.');
    return;
  }

  if (docIds.length < checkedCount) {
    if (typeof showError === 'function') showError(`${checkedCount}개 중 ${checkedCount - docIds.length}개 파일은 미동기화 상태로 제외됩니다. 동기화된 ${docIds.length}개 파일만 Reasoning을 실행합니다.`);
  }

  // 기존 모달 제거
  let modal = document.getElementById('reasoning-mode-modal');
  if (modal) modal.remove();

  modal = document.createElement('div');
  modal.id = 'reasoning-mode-modal';
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-content reasoning-modal">
      <h3>Reasoning 모드 선택</h3>
      <p>${docIds.length}개 문서 선택됨</p>
      <div class="mode-options">
        <label class="mode-option">
          <input type="radio" name="reason-mode" value="design_explain" checked>
          <span class="mode-label">설계 설명 (Design Explain)</span>
          <span class="mode-desc">아키텍처와 설계 배경을 분석합니다</span>
        </label>
        <label class="mode-option">
          <input type="radio" name="reason-mode" value="risk_review">
          <span class="mode-label">리스크 검토 (Risk Review)</span>
          <span class="mode-desc">잠재적 리스크와 문제점을 식별합니다</span>
        </label>
        <label class="mode-option">
          <input type="radio" name="reason-mode" value="next_steps">
          <span class="mode-label">다음 단계 (Next Steps)</span>
          <span class="mode-desc">다음 단계 액션 아이템을 도출합니다</span>
        </label>
        <label class="mode-option">
          <input type="radio" name="reason-mode" value="history_trace">
          <span class="mode-label">이력 추적 (History Trace)</span>
          <span class="mode-desc">변경 이력과 맥락을 추적합니다</span>
        </label>
      </div>
      <div class="modal-field">
        <label for="reason-question">질문 (선택)</label>
        <input type="text" id="reason-question" placeholder="분석할 내용에 대한 질문을 입력하세요...">
      </div>
      <div class="modal-actions">
        <button class="btn btn-primary" id="run-bulk-reasoning">실행</button>
        <button class="btn btn-secondary" id="cancel-reasoning-modal">취소</button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  document.getElementById('run-bulk-reasoning').addEventListener('click', () => {
    const mode = document.querySelector('input[name="reason-mode"]:checked').value;
    const question = document.getElementById('reason-question').value.trim();
    modal.remove();
    executeBulkReasoning(docIds, mode, question);
  });
  document.getElementById('cancel-reasoning-modal').addEventListener('click', () => modal.remove());
  modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
}

/**
 * 벌크 Reasoning 실행
 */
async function executeBulkReasoning(documentIds, mode, question) {
  try {
    if (typeof showSuccess === 'function') showSuccess(`${documentIds.length}개 문서 Reasoning 실행 중...`);
    const body = { document_ids: documentIds, mode: mode };
    if (question) body.question = question;

    const res = await fetch('/api/reasoning/run-on-documents', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Reasoning 실행 실패');
    }

    const data = await res.json();
    if (typeof showSuccess === 'function') {
      showSuccess(`Reasoning 완료: ${data.document_count}개 문서, ${data.chunk_count}개 청크 분석`);
    }
    // 결과 페이지로 이동
    if (data.session_id) {
      window.location.href = '/reason?share=' + encodeURIComponent(data.session_id);
    }
  } catch (error) {
    console.error('벌크 Reasoning 실패:', error);
    if (typeof showError === 'function') showError(error.message);
  }
}
