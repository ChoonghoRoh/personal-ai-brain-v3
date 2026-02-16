/**
 * Template Management Page JS (Phase 11-3)
 */

// State
let currentPage = 1;
let itemsPerPage = 20;
let totalItems = 0;
let selectedTemplateId = null;
let isNewTemplate = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initEventListeners();
  loadTemplates();
});

function initHeader() {
  if (typeof initLayout === 'function') initLayout();
  if (typeof renderHeader === 'function') {
    renderHeader({
      subtitle: '템플릿 관리',
      currentPath: '/admin/settings/templates'
    });
  }
}

function initEventListeners() {
  // Filter apply
  document.getElementById('filter-apply-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadTemplates();
  });

  // Create new template
  document.getElementById('create-template-btn')?.addEventListener('click', createNewTemplate);

  // Save draft
  document.getElementById('save-draft-btn')?.addEventListener('click', saveDraft);

  // Publish
  document.getElementById('publish-btn')?.addEventListener('click', publishTemplate);

  // Delete
  document.getElementById('delete-btn')?.addEventListener('click', deleteTemplate);

  // Content change - extract variables
  document.getElementById('template-content')?.addEventListener('input', updateVariables);

  // Enter key in search
  document.getElementById('filter-search')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadTemplates();
    }
  });
}

async function loadTemplates() {
  const tableBody = document.getElementById('template-table');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="4" class="loading">로딩 중...</td></tr>';

  try {
    const params = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      template_type: document.getElementById('filter-type')?.value || '',
      status: document.getElementById('filter-status')?.value || '',
      search: document.getElementById('filter-search')?.value || '',
    };

    const queryString = buildQueryString(params);
    const data = await adminApiCall(`/templates${queryString}`);

    totalItems = data.total || 0;
    const templates = data.items || [];

    if (templates.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" class="loading">템플릿이 없습니다</td></tr>';
      return;
    }

    tableBody.innerHTML = templates.map(t => `
      <tr data-id="${t.id}" class="${t.id === selectedTemplateId ? 'selected' : ''}" onclick="selectTemplate('${t.id}')">
        <td>${truncateText(t.name, 30)}</td>
        <td>${t.template_type || '-'}</td>
        <td>${createStatusBadge(t.status)}</td>
        <td>${formatDate(t.updated_at)}</td>
      </tr>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    updatePaginationInfo('pagination-info', currentPage, itemsPerPage, totalItems);
    renderPagination('pagination-buttons', currentPage, totalPages, (page) => {
      currentPage = page;
      loadTemplates();
    });

  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="4" class="loading">템플릿 로딩 오류</td></tr>';
    showError('템플릿 로딩 실패: ' + error.message);
  }
}

async function selectTemplate(id) {
  selectedTemplateId = id;
  isNewTemplate = false;

  // Update table selection
  document.querySelectorAll('#template-table tr').forEach(tr => {
    tr.classList.toggle('selected', tr.dataset.id === id);
  });

  try {
    const template = await adminApiCall(`/templates/${id}`);
    populateForm(template);
    enableEditorButtons(template.status);
    document.getElementById('editor-title').textContent = '템플릿 수정';
  } catch (error) {
    showError('템플릿 로딩 실패: ' + error.message);
  }
}

function createNewTemplate() {
  selectedTemplateId = null;
  isNewTemplate = true;

  // Clear selection
  document.querySelectorAll('#template-table tr').forEach(tr => {
    tr.classList.remove('selected');
  });

  // Clear form
  document.getElementById('template-form')?.reset();
  document.getElementById('template-status').value = 'draft';
  document.getElementById('template-variables').innerHTML = '<span class="hint">내용에서 변수가 자동 감지됩니다: {{변수명}}</span>';

  // Enable save button
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = true;
  document.getElementById('delete-btn').disabled = true;

  document.getElementById('editor-title').textContent = '새 템플릿';
}

function populateForm(template) {
  document.getElementById('template-name').value = template.name || '';
  document.getElementById('template-type').value = template.template_type || '';
  document.getElementById('template-status').value = template.status || 'draft';
  document.getElementById('template-description').value = template.description || '';
  document.getElementById('template-content').value = template.content || '';

  // Update variables display
  updateVariables();
}

function updateVariables() {
  const content = document.getElementById('template-content')?.value || '';
  const variables = extractVariables(content);
  const variablesEl = document.getElementById('template-variables');
  if (variablesEl) {
    variablesEl.innerHTML = renderVariableTags(variables);
  }
}

function enableEditorButtons(status) {
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = status === 'published';
  document.getElementById('delete-btn').disabled = false;
}

function getFormData() {
  const content = document.getElementById('template-content')?.value || '';
  return {
    name: document.getElementById('template-name')?.value || '',
    template_type: document.getElementById('template-type')?.value || '',
    description: document.getElementById('template-description')?.value || '',
    content: content,
    variables: extractVariables(content),
  };
}

async function saveDraft() {
  const data = getFormData();

  if (!data.name || !data.template_type || !data.content) {
    showError('필수 항목을 모두 입력해주세요');
    return;
  }

  try {
    if (isNewTemplate) {
      const created = await adminApiCall('/templates', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      selectedTemplateId = created.id;
      isNewTemplate = false;
      showSuccess('템플릿이 생성되었습니다');
    } else {
      await adminApiCall(`/templates/${selectedTemplateId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      showSuccess('템플릿이 저장되었습니다');
    }

    loadTemplates();
    if (selectedTemplateId) {
      selectTemplate(selectedTemplateId);
    }
  } catch (error) {
    showError('템플릿 저장 실패: ' + error.message);
  }
}

async function publishTemplate() {
  if (!selectedTemplateId) return;

  const reason = prompt('게시 사유를 입력하세요:');
  if (!reason) {
    showError('게시 사유는 필수입니다');
    return;
  }

  try {
    await adminApiCall(`/templates/${selectedTemplateId}/publish`, {
      method: 'POST',
      body: JSON.stringify({ change_reason: reason }),
    });
    showSuccess('템플릿이 게시되었습니다');
    loadTemplates();
    selectTemplate(selectedTemplateId);
  } catch (error) {
    showError('템플릿 게시 실패: ' + error.message);
  }
}

async function deleteTemplate() {
  if (!selectedTemplateId) return;

  if (!confirmAction('이 템플릿을 삭제하시겠습니까?')) {
    return;
  }

  try {
    await adminApiCall(`/templates/${selectedTemplateId}`, {
      method: 'DELETE',
    });
    showSuccess('템플릿이 삭제되었습니다');
    selectedTemplateId = null;
    createNewTemplate();
    loadTemplates();
  } catch (error) {
    showError('템플릿 삭제 실패: ' + error.message);
  }
}

// Export for global use
if (typeof window !== 'undefined') {
  window.selectTemplate = selectTemplate;
}
