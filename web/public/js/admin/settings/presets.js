/**
 * Prompt Preset Management Page JS (Phase 11-3)
 */

// State
let currentPage = 1;
let itemsPerPage = 20;
let totalItems = 0;
let selectedPresetId = null;
let isNewPreset = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initEventListeners();
  loadPresets();
});

function initHeader() {
  if (typeof initLayout === 'function') initLayout();
  if (typeof renderHeader === 'function') {
    renderHeader({
      subtitle: '프롬프트 프리셋 관리',
      currentPath: '/admin/settings/presets'
    });
  }
}

function initEventListeners() {
  // Filter apply
  document.getElementById('filter-apply-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadPresets();
  });

  // Create new preset
  document.getElementById('create-preset-btn')?.addEventListener('click', createNewPreset);

  // Save draft
  document.getElementById('save-draft-btn')?.addEventListener('click', saveDraft);

  // Publish
  document.getElementById('publish-btn')?.addEventListener('click', publishPreset);

  // Delete
  document.getElementById('delete-btn')?.addEventListener('click', deletePreset);

  // Slider value display
  document.getElementById('preset-temperature')?.addEventListener('input', (e) => {
    document.getElementById('temp-value').textContent = e.target.value;
  });

  document.getElementById('preset-top-p')?.addEventListener('input', (e) => {
    document.getElementById('top-p-value').textContent = e.target.value;
  });

  // Enter key in search
  document.getElementById('filter-search')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadPresets();
    }
  });
}

async function loadPresets() {
  const tableBody = document.getElementById('preset-table');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="4" class="loading">로딩 중...</td></tr>';

  try {
    const params = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      task_type: document.getElementById('filter-task-type')?.value || '',
      status: document.getElementById('filter-status')?.value || '',
      search: document.getElementById('filter-search')?.value || '',
    };

    const queryString = buildQueryString(params);
    const data = await adminApiCall(`/presets${queryString}`);

    totalItems = data.total || 0;
    const presets = data.items || [];

    if (presets.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" class="loading">프리셋이 없습니다</td></tr>';
      return;
    }

    tableBody.innerHTML = presets.map(p => `
      <tr data-id="${p.id}" class="${p.id === selectedPresetId ? 'selected' : ''}" onclick="selectPreset('${p.id}')">
        <td>${truncateText(p.name, 30)}</td>
        <td>${p.task_type || '-'}</td>
        <td>${p.model_name || '-'}</td>
        <td>${createStatusBadge(p.status)}</td>
      </tr>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    updatePaginationInfo('pagination-info', currentPage, itemsPerPage, totalItems);
    renderPagination('pagination-buttons', currentPage, totalPages, (page) => {
      currentPage = page;
      loadPresets();
    });

  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="4" class="loading">프리셋 로딩 오류</td></tr>';
    showError('프리셋 로딩 실패: ' + error.message);
  }
}

async function selectPreset(id) {
  selectedPresetId = id;
  isNewPreset = false;

  // Update table selection
  document.querySelectorAll('#preset-table tr').forEach(tr => {
    tr.classList.toggle('selected', tr.dataset.id === id);
  });

  try {
    const preset = await adminApiCall(`/presets/${id}`);
    populateForm(preset);
    enableEditorButtons(preset.status);
    document.getElementById('editor-title').textContent = '프리셋 수정';
  } catch (error) {
    showError('프리셋 로딩 실패: ' + error.message);
  }
}

function createNewPreset() {
  selectedPresetId = null;
  isNewPreset = true;

  // Clear selection
  document.querySelectorAll('#preset-table tr').forEach(tr => {
    tr.classList.remove('selected');
  });

  // Clear form
  document.getElementById('preset-form')?.reset();
  document.getElementById('preset-status').value = 'draft';
  document.getElementById('preset-temperature').value = 0.7;
  document.getElementById('temp-value').textContent = '0.7';
  document.getElementById('preset-top-p').value = 0.9;
  document.getElementById('top-p-value').textContent = '0.9';

  // Enable save button
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = true;
  document.getElementById('delete-btn').disabled = true;

  document.getElementById('editor-title').textContent = '새 프리셋';
}

function populateForm(preset) {
  document.getElementById('preset-name').value = preset.name || '';
  document.getElementById('preset-task-type').value = preset.task_type || '';
  document.getElementById('preset-status').value = preset.status || 'draft';
  document.getElementById('preset-model').value = preset.model_name || '';
  document.getElementById('preset-max-tokens').value = preset.max_tokens || 4096;
  document.getElementById('preset-temperature').value = preset.temperature || 0.7;
  document.getElementById('temp-value').textContent = preset.temperature || 0.7;
  document.getElementById('preset-top-p').value = preset.top_p || 0.9;
  document.getElementById('top-p-value').textContent = preset.top_p || 0.9;
  document.getElementById('preset-description').value = preset.description || '';
  document.getElementById('preset-system-prompt').value = preset.system_prompt || '';
  document.getElementById('preset-constraints').value = (preset.constraints || []).join(', ');
}

function enableEditorButtons(status) {
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = status === 'published';
  document.getElementById('delete-btn').disabled = false;
}

function getFormData() {
  const constraintsStr = document.getElementById('preset-constraints')?.value || '';
  const constraints = constraintsStr.split(',').map(s => s.trim()).filter(s => s);

  return {
    name: document.getElementById('preset-name')?.value || '',
    task_type: document.getElementById('preset-task-type')?.value || '',
    description: document.getElementById('preset-description')?.value || '',
    model_name: document.getElementById('preset-model')?.value || '',
    max_tokens: parseInt(document.getElementById('preset-max-tokens')?.value) || 4096,
    temperature: parseFloat(document.getElementById('preset-temperature')?.value) || 0.7,
    top_p: parseFloat(document.getElementById('preset-top-p')?.value) || 0.9,
    system_prompt: document.getElementById('preset-system-prompt')?.value || '',
    constraints: constraints,
  };
}

async function saveDraft() {
  const data = getFormData();

  if (!data.name || !data.task_type || !data.model_name) {
    showError('필수 항목을 모두 입력해주세요');
    return;
  }

  try {
    if (isNewPreset) {
      const created = await adminApiCall('/presets', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      selectedPresetId = created.id;
      isNewPreset = false;
      showSuccess('프리셋이 생성되었습니다');
    } else {
      await adminApiCall(`/presets/${selectedPresetId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      showSuccess('프리셋이 저장되었습니다');
    }

    loadPresets();
    if (selectedPresetId) {
      selectPreset(selectedPresetId);
    }
  } catch (error) {
    showError('프리셋 저장 실패: ' + error.message);
  }
}

async function publishPreset() {
  if (!selectedPresetId) return;

  const reason = prompt('게시 사유를 입력하세요:');
  if (!reason) {
    showError('게시 사유는 필수입니다');
    return;
  }

  try {
    await adminApiCall(`/presets/${selectedPresetId}/publish`, {
      method: 'POST',
      body: JSON.stringify({ change_reason: reason }),
    });
    showSuccess('프리셋이 게시되었습니다');
    loadPresets();
    selectPreset(selectedPresetId);
  } catch (error) {
    showError('프리셋 게시 실패: ' + error.message);
  }
}

async function deletePreset() {
  if (!selectedPresetId) return;

  if (!confirmAction('이 프리셋을 삭제하시겠습니까?')) {
    return;
  }

  try {
    await adminApiCall(`/presets/${selectedPresetId}`, {
      method: 'DELETE',
    });
    showSuccess('프리셋이 삭제되었습니다');
    selectedPresetId = null;
    createNewPreset();
    loadPresets();
  } catch (error) {
    showError('프리셋 삭제 실패: ' + error.message);
  }
}

// Export for global use
if (typeof window !== 'undefined') {
  window.selectPreset = selectPreset;
}
