// Phase 15-5-3: Admin 사용자 관리 JS (ESM)

function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function formatDate(isoDate) {
  if (!isoDate) return '-';
  return new Date(isoDate).toLocaleString('ko-KR', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  });
}

function getAuthHeaders() {
  const headers = { 'Content-Type': 'application/json' };
  const token = localStorage.getItem('auth_token');
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

const ROLE_LABELS = {
  user: '일반 사용자',
  admin_knowledge: '지식 관리자',
  admin_system: '시스템 관리자'
};

// ============================================
// State
// ============================================
let currentUsers = [];
let editingUserId = null;

// ============================================
// API
// ============================================
async function fetchUsers(params = {}) {
  const qs = new URLSearchParams();
  if (params.q) qs.set('q', params.q);
  if (params.role) qs.set('role', params.role);
  if (params.is_active !== undefined && params.is_active !== '') qs.set('is_active', params.is_active);
  qs.set('limit', '100');
  qs.set('offset', '0');

  const res = await fetch(`/api/admin/users?${qs}`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error('사용자 목록 로드 실패');
  return res.json();
}

async function createUser(data) {
  const res = await fetch('/api/admin/users', {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || '사용자 생성 실패');
  }
  return res.json();
}

async function updateUser(id, data) {
  const res = await fetch(`/api/admin/users/${id}`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || '사용자 수정 실패');
  }
  return res.json();
}

async function deactivateUser(id) {
  const res = await fetch(`/api/admin/users/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders()
  });
  if (!res.ok) throw new Error('사용자 비활성화 실패');
  return res.json();
}

async function resetPassword(id, newPassword) {
  const res = await fetch(`/api/admin/users/${id}/reset-password`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ new_password: newPassword })
  });
  if (!res.ok) throw new Error('비밀번호 초기화 실패');
  return res.json();
}

// ============================================
// Render
// ============================================
function renderUsersTable(users, total) {
  const tbody = document.getElementById('users-table-body');
  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="loading">사용자가 없습니다.</td></tr>';
    document.getElementById('pagination-info').textContent = '';
    return;
  }

  tbody.innerHTML = users.map(u => `
    <tr data-id="${u.id}">
      <td>${u.id}</td>
      <td><strong>${esc(u.username)}</strong></td>
      <td>${esc(u.display_name) || '-'}</td>
      <td><span class="role-badge ${u.role}">${ROLE_LABELS[u.role] || u.role}</span></td>
      <td><span class="status-badge ${u.is_active ? 'active' : 'inactive'}">${u.is_active ? '활성' : '비활성'}</span></td>
      <td>${formatDate(u.last_login_at)}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-secondary btn-small edit-btn" data-id="${u.id}">수정</button>
          ${u.is_active ? `<button class="btn btn-danger deactivate-btn" data-id="${u.id}">비활성화</button>` : ''}
        </div>
      </td>
    </tr>
  `).join('');

  document.getElementById('pagination-info').textContent = `총 ${total}명`;
  currentUsers = users;
}

// ============================================
// Form
// ============================================
function showForm(mode, user) {
  const panel = document.getElementById('user-form-panel');
  const container = document.querySelector('.users-container');
  const title = document.getElementById('form-title');
  const passwordGroup = document.getElementById('password-group');
  const activeGroup = document.getElementById('active-group');
  const resetSection = document.getElementById('reset-password-section');
  const usernameInput = document.getElementById('form-username');

  panel.style.display = 'block';
  container.classList.add('has-form');

  if (mode === 'create') {
    title.textContent = '사용자 추가';
    editingUserId = null;
    document.getElementById('user-form').reset();
    document.getElementById('form-user-id').value = '';
    passwordGroup.style.display = 'block';
    document.getElementById('form-password').required = true;
    activeGroup.style.display = 'none';
    resetSection.style.display = 'none';
    usernameInput.readOnly = false;
  } else {
    title.textContent = '사용자 수정';
    editingUserId = user.id;
    document.getElementById('form-user-id').value = user.id;
    usernameInput.value = user.username;
    usernameInput.readOnly = true;
    document.getElementById('form-display-name').value = user.display_name || '';
    document.getElementById('form-email').value = user.email || '';
    document.getElementById('form-role').value = user.role;
    document.getElementById('form-is-active').checked = user.is_active;
    passwordGroup.style.display = 'none';
    document.getElementById('form-password').required = false;
    activeGroup.style.display = 'block';
    resetSection.style.display = 'block';
  }
}

function hideForm() {
  document.getElementById('user-form-panel').style.display = 'none';
  document.querySelector('.users-container').classList.remove('has-form');
  editingUserId = null;
}

// ============================================
// Load
// ============================================
async function loadUsers() {
  try {
    const q = document.getElementById('search-input').value;
    const role = document.getElementById('role-filter').value;
    const is_active = document.getElementById('status-filter').value;
    const data = await fetchUsers({ q, role, is_active });
    renderUsersTable(data.items, data.total);
  } catch (err) {
    showError(err.message);
  }
}

// ============================================
// Event handlers
// ============================================
function init() {
  // 사용자 추가 버튼
  document.getElementById('add-user-btn').addEventListener('click', () => showForm('create'));

  // 취소 버튼
  document.getElementById('form-cancel-btn').addEventListener('click', hideForm);

  // 폼 제출
  document.getElementById('user-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      if (editingUserId) {
        // 수정
        await updateUser(editingUserId, {
          display_name: document.getElementById('form-display-name').value || null,
          email: document.getElementById('form-email').value || null,
          role: document.getElementById('form-role').value,
          is_active: document.getElementById('form-is-active').checked,
        });
        showSuccess('사용자 정보가 수정되었습니다.');
      } else {
        // 생성
        const password = document.getElementById('form-password').value;
        if (!password || password.length < 8) {
          showError('비밀번호는 8자 이상이어야 합니다.');
          return;
        }
        await createUser({
          username: document.getElementById('form-username').value,
          password: password,
          display_name: document.getElementById('form-display-name').value || null,
          email: document.getElementById('form-email').value || null,
          role: document.getElementById('form-role').value,
        });
        showSuccess('사용자가 생성되었습니다.');
      }
      hideForm();
      loadUsers();
    } catch (err) {
      showError(err.message);
    }
  });

  // 비밀번호 초기화
  document.getElementById('reset-password-btn').addEventListener('click', async () => {
    const newPw = document.getElementById('reset-new-password').value;
    if (!newPw || newPw.length < 8) {
      showError('비밀번호는 8자 이상이어야 합니다.');
      return;
    }
    try {
      await resetPassword(editingUserId, newPw);
      showSuccess('비밀번호가 초기화되었습니다.');
      document.getElementById('reset-new-password').value = '';
    } catch (err) {
      showError(err.message);
    }
  });

  // 테이블 클릭 이벤트 (이벤트 위임)
  document.getElementById('users-table-body').addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-btn');
    const deactivateBtn = e.target.closest('.deactivate-btn');

    if (editBtn) {
      const id = parseInt(editBtn.dataset.id);
      const user = currentUsers.find(u => u.id === id);
      if (user) showForm('edit', user);
    }

    if (deactivateBtn) {
      const id = parseInt(deactivateBtn.dataset.id);
      const user = currentUsers.find(u => u.id === id);
      if (user && confirm(`'${user.username}' 사용자를 비활성화하시겠습니까?`)) {
        deactivateUser(id)
          .then(() => {
            showSuccess('사용자가 비활성화되었습니다.');
            loadUsers();
          })
          .catch(err => showError(err.message));
      }
    }
  });

  // 필터 변경
  let debounceTimer;
  document.getElementById('search-input').addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(loadUsers, 300);
  });
  document.getElementById('role-filter').addEventListener('change', loadUsers);
  document.getElementById('status-filter').addEventListener('change', loadUsers);

  // 초기 로드
  loadUsers();
}

document.addEventListener('DOMContentLoaded', init);
