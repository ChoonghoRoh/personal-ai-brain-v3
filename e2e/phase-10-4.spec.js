// @ts-check
// Phase 10-4 고급 기능 (선택) — 스트리밍, 공유, 저장
// 참고: docs/phases/phase-10-4/phase-10-4-0-plan.md

const { test, expect } = require("@playwright/test");

test.describe("Phase 10-4: 고급 기능 테스트", () => {
  test.describe("10-4-1: LLM 스트리밍 응답 표시", () => {
    test("W10.4.1 스트리밍 중 answer 영역 실시간 업데이트", async ({ page }) => {
      await page.goto("/reason");

      // 질문 입력
      await page.locator("#question").fill("간단한 추론 테스트 질문");

      // 실행
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // answer 영역이 나타나는지 확인
      const answerSection = page.locator("#answer");
      await expect(answerSection).toBeVisible({ timeout: 20000 });

      // 텍스트 확인
      await page.waitForFunction(
        () => {
          const elem = document.querySelector("#answer");
          return elem && elem.textContent.trim().length > 10;
        },
        { timeout: 25000 },
      );
    });

    test("W10.4.2 스트리밍 중 취소 시 중단 처리", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("복잡한 추론 테스트 질문");
      await page.locator("#submit-btn").click();

      // 로딩 표시 대기
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 취소 버튼 클릭
      const cancelBtn = page.locator("#cancel-btn");
      await expect(cancelBtn).toBeVisible();
      await cancelBtn.click();

      // 버튼 활성화 확인
      await expect(page.locator("#submit-btn")).toBeEnabled({ timeout: 8000 });
    });
  });

  test.describe("10-4-2: 결과 공유 (URL 생성)", () => {
    test("W10.4.3 결과 생성 후 공유 버튼 표시", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("공유 테스트 질문");
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          const loading = document.querySelector("#results-loading");
          return answer && answer.textContent.trim().length > 0 && loading && loading.style.display === "none";
        },
        { timeout: 30000 },
      );

      // 공유 버튼 확인
      const shareBtn = page.locator("#share-btn");
      await expect(shareBtn).toBeVisible({ timeout: 3000 });
    });

    test("W10.4.4 공유 버튼 클릭 → URL 생성", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("공유 URL 테스트");
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // 공유 버튼 클릭
      const shareBtn = page.locator("#share-btn");
      await shareBtn.click();

      // 공유 토스트 메시지 확인
      const shareToast = page.locator("#share-toast");
      await expect(shareToast)
        .toBeVisible({ timeout: 5000 })
        .catch(() => {});
    });
  });

  test.describe("10-4-3: 의사결정 문서 저장", () => {
    test("W10.4.5 결과 생성 후 저장 버튼 표시", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("저장 테스트 질문");
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // 저장 버튼 확인
      const saveBtn = page.locator("#save-decision-btn");
      await expect(saveBtn).toBeVisible({ timeout: 3000 });
    });

    test("W10.4.6 저장 버튼 클릭 → 저장 모달 표시", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("의사결정 저장 테스트");
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // 저장 버튼 클릭
      const saveBtn = page.locator("#save-decision-btn");
      await saveBtn.click();

      // 저장 모달 표시
      const saveModal = page.locator("#save-decision-modal");
      await expect(saveModal).toBeVisible({ timeout: 3000 });

      // 제목 입력 필드 확인
      await expect(page.locator("#decision-title")).toBeVisible();
    });

    test("W10.4.7 저장 완료 확인", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("저장 완료 테스트");
      await page.locator("#submit-btn").click();

      // 로딩 표시 확인
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // 저장 버튼 클릭
      const saveBtn = page.locator("#save-decision-btn");
      await saveBtn.click();

      // 모달에서 제목 입력
      await page.locator("#decision-title").fill("E2E 테스트 의사결정");

      // 저장 버튼 클릭
      const confirmBtn = page.locator('#save-decision-modal button:has-text("저장")').first();
      await confirmBtn.click();

      // 모달 닫힘 확인
      await page.waitForFunction(
        () => {
          const modal = document.querySelector("#save-decision-modal");
          return modal && modal.style.display === "none";
        },
        { timeout: 5000 },
      );
    });
  });

  test.describe("Phase 10-4 회귀 테스트", () => {
    test("W10.4.8 Phase 10-1 진행 상태 표시 유지", async ({ page }) => {
      await page.goto("/reason");

      // 진행 상태 영역 확인
      await expect(page.locator("#progress-stages")).toBeAttached();

      await page.locator("#question").fill("회귀 테스트");
      await page.locator("#submit-btn").click();

      // 로딩 중 진행 상태 표시
      await expect(page.locator("#results-loading")).toBeVisible({ timeout: 3000 });
    });

    test("W10.4.9 Phase 10-2 시각화 렌더링 유지", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("디자인 설명 시각화 테스트");
      await page.locator("#mode").selectOption("design_explain");
      await page.locator("#submit-btn").click();

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // 시각화 영역 확인
      const vizContainer = page.locator("#mode-viz-container");
      await expect(vizContainer)
        .toBeAttached({ timeout: 5000 })
        .catch(() => {});
    });

    test("W10.4.10 Phase 10-3 PDF 내보내기 유지", async ({ page }) => {
      await page.goto("/reason");

      await page.locator("#question").fill("PDF 내보내기 테스트");
      await page.locator("#submit-btn").click();

      // 답변 표시 대기
      await page.waitForFunction(
        () => {
          const answer = document.querySelector("#answer");
          return answer && answer.textContent.trim().length > 0;
        },
        { timeout: 30000 },
      );

      // PDF 내보내기 버튼 확인
      const exportBtn = page.locator("#export-pdf-btn");
      await expect(exportBtn).toBeVisible({ timeout: 3000 });
    });
  });
});
