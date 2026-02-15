// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Phase 13-3-2: Admin 지식 6개 + 설정 5개 진입 E2E
 * 대상: /admin/* 6개 + /admin/settings/* 5개
 */

const ADMIN_KNOWLEDGE_PAGES = [
  { path: '/admin/groups', label: '키워드 관리' },
  { path: '/admin/labels', label: '라벨 관리' },
  { path: '/admin/chunk-create', label: '청크 생성' },
  { path: '/admin/approval', label: '청크 승인' },
  { path: '/admin/chunk-labels', label: '청크 관리' },
  { path: '/admin/statistics', label: '통계' },
];

const ADMIN_SETTINGS_PAGES = [
  { path: '/admin/settings/templates', label: '템플릿' },
  { path: '/admin/settings/presets', label: '프리셋' },
  { path: '/admin/settings/rag-profiles', label: 'RAG 프로필' },
  { path: '/admin/settings/policy-sets', label: '정책' },
  { path: '/admin/settings/audit-logs', label: '변경 이력' },
];

test.describe('Phase 13-3-2: Admin 지식 메뉴 6개 진입', () => {

  for (const { path, label } of ADMIN_KNOWLEDGE_PAGES) {
    test(`${label} (${path}) 페이지가 200으로 로드된다`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response.status()).toBe(200);
      await expect(page).toHaveTitle(/.+/);
    });

    test(`${label} (${path}) Admin 공통 shell이 로드된다`, async ({ page }) => {
      await page.goto(path);
      // Admin 공통 shell: .container > header (admin-common.js가 렌더링)
      const container = page.locator('.container');
      await expect(container).toBeVisible({ timeout: 5000 });

      // admin-common.js가 #header-placeholder를 제거하고 header를 .container afterbegin에 삽입
      const header = page.locator('.container > header');
      await expect(header).toBeVisible({ timeout: 10000 });
    });

    test(`${label} (${path}) 헤더 활성 메뉴가 Admin 영역이다`, async ({ page }) => {
      await page.goto(path);
      const activeLink = page.locator('.container > header nav a.active');
      await expect(activeLink.first()).toBeVisible({ timeout: 10000 });
    });
  }
});

test.describe('Phase 13-3-2: Admin 설정 메뉴 5개 진입', () => {

  for (const { path, label } of ADMIN_SETTINGS_PAGES) {
    test(`${label} (${path}) 페이지가 200으로 로드된다`, async ({ page }) => {
      const response = await page.goto(path);
      expect(response.status()).toBe(200);
      await expect(page).toHaveTitle(/.+/);
    });

    test(`${label} (${path}) Admin 공통 shell이 로드된다`, async ({ page }) => {
      await page.goto(path);
      const header = page.locator('.container > header');
      await expect(header).toBeVisible({ timeout: 10000 });
    });
  }
});
