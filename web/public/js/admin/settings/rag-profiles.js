/**
 * RAG Profile Management Page JS (Phase 11-3)
 */

// State
let currentPage = 1;
let itemsPerPage = 20;
let totalItems = 0;
let selectedProfileId = null;
let isNewProfile = false;

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initEventListeners();
  loadProfiles();
});

function initHeader() {
  if (typeof initLayout === 'function') initLayout();
  if (typeof renderHeader === 'function') {
    renderHeader({
      subtitle: 'RAG 프로필 관리',
      currentPath: '/admin/settings/rag-profiles'
    });
  }
}

function initEventListeners() {
  // Filter apply
  document.getElementById('filter-apply-btn')?.addEventListener('click', () => {
    currentPage = 1;
    loadProfiles();
  });

  // Create new profile
  document.getElementById('create-profile-btn')?.addEventListener('click', createNewProfile);

  // Save draft
  document.getElementById('save-draft-btn')?.addEventListener('click', saveDraft);

  // Publish
  document.getElementById('publish-btn')?.addEventListener('click', publishProfile);

  // Delete
  document.getElementById('delete-btn')?.addEventListener('click', deleteProfile);

  // Slider value displays
  document.getElementById('profile-chunk-size')?.addEventListener('input', (e) => {
    document.getElementById('chunk-size-value').textContent = e.target.value;
  });

  document.getElementById('profile-chunk-overlap')?.addEventListener('input', (e) => {
    document.getElementById('chunk-overlap-value').textContent = e.target.value;
  });

  document.getElementById('profile-top-k')?.addEventListener('input', (e) => {
    document.getElementById('top-k-value').textContent = e.target.value;
  });

  document.getElementById('profile-score-threshold')?.addEventListener('input', (e) => {
    document.getElementById('score-value').textContent = e.target.value;
  });

  // Enter key in search
  document.getElementById('filter-search')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      currentPage = 1;
      loadProfiles();
    }
  });
}

async function loadProfiles() {
  const tableBody = document.getElementById('profile-table');
  if (!tableBody) return;

  tableBody.innerHTML = '<tr><td colspan="4" class="loading">로딩 중...</td></tr>';

  try {
    const params = {
      limit: itemsPerPage,
      offset: (currentPage - 1) * itemsPerPage,
      status: document.getElementById('filter-status')?.value || '',
      search: document.getElementById('filter-search')?.value || '',
    };

    const queryString = buildQueryString(params);
    const data = await adminApiCall(`/rag-profiles${queryString}`);

    totalItems = data.total || 0;
    const profiles = data.items || [];

    if (profiles.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="4" class="loading">프로필이 없습니다</td></tr>';
      return;
    }

    tableBody.innerHTML = profiles.map(p => `
      <tr data-id="${p.id}" class="${p.id === selectedProfileId ? 'selected' : ''}" onclick="selectProfile('${p.id}')">
        <td>${truncateText(p.name, 30)}</td>
        <td>${p.chunk_size || '-'}</td>
        <td>${p.top_k || '-'}</td>
        <td>${createStatusBadge(p.status)}</td>
      </tr>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    updatePaginationInfo('pagination-info', currentPage, itemsPerPage, totalItems);
    renderPagination('pagination-buttons', currentPage, totalPages, (page) => {
      currentPage = page;
      loadProfiles();
    });

  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="4" class="loading">프로필 로딩 오류</td></tr>';
    showError('프로필 로딩 실패: ' + error.message);
  }
}

async function selectProfile(id) {
  selectedProfileId = id;
  isNewProfile = false;

  // Update table selection
  document.querySelectorAll('#profile-table tr').forEach(tr => {
    tr.classList.toggle('selected', tr.dataset.id === id);
  });

  try {
    const profile = await adminApiCall(`/rag-profiles/${id}`);
    populateForm(profile);
    enableEditorButtons(profile.status);
    document.getElementById('editor-title').textContent = 'RAG 프로필 수정';
  } catch (error) {
    showError('프로필 로딩 실패: ' + error.message);
  }
}

function createNewProfile() {
  selectedProfileId = null;
  isNewProfile = true;

  // Clear selection
  document.querySelectorAll('#profile-table tr').forEach(tr => {
    tr.classList.remove('selected');
  });

  // Clear form
  document.getElementById('profile-form')?.reset();
  document.getElementById('profile-status').value = 'draft';

  // Reset slider displays
  document.getElementById('chunk-size-value').textContent = '1000';
  document.getElementById('chunk-overlap-value').textContent = '200';
  document.getElementById('top-k-value').textContent = '5';
  document.getElementById('score-value').textContent = '0.7';

  // Enable save button
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = true;
  document.getElementById('delete-btn').disabled = true;

  document.getElementById('editor-title').textContent = '새 RAG 프로필';
}

function populateForm(profile) {
  document.getElementById('profile-name').value = profile.name || '';
  document.getElementById('profile-status').value = profile.status || 'draft';
  document.getElementById('profile-description').value = profile.description || '';

  // Chunking settings
  document.getElementById('profile-chunk-size').value = profile.chunk_size || 1000;
  document.getElementById('chunk-size-value').textContent = profile.chunk_size || 1000;
  document.getElementById('profile-chunk-overlap').value = profile.chunk_overlap || 200;
  document.getElementById('chunk-overlap-value').textContent = profile.chunk_overlap || 200;

  // Retrieval settings
  document.getElementById('profile-top-k').value = profile.top_k || 5;
  document.getElementById('top-k-value').textContent = profile.top_k || 5;
  document.getElementById('profile-score-threshold').value = profile.score_threshold || 0.7;
  document.getElementById('score-value').textContent = profile.score_threshold || 0.7;
  document.getElementById('profile-rerank-enabled').checked = profile.rerank_enabled || false;
  document.getElementById('profile-rerank-top-n').value = profile.rerank_top_n || 3;

  // Filter priority
  document.getElementById('profile-filter-priority').value =
    profile.filter_priority ? JSON.stringify(profile.filter_priority, null, 2) : '';
}

function enableEditorButtons(status) {
  document.getElementById('save-draft-btn').disabled = false;
  document.getElementById('publish-btn').disabled = status === 'published';
  document.getElementById('delete-btn').disabled = false;
}

function getFormData() {
  let filterPriority = null;
  const filterPriorityStr = document.getElementById('profile-filter-priority')?.value;
  if (filterPriorityStr) {
    try {
      filterPriority = JSON.parse(filterPriorityStr);
    } catch (e) {
      // Invalid JSON, will be validated
    }
  }

  return {
    name: document.getElementById('profile-name')?.value || '',
    description: document.getElementById('profile-description')?.value || '',
    chunk_size: parseInt(document.getElementById('profile-chunk-size')?.value) || 1000,
    chunk_overlap: parseInt(document.getElementById('profile-chunk-overlap')?.value) || 200,
    top_k: parseInt(document.getElementById('profile-top-k')?.value) || 5,
    score_threshold: parseFloat(document.getElementById('profile-score-threshold')?.value) || 0.7,
    rerank_enabled: document.getElementById('profile-rerank-enabled')?.checked || false,
    rerank_top_n: parseInt(document.getElementById('profile-rerank-top-n')?.value) || 3,
    filter_priority: filterPriority,
  };
}

async function saveDraft() {
  const data = getFormData();

  if (!data.name) {
    showError('프로필 이름을 입력해주세요');
    return;
  }

  try {
    if (isNewProfile) {
      const created = await adminApiCall('/rag-profiles', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      selectedProfileId = created.id;
      isNewProfile = false;
      showSuccess('RAG 프로필이 생성되었습니다');
    } else {
      await adminApiCall(`/rag-profiles/${selectedProfileId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
      showSuccess('RAG 프로필이 저장되었습니다');
    }

    loadProfiles();
    if (selectedProfileId) {
      selectProfile(selectedProfileId);
    }
  } catch (error) {
    showError('프로필 저장 실패: ' + error.message);
  }
}

async function publishProfile() {
  if (!selectedProfileId) return;

  const reason = prompt('게시 사유를 입력하세요:');
  if (!reason) {
    showError('게시 사유는 필수입니다');
    return;
  }

  try {
    await adminApiCall(`/rag-profiles/${selectedProfileId}/publish`, {
      method: 'POST',
      body: JSON.stringify({ change_reason: reason }),
    });
    showSuccess('RAG 프로필이 게시되었습니다');
    loadProfiles();
    selectProfile(selectedProfileId);
  } catch (error) {
    showError('프로필 게시 실패: ' + error.message);
  }
}

async function deleteProfile() {
  if (!selectedProfileId) return;

  if (!confirmAction('이 RAG 프로필을 삭제하시겠습니까?')) {
    return;
  }

  try {
    await adminApiCall(`/rag-profiles/${selectedProfileId}`, {
      method: 'DELETE',
    });
    showSuccess('RAG 프로필이 삭제되었습니다');
    selectedProfileId = null;
    createNewProfile();
    loadProfiles();
  } catch (error) {
    showError('프로필 삭제 실패: ' + error.message);
  }
}

// Export for global use
if (typeof window !== 'undefined') {
  window.selectProfile = selectProfile;
}
