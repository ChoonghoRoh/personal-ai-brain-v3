// AI 자동화 JS 모듈 (ESM)
// API/SSE 통신은 ai-automation-api.js 참조
// esc(), getAuthHeaders()는 utils.js 전역 함수 사용

// Phase 16-3-2: Virtual Scroll 상태
const VS_ITEM_HEIGHT = 40;
const VS_BUFFER = 2;
let vsFilteredDocs = [];
let vsScrollHandler = null;

/**
 * 문서 리스트 렌더링 (Virtual Scroll)
 */
function renderDocumentList(documents) {
  const listEl = document.getElementById('document-list');
  if (!listEl) return;

  if (documents.length === 0) {
    listEl.innerHTML = '<div class="empty-state">문서가 없습니다.</div>';
    return;
  }

  const validDocuments = documents.filter(doc => doc.document_id);
  if (validDocuments.length === 0) {
    listEl.innerHTML = '<div class="empty-state">인덱싱된 문서가 없습니다.</div>';
    return;
  }

  vsFilteredDocs = validDocuments;
  const totalHeight = validDocuments.length * VS_ITEM_HEIGHT;

  listEl.innerHTML = '';
  listEl.classList.add('vs-container');

  const spacer = document.createElement('div');
  spacer.className = 'vs-spacer';
  spacer.style.height = totalHeight + 'px';
  listEl.appendChild(spacer);

  const viewport = document.createElement('div');
  viewport.className = 'vs-viewport';
  listEl.appendChild(viewport);

  if (vsScrollHandler) listEl.removeEventListener('scroll', vsScrollHandler);
  vsScrollHandler = () => vsRenderVisible(listEl, viewport);
  listEl.addEventListener('scroll', vsScrollHandler);

  vsRenderVisible(listEl, viewport);
  updateSelectedCount();
}

/**
 * Virtual Scroll: 가시 영역 노드만 렌더
 */
function vsRenderVisible(listEl, viewport) {
  const scrollTop = listEl.scrollTop;
  const containerHeight = listEl.clientHeight;
  const totalCount = vsFilteredDocs.length;

  let startIdx = Math.floor(scrollTop / VS_ITEM_HEIGHT) - VS_BUFFER;
  let endIdx = Math.ceil((scrollTop + containerHeight) / VS_ITEM_HEIGHT) + VS_BUFFER;
  startIdx = Math.max(0, startIdx);
  endIdx = Math.min(totalCount, endIdx);

  viewport.style.position = 'absolute';
  viewport.style.top = (startIdx * VS_ITEM_HEIGHT) + 'px';
  viewport.style.left = '0';
  viewport.style.right = '0';

  const fragment = document.createDocumentFragment();

  for (let i = startIdx; i < endIdx; i++) {
    const doc = vsFilteredDocs[i];
    const docId = doc.document_id;
    const fileName = esc(doc.file_name || '');
    const isSelected = selectedDocuments.has(docId);
    const isCompleted = completedDocuments.has(docId);

    const item = document.createElement('div');
    item.className = 'document-item' + (isSelected ? ' selected' : '') + (isCompleted ? ' doc-completed' : '');
    item.dataset.docId = docId;
    item.style.height = VS_ITEM_HEIGHT + 'px';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.id = 'doc-' + docId;
    checkbox.checked = isSelected;

    const label = document.createElement('label');
    label.className = 'document-item-label';
    label.setAttribute('for', 'doc-' + docId);
    label.textContent = fileName;

    if (isCompleted) {
      const check = document.createElement('span');
      check.className = 'doc-check';
      check.textContent = ' \u2713';
      label.appendChild(check);
    }

    item.appendChild(checkbox);
    item.appendChild(label);

    const toggleSelection = () => {
      if (selectedDocuments.has(docId)) selectedDocuments.delete(docId);
      else selectedDocuments.add(docId);
      vsRenderVisible(listEl, viewport);
      updateSelectedCount();
    };
    checkbox.addEventListener('change', toggleSelection);
    item.addEventListener('click', (e) => { if (e.target !== checkbox) toggleSelection(); });

    fragment.appendChild(item);
  }

  viewport.innerHTML = '';
  viewport.appendChild(fragment);
}

/**
 * 선택된 문서 수 업데이트
 */
function updateSelectedCount() {
  const countEl = document.getElementById('selected-count');
  if (countEl) countEl.textContent = selectedDocuments.size;
  updateSelectionSummary();
}

/**
 * 선택 문서 요약 표시
 */
function updateSelectionSummary() {
  const selectedCount = selectedDocuments.size;
  const estimatedChunks = selectedCount * 12;
  const estimatedMinutes = Math.ceil(estimatedChunks / 10);

  const summaryEl = document.getElementById('selection-summary');
  if (!summaryEl) return;

  if (selectedCount === 0) { summaryEl.style.display = 'none'; return; }

  summaryEl.style.display = 'block';
  summaryEl.textContent = `선택: ${selectedCount}개 | 예상 청크: ~${estimatedChunks} | 예상 소요: ~${estimatedMinutes}분`;

  if (selectedCount > 50) {
    summaryEl.classList.add('selection-warn');
    summaryEl.textContent += ' \u26A0 대량 처리 \u2014 배치 분할 권장';
  } else {
    summaryEl.classList.remove('selection-warn');
  }
}

/**
 * 전체 선택 / 선택 해제
 */
function selectAllDocuments() {
  allDocuments.filter(doc => doc.document_id).forEach(doc => selectedDocuments.add(doc.document_id));
  renderDocumentList(allDocuments);
}

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
  if (!query) { renderDocumentList(allDocuments); return; }
  renderDocumentList(allDocuments.filter(doc => (doc.file_name || '').toLowerCase().includes(query)));
}

/**
 * Progress Bar 업데이트
 */
function updateProgress(progress) {
  const progressBar = document.getElementById('progress-bar');
  const progressPercent = document.getElementById('progress-percent');
  if (progressBar) progressBar.style.width = `${progress}%`;
  if (progressPercent) progressPercent.textContent = `${Math.round(progress)}%`;
}

/**
 * 현재 단계 업데이트
 */
function updateStage(stage, stageName) {
  const progressStage = document.getElementById('progress-stage');
  if (progressStage) progressStage.textContent = stageName;

  document.querySelectorAll('.stage-item').forEach(item => {
    const itemStage = parseInt(item.dataset.stage);
    item.classList.remove('active', 'completed');
    if (itemStage < stage) item.classList.add('completed');
    else if (itemStage === stage) item.classList.add('active');
  });
}

/**
 * 완료 처리
 */
function handleComplete(data) {
  showSuccess('워크플로우가 완료되었습니다!');
  displayResults(data);
  loadTaskHistory();
}

/**
 * 진행 패널 표시
 */
function showProgressPanel() {
  const progressPanel = document.getElementById('workflow-progress');
  if (progressPanel) progressPanel.style.display = 'block';
}

/**
 * 워크플로우 UI 리셋
 */
function resetWorkflowUI() {
  const runBtn = document.getElementById('run-workflow-btn');
  const cancelBtn = document.getElementById('cancel-workflow-btn');
  if (runBtn) { runBtn.style.display = 'block'; runBtn.disabled = false; }
  if (cancelBtn) cancelBtn.style.display = 'none';
  currentTaskId = null;
}

/**
 * 배치 완료 시 문서별 결과 처리
 */
function handleDocResult(data) {
  const docIds = data.document_ids || [];
  docIds.forEach(id => completedDocuments.add(id));

  docIds.forEach(id => {
    const item = document.querySelector(`.document-item[data-doc-id="${id}"]`);
    if (item && !item.classList.contains('doc-completed')) {
      item.classList.add('doc-completed');
      const label = item.querySelector('.document-item-label');
      if (label && !label.querySelector('.doc-check')) {
        const check = document.createElement('span');
        check.className = 'doc-check';
        check.textContent = ' \u2713';
        label.appendChild(check);
      }
    }
  });

  const resultsContainer = document.getElementById('results-container');
  if (resultsContainer) {
    const stats = data.stats || {};
    const batchHtml = `
      <div class="result-item batch-result">
        <h5>배치 ${esc(String((data.batch_index || 0) + 1))} 완료 (${esc(String(docIds.length))}개 문서)</h5>
        <div class="result-content">
          청크: ${esc(String(stats.chunks_created || 0))}개,
          키워드: ${esc(String(stats.keywords_extracted || 0))}개,
          라벨: ${esc(String(stats.labels_matched || 0))}개
        </div>
      </div>
    `;
    resultsContainer.insertAdjacentHTML('beforeend', batchHtml);
    resultsContainer.style.display = 'block';
  }

  const docProgressEl = document.getElementById('doc-progress');
  if (docProgressEl) {
    const totalSelected = selectedDocuments.size || docIds.length;
    docProgressEl.textContent = `${completedDocuments.size}/${totalSelected} 문서 완료`;
  }
}

/**
 * 결과 표시
 */
function displayResults(data) {
  const resultsContainer = document.getElementById('results-container');
  if (!resultsContainer) return;

  let html = '';
  if (data.chunks_created) html += `<div class="result-item"><h5>✅ 청크 생성</h5><div class="result-content">총 ${esc(String(data.chunks_created))}개의 청크가 생성되었습니다.</div></div>`;
  if (data.keywords_extracted) html += `<div class="result-item"><h5>🔑 키워드 추출</h5><div class="result-content">총 ${esc(String(data.keywords_extracted))}개의 키워드가 추출되었습니다.</div></div>`;
  if (data.labels_matched) html += `<div class="result-item"><h5>🏷️ 라벨 매칭</h5><div class="result-content">총 ${esc(String(data.labels_matched))}개의 라벨이 매칭되었습니다.</div></div>`;
  if (data.chunks_approved) html += `<div class="result-item"><h5>✔️ 승인 처리</h5><div class="result-content">${esc(String(data.chunks_approved))}개의 청크가 자동 승인되었습니다.</div></div>`;
  if (data.chunks_embedded) html += `<div class="result-item"><h5>📦 Qdrant 임베딩</h5><div class="result-content">${esc(String(data.chunks_embedded))}개의 청크가 임베딩되었습니다.</div></div>`;
  if (!html) html = '<div class="empty-state">결과 데이터가 없습니다.</div>';
  resultsContainer.innerHTML = html;

  if (data.chunks_created && !data.chunks_approved) {
    const pendingPanel = document.getElementById('pending-approvals');
    if (pendingPanel) pendingPanel.style.display = 'block';
  }
}

/**
 * 태스크 이력 렌더링
 */
function renderTaskHistory(tasks) {
  const taskListEl = document.getElementById('task-list');
  if (!taskListEl) return;
  if (tasks.length === 0) { taskListEl.innerHTML = '<div class="empty-state">이력이 없습니다.</div>'; return; }
  taskListEl.innerHTML = tasks.slice(0, 5).map(task => {
    const taskId = esc(task.task_id || '');
    const status = task.status || 'unknown';
    let statusLabel = status;
    if (status === 'running') statusLabel = '실행 중';
    else if (status === 'completed') statusLabel = '완료';
    else if (status === 'failed') statusLabel = '실패';
    return `<div class="task-item ${status}"><span class="task-id">${taskId}</span><span class="task-status ${status}">${esc(statusLabel)}</span></div>`;
  }).join('');
}

/**
 * 페이지 초기화
 */
document.addEventListener('DOMContentLoaded', async function () {
  if (typeof initializeAdminPage === 'function') {
    initializeAdminPage({
      title: '🤖 AI 자동화',
      subtitle: '문서 자동 분석 및 라벨링',
      currentPath: '/admin/ai-automation',
    });
  }

  await loadDocuments();
  await loadTaskHistory();

  const selectAllBtn = document.getElementById('select-all-btn');
  if (selectAllBtn) selectAllBtn.addEventListener('click', selectAllDocuments);

  const deselectAllBtn = document.getElementById('deselect-all-btn');
  if (deselectAllBtn) deselectAllBtn.addEventListener('click', deselectAllDocuments);

  const documentSearch = document.getElementById('document-search');
  if (documentSearch) documentSearch.addEventListener('input', filterDocuments);

  const runWorkflowBtn = document.getElementById('run-workflow-btn');
  if (runWorkflowBtn) runWorkflowBtn.addEventListener('click', runWorkflow);

  const cancelWorkflowBtn = document.getElementById('cancel-workflow-btn');
  if (cancelWorkflowBtn) cancelWorkflowBtn.addEventListener('click', cancelWorkflow);

  const approvePendingBtn = document.getElementById('approve-pending-btn');
  if (approvePendingBtn) approvePendingBtn.addEventListener('click', approvePending);
});

window.addEventListener('beforeunload', () => { disconnectSSE(); });
