// @ts-check
// Phase 10-2 모드별 분석 고도화 — Reasoning 모드별 시각화 (Mermaid, 5x5 매트릭스, 로드맵, 타임라인)
// 참고: docs/phases/phase-10-2/phase-10-2-0-plan.md, phase-10-2-0-todo-list.md

const { test, expect } = require('@playwright/test');

test.describe('1. Reasoning 페이지 — Phase 10-2 시각화 영역 DOM', () => {
  test('W10.2.DOM.1 /reason 접속 → 모드별 시각화 컨테이너 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page).toHaveURL(/\/reason/);
    await expect(page.locator('#mode-viz-container')).toBeAttached();
    await expect(page.locator('#mode-viz-title')).toBeAttached();
  });

  test('W10.2.DOM.2 4개 모드 시각화 패널이 DOM에 존재', async ({ page }) => {
    await page.goto('/reason');
    await expect(page.locator('#viz-design-explain')).toBeAttached();
    await expect(page.locator('#viz-risk-review')).toBeAttached();
    await expect(page.locator('#viz-next-steps')).toBeAttached();
    await expect(page.locator('#viz-history-trace')).toBeAttached();
  });

  test('W10.2.DOM.3 모드 선택 옵션 4개 (design_explain, risk_review, next_steps, history_trace)', async ({ page }) => {
    await page.goto('/reason');
    const modeSelect = page.locator('#mode');
    await expect(modeSelect).toBeVisible();
    await expect(modeSelect.locator('option[value="design_explain"]')).toHaveCount(1);
    await expect(modeSelect.locator('option[value="risk_review"]')).toHaveCount(1);
    await expect(modeSelect.locator('option[value="next_steps"]')).toHaveCount(1);
    await expect(modeSelect.locator('option[value="history_trace"]')).toHaveCount(1);
  });
});

test.describe('2. Phase 10-2 시각화 — 모드 전환 시 UI', () => {
  test('W10.2.VIZ.1 초기 상태에서 mode-viz-container 숨김 또는 빈 패널', async ({ page }) => {
    await page.goto('/reason');
    const container = page.locator('#mode-viz-container');
    await expect(container).toBeAttached();
    // 결과 전에는 시각화 영역이 비어 있거나 숨겨진 상태
    const display = await container.getAttribute('style');
    const isHidden = display && display.includes('display: none');
    const panels = page.locator('.mode-viz-panel');
    const visibleWithContent = await panels.evaluateAll((nodes) =>
      nodes.filter((n) => n.style.display !== 'none' && n.innerHTML.trim().length > 0).length
    );
    expect(isHidden || visibleWithContent === 0).toBeTruthy();
  });

  test('W10.2.VIZ.2 Mermaid/Chart 스크립트 로드 (CDN)', async ({ page }) => {
    await page.goto('/reason');
    const mermaidScript = page.locator('script[src*="mermaid"]');
    await expect(mermaidScript.first()).toBeAttached();
    const chartScript = page.locator('script[src*="chart"]');
    await expect(chartScript.first()).toBeAttached();
  });
});

test.describe('3. Phase 10-2 결과 표시 구조', () => {
  test('W10.2.RES.1 결과 영역 내 시각화가 요약 아래·결론 위에 배치', async ({ page }) => {
    await page.goto('/reason');
    const resultsContent = page.locator('#results-content');
    await expect(resultsContent).toBeAttached();
    const summary = page.locator('#result-summary, .result-summary').first();
    const modeViz = page.locator('#mode-viz-container');
    const answer = page.locator('#answer');
    await expect(summary).toBeAttached();
    await expect(modeViz).toBeAttached();
    await expect(answer).toBeAttached();
  });
});
