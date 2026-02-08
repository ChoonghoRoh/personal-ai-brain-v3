/**
 * Reasoning Lab — Viz Loader (Phase 10-3-2)
 * 시각화 라이브러리 로딩 상태 감지·에러 처리·폴백 일관화.
 * 의존성: 없음 (CDN 로드 이후 동작)
 */
(function () {
  "use strict";

  /** 라이브러리 상태 */
  var VIZ_STATUS = {
    mermaid: "pending",
    chartjs: "pending",
  };

  /** Mermaid 초기화 (1회) */
  function initMermaid() {
    if (typeof mermaid === "undefined") {
      VIZ_STATUS.mermaid = "unavailable";
      return false;
    }
    if (VIZ_STATUS.mermaid === "ready") return true;
    try {
      if (typeof mermaid.initialize === "function") {
        mermaid.initialize({
          startOnLoad: false,
          theme: document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "default",
          securityLevel: "loose",
        });
      }
      VIZ_STATUS.mermaid = "ready";
      return true;
    } catch (e) {
      console.warn("Mermaid 초기화 실패:", e);
      VIZ_STATUS.mermaid = "error";
      return false;
    }
  }

  /** Chart.js 가용 여부 확인 */
  function initChartJS() {
    if (typeof Chart === "undefined") {
      VIZ_STATUS.chartjs = "unavailable";
      return false;
    }
    VIZ_STATUS.chartjs = "ready";
    return true;
  }

  /**
   * Mermaid 다이어그램 렌더링 (공통)
   * @param {string} containerId - 렌더링 대상 DOM ID
   * @param {string} code - Mermaid 코드
   * @param {function} [onError] - 에러 콜백
   */
  function renderMermaidDiagram(containerId, code, onError) {
    var target = document.getElementById(containerId);
    if (!target) return;

    if (!initMermaid()) {
      target.innerHTML = '<pre class="mermaid-code viz-fallback-code">' + escViz(code) + "</pre>";
      return;
    }

    var svgId = containerId + "-svg-" + Date.now();
    if (typeof mermaid.render === "function") {
      mermaid
        .render(svgId, code)
        .then(function (out) {
          if (out && out.svg) {
            target.innerHTML = out.svg;
            if (typeof out.bindFunctions === "function") out.bindFunctions(target);
          } else {
            target.innerHTML = '<pre class="mermaid-code">' + escViz(code) + "</pre>";
          }
        })
        .catch(function (err) {
          var msg = "다이어그램 렌더링 실패: " + String(err.message || err);
          target.innerHTML =
            '<p class="viz-error">' +
            escViz(msg) +
            '</p><button type="button" class="viz-retry-btn" aria-label="다이어그램 재시도">재시도</button>';
          var retryBtn = target.querySelector(".viz-retry-btn");
          if (retryBtn) {
            retryBtn.addEventListener("click", function () {
              renderMermaidDiagram(containerId, code, onError);
            });
          }
          if (onError) onError(err);
        });
    } else {
      target.className += " mermaid";
      target.textContent = code;
      mermaid.run({ nodes: [target], suppressErrors: true }).catch(function (err) {
        var msg = "렌더링 실패: " + String(err.message || err);
        target.innerHTML =
          '<p class="viz-error">' +
          escViz(msg) +
          '</p><button type="button" class="viz-retry-btn" aria-label="다이어그램 재시도">재시도</button>';
        var retryBtn = target.querySelector(".viz-retry-btn");
        if (retryBtn) {
          retryBtn.addEventListener("click", function () {
            renderMermaidDiagram(containerId, code, onError);
          });
        }
        if (onError) onError(err);
      });
    }
  }

  /** 간단한 HTML 이스케이프 */
  function escViz(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  /** 시각화 상태 조회 */
  function getStatus() {
    return { mermaid: VIZ_STATUS.mermaid, chartjs: VIZ_STATUS.chartjs };
  }

  /** 다크 모드 전환 시 Mermaid 테마 재초기화 */
  function updateTheme(isDark) {
    if (typeof mermaid !== "undefined" && typeof mermaid.initialize === "function") {
      VIZ_STATUS.mermaid = "pending";
      mermaid.initialize({
        startOnLoad: false,
        theme: isDark ? "dark" : "default",
        securityLevel: "loose",
      });
      VIZ_STATUS.mermaid = "ready";
    }
  }

  window.ReasonVizLoader = {
    initMermaid: initMermaid,
    initChartJS: initChartJS,
    renderMermaidDiagram: renderMermaidDiagram,
    getStatus: getStatus,
    updateTheme: updateTheme,
  };
})();
