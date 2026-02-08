// @ts-check
// Phase 10-3 공통 결과 구조 + 시각화 통합 + PDF 내보내기
// 참고: docs/phases/phase-10-3/phase-10-3-0-plan.md

const { test, expect } = require("@playwright/test");

test.describe("1. Phase 10-3 공통 결과 구조 DOM", () => {
  test("W10.3.DOM.1 /reason 접속 → 결과 구조 섹션 DOM 존재", async ({ page }) => {
    await page.goto("/reason");
    await expect(page).toHaveURL(/\/reason/);

    // 결과 컨테이너
    await expect(page.locator("#results")).toBeAttached();
    await expect(page.locator("#results-content")).toBeAttached();

    // 요약/상세/시각화/인사이트 섹션
    await expect(page.locator(".result-section-summary")).toBeAttached();
    await expect(page.locator(".result-section-detail")).toBeAttached();
    await expect(page.locator("#mode-viz-container")).toBeAttached();
    await expect(page.locator("#recommendations-section")).toBeAttached();
  });

  test("W10.3.DOM.2 공통 결과 구조 내부 핵심 요소 존재", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator("#result-summary-text")).toBeAttached();
    await expect(page.locator("#result-summary")).toBeAttached();
    await expect(page.locator("#answer")).toBeAttached();
    await expect(page.locator("#reasoning-steps")).toBeAttached();
  });
});

test.describe("2. Phase 10-3 시각화 통합 구성", () => {
  test("W10.3.VIZ.1 시각화 패널 4개가 DOM에 존재", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator("#viz-design-explain")).toBeAttached();
    await expect(page.locator("#viz-risk-review")).toBeAttached();
    await expect(page.locator("#viz-next-steps")).toBeAttached();
    await expect(page.locator("#viz-history-trace")).toBeAttached();
  });

  test("W10.3.VIZ.2 시각화 로더 스크립트 로드", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator('script[src*="reason-viz-loader"]')).toBeAttached();
    await expect(page.locator('script[src*="mermaid"]')).toBeAttached();
    await expect(page.locator('script[src*="chart"]')).toBeAttached();
  });
});

test.describe("3. Phase 10-3 PDF 내보내기", () => {
  test("W10.3.PDF.1 PDF 내보내기 버튼 존재", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator("#export-pdf-btn")).toBeAttached();
  });

  test("W10.3.PDF.2 PDF 라이브러리 스크립트 로드", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator('script[src*="html2canvas"]')).toBeAttached();
    await expect(page.locator('script[src*="jspdf"]')).toBeAttached();
  });
});

test.describe("4. Phase 10-3 인사이트 영역 구성", () => {
  test("W10.3.INS.1 인사이트 탭/패널 구조 존재", async ({ page }) => {
    await page.goto("/reason");
    await expect(page.locator(".recommendations-toggles")).toBeAttached();
    await expect(page.locator("#related-chunks-panel")).toBeAttached();
    await expect(page.locator("#sample-questions-panel")).toBeAttached();
    await expect(page.locator("#suggested-labels-panel")).toBeAttached();
    await expect(page.locator("#explore-more-panel")).toBeAttached();
  });
});
