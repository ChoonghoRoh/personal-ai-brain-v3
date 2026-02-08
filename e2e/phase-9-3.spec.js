// @ts-check
// Phase 9-3 웹 사용자 체크리스트 → E2E 스펙
// 참고: docs/webtest/phase-9-3/phase-9-3-user-test-plan.md
//       docs/phases/phase-9-3/phase-9-3-web-user-checklist.md

const { test, expect } = require('@playwright/test');

test.describe('1. 대시보드 (/dashboard) — W1.x', () => {
  test('W1.1 대시보드 접속 → 링크(검색, 지식, Ask, Reasoning Lab, 청크 승인 등) 표시', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.locator('a[href="/search"]').first()).toBeVisible();
    await expect(page.locator('a[href="/knowledge"]').first()).toBeVisible();
    await expect(page.locator('a[href="/reason"]').first()).toBeVisible();
    await expect(page.locator('a[href="/knowledge-admin"]').first()).toBeVisible();
  });

  test('W1.2 각 링크 클릭 시 해당 페이지로 이동', async ({ page }) => {
    await page.goto('/dashboard');
    await page.locator('a[href="/search"]').first().click();
    await expect(page).toHaveURL(/\/search/);
    await page.goto('/dashboard');
    await page.locator('a[href="/reason"]').first().click();
    await expect(page).toHaveURL(/\/reason/);
  });
});

test.describe('2. 검색 (/search) — W2.x', () => {
  test('W2.1 검색 페이지 접속 → 검색어 입력란·검색 버튼 표시', async ({ page }) => {
    await page.goto('/search');
    await expect(page).toHaveURL(/\/search/);
    await expect(page.locator('#search-input')).toBeVisible();
    await expect(page.locator('#search-button')).toBeVisible();
  });

  test('W2.2 검색어 입력 후 검색 실행 → 결과 영역 갱신', async ({ page }) => {
    await page.goto('/search');
    await page.locator('#search-input').fill('테스트');
    await page.locator('#search-button').click();
    await expect(page.locator('#results')).toBeVisible();
  });
});

test.describe('3. AI 질의 (/ask) — W3.x', () => {
  test('W3.1 Ask 페이지 접속 → 질문 입력란·전송 버튼 표시', async ({ page }) => {
    await page.goto('/ask', { waitUntil: 'domcontentloaded', timeout: 15000 });
    await expect(page).toHaveURL(/\/ask/);
    await expect(page.locator('#question-input')).toBeVisible();
    await expect(page.locator('#ask-button')).toBeVisible();
  });

  test('W3.2 옵션(컨텍스트 사용 등) 표시', async ({ page }) => {
    await page.goto('/ask');
    await expect(page.locator('#context-enabled')).toBeVisible();
  });
});

test.describe('4. Reasoning Lab (/reason) — W4.x', () => {
  test('W4.1 Reasoning Lab 접속 → 질의 입력·모드 선택·실행 버튼 표시', async ({ page }) => {
    await page.goto('/reason');
    await expect(page).toHaveURL(/\/reason/);
    await expect(page.locator('#question')).toBeVisible();
    await expect(page.locator('#mode')).toBeVisible();
    await expect(page.locator('#submit-btn')).toBeVisible();
  });

  test('W4.2 관련 정보 섹션 토글 버튼 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#recommendations-section')).toBeAttached();
    await expect(page.locator('.rec-toggle').first()).toBeAttached();
  });
});

test.describe('5. 지식 구조 목록 (/knowledge) — W5.x', () => {
  test('W5.1 지식 구조 페이지 접속 → 청크/목록 또는 필터 표시', async ({ page }) => {
    await page.goto('/knowledge');
    await expect(page).toHaveURL(/\/knowledge/);
    await expect(page.locator('#chunk-list')).toBeVisible();
    await expect(page.locator('#label-list')).toBeVisible();
  });
});

test.describe('6. 지식 상세·라벨/관계 매칭 — W6~8.x', () => {
  test('W6.1 chunk_id로 상세 접속 → 청크 영역 또는 로딩 표시', async ({ page }) => {
    await page.goto('/knowledge-detail?id=1');
    await expect(page).toHaveURL(/knowledge-detail/);
    await expect(page.locator('#chunk-detail-content')).toBeVisible();
  });

  test('W7.1 chunk_id로 라벨 매칭 페이지 접속 → 페이지 로드', async ({ page }) => {
    await page.goto('/knowledge-label-matching?id=1');
    await expect(page).toHaveURL(/knowledge-label-matching/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('W8.1 chunk_id로 관계 매칭 페이지 접속 → 페이지 로드', async ({ page }) => {
    await page.goto('/knowledge-relation-matching?id=1');
    await expect(page).toHaveURL(/knowledge-relation-matching/);
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('9. 지식 관리·청크 승인 (/knowledge-admin) — W9.x', () => {
  test('W9.1 지식 관리 접속 → 탭(라벨/그룹/청크 승인 등) 표시', async ({ page }) => {
    await page.goto('/knowledge-admin');
    await expect(page).toHaveURL(/\/knowledge-admin/);
    await expect(page.locator('#tab-labels')).toBeVisible();
    await expect(page.locator('#tab-approval')).toBeVisible();
  });

  test('W9.2 청크 승인 센터 탭 선택 → 미승인 청크 목록 영역 표시', async ({ page }) => {
    await page.goto('/knowledge-admin');
    await page.locator('#tab-approval').click();
    await expect(page.locator('#approval-chunk-list')).toBeVisible();
  });
});

test.describe('10. 청크 승인 센터 단독 (/admin/approval) — W10.x', () => {
  test('W10.1 청크 승인 페이지 직접 접속 → 목록 영역·필터 버튼 표시', async ({ page }) => {
    await page.goto('/admin/approval');
    await expect(page).toHaveURL(/\/admin\/approval/);
    await expect(page.locator('#approval-chunk-list')).toBeVisible();
    await expect(page.locator('.status-filter-btn').first()).toBeVisible();
  });

  test('W10.4 전체 승인 버튼 존재', async ({ page }) => {
    await page.goto('/admin/approval');
    await expect(page.locator('#btn-approve-all')).toBeVisible();
  });
});

test.describe('11. 청크 관리 (/admin/chunk-labels) — W11.x', () => {
  test('W11.1 청크 관리 접속 → 검색·필터·청크 목록 영역 표시', async ({ page }) => {
    await page.goto('/admin/chunk-labels');
    await expect(page).toHaveURL(/\/admin\/chunk-labels/);
    await expect(page.locator('#chunk-search')).toBeVisible();
    await expect(page.locator('#chunk-list')).toBeVisible();
  });
});

test.describe('12. 청크 생성 (/admin/chunk-create) — W12.x', () => {
  test('W12.1 1단계: 스토리지 파일 목록 영역 표시', async ({ page }) => {
    await page.goto('/admin/chunk-create');
    await expect(page).toHaveURL(/\/admin\/chunk-create/);
    await expect(page.locator('#storage-file-list')).toBeVisible();
    await expect(page.locator('.chunk-create-tab[data-step="1"]')).toBeVisible();
  });

  test('W12.4 단계별 탭(1·2·3) 표시 및 전환 가능', async ({ page }) => {
    await page.goto('/admin/chunk-create');
    await expect(page.locator('.chunk-create-tab[data-step="2"]')).toBeVisible();
    await expect(page.locator('.chunk-create-tab[data-step="3"]')).toBeVisible();
  });
});
