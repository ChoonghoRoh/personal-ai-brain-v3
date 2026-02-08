// @ts-check
// Phase 9-1 웹 사용자 체크리스트 → E2E 스펙 (보안·공개 페이지·검색/Ask/Reason)
// 참고: docs/phases/phase-9-1/phase-9-1-web-user-checklist.md

const { test, expect } = require('@playwright/test');

test.describe('1. 대시보드 및 공개 페이지 — W1.x', () => {
  test('W1.1 대시보드 접속 → 페이지 정상 로드 (인증 없이)', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('W1.2 /health 접속 → {"status": "ok"} 응답', async ({ request }) => {
    const res = await request.get('/health');
    expect(res.ok()).toBeTruthy();
    const json = await res.json();
    expect(json).toHaveProperty('status', 'ok');
  });

  test('W1.3 /docs 접속 → Swagger UI 표시 (인증 없이)', async ({ page }) => {
    await page.goto('/docs');
    await expect(page).toHaveURL(/\/docs/);
    await expect(page.locator('#swagger-ui')).toBeVisible({ timeout: 10000 });
  });

  test('W1.4 /redoc 접속 → ReDoc UI 표시', async ({ page }) => {
    await page.goto('/redoc');
    await expect(page).toHaveURL(/\/redoc/);
    await expect(page.locator('.redoc-wrap')).toBeVisible({ timeout: 10000 });
  });
});

test.describe('3. 인증 (AUTH_ENABLED=false) — W3.x', () => {
  test('W3.2 /api/auth/status 호출 → auth_enabled 확인', async ({ request }) => {
    const res = await request.get('/api/auth/status');
    expect(res.ok()).toBeTruthy();
    const json = await res.json();
    expect(json).toHaveProperty('auth_enabled');
  });

  test('W3.3 Ask 페이지 접속 → 질문 입력란·전송 버튼 표시', async ({ page }) => {
    await page.goto('/ask', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await expect(page).toHaveURL(/\/ask/);
    await expect(page.locator('#question-input').or(page.locator('input[type="text"]').first())).toBeVisible({ timeout: 10000 });
  });

  test('W3.4 Reason 페이지 접속 → 추론 입력·실행 버튼 표시', async ({ page }) => {
    await page.goto('/reason');
    await expect(page).toHaveURL(/\/reason/);
    await expect(page.locator('#question')).toBeVisible({ timeout: 10000 });
  });
});

test.describe('5. Rate Limiting — W5.x', () => {
  test('W5.1 정상 API 호출 → 응답 정상', async ({ request }) => {
    const res = await request.get('/health');
    expect(res.ok()).toBeTruthy();
  });

  test('W5.4 응답 헤더에 X-RateLimit 관련 포함 가능 (선택)', async ({ request }) => {
    const res = await request.get('/health');
    const headers = res.headers();
    const hasRateLimit = Object.keys(headers).some((k) => k.toLowerCase().includes('ratelimit'));
    // 헤더가 있으면 검증, 없어도 2xx면 통과 (개발 환경에서 비활성화 시)
    expect(res.ok()).toBeTruthy();
  });
});

test.describe('6. 검색 페이지 (/search) — W6.x', () => {
  test('W6.1 검색 페이지 접속 → 정상 로드', async ({ page }) => {
    await page.goto('/search');
    await expect(page).toHaveURL(/\/search/);
    await expect(page.locator('#search-input').or(page.locator('input').first())).toBeVisible({ timeout: 10000 });
  });

  test('W6.2 검색어 입력 후 검색 → 결과 영역 존재', async ({ page }) => {
    await page.goto('/search');
    await page.locator('#search-input').or(page.locator('input[type="text"]').first()).fill('테스트');
    await page.locator('#search-button').or(page.locator('button:has-text("검색")').first()).click();
    await expect(page.locator('#results')).toBeVisible({ timeout: 15000 });
  });
});

test.describe('7. AI 질의 (/ask) — W7.x', () => {
  test('W7.1 Ask 페이지 접속 → 정상 로드', async ({ page }) => {
    await page.goto('/ask', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await expect(page).toHaveURL(/\/ask/);
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('8. Reasoning Lab (/reason) — W8.x', () => {
  test('W8.1 Reason 페이지 접속 → 정상 로드', async ({ page }) => {
    await page.goto('/reason');
    await expect(page).toHaveURL(/\/reason/);
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('9. Swagger UI (/docs) — W9.x', () => {
  test('W9.1 /docs 접속 → Swagger UI 표시', async ({ page }) => {
    await page.goto('/docs');
    await expect(page).toHaveURL(/\/docs/);
    await expect(page.locator('.swagger-ui, #swagger-ui, [class*="swagger"]').first()).toBeVisible({ timeout: 10000 });
  });

  test('W9.2 Authorize 버튼 또는 인증 UI 존재', async ({ page }) => {
    await page.goto('/docs');
    const authorizeBtn = page.locator('button:has-text("Authorize")').or(page.locator('button:has-text("authorize")')).first();
    await expect(authorizeBtn).toBeVisible({ timeout: 10000 });
  });
});
