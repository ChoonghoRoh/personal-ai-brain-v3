// 파일관리 JS 모듈 (ESM)
// Phase 15-9: 트리뷰 + 2탭 구조 리디자인
// Phase 16-5: 오케스트레이터 — 테이블 렌더 + 이벤트 + 탭전환 + 벌크 Reasoning

import {
  setRenderFileList,
  _currentPage,
  formatDate,
  loadFolderConfig,
  saveFolderConfig,
  showEditFolderUI,
  hideEditFolderUI,
  loadFileList,
  handleUpload,
  handleSync,
  handleSelectFile,
  handleFileSelected,
  handleCancelUpload,
  setupDragAndDrop,
} from './knowledge-files-api.js';
import { initTreeView } from './knowledge-files-tree.js';

// ── 전역 함수 (utils.js / admin-common.js) ──
// esc, formatFileSize, getAuthHeaders, showError, showSuccess, initializeAdminPage

// ============================================
// 테이블 렌더링
// ============================================

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

// 콜백 주입
setRenderFileList(renderFileList);

// ============================================
// 탭 전환
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

// ============================================
// 페이지 초기화
// ============================================

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
