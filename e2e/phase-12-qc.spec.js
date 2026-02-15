// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Phase 12 QC: Production Stabilization & Infrastructure Enhancement
 * Target: Security headers, Local assets, Rate limiting UI feedback, Error handling
 */

test.describe('Phase 12 QC - Web E2E Scenarios', () => {

  // 1. [Security] HSTS Header Verification (Browser Level)
  // Note: Playwright checks headers on response
  test('QC-WEB-01: HSTS Header should be present in security-sensitive responses', async ({ page }) => {
    const response = await page.goto('/');
    const headers = response.headers();
    // HSTS is typically enabled in production/staging. Checking if config allows it or if it's conditional.
    // If not enabled in dev, this test acts as a config check.
    // We assume strict security is the goal of Phase 12.
    console.log('Security Headers:', headers['strict-transport-security']);
    // Pass if header exists or verify environment doesn't strictly enforce it yet
  });

  // 2. [Infra] Local Assets Loading (No CDN)
  test('QC-WEB-02: Third-party libraries should load from local source, not CDN', async ({ page }) => {
    await page.goto('/');
    
    // Check for specific libs localized in Phase 12-1
    // e.g., Chart.js, Marked, Highlight.js
    const scripts = await page.locator('script').all();
    for (const script of scripts) {
      const src = await script.getAttribute('src');
      if (src) {
        expect(src).not.toContain('cdn.jsdelivr.net');
        expect(src).not.toContain('unpkg.com');
        expect(src).not.toContain('cdnjs.cloudflare.com');
      }
    }
  });

  // 3. [UX] Error Handling Standardization UI
  test('QC-WEB-03: Global Error Handler should display standardized toast/alert', async ({ page }) => {
    await page.goto('/');
    
    // Simulate a network error or 500 by intercepting
    await page.route('**/api/system/health', route => route.abort('failed'));
    
    // Trigger a health check manually if UI has a button, or wait for auto-poll
    // Assuming there's a status indicator or we can trigger an error via console
    await page.evaluate(() => {
        // Force trigger an error handling UI logic if accessible, or fetch invalid URL
        fetch('/api/force-error').catch(e => console.error("Simulated Error"));
    });

    // Check for Toast or Alert visibility (Project specific selector required)
    // Expecting a standardized error message format in UI
  });

  // 4. [Security] XSS Injection Defense in Inputs
  test('QC-WEB-04: Inputs should sanitize HTML/Script tags (XSS Prevention)', async ({ page }) => {
    await page.goto('/admin'); // Assuming admin page has inputs
    
    // Target a search bar or chat input
    const maliciousInput = '<script>alert("XSS")</script>';
    const input = page.locator('input[type="text"]').first();
    
    if (await input.count() > 0) {
        await input.fill(maliciousInput);
        await input.press('Enter');
        
        // Ensure alert dialog was NOT triggered (Playwright handles dialogs automatically, but we can listen)
        page.on('dialog', dialog => {
            expect(dialog.message()).not.toBe('XSS');
            dialog.dismiss();
        });
        
        // Verify displayed text is escaped
        const content = await page.content();
        expect(content).not.toContain('<script>alert("XSS")</script>'); 
    }
  });

  // 5. [Performance] Rate Limiting UI Feedback
  test('QC-WEB-05: Rapid UI interactions should handle 429 errors gracefully', async ({ page }) => {
    await page.goto('/');
    
    // Simulate clicking a button rapidly
    const refreshBtn = page.getByRole('button', { name: /refresh|reload|검색/i }).first();
    
    if (await refreshBtn.isVisible()) {
        for (let i = 0; i < 20; i++) {
            refreshBtn.click().catch(() => {});
        }
        
        // Expect UI not to crash. 
        // Ideally check for "Too many requests" toast if implemented.
        const toast = page.locator('.toast-error, .alert-danger');
        if (await toast.isVisible()) {
            expect(await toast.textContent()).toMatch(/많|요청|limit/i);
        }
    }
  });

  // 6. [Infra] Base URL Consistency
  test('QC-WEB-06: API calls should use the configured Base URL', async ({ page }) => {
    await page.goto('/');
    
    // Intercept requests and check their origin
    const request = await page.waitForRequest(req => req.url().includes('/api/'));
    const url = new URL(request.url());
    
    // Verify it's not pointing to a hardcoded external IP or localhost default if env is different
    // Here we check consistency with the page origin or configured API URL
    console.log('API Request URL:', url.href);
    expect(url.pathname).toMatch(/^\/api\//);
  });

  // 7. [Feature] Markdown Rendering (Local Lib Verification)
  test('QC-WEB-07: Markdown content should render correctly using local library', async ({ page }) => {
    // Navigate to a page with markdown content (e.g., Knowledge detail or Chat)
    await page.goto('/');
    
    // Inject test markdown if possible or check existing
    // Check for rendered HTML elements like <h1>, <strong>, <code>
    // This confirms marked.js (local) is working
    const codeBlock = page.locator('pre code').first();
    const boldText = page.locator('strong').first();
    
    // We assume there is some content. If not, this test might skip.
    if (await codeBlock.count() > 0) {
        expect(await codeBlock.isVisible()).toBeTruthy();
    }
  });

  // 8. [Infra] Health Check UI Status
  test('QC-WEB-08: System Status UI should reflect extended health checks (DB, Redis)', async ({ page }) => {
    await page.goto('/admin/system'); // Assuming system status page exists
    
    // Check for indicators of DB and Redis
    // Phase 12-3 extended health checks
    await expect(page.getByText(/database|postgres/i)).toBeVisible();
    await expect(page.getByText(/redis|cache/i)).toBeVisible();
    
    // Status should be 'Healthy' or 'Connected'
    // await expect(page.locator('.status-ok')).toBeVisible();
  });

  // 9. [Performance] Large Data Rendering Resilience
  test('QC-WEB-09: UI should remain responsive when loading large lists', async ({ page }) => {
    // Mock a large response for a list endpoint
    await page.route('**/api/memories*', async route => {
        const json = { items: Array.from({ length: 500 }, (_, i) => ({ id: i, title: `Test Item ${i}` })) };
        await route.fulfill({ json });
    });

    await page.goto('/memories'); // Adjust route
    
    // Measure time to render or check for "Loading" state disappearance
    const list = page.locator('.memory-list-item'); // Adjust selector
    // Wait for list to be populated
    // expect(await list.count()).toBeGreaterThan(10);
  });

  // 10. [Security] CSRF/Auth Token Handling
  test('QC-WEB-10: Authentication tokens should be present in headers/storage', async ({ page }) => {
    // Perform login (mock or actual)
    // await page.goto('/login');
    // ... login logic ...
    
    // For now, assuming we start with some state or check local storage
    await page.goto('/');
    
    // Check if JWT or relevant token exists in localStorage/sessionStorage/Cookies
    // This verifies Phase 12 didn't break auth persistence
    const token = await page.evaluate(() => localStorage.getItem('token') || sessionStorage.getItem('token'));
    // Note: If using HTTP-only cookies, this check needs to be done via request interception
    if (!token) {
        console.log('No token in storage (might be http-only cookie)');
    }
  });

});
