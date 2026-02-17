// 파일관리 — API 및 데이터 처리 모듈
// Phase 16-5: knowledge-files.js에서 분할

// ── 전역 함수 (utils.js / admin-common.js) ──
// esc, formatFileSize, getAuthHeaders, showError, showSuccess

/** renderFileList 콜백 (main 모듈에서 주입) */
let _renderFileList = null;

/**
 * renderFileList 콜백 설정
 * @param {Function} fn - renderFileList 함수
 */
export function setRenderFileList(fn) {
  _renderFileList = fn;
}

/**
 * ISO 날짜를 로컬 형식으로 변환
 * @param {string} isoDate - ISO 날짜 문자열
 * @returns {string} 포맷된 날짜 문자열
 */
export function formatDate(isoDate) {
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

/** 현재 페이지 (0-based) */
export let _currentPage = 0;

/**
 * 폴더 경로 로드
 */
export async function loadFolderConfig() {
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
export function showEditFolderUI() {
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
export function hideEditFolderUI() {
  const display = document.querySelector('.folder-display');
  const edit = document.querySelector('.folder-edit');

  if (display) display.style.display = 'block';
  if (edit) edit.style.display = 'none';
}

/**
 * 폴더 경로 저장
 */
export async function saveFolderConfig() {
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
 * @param {number} [page] - 이동할 페이지 (0-based). 생략 시 현재 페이지 유지
 */
export async function loadFileList(page) {
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
    if (_renderFileList) {
      _renderFileList(data.items || [], data.total_count || 0, limit, offset);
    }
  } catch (error) {
    console.error('파일 목록 로드 실패:', error);
    showError(error.message);
    tbody.innerHTML = '<tr><td colspan="8" class="error-cell">파일 목록을 불러오는 데 실패했습니다.</td></tr>';
  }
}

/**
 * 파일 선택 버튼 핸들러
 */
export function handleSelectFile() {
  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    fileInput.click();
  }
}

/**
 * 파일 선택 후 업로드 UI 표시
 */
export function handleFileSelected(event) {
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
export function handleCancelUpload() {
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
export async function handleUpload() {
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
export function setupDragAndDrop() {
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
export async function handleSync() {
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
export function renderSyncResult(result) {
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
