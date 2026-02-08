// @ts-check
// Phase 11-2 Admin CRUD API E2E 테스트
// 참고: docs/phases/phase-11-2/phase-11-2-0-plan.md
//       docs/webtest/phase-11-2/phase-11-2-webtest-execution-report.md

const { test, expect } = require("@playwright/test");

test.describe("Phase 11-2: Admin CRUD API 테스트", () => {
  test.describe("1. Schemas API — /api/admin/schemas", () => {
    test("1.1 GET /api/admin/schemas 목록 조회 → 200, items·total 반환", async ({ request }) => {
      const response = await request.get("/api/admin/schemas?limit=10");
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty("items");
      expect(data).toHaveProperty("total");
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(typeof data.total).toBe("number");
    });

    test("1.2 GET /api/admin/schemas 페이지네이션 → limit, offset 작동", async ({ request }) => {
      const response1 = await request.get("/api/admin/schemas?limit=2&offset=0");
      expect(response1.status()).toBe(200);
      const data1 = await response1.json();
      expect(data1.items.length).toBeLessThanOrEqual(2);

      const response2 = await request.get("/api/admin/schemas?limit=2&offset=2");
      expect(response2.status()).toBe(200);
      const data2 = await response2.json();
      // 페이지네이션 작동 확인 (첫 번째와 두 번째 페이지의 아이템이 다름)
      if (data1.items.length > 0 && data2.items.length > 0) {
        expect(data1.items[0].id).not.toBe(data2.items[0].id);
      }
    });
  });

  test.describe("2. Templates API — /api/admin/templates", () => {
    test("2.1 GET /api/admin/templates 목록 조회 → 200, items·total 반환", async ({ request }) => {
      const response = await request.get("/api/admin/templates?limit=10");
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty("items");
      expect(data).toHaveProperty("total");
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(data.total).toBeGreaterThanOrEqual(0);
    });

    test("2.2 GET /api/admin/templates 템플릿 데이터 구조 검증", async ({ request }) => {
      const response = await request.get("/api/admin/templates?limit=5");
      expect(response.status()).toBe(200);
      const data = await response.json();
      if (data.items.length > 0) {
        const template = data.items[0];
        expect(template).toHaveProperty("id");
        expect(template).toHaveProperty("name");
        expect(template).toHaveProperty("template_type");
        expect(template).toHaveProperty("status");
      }
    });
  });

  test.describe("3. Prompt Presets API — /api/admin/presets", () => {
    test("3.1 GET /api/admin/presets 목록 조회 → 200, items·total 반환", async ({ request }) => {
      const response = await request.get("/api/admin/presets?limit=10");
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty("items");
      expect(data).toHaveProperty("total");
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(data.total).toBeGreaterThanOrEqual(0);
    });

    test("3.2 GET /api/admin/presets 프리셋 데이터 구조 검증", async ({ request }) => {
      const response = await request.get("/api/admin/presets?limit=5");
      expect(response.status()).toBe(200);
      const data = await response.json();
      if (data.items.length > 0) {
        const preset = data.items[0];
        expect(preset).toHaveProperty("id");
        expect(preset).toHaveProperty("name");
        expect(preset).toHaveProperty("task_type"); // preset_type 대신 task_type
        expect(preset).toHaveProperty("status");
      }
    });
  });

  test.describe("4. RAG Profiles API — /api/admin/rag-profiles", () => {
    test("4.1 GET /api/admin/rag-profiles 목록 조회 → 200, items·total 반환", async ({ request }) => {
      const response = await request.get("/api/admin/rag-profiles?limit=10");
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty("items");
      expect(data).toHaveProperty("total");
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(data.total).toBeGreaterThanOrEqual(0);
    });

    test("4.2 GET /api/admin/rag-profiles RAG 프로필 데이터 구조 검증", async ({ request }) => {
      const response = await request.get("/api/admin/rag-profiles?limit=5");
      expect(response.status()).toBe(200);
      const data = await response.json();
      if (data.items.length > 0) {
        const profile = data.items[0];
        expect(profile).toHaveProperty("id");
        expect(profile).toHaveProperty("name");
        expect(profile).toHaveProperty("description");
        expect(profile).toHaveProperty("status");
      }
    });
  });

  test.describe("5. Policy Sets API — /api/admin/policy-sets", () => {
    test("5.1 GET /api/admin/policy-sets 목록 조회 → 200, items·total 반환", async ({ request }) => {
      const response = await request.get("/api/admin/policy-sets?limit=10");
      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty("items");
      expect(data).toHaveProperty("total");
      expect(Array.isArray(data.items)).toBeTruthy();
      expect(data.total).toBeGreaterThanOrEqual(0);
    });

    test("5.2 GET /api/admin/policy-sets 정책 세트 데이터 구조 검증", async ({ request }) => {
      const response = await request.get("/api/admin/policy-sets?limit=5");
      expect(response.status()).toBe(200);
      const data = await response.json();
      if (data.items.length > 0) {
        const policySet = data.items[0];
        expect(policySet).toHaveProperty("id");
        expect(policySet).toHaveProperty("name");
        expect(policySet).toHaveProperty("description");
        expect(policySet).toHaveProperty("is_active"); // status 대신 is_active
      }
    });
  });

  test.describe("6. API 공통 기능 검증", () => {
    test("6.1 잘못된 limit 값 → 적절한 에러 또는 기본값 처리", async ({ request }) => {
      const response = await request.get("/api/admin/templates?limit=-1");
      // 400 에러 또는 200 + 기본값 처리
      expect([200, 400, 422]).toContain(response.status());
    });

    test("6.2 없는 엔드포인트 → 404", async ({ request }) => {
      const response = await request.get("/api/admin/nonexistent");
      expect(response.status()).toBe(404);
    });

    test("6.3 모든 Admin API 엔드포인트 응답 시간 < 2초", async ({ request }) => {
      const endpoints = [
        "/api/admin/schemas?limit=5",
        "/api/admin/templates?limit=5",
        "/api/admin/presets?limit=5",
        "/api/admin/rag-profiles?limit=5",
        "/api/admin/policy-sets?limit=5",
      ];

      for (const endpoint of endpoints) {
        const start = Date.now();
        const response = await request.get(endpoint);
        const duration = Date.now() - start;
        expect(response.status()).toBe(200);
        expect(duration).toBeLessThan(2000);
      }
    });
  });
});
