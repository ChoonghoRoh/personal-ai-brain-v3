// 파일관리 JS 모듈 (ESM)

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

/**
 * 파일 목록 로드
 */
async function loadFileList() {
  const tbody = document.getElementById('files-table-body');
  if (!tbody) return;

  tbody.innerHTML = '<tr><td colspan="6" class="loading">파일 목록을 불러오는 중...</td></tr>';

  try {
    const maxDepth = document.getElementById('files-max-depth')?.value || '3';
    const limit = document.getElementById('files-limit')?.value || '100';

    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const url = `/api/knowledge/folder-files?max_depth=${maxDepth}&limit=${limit}&offset=0`;
    const res = await fetch(url, { headers });

    if (!res.ok) {
      throw new Error('파일 목록을 불러올 수 없습니다.');
    }

    const data = await res.json();
    renderFileList(data.items || [], data.total_count || 0);
  } catch (error) {
    console.error('파일 목록 로드 실패:', error);
    showError(error.message);
    tbody.innerHTML = '<tr><td colspan="6" class="error-cell">파일 목록을 불러오는 데 실패했습니다.</td></tr>';
  }
}

/**
 * 파일 목록 테이블 렌더링
 * @param {Array} items - 파일 목록 배열
 * @param {number} totalCount - 전체 파일 수
 */
function renderFileList(items, totalCount) {
  const tbody = document.getElementById('files-table-body');
  const paginationInfo = document.getElementById('files-pagination-info');

  if (!tbody) return;

  if (items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty-cell">파일이 없습니다.</td></tr>';
    if (paginationInfo) paginationInfo.textContent = '';
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

    return `
      <tr>
        <td title="${esc(item.relative_path || '')}">${fileName}</td>
        <td>${size}</td>
        <td>${updatedAt}</td>
        <td>${docId}</td>
        <td>${chunkCount}</td>
        <td>${statusBadge}</td>
      </tr>
    `;
  }).join('');

  tbody.innerHTML = rows;

  if (paginationInfo) {
    paginationInfo.textContent = `총 ${totalCount}개 파일 중 ${items.length}개 표시`;
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

  // 폴더 경로 로드
  await loadFolderConfig();

  // 파일 목록 로드
  await loadFileList();

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

  // 드래그앤드롭 설정
  setupDragAndDrop();
});
