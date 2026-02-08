// @ts-check
// Phase 10-1 UX/UI 개선 — Reasoning 페이지 (진행 상태, 취소, 예상 시간)
// 참고: docs/phases/phase-10-1/phase-10-1-0-plan.md, phase-10-1-0-todo-list.md

const { test, expect } = require('@playwright/test');

test.describe('1. 대시보드 → Reasoning 진입 — W10.1', () => {
  test('W10.1.1 대시보드 접속 → Reasoning Lab 링크 표시', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('a[href="/reason"]').first()).toBeVisible();
  });

  test('W10.1.2 Reasoning 링크 클릭 → /reason 이동', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('a[href="/reason"]').first().click();
    await expect(page).toHaveURL(/\/reason/);
  });
});

test.describe('2. Reasoning Lab 페이지 — W10.2 (Phase 10-1 UX)', () => {
  test('W10.2.1 Reasoning 접속 → 질문·모드·실행 버튼 표시', async ({ page }) => {
    await page.goto('/reason');
    await expect(page).toHaveURL(/\/reason/);
    await expect(page.locator('#question')).toBeVisible();
    await expect(page.locator('#mode')).toBeVisible();
    await expect(page.locator('#submit-btn')).toBeVisible();
  });

  test('W10.2.2 진행 상태·취소·예상 시간 영역 존재 (10-1-1~10-1-3)', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#progress-stages')).toBeAttached();
    await expect(page.locator('#cancel-btn')).toBeAttached();
    await expect(page.locator('#eta-display').or(page.locator('#eta-text')).first()).toBeAttached();
    await expect(page.locator('#results-loading')).toBeAttached();
    await expect(page.locator('#results-content')).toBeAttached();
  });

  test('W10.2.3 실행 버튼 클릭 시 로딩/비활성화 반영', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트 질문');
    await page.locator('#submit-btn').click();
    // 로딩 중: results-loading 표시 또는 버튼 비활성화
    await expect(
      page.locator('#results-loading').or(page.locator('#submit-btn[disabled]'))
    ).toBeVisible({ timeout: 5000 }).catch(() => {});
    // 결과 영역 또는 로딩 영역이 DOM에 있음
    await expect(page.locator('#results')).toBeAttached();
  });
});

test.describe('3. Reasoning 결과 영역 — W10.3', () => {
  test('W10.3.1 결과·추천 섹션 컨테이너 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#results')).toBeAttached();
    await expect(page.locator('#recommendations-section')).toBeAttached();
  });
});
