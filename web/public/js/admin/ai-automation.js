// AI 자동화 JS 모듈 (ESM)

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

// 전역 상태 관리
let selectedDocuments = new Set();
let allDocuments = [];
let currentTaskId = null;
let eventSource = null;

/**
 * 문서 목록 로드
 */
async function loadDocuments() {
  const listEl = document.getElementById('document-list');
  if (!listEl) return;

  listEl.innerHTML = '<div class="loading">문서 목록을 불러오는 중...</div>';

  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    // Phase 15-1에서 구현된 API 사용
    const url = '/api/knowledge/folder-files?max_depth=10&limit=500&offset=0';
    const res = await fetch(url, { headers });

    if (!res.ok) {
      throw new Error('문서 목록을 불러올 수 없습니다.');
    }

    const data = await res.json();
    allDocuments = data.items || [];
    renderDocumentList(allDocuments);
  } catch (error) {
    console.error('문서 목록 로드 실패:', error);
    showError(error.message);
    listEl.innerHTML = '<div class="empty-state">문서 목록을 불러오는 데 실패했습니다.</div>';
  }
}

/**
 * 문서 목록 렌더링
 * @param {Array} documents - 문서 목록 배열
 */
function renderDocumentList(documents) {
  const listEl = document.getElementById('document-list');
  if (!listEl) return;

  if (documents.length === 0) {
    listEl.innerHTML = '<div class="empty-state">문서가 없습니다.</div>';
    return;
  }

  // document_id가 있는 문서만 필터링
  const validDocuments = documents.filter(doc => doc.document_id);

  if (validDocuments.length === 0) {
    listEl.innerHTML = '<div class="empty-state">인덱싱된 문서가 없습니다.</div>';
    return;
  }

  const html = validDocuments.map(doc => {
    const docId = doc.document_id;
    const fileName = esc(doc.file_name || '');
    const isSelected = selectedDocuments.has(docId);
    const selectedClass = isSelected ? 'selected' : '';

    return `
      <div class="document-item ${selectedClass}" data-doc-id="${docId}">
        <input type="checkbox" id="doc-${docId}" ${isSelected ? 'checked' : ''} />
        <label class="document-item-label" for="doc-${docId}">${fileName}</label>
      </div>
    `;
  }).join('');

  listEl.innerHTML = html;

  // 체크박스 이벤트 리스너
  listEl.querySelectorAll('.document-item').forEach(item => {
    const checkbox = item.querySelector('input[type="checkbox"]');
    const docId = parseInt(item.dataset.docId);

    const toggleSelection = () => {
      if (selectedDocuments.has(docId)) {
        selectedDocuments.delete(docId);
        item.classList.remove('selected');
        checkbox.checked = false;
      } else {
        selectedDocuments.add(docId);
        item.classList.add('selected');
        checkbox.checked = true;
      }
      updateSelectedCount();
    };

    checkbox.addEventListener('change', toggleSelection);
    item.addEventListener('click', (e) => {
      if (e.target !== checkbox) {
        toggleSelection();
      }
    });
  });

  updateSelectedCount();
}

/**
 * 선택된 문서 수 업데이트
 */
function updateSelectedCount() {
  const countEl = document.getElementById('selected-count');
  if (countEl) {
    countEl.textContent = selectedDocuments.size;
  }
}

/**
 * 전체 선택
 */
function selectAllDocuments() {
  const validDocuments = allDocuments.filter(doc => doc.document_id);
  validDocuments.forEach(doc => {
    selectedDocuments.add(doc.document_id);
  });
  renderDocumentList(allDocuments);
}

/**
 * 선택 해제
 */
function deselectAllDocuments() {
  selectedDocuments.clear();
  renderDocumentList(allDocuments);
}

/**
 * 문서 검색 필터
 */
function filterDocuments() {
  const searchInput = document.getElementById('document-search');
  if (!searchInput) return;

  const query = searchInput.value.toLowerCase().trim();

  if (!query) {
    renderDocumentList(allDocuments);
    return;
  }

  const filtered = allDocuments.filter(doc => {
    const fileName = (doc.file_name || '').toLowerCase();
    return fileName.includes(query);
  });

  renderDocumentList(filtered);
}

/**
 * 워크플로우 실행
 */
async function runWorkflow() {
  if (selectedDocuments.size === 0) {
    showError('최소 1개 이상의 문서를 선택하세요.');
    return;
  }

  const autoApproveCheckbox = document.getElementById('auto-approve-checkbox');
  const autoApprove = autoApproveCheckbox ? autoApproveCheckbox.checked : false;

  const runBtn = document.getElementById('run-workflow-btn');
  const cancelBtn = document.getElementById('cancel-workflow-btn');

  try {
    if (runBtn) runBtn.disabled = true;

    const headers = getAuthHeaders();
    const res = await fetch('/api/automation/run-full', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        document_ids: Array.from(selectedDocuments),
        auto_approve: autoApprove
      })
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || '워크플로우 실행에 실패했습니다.');
    }

    const data = await res.json();
    currentTaskId = data.task_id;

    showSuccess('워크플로우가 시작되었습니다.');

    // UI 업데이트
    if (runBtn) runBtn.style.display = 'none';
    if (cancelBtn) cancelBtn.style.display = 'block';

    // 진행 상태 표시
    showProgressPanel();

    // SSE 연결
    connectSSE(currentTaskId);

  } catch (error) {
    console.error('워크플로우 실행 실패:', error);
    showError(error.message);
    if (runBtn) runBtn.disabled = false;
  }
}

/**
 * 워크플로우 취소
 */
async function cancelWorkflow() {
  if (!currentTaskId) return;

  try {
    const headers = getAuthHeaders();
    const res = await fetch(`/api/automation/cancel/${currentTaskId}`, {
      method: 'POST',
      headers
    });

    if (!res.ok) {
      throw new Error('워크플로우 취소에 실패했습니다.');
    }

    showSuccess('워크플로우가 취소되었습니다.');
    disconnectSSE();
    resetWorkflowUI();
  } catch (error) {
    console.error('워크플로우 취소 실패:', error);
    showError(error.message);
  }
}

/**
 * SSE 연결
 * @param {string} taskId - 태스크 ID
 */
function connectSSE(taskId) {
  disconnectSSE();

  const url = `/api/automation/progress/${taskId}`;
  eventSource = new EventSource(url);

  // BE sends 'progress' events with stage_name, progress_pct, message
  eventSource.addEventListener('progress', (event) => {
    try {
      const data = JSON.parse(event.data);
      updateProgress(data.progress_pct || 0);
      if (data.stage_name) {
        updateStage(getStageNumber(data.stage_name), data.stage_name);
      }
    } catch (e) {
      console.error('Progress 이벤트 파싱 실패:', e);
    }
  });

  // BE sends 'result' event with results object on completion
  eventSource.addEventListener('result', (event) => {
    try {
      const data = JSON.parse(event.data);
      handleComplete(data.results || data);
    } catch (e) {
      console.error('Result 이벤트 파싱 실패:', e);
    }
  });

  // BE sends 'done' event as final signal
  eventSource.addEventListener('done', () => {
    disconnectSSE();
    resetWorkflowUI();
  });

  // BE sends 'error' event on failure
  eventSource.addEventListener('error', (event) => {
    try {
      const data = JSON.parse(event.data);
      showError(data.message || '워크플로우 실행 중 오류가 발생했습니다.');
      disconnectSSE();
      resetWorkflowUI();
    } catch (e) {
      // SSE 연결 자체의 onerror와 구분
      if (event.data) {
        showError('워크플로우 연결이 끊어졌습니다.');
        disconnectSSE();
        resetWorkflowUI();
      }
    }
  });

  // BE sends 'cancelled' event
  eventSource.addEventListener('cancelled', (event) => {
    try {
      const data = JSON.parse(event.data);
      showSuccess(data.message || '워크플로우가 취소되었습니다.');
    } catch (e) {
      showSuccess('워크플로우가 취소되었습니다.');
    }
    disconnectSSE();
    resetWorkflowUI();
  });

  eventSource.onerror = (err) => {
    console.error('SSE 연결 오류:', err);
    disconnectSSE();
  };
}

/**
 * 단계 이름으로 단계 번호 반환
 * @param {string} stageName - 단계 이름
 * @returns {number} 단계 번호 (1-6)
 */
function getStageNumber(stageName) {
  const stageMap = {
    '문서 텍스트 추출': 1,
    '청크 생성': 2,
    '키워드 추출': 3,
    '라벨 생성/매칭': 4,
    '승인 처리': 5,
    'Qdrant 임베딩': 6,
  };
  return stageMap[stageName] || 1;
}

/**
 * SSE 연결 해제
 */
function disconnectSSE() {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
}

/**
 * Progress Bar 업데이트
 * @param {number} progress - 진행률 (0-100)
 */
function updateProgress(progress) {
  const progressBar = document.getElementById('progress-bar');
  const progressPercent = document.getElementById('progress-percent');

  if (progressBar) {
    progressBar.style.width = `${progress}%`;
  }
  if (progressPercent) {
    progressPercent.textContent = `${Math.round(progress)}%`;
  }
}

/**
 * 현재 단계 업데이트
 * @param {number} stage - 현재 단계 (1-6)
 * @param {string} stageName - 단계 이름
 */
function updateStage(stage, stageName) {
  const progressStage = document.getElementById('progress-stage');
  if (progressStage) {
    progressStage.textContent = stageName;
  }

  // 단계 아이템 업데이트
  document.querySelectorAll('.stage-item').forEach(item => {
    const itemStage = parseInt(item.dataset.stage);
    item.classList.remove('active', 'completed');

    if (itemStage < stage) {
      item.classList.add('completed');
    } else if (itemStage === stage) {
      item.classList.add('active');
    }
  });
}

/**
 * 완료 처리
 * @param {object} data - 완료 데이터
 */
function handleComplete(data) {
  showSuccess('워크플로우가 완료되었습니다!');

  // 결과 표시
  displayResults(data);

  // 태스크 이력 새로고침
  loadTaskHistory();
}

/**
 * 진행 패널 표시
 */
function showProgressPanel() {
  const progressPanel = document.getElementById('workflow-progress');
  if (progressPanel) {
    progressPanel.style.display = 'block';
  }
}

/**
 * 워크플로우 UI 리셋
 */
function resetWorkflowUI() {
  const runBtn = document.getElementById('run-workflow-btn');
  const cancelBtn = document.getElementById('cancel-workflow-btn');

  if (runBtn) {
    runBtn.style.display = 'block';
    runBtn.disabled = false;
  }
  if (cancelBtn) {
    cancelBtn.style.display = 'none';
  }

  currentTaskId = null;
}

/**
 * 결과 표시
 * @param {object} data - 결과 데이터
 */
function displayResults(data) {
  const resultsContainer = document.getElementById('results-container');
  if (!resultsContainer) return;

  let html = '';

  if (data.chunks_created) {
    html += `
      <div class="result-item">
        <h5>✅ 청크 생성</h5>
        <div class="result-content">총 ${data.chunks_created}개의 청크가 생성되었습니다.</div>
      </div>
    `;
  }

  if (data.keywords_extracted) {
    html += `
      <div class="result-item">
        <h5>🔑 키워드 추출</h5>
        <div class="result-content">총 ${data.keywords_extracted}개의 키워드가 추출되었습니다.</div>
      </div>
    `;
  }

  if (data.labels_matched) {
    html += `
      <div class="result-item">
        <h5>🏷️ 라벨 매칭</h5>
        <div class="result-content">총 ${data.labels_matched}개의 라벨이 매칭되었습니다.</div>
      </div>
    `;
  }

  if (data.chunks_approved) {
    html += `
      <div class="result-item">
        <h5>✔️ 승인 처리</h5>
        <div class="result-content">${data.chunks_approved}개의 청크가 자동 승인되었습니다.</div>
      </div>
    `;
  }

  if (data.chunks_embedded) {
    html += `
      <div class="result-item">
        <h5>📦 Qdrant 임베딩</h5>
        <div class="result-content">${data.chunks_embedded}개의 청크가 임베딩되었습니다.</div>
      </div>
    `;
  }

  if (!html) {
    html = '<div class="empty-state">결과 데이터가 없습니다.</div>';
  }

  resultsContainer.innerHTML = html;

  // auto_approve=false 시 승인 대기 패널 표시
  if (data.chunks_created && !data.chunks_approved) {
    const pendingPanel = document.getElementById('pending-approvals');
    if (pendingPanel) {
      pendingPanel.style.display = 'block';
    }
  }
}

/**
 * 태스크 이력 로드
 */
async function loadTaskHistory() {
  const taskListEl = document.getElementById('task-list');
  if (!taskListEl) return;

  taskListEl.innerHTML = '<div class="loading">이력을 불러오는 중...</div>';

  try {
    const headers = {};
    const token = localStorage.getItem('auth_token');
    if (token) {
      headers['Authorization'] = 'Bearer ' + token;
    }

    const res = await fetch('/api/automation/tasks', { headers });

    if (!res.ok) {
      throw new Error('태스크 이력을 불러올 수 없습니다.');
    }

    const data = await res.json();
    renderTaskHistory(data.tasks || []);
  } catch (error) {
    console.error('태스크 이력 로드 실패:', error);
    taskListEl.innerHTML = '<div class="empty-state">이력을 불러오는 데 실패했습니다.</div>';
  }
}

/**
 * 태스크 이력 렌더링
 * @param {Array} tasks - 태스크 목록
 */
function renderTaskHistory(tasks) {
  const taskListEl = document.getElementById('task-list');
  if (!taskListEl) return;

  if (tasks.length === 0) {
    taskListEl.innerHTML = '<div class="empty-state">이력이 없습니다.</div>';
    return;
  }

  const html = tasks.slice(0, 5).map(task => {
    const taskId = esc(task.task_id || '');
    const status = task.status || 'unknown';
    const statusClass = status;

    let statusLabel = status;
    if (status === 'running') statusLabel = '실행 중';
    else if (status === 'completed') statusLabel = '완료';
    else if (status === 'failed') statusLabel = '실패';

    return `
      <div class="task-item ${statusClass}">
        <span class="task-id">${taskId}</span>
        <span class="task-status ${statusClass}">${statusLabel}</span>
      </div>
    `;
  }).join('');

  taskListEl.innerHTML = html;
}

/**
 * 승인 대기 항목 처리
 */
async function approvePending() {
  if (!currentTaskId) return;

  try {
    const headers = getAuthHeaders();
    const res = await fetch('/api/automation/approve-pending', {
      method: 'POST',
      headers,
      body: JSON.stringify({ task_id: currentTaskId })
    });

    if (!res.ok) {
      throw new Error('승인 처리에 실패했습니다.');
    }

    showSuccess('승인 처리가 완료되었습니다.');

    // 승인 대기 패널 숨기기
    const pendingPanel = document.getElementById('pending-approvals');
    if (pendingPanel) {
      pendingPanel.style.display = 'none';
    }
  } catch (error) {
    console.error('승인 처리 실패:', error);
    showError(error.message);
  }
}

/**
 * 페이지 초기화
 */
document.addEventListener('DOMContentLoaded', async function () {
  // Header 초기화
  if (typeof initializeAdminPage === 'function') {
    initializeAdminPage({
      title: '🤖 AI 자동화',
      subtitle: '문서 자동 분석 및 라벨링',
      currentPath: '/admin/ai-automation',
    });
  }

  // 문서 목록 로드
  await loadDocuments();

  // 태스크 이력 로드
  await loadTaskHistory();

  // 이벤트 리스너 등록
  const selectAllBtn = document.getElementById('select-all-btn');
  if (selectAllBtn) {
    selectAllBtn.addEventListener('click', selectAllDocuments);
  }

  const deselectAllBtn = document.getElementById('deselect-all-btn');
  if (deselectAllBtn) {
    deselectAllBtn.addEventListener('click', deselectAllDocuments);
  }

  const documentSearch = document.getElementById('document-search');
  if (documentSearch) {
    documentSearch.addEventListener('input', filterDocuments);
  }

  const runWorkflowBtn = document.getElementById('run-workflow-btn');
  if (runWorkflowBtn) {
    runWorkflowBtn.addEventListener('click', runWorkflow);
  }

  const cancelWorkflowBtn = document.getElementById('cancel-workflow-btn');
  if (cancelWorkflowBtn) {
    cancelWorkflowBtn.addEventListener('click', cancelWorkflow);
  }

  const approvePendingBtn = document.getElementById('approve-pending-btn');
  if (approvePendingBtn) {
    approvePendingBtn.addEventListener('click', approvePending);
  }
});

// 페이지 언로드 시 SSE 연결 해제
window.addEventListener('beforeunload', () => {
  disconnectSSE();
});
