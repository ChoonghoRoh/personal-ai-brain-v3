// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Phase 13-4-1: 메뉴/페이지 접근 로그 테이블 도입 검증
 * 대상: /dashboard 접근 후 DB 로그 기록 여부 확인
 */

test.describe('Phase 13-4-1: 페이지 접근 로그 검증', () => {

  test('사용자 페이지 접근 시 로그가 DB에 기록된다', async ({ page, request }) => {
    // 1. 특정 페이지(/dashboard)에 접근
    console.log('Step 1: Accessing /dashboard');
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
    
    // 미들웨어가 DB에 기록할 시간을 잠시 기다림
    await page.waitForTimeout(1000);

    // 2. 접근 로그 API 호출하여 확인
    console.log('Step 2: Checking access logs via API');
    const response = await request.get('/api/system/statistics/access-logs?limit=5');
    expect(response.ok()).toBeTruthy();
    
    const logs = await response.json();
    expect(Array.isArray(logs)).toBeTruthy();
    expect(logs.length).toBeGreaterThan(0);

    // 3. 최신 로그 중 /dashboard 경로가 있는지 확인
    const latestLog = logs[0];
    console.log('Latest log:', latestLog);
    
    // 최신 로그가 /dashboard이거나, 상위 5개 중 하나가 /dashboard여야 함
    const hasDashboardLog = logs.some(log => log.path === '/dashboard');
    expect(hasDashboardLog).toBeTruthy();
    
    expect(latestLog).toHaveProperty('id');
    expect(latestLog).toHaveProperty('path');
    expect(latestLog).toHaveProperty('method', 'GET');
    expect(latestLog).toHaveProperty('status_code', 200);
    expect(latestLog).toHaveProperty('accessed_at');
  });

  test('Admin 설정 페이지 접근 로그 기록 확인', async ({ page, request }) => {
    // 1. Admin 설정 페이지 접근
    const testPath = '/admin/settings/templates';
    await page.goto(testPath);
    await page.waitForTimeout(1000);

    // 2. 로그 확인
    const response = await request.get('/api/system/statistics/access-logs?limit=10');
    const logs = await response.json();
    
    const hasAdminLog = logs.some(log => log.path === testPath);
    expect(hasAdminLog).toBeTruthy();
  });

  test('API 호출(/api/*)은 접근 로그에 기록되지 않아야 함', async ({ page, request }) => {
    // 1. 기존 로그 수 확인
    const initialRes = await request.get('/api/system/statistics/access-logs?limit=1');
    expect(initialRes.ok()).toBeTruthy();
    const initialLogs = await initialRes.json();
    const lastIdBefore = (Array.isArray(initialLogs) && initialLogs.length > 0) ? initialLogs[0].id : 0;

    // 2. API 호출 실행
    await request.get('/api/system/status');
    await page.waitForTimeout(1000);

    // 3. 로그 수에 변화가 없거나, 새로운 로그의 경로가 API가 아니어야 함
    const afterRes = await request.get('/api/system/statistics/access-logs?limit=5');
    expect(afterRes.ok()).toBeTruthy();
    const afterLogs = await afterRes.json();
    
    if (Array.isArray(afterLogs) && afterLogs.length > 0) {
        // 새 로그가 생겼다면 그 경로는 /api/로 시작하지 않아야 함
        const newLogs = afterLogs.filter(log => log.id > lastIdBefore);
        for (const log of newLogs) {
            expect(log.path).not.toMatch(/^\/api\//);
        }
    }
  });
});
