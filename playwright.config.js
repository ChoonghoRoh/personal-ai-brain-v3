// @ts-check
// Web 사용자 테스트용 Playwright 설정.
// 가이드: docs/webtest/web-user-test-setup-guide.md

const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: 'e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    // ver3: docker-compose가 8001로 노출. BASE_URL 없으면 8001 사용
    baseURL: process.env.BASE_URL || 'http://localhost:8001',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // 테스트 전 백엔드 자동 기동이 필요하면 아래 주석을 해제하고, 환경에 맞게 command를 수정하세요. ver3: 8001
  // webServer: {
  //   command: 'docker-compose up -d && npx wait-on http://localhost:8001/docs',
  //   url: 'http://localhost:8001',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120_000,
  // },
});
