/**
 * Login Page JS (Phase 14 QC 4.1)
 */

document.addEventListener('DOMContentLoaded', () => {
  checkExistingAuth();
  document.getElementById('login-form').addEventListener('submit', handleLogin);
});

/**
 * 이미 인증된 경우 대시보드로 리다이렉트
 */
async function checkExistingAuth() {
  const token = localStorage.getItem('auth_token');
  if (!token) return;

  try {
    const res = await fetch('/api/auth/me', {
      headers: { 'Authorization': 'Bearer ' + token }
    });
    if (res.ok) {
      const data = await res.json();
      if (data.authenticated) {
        const returnTo = new URLSearchParams(window.location.search).get('return_to');
        window.location.href = returnTo || '/dashboard';
      }
    }
  } catch (e) {
    // 토큰 무효 — 로그인 폼 표시 유지
  }
}

/**
 * 로그인 폼 제출 처리
 */
async function handleLogin(e) {
  e.preventDefault();

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;
  const errorEl = document.getElementById('login-error');
  const submitBtn = e.target.querySelector('button[type="submit"]');

  errorEl.style.display = 'none';
  submitBtn.disabled = true;
  submitBtn.textContent = '로그인 중...';

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || '로그인에 실패했습니다');
    }

    const data = await res.json();
    localStorage.setItem('auth_token', data.access_token);

    const returnTo = new URLSearchParams(window.location.search).get('return_to');
    window.location.href = returnTo || '/dashboard';
  } catch (error) {
    errorEl.textContent = error.message;
    errorEl.style.display = 'block';
    submitBtn.disabled = false;
    submitBtn.textContent = '로그인';
  }
}
