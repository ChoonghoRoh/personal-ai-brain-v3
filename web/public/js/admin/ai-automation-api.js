/**
 * AI 자동화 API 모듈
 * API 통신, SSE 연결, 태스크 이력 관련 함수
 */

// 전역 상태 관리
let selectedDocuments = new Set();
let completedDocuments = new Set();
let allDocuments = [];
let currentTaskId = null;
let eventSource = null;
let lastHeartbeatTime = Date.now();
let heartbeatCheckInterval = null;

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
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const url = '/api/automation/documents?limit=1000&offset=0';
    const res = await fetch(url, { headers });

    if (!res.ok) throw new Error('문서 목록을 불러올 수 없습니다.');

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
    completedDocuments.clear();

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
    if (runBtn) runBtn.style.display = 'none';
    if (cancelBtn) cancelBtn.style.display = 'block';
    showProgressPanel();
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

    if (!res.ok) throw new Error('워크플로우 취소에 실패했습니다.');

    showSuccess('워크플로우가 취소되었습니다.');
    disconnectSSE();
    resetWorkflowUI();
  } catch (error) {
    console.error('워크플로우 취소 실패:', error);
    showError(error.message);
  }
}

/**
 * SSE 재연결
 */
function reconnectSSE(taskId) {
  disconnectSSE();
  setTimeout(() => connectSSE(taskId), 3000);
}

/**
 * SSE 연결
 */
function connectSSE(taskId) {
  disconnectSSE();
  currentTaskId = taskId;

  const url = `/api/automation/progress/${taskId}`;
  eventSource = new EventSource(url);

  lastHeartbeatTime = Date.now();
  eventSource.addEventListener('heartbeat', () => {
    lastHeartbeatTime = Date.now();
  });

  heartbeatCheckInterval = setInterval(() => {
    if (Date.now() - lastHeartbeatTime > 30000) {
      console.warn('SSE heartbeat 타임아웃, 재연결 시도...');
      reconnectSSE(currentTaskId);
    }
  }, 5000);

  eventSource.addEventListener('progress', (event) => {
    try {
      const data = JSON.parse(event.data);
      updateProgress(data.progress_pct || 0);
      if (data.stage_name) updateStage(getStageNumber(data.stage_name), data.stage_name);
      if (data.detail && typeof data.detail === 'object' && data.detail.current != null) {
        const detailEl = document.getElementById('progress-detail');
        if (detailEl) detailEl.textContent = `${data.detail.current}/${data.detail.total} ${data.detail.item_name || ''}`;
      }
      if (data.eta_seconds != null) {
        const etaEl = document.getElementById('progress-eta');
        if (etaEl) etaEl.textContent = `예상 잔여: ~${Math.ceil(data.eta_seconds / 60)}분`;
      }
    } catch (e) {
      console.error('Progress 이벤트 파싱 실패:', e);
    }
  });

  eventSource.addEventListener('result', (event) => {
    try {
      const data = JSON.parse(event.data);
      handleComplete(data.results || data);
    } catch (e) {
      console.error('Result 이벤트 파싱 실패:', e);
    }
  });

  eventSource.addEventListener('done', () => {
    disconnectSSE();
    resetWorkflowUI();
  });

  eventSource.addEventListener('error', (event) => {
    try {
      const data = JSON.parse(event.data);
      showError(data.message || '워크플로우 실행 중 오류가 발생했습니다.');
      disconnectSSE();
      resetWorkflowUI();
    } catch (e) {
      if (event.data) {
        showError('워크플로우 연결이 끊어졌습니다.');
        disconnectSSE();
        resetWorkflowUI();
      }
    }
  });

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

  eventSource.addEventListener('doc_result', (event) => {
    try {
      handleDocResult(JSON.parse(event.data));
    } catch (e) {
      console.error('doc_result 이벤트 파싱 실패:', e);
    }
  });

  eventSource.onerror = (err) => {
    console.error('SSE 연결 오류:', err);
    disconnectSSE();
  };
}

/**
 * 단계 이름 → 번호
 */
function getStageNumber(stageName) {
  const stageMap = {
    '문서 텍스트 추출': 1, '청크 생성': 2, '키워드 추출': 3,
    '라벨 생성/매칭': 4, '승인 처리': 5, 'Qdrant 임베딩': 6,
  };
  return stageMap[stageName] || 1;
}

/**
 * SSE 연결 해제
 */
function disconnectSSE() {
  if (heartbeatCheckInterval) {
    clearInterval(heartbeatCheckInterval);
    heartbeatCheckInterval = null;
  }
  if (eventSource) {
    eventSource.close();
    eventSource = null;
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
    if (token) headers['Authorization'] = 'Bearer ' + token;

    const res = await fetch('/api/automation/tasks', { headers });
    if (!res.ok) throw new Error('태스크 이력을 불러올 수 없습니다.');

    const data = await res.json();
    renderTaskHistory(data.tasks || []);
  } catch (error) {
    console.error('태스크 이력 로드 실패:', error);
    taskListEl.innerHTML = '<div class="empty-state">이력을 불러오는 데 실패했습니다.</div>';
  }
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

    if (!res.ok) throw new Error('승인 처리에 실패했습니다.');

    showSuccess('승인 처리가 완료되었습니다.');
    const pendingPanel = document.getElementById('pending-approvals');
    if (pendingPanel) pendingPanel.style.display = 'none';
  } catch (error) {
    console.error('승인 처리 실패:', error);
    showError(error.message);
  }
}
