// @ts-check
// Web 사용자 테스트용 스모크 테스트.
// 가이드: docs/webtest/web-user-test-setup-guide.md
// 실행 전 백엔드가 http://localhost:8001 (ver3) 에서 기동 중이어야 합니다. BASE_URL로 변경 가능.

const { test, expect } = require('@playwright/test');

test.describe('스모크: Base URL 접근', () => {
  test('대시보드 페이지가 로드된다', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page).toHaveTitle(/.+/);
  });

  test('API 문서 페이지가 로드된다', async ({ page }) => {
    await page.goto('/docs');
    await expect(page).toHaveURL(/\/docs/);
    await expect(page.locator('body')).toBeVisible();
  });
});
