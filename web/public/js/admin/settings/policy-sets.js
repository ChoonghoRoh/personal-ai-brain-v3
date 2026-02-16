/**
 * Policy Set Management Page JS (Phase 11-3)
 */

// State
let currentPage = 1;
let itemsPerPage = 20;
let totalItems = 0;
let selectedPolicyId = null;
let isNewPolicy = false;

// Cached dropdown options
let templatesCache = [];
let presetsCache = [];
let ragProfilesCache = [];

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initEventListeners();
  loadDropdownOptions();
  loadPolicies();
});

function initHeader() {
  if (typeof initLayout === 'function') initLayout();
  if (typeof renderHeader === 'function') {
    renderHeader({
      subtitle: '정책 관리',
      currentPath: '/admin/settings/policy-sets'
    });
  }
}

function initEventListeners() {
  // Filter apply
  document.getElementById('filter-apply-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadPolicies();
  });

  // Create new policy
  document.getElementById('create-policy-btn')?.addEventListener('click', createNewPolicy);

  // Save
  document.getElementById('save-btn')?.addEventListener('click', savePolicy);

  // Delete
  document.getElementById('delete-btn')?.addEventListener('click', deletePolicy);

  // Priority slider
  document.getElementById('policy-priority')?.addEventListener('input', (e) => {
    document.getElementById('priority-value').textContent = e.target.value;
  });

  // Enter key in search
  document.getElementById('filter-search')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadPolicies();
    }
  });
}

async function loadDropdownOptions() {
  try {
    // Load templates, presets, and RAG profiles for dropdowns
    const [templatesData, presetsData, ragProfilesData] = await Promise.all([
      adminApiCall('/templates?status=published&limit=100'),
      adminApiCall('/presets?status=published&limit=100'),
      adminApiCall('/rag-profiles?status=published&limit=100'),
    ]);

    templatesCache = templatesData.items || [];
    presetsCache = presetsData.items || [];
    ragProfilesCache = ragProfilesData.items || [];

    populateDropdowns();
  } catch (error) {
    console.error('드롭다운 옵션 로딩 실패:', error);
  }
}

function populateDropdowns() {
  // Templates dropdown
  const templateSelect = document.getElementById('policy-template');
  if (templateSelect) {
    templateSelect.innerHTML = '<option value="">템플릿 선택</option>' +
      templatesCache.map(t => `<option value="${t.id}">${t.name}</option>`).join('');
  }

  // Presets dropdown
  const presetSelect = document.getElementById('policy-preset');
  if (presetSelect) {
    presetSelect.innerHTML = '<option value="">프리셋 선택</option>' +
      presetsCache.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
  }

  // RAG Profiles dropdown
  const ragProfileSelect = document.getElementById('policy-rag-profile');
  if (ragProfileSelect) {
    ragProfileSelect.innerHTML = '<option value="">RAG 프로필 선택</option>' +
      ragProfilesCache.map(r => `<option value="${r.id}">${r.name}</option>`).join('');
  }
}

async function loadPolicies() {
  const tableBody = document.getElementById('policy-table');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="4" class="loading">로딩 중...</td></tr>';

  try {
    const params = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      is_active: document.getElementById('filter-active')?.value || '',
      search: document.getElementById('filter-search')?.value || '',
    };

    const queryString = buildQueryString(params);
    const data = await adminApiCall(`/policy-sets${queryString}`);

    totalItems = data.total || 0;
    const policies = data.items || [];

    if (policies.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" class="loading">정책이 없습니다</td></tr>';
      return;
    }

    tableBody.innerHTML = policies.map(p => {
      const effectiveStr = p.effective_from || p.effective_until
        ? `${formatDate(p.effective_from) || '미정'} - ${formatDate(p.effective_until) || '미정'}`
        : '항상';
      return `
        <tr data-id="${p.id}" class="${p.id === selectedPolicyId ? 'selected' : ''}" onclick="selectPolicy('${p.id}')">
          <td>${truncateText(p.name, 30)}</td>
          <td>${p.priority}</td>
          <td>${createActiveBadge(p.is_active)}</td>
          <td>${truncateText(effectiveStr, 25)}</td>
        </tr>
      `;
    }).join('');

    // Update pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    updatePaginationInfo('pagination-info', currentPage, itemsPerPage, totalItems);
    renderPagination('pagination-buttons', currentPage, totalPages, (page) => {
      currentPage = page;
      loadPolicies();
    });

  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="4" class="loading">정책 로딩 오류</td></tr>';
    showError('정책 로딩 실패: ' + error.message);
  }
}

async function selectPolicy(id) {
  selectedPolicyId = id;
  isNewPolicy = false;

  // Update table selection
  document.querySelectorAll('#policy-table tr').forEach(tr => {
    tr.classList.toggle('selected', tr.dataset.id === id);
  });

  try {
    const policy = await adminApiCall(`/policy-sets/${id}`);
    populateForm(policy);
    enableEditorButtons();
    document.getElementById('editor-title').textContent = '정책 수정';
  } catch (error) {
    showError('정책 로딩 실패: ' + error.message);
  }
}

function createNewPolicy() {
  selectedPolicyId = null;
  isNewPolicy = true;

  // Clear selection
  document.querySelectorAll('#policy-table tr').forEach(tr => {
    tr.classList.remove('selected');
  });

  // Clear form
  document.getElementById('policy-form')?.reset();
  document.getElementById('policy-priority').value = 0;
  document.getElementById('priority-value').textContent = '0';
  document.getElementById('policy-active').checked = true;

  // Enable save button
  document.getElementById('save-btn').disabled = false;
  document.getElementById('delete-btn').disabled = true;

  document.getElementById('editor-title').textContent = '새 정책';
}

function populateForm(policy) {
  document.getElementById('policy-name').value = policy.name || '';
  document.getElementById('policy-description').value = policy.description || '';
  document.getElementById('policy-project').value = policy.project_id || '';
  document.getElementById('policy-user-group').value = policy.user_group || '';
  document.getElementById('policy-template').value = policy.template_id || '';
  document.getElementById('policy-preset').value = policy.prompt_preset_id || '';
  document.getElementById('policy-rag-profile').value = policy.rag_profile_id || '';
  document.getElementById('policy-priority').value = policy.priority || 0;
  document.getElementById('priority-value').textContent = policy.priority || 0;
  document.getElementById('policy-active').checked = policy.is_active !== false;
  document.getElementById('policy-effective-from').value = formatDateForInput(policy.effective_from);
  document.getElementById('policy-effective-until').value = formatDateForInput(policy.effective_until);
}

function enableEditorButtons() {
  document.getElementById('save-btn').disabled = false;
  document.getElementById('delete-btn').disabled = false;
}

function getFormData() {
  const effectiveFrom = document.getElementById('policy-effective-from')?.value;
  const effectiveUntil = document.getElementById('policy-effective-until')?.value;

  return {
    name: document.getElementById('policy-name')?.value || '',
    description: document.getElementById('policy-description')?.value || '',
    project_id: document.getElementById('policy-project')?.value || null,
    user_group: document.getElementById('policy-user-group')?.value || null,
    template_id: document.getElementById('policy-template')?.value || null,
    prompt_preset_id: document.getElementById('policy-preset')?.value || null,
    rag_profile_id: document.getElementById('policy-rag-profile')?.value || null,
    priority: parseInt(document.getElementById('policy-priority')?.value) || 0,
    is_active: document.getElementById('policy-active')?.checked || false,
    effective_from: effectiveFrom ? new Date(effectiveFrom).toISOString() : null,
    effective_until: effectiveUntil ? new Date(effectiveUntil).toISOString() : null,
  };
}

async function savePolicy() {
  const data = getFormData();

  if (!data.name) {
    showError('정책 이름을 입력해주세요');
    return;
  }

  try {
    if (isNewPolicy) {
      const created = await adminApiCall('/policy-sets', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      selectedPolicyId = created.id;
      isNewPolicy = false;
      showSuccess('정책이 생성되었습니다');
    } else {
      await adminApiCall(`/policy-sets/${selectedPolicyId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      showSuccess('정책이 저장되었습니다');
    }

    loadPolicies();
    if (selectedPolicyId) {
      selectPolicy(selectedPolicyId);
    }
  } catch (error) {
    showError('정책 저장 실패: ' + error.message);
  }
}

async function deletePolicy() {
  if (!selectedPolicyId) return;

  if (!confirmAction('이 정책을 삭제하시겠습니까?')) {
    return;
  }

  try {
    await adminApiCall(`/policy-sets/${selectedPolicyId}`, {
      method: 'DELETE',
    });
    showSuccess('정책이 삭제되었습니다');
    selectedPolicyId = null;
    createNewPolicy();
    loadPolicies();
  } catch (error) {
    showError('정책 삭제 실패: ' + error.message);
  }
}

// Export for global use
if (typeof window !== 'undefined') {
  window.selectPolicy = selectPolicy;
}
