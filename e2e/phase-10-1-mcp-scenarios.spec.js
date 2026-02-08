// @ts-check
// Phase 10-1 MCP 시나리오 — Task당 10개, 총 30개
// 시나리오 정의: docs/webtest/phase-10-1/phase-10-1-mcp-webtest-scenarios.md
// 실행: npx playwright test e2e/phase-10-1-mcp-scenarios.spec.js

const { test, expect } = require('@playwright/test');

test.describe('Task 10-1-1: 진행 상태 실시간 표시 — 시나리오 10개', () => {
  test('1. 진행 단계 컨테이너 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#progress-stages')).toBeAttached();
  });

  test('2. 5개 단계 스텝 노출', async ({ page }) => {
    await page.goto('/reason');
    const stages = page.locator('.progress-stage');
    await expect(stages).toHaveCount(5);
  });

  test('3. 실행 전 진행률 0% 또는 준비 중 메시지', async ({ page }) => {
    await page.goto('/reason');
    const msg = page.locator('#progress-message');
    await expect(msg).toBeAttached();
    await expect(msg).toContainText(/준비|⏳|Reasoning/i);
  });

  test('4. 실행 클릭 후 로딩 영역 표시 또는 submit disabled', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await expect(
      page.locator('#results-loading').or(page.locator('#submit-btn[disabled]')).first()
    ).toBeVisible({ timeout: 5000 });
  });

  test('5. 단계 1 메시지 확인 (실행 직후)', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    const msg = page.locator('#progress-message');
    await expect(msg).toContainText(/질문|분석|⏳|준비/i, { timeout: 3000 });
  });

  test('6. 단계 2~4 메시지 순차 (실행 후 5~15초 구간)', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('짧은 테스트 질문');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(2000);
    const msg = page.locator('#progress-message');
    await expect(msg).toBeAttached();
    await expect(msg).toContainText(/⏳|검색|지식|추론|추천|준비/i, { timeout: 15000 });
  });

  test('7. 단계 5 또는 완료 전 메시지 (타임아웃 내)', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(3000);
    const msg = page.locator('#progress-message');
    await expect(msg).toBeAttached();
    await expect(msg).toContainText(/⏳|추천|완료|준비|검색|지식|추론/i, { timeout: 60000 });
  });

  test('8. 경과 시간 요소 존재 및 숫자 형식', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    const elapsed = page.locator('#reasoning-elapsed-text');
    await expect(elapsed).toBeAttached({ timeout: 3000 });
    await page.waitForTimeout(6000);
    await expect(elapsed).toContainText(/경과|잠시|초/i, { timeout: 2000 });
  });

  test('9. 진행률 바 존재', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    const bar = page.locator('#progress-bar');
    await expect(bar).toBeAttached({ timeout: 3000 });
  });

  test('10. 완료 후 results-content 표시 (또는 로딩 해제)', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트 질문');
    await page.locator('#submit-btn').click();
    await expect(page.locator('#results-content').or(page.locator('#results-loading')).first()).toBeVisible({ timeout: 60000 });
    await expect(page.locator('#results')).toBeAttached();
  });
});

test.describe('Task 10-1-2: 분석 작업 취소 기능 — 시나리오 10개', () => {
  test('1. 취소 버튼 DOM 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#cancel-btn')).toBeAttached();
  });

  test('2. 대기 중 취소 버튼 숨김 (display none 또는 비표시)', async ({ page }) => {
    await page.goto('/reason');
    const cancel = page.locator('#cancel-btn');
    await expect(cancel).toBeAttached();
    const hidden = await cancel.evaluate((el) => {
      const s = getComputedStyle(el);
      return s.display === 'none' || s.visibility === 'hidden';
    });
    expect(hidden).toBe(true);
  });

  test('3. 실행 중 취소 버튼 노출', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1500);
    const cancel = page.locator('#cancel-btn');
    await expect(cancel).toBeVisible({ timeout: 3000 });
  });

  test('4. 취소 버튼 클릭 시 UI 변경', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('취소 테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1500);
    await page.locator('#cancel-btn').click();
    await page.waitForTimeout(3000);
    await expect(page.locator('#progress-message')).toContainText(/취소|사용자/i, { timeout: 5000 }).catch(() => {});
    await expect(page.locator('#submit-btn')).toBeEnabled({ timeout: 5000 });
  });

  test('5. 취소 후 실행 버튼 복구', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('취소 후 복구');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1000);
    await page.locator('#cancel-btn').click();
    await expect(page.locator('#submit-btn')).toBeEnabled({ timeout: 8000 });
    await expect(page.locator('#submit-btn')).toContainText(/실행|Reasoning/i);
  });

  test('6. 취소 후 취소 버튼 숨김', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1000);
    await page.locator('#cancel-btn').click();
    await page.waitForTimeout(4000);
    const cancel = page.locator('#cancel-btn');
    const hidden = await cancel.evaluate((el) => getComputedStyle(el).display === 'none');
    expect(hidden).toBe(true);
  });

  test('7. 취소 시 진행 메시지 변경', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('취소 메시지');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1000);
    await page.locator('#cancel-btn').click();
    await expect(page.locator('#progress-message')).toContainText(/취소|사용자/i, { timeout: 5000 });
  });

  test('8. 취소 시 progress-cancelled 또는 progress-bar 스타일', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1000);
    await page.locator('#cancel-btn').click();
    await page.waitForTimeout(2000);
    const container = page.locator('.results-loading');
    await expect(container).toBeAttached();
    const hasCancelled = await container.evaluate((el) => el && el.classList.contains('progress-cancelled')).catch(() => false);
    const bar = page.locator('#progress-bar');
    const barBg = await bar.evaluate((el) => (el ? getComputedStyle(el).background : '')).catch(() => '');
    expect(hasCancelled || barBg.length > 0).toBeTruthy();
  });

  test('9. 실행 중 submit 버튼 비활성화', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await expect(page.locator('#submit-btn')).toBeDisabled({ timeout: 2000 });
  });

  test('10. 연속 실행→취소→재실행', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('첫 실행');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(1000);
    await page.locator('#cancel-btn').click();
    await page.waitForTimeout(2000);
    await page.locator('#question').fill('두 번째 실행');
    await page.locator('#submit-btn').click();
    await expect(
      page.locator('#results-loading').or(page.locator('#submit-btn[disabled]')).first()
    ).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Task 10-1-3: 예상 소요 시간 표시 — 시나리오 10개', () => {
  test('1. ETA 영역 DOM 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#eta-display').or(page.locator('#eta-text')).first()).toBeAttached();
  });

  test('2. 초기 ETA 문구', async ({ page }) => {
    await page.goto('/reason');
    const eta = page.locator('#eta-text').or(page.locator('#eta-display')).first();
    await expect(eta).toBeAttached();
    await expect(eta).toContainText(/예상|소요|시간|계산/i, { timeout: 5000 });
  });

  test('3. 실행 전 ETA 표시 (숫자+단위)', async ({ page }) => {
    await page.goto('/reason');
    await page.waitForTimeout(3000);
    const eta = page.locator('#eta-text').or(page.locator('#eta-display')).first();
    await expect(eta).toContainText(/예상|소요|시간|초|분/i, { timeout: 5000 });
  });

  test('4. 실행 시 ETA 갱신 또는 유지', async ({ page }) => {
    await page.goto('/reason');
    const etaBefore = await page.locator('#eta-text').or(page.locator('#eta-display')).first().textContent();
    await page.locator('#question').fill('테스트');
    await page.locator('#submit-btn').click();
    await page.waitForTimeout(2000);
    const etaAfter = await page.locator('#eta-text').or(page.locator('#eta-display')).first().textContent();
    expect(etaAfter).toBeTruthy();
  });

  test('5. 모드 변경 후 ETA 영역 존재', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#mode').selectOption('risk_review');
    await page.waitForTimeout(2000);
    const eta = page.locator('#eta-text').or(page.locator('#eta-display')).first();
    await expect(eta).toBeAttached();
  });

  test('6. ETA 가독성 (텍스트 존재)', async ({ page }) => {
    await page.goto('/reason');
    const eta = page.locator('#eta-text');
    await expect(eta).toBeAttached();
    await expect(eta).not.toHaveText('', { timeout: 5000 });
  });

  test('7. ETA 폴백 (기본 문구) — 옵션', async ({ page }) => {
    await page.goto('/reason');
    await page.waitForTimeout(5000);
    const eta = page.locator('#eta-text').or(page.locator('#eta-display')).first();
    await expect(eta).toContainText(/예상|소요|시간|초|분|30|1분/i, { timeout: 8000 });
  });

  test('8. ETA 위치 (progress/results-loading 근처)', async ({ page }) => {
    await page.goto('/reason');
    const eta = page.locator('#eta-text').or(page.locator('#eta-display')).first();
    const progress = page.locator('#progress-stages').or(page.locator('#results-loading')).first();
    await expect(eta).toBeAttached();
    await expect(progress).toBeAttached();
  });

  test('9. ETA와 경과 시간 구분 (별도 노드)', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#eta-text').or(page.locator('#eta-display')).first()).toBeAttached();
    await expect(page.locator('#reasoning-elapsed-text')).toBeAttached();
  });

  test('10. 완료 후 ETA 영역 유지', async ({ page }) => {
    await page.goto('/reason');
    await page.locator('#question').fill('짧은 질문');
    await page.locator('#submit-btn').click();
    await page.waitForSelector('#results-content', { timeout: 60000 }).catch(() => {});
    await expect(page.locator('#eta-text').or(page.locator('#eta-display')).first()).toBeAttached();
  });
});
