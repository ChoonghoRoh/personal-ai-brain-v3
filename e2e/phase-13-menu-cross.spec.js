// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Phase 13-3-3: 메뉴 간 이동·404 시나리오 E2E
 */

test.describe('Phase 13-3-3: 메뉴 간 이동', () => {

  test('사용자 → Admin 지식 → Admin 설정 → 사용자 전체 순회', async ({ page }) => {
    // 1) 사용자 메뉴: 대시보드
    let response = await page.goto('/dashboard');
    expect(response.status()).toBe(200);

    // 2) Admin 지식 메뉴: 키워드 관리
    response = await page.goto('/admin/groups');
    expect(response.status()).toBe(200);

    // 3) Admin 설정 메뉴: 템플릿
    response = await page.goto('/admin/settings/templates');
    expect(response.status()).toBe(200);

    // 4) 다시 사용자 메뉴: 검색
    response = await page.goto('/search');
    expect(response.status()).toBe(200);
  });

  test('사용자 메뉴에서 Admin 지식 메뉴로 이동 시 헤더 활성이 변경된다', async ({ page }) => {
    await page.goto('/dashboard');
    const dashboardActive = page.locator('.container > header nav a.active');
    await expect(dashboardActive.first()).toBeVisible({ timeout: 10000 });

    await page.goto('/admin/labels');
    const adminActive = page.locator('.container > header nav a.active');
    await expect(adminActive.first()).toBeVisible({ timeout: 10000 });
  });

  test('Admin 지식 메뉴에서 Admin 설정 메뉴로 이동', async ({ page }) => {
    let response = await page.goto('/admin/chunk-labels');
    expect(response.status()).toBe(200);

    response = await page.goto('/admin/settings/presets');
    expect(response.status()).toBe(200);
  });

  test('Admin 설정 메뉴에서 사용자 메뉴로 이동', async ({ page }) => {
    let response = await page.goto('/admin/settings/policy-sets');
    expect(response.status()).toBe(200);

    response = await page.goto('/logs');
    expect(response.status()).toBe(200);
  });
});

test.describe('Phase 13-3-3: 404 시나리오', () => {

  test('/admin/unknown 접근 시 404 응답', async ({ page }) => {
    const response = await page.goto('/admin/unknown');
    expect(response.status()).toBe(404);
  });

  test('/admin/settings/unknown 접근 시 404 응답', async ({ page }) => {
    const response = await page.goto('/admin/settings/unknown');
    expect(response.status()).toBe(404);
  });

  test('/dashbord (오타) 접근 시 404 응답', async ({ page }) => {
    const response = await page.goto('/dashbord');
    expect(response.status()).toBe(404);
  });

  test('404 페이지에 네비게이션이 포함된다', async ({ page }) => {
    await page.goto('/admin/unknown');
    // 404.html에도 header-component.js가 로드되어 header가 렌더링됨
    const header = page.locator('.container > header');
    await expect(header).toBeVisible({ timeout: 10000 });
  });

  test('404 페이지에 대시보드 링크가 있다', async ({ page }) => {
    await page.goto('/admin/unknown');
    const link = page.locator('a[href="/dashboard"]');
    await expect(link.first()).toBeVisible({ timeout: 10000 });
  });
});
