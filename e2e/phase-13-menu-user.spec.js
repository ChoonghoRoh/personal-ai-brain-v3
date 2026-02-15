// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Phase 13-3-1: 사용자 메뉴 6개 진입·헤더 활성 E2E
 * 대상: /dashboard, /search, /knowledge, /reason, /ask, /logs
 */

const USER_MENU_PAGES = [
  { path: '/dashboard', label: '대시보드' },
  { path: '/search', label: '검색' },
  { path: '/knowledge', label: '지식 구조' },
  { path: '/reason', label: 'Reasoning' },
  { path: '/ask', label: 'AI 질의' },
  { path: '/logs', label: '로그' },
];

test.describe('Phase 13-3-1: 사용자 메뉴 진입·헤더 활성', () => {

  for (const { path, label } of USER_MENU_PAGES) {
    test(`${label} (${path}) 페이지가 로드된다`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response.status()).toBe(200);
      await expect(page).toHaveURL(new RegExp(path.replace('/', '\\/')));
      await expect(page).toHaveTitle(/.+/);
    });

    test(`${label} (${path}) 헤더가 렌더링된다`, async ({ page }) => {
      await page.goto(path);
      // admin-common.js가 #header-placeholder를 제거하고 .container afterbegin에 header 삽입
      const header = page.locator('.container > header');
      await expect(header).toBeVisible({ timeout: 10000 });
    });

    test(`${label} (${path}) 메뉴 활성 하이라이트가 적용된다`, async ({ page }) => {
      await page.goto(path);
      // header-component.js가 활성 메뉴에 'active' 클래스 적용
      const activeLink = page.locator('.container > header nav a.active');
      await expect(activeLink.first()).toBeVisible({ timeout: 10000 });
    });
  }

  test('루트(/) 접근 시 대시보드가 로드된다', async ({ page }) => {
    const response = await page.goto('/');
    expect(response.status()).toBe(200);
    await expect(page).toHaveTitle(/.+/);
  });
});
