/**
 * Reasoning Lab — Visualization 렌더 레이어
 * 모드별 시각화(Mermaid, 리스크, 로드맵, 타임라인) 담당
 * 의존성: reason-model(MODE_VIZ_TITLES), utils(escapeHtml), reason-viz-loader
 * IIFE 패턴, window.ReasonRenderViz 으로 export
 */
(function () {
  "use strict";

  var MODE_VIZ_TITLES =
    (window.ReasonModel && window.ReasonModel.MODE_VIZ_TITLES) ||
    {
      design_explain: "📐 설계/배경 시각화",
      risk_review: "⚠️ 리스크 매트릭스",
      next_steps: "🚀 다음 단계 로드맵",
      history_trace: "📜 히스토리 타임라인",
    };

  function esc(s) {
    return typeof escapeHtml === "function" ? escapeHtml(s) : String(s).replace(/[&<>"']/g, function (c) {
      var m = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
      return m[c] || c;
    });
  }

  // ---------- 모드별 시각화 ----------
  function renderModeViz(result, mode) {
    var container = document.getElementById("mode-viz-container");
    var titleEl = document.getElementById("mode-viz-title");
    if (!container || !titleEl) return;
    var vizTitle = MODE_VIZ_TITLES[mode] || "시각화";
    titleEl.innerHTML = '<span class="section-badge">2</span> ' + esc(vizTitle);
    var panel = null;
    switch (mode) {
      case "design_explain":
        panel = document.getElementById("viz-design-explain");
        if (panel) { renderDesignExplainViz(result, panel); panel.style.display = "block"; }
        break;
      case "risk_review":
        panel = document.getElementById("viz-risk-review");
        if (panel) { renderRiskReviewViz(result, panel); panel.style.display = "block"; }
        break;
      case "next_steps":
        panel = document.getElementById("viz-next-steps");
        if (panel) { renderNextStepsViz(result, panel); panel.style.display = "block"; }
        break;
      case "history_trace":
        panel = document.getElementById("viz-history-trace");
        if (panel) { renderHistoryTraceViz(result, panel); panel.style.display = "block"; }
        break;
      default:
        break;
    }
    if (panel && panel.innerHTML.trim()) {
      container.style.display = "block";
    }
  }

  function renderDesignExplainViz(result, container) {
    var text = [result.answer || "", (result.reasoning_steps || []).join("\n")].join("\n");
    var mermaidMatch = text.match(/```\s*mermaid\s*([\s\S]*?)```/i);
    if (!mermaidMatch) mermaidMatch = text.match(/```\s*mermaid\s*([\s\S]+)/i);
    if (!mermaidMatch && /flowchart|graph\s+(LR|TD|TB|BT)|sequenceDiagram|classDiagram/.test(text)) {
      var start = text.search(/(?:^|\n)\s*(flowchart|graph\s+(?:LR|TD|TB|BT)|sequenceDiagram|classDiagram)/im);
      if (start >= 0) {
        var rest = text.slice(start).trim();
        var endMatch = rest.match(/\n```\s*$/m);
        var code = endMatch ? rest.slice(0, endMatch.index).trim() : rest.trim();
        if (code.length > 10) mermaidMatch = [null, code];
      }
    }
    if (!mermaidMatch) {
      container.innerHTML =
        '<p class="viz-fallback">Mermaid 다이어그램을 표시하려면 LLM 응답에 <code>```mermaid ... ```</code> 블록을 포함해 주세요.</p>';
      return;
    }
    var mermaidCode = mermaidMatch[1].trim();
    var id = "mermaid-viz-" + Date.now();
    container.innerHTML = '<div class="mermaid-viz-wrapper"><div id="' + id + '" class="mermaid-viz"></div></div>';
    if (window.ReasonVizLoader) {
      window.ReasonVizLoader.renderMermaidDiagram(id, mermaidCode);
    } else {
      var target = document.getElementById(id);
      if (target) target.innerHTML = '<pre class="mermaid-code">' + esc(mermaidCode) + "</pre>";
    }
  }

  function renderRiskReviewViz(result, container) {
    var steps = result.reasoning_steps || [];
    var items = steps.map(function (s, i) {
      return {
        label: (s || "").substring(0, 60) + ((s || "").length > 60 ? "…" : ""),
        severity: Math.min(5, (i % 5) + 1),
        likelihood: Math.min(5, ((i * 2) % 5) + 1),
      };
    });
    if (items.length === 0 && result.answer) {
      items.push({ label: (result.answer || "").substring(0, 80) + "…", severity: 3, likelihood: 3 });
    }
    var severityLabels = ["1 낮음", "2", "3", "4", "5 높음"];
    var likelihoodLabels = ["1 낮음", "2", "3", "4", "5 높음"];
    var table = '<table class="risk-matrix-table"><thead><tr><th></th>';
    for (var l = 0; l < 5; l++) table += "<th>" + likelihoodLabels[l] + "</th>";
    table += "</tr></thead><tbody>";
    var cellMap = {};
    items.forEach(function (it) {
      var key = (it.severity - 1) * 5 + (it.likelihood - 1);
      if (!cellMap[key]) cellMap[key] = [];
      cellMap[key].push(it.label);
    });
    for (var s = 5; s >= 1; s--) {
      table += "<tr><th>" + severityLabels[s - 1] + "</th>";
      for (var ll = 1; ll <= 5; ll++) {
        var key = (s - 1) * 5 + (ll - 1);
        var labels = cellMap[key] || [];
        var riskClass = s >= 4 && ll >= 4 ? "high" : s >= 3 && ll >= 3 ? "medium" : "low";
        table +=
          '<td class="risk-cell ' + riskClass + '">' +
          labels.map(function (lb) { return '<span class="risk-item">' + esc(lb) + "</span>"; }).join("") +
          "</td>";
      }
      table += "</tr>";
    }
    table += "</tbody></table>";
    container.innerHTML =
      '<div class="risk-matrix-wrapper"><p class="risk-matrix-caption">심각도(행) × 가능성(열)</p>' + table + "</div>";
    renderRiskImpactGraph(result, container);
  }

  function renderRiskImpactGraph(result, container) {
    var relations = result.relations || [];
    if (relations.length === 0) return;
    var nodeMap = {};
    var nodeIdx = 0;
    function nodeId(label) {
      if (!nodeMap[label]) nodeMap[label] = "R" + (nodeIdx++);
      return nodeMap[label];
    }
    function sanitize(s) {
      return (s || "").replace(/["\\]/g, "'").replace(/[\r\n]+/g, " ").replace(/[|[\]{}()#<>]/g, " ").replace(/\s+/g, " ").trim().substring(0, 35);
    }
    var lines = ["graph LR"];
    relations.forEach(function (rel) {
      var src = sanitize(rel.source);
      var tgt = sanitize(rel.target);
      var typ = sanitize(rel.type || "관련");
      if (!src || !tgt) return;
      lines.push("    " + nodeId(src) + '["' + src + '"]' + " -->|" + typ + "| " + nodeId(tgt) + '["' + tgt + '"]');
    });
    if (lines.length <= 1) return;
    var mermaidCode = lines.join("\n");
    var id = "impact-graph-" + Date.now();
    var html =
      '<div class="risk-impact-graph"><h4 class="risk-impact-title">영향 관계 그래프</h4>' +
      '<div class="mermaid-viz-wrapper"><div id="' + id + '" class="mermaid-viz"></div></div></div>';
    container.insertAdjacentHTML("beforeend", html);
    if (window.ReasonVizLoader) {
      window.ReasonVizLoader.renderMermaidDiagram(id, mermaidCode);
    } else {
      var target = document.getElementById(id);
      if (target) target.innerHTML = '<pre class="mermaid-code">' + esc(mermaidCode) + "</pre>";
    }
  }

  function renderNextStepsViz(result, container) {
    var steps = result.reasoning_steps || [];
    if (steps.length === 0 && result.answer) {
      (result.answer || "").split(/\n+/).filter(Boolean).forEach(function (p) {
        if (p.trim()) steps.push(p.trim());
      });
    }
    if (steps.length === 0) {
      container.innerHTML = '<p class="viz-fallback">다음 단계 항목이 없습니다.</p>';
      return;
    }
    var html = '<div class="roadmap-timeline">';
    steps.forEach(function (step, i) {
      html += '<div class="roadmap-item"><div class="roadmap-phase">' + (i + 1) + '</div><div class="roadmap-content">' + esc(step || "") + "</div></div>";
    });
    html += "</div>";
    container.innerHTML = html;
  }

  function renderHistoryTraceViz(result, container) {
    var steps = result.reasoning_steps || [];
    var items = steps.length ? steps : (result.answer || "").split(/\n+/).filter(Boolean);
    if (items.length === 0) {
      container.innerHTML = '<p class="viz-fallback">타임라인 이벤트가 없습니다.</p>';
      return;
    }
    var html = '<div class="history-timeline">';
    items.forEach(function (item) {
      html += '<div class="history-timeline-item"><div class="history-timeline-marker"></div><div class="history-timeline-content">' + esc(String(item).trim()) + "</div></div>";
    });
    html += "</div>";
    container.innerHTML = html;
    renderBeforeAfterComparison(result, container);
  }

  function renderBeforeAfterComparison(result, container) {
    var text = result.answer || "";
    var steps = result.reasoning_steps || [];
    var combined = text + "\n" + steps.join("\n");
    var lines = combined.split("\n").filter(function (l) { return l.trim(); });
    var beforeItems = [];
    var afterItems = [];
    var currentSection = null;
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (/^(?:이전|변경\s*전|기존|과거|Before)\s*[:：]/i.test(line)) {
        currentSection = "before";
        var content = line.replace(/^(?:이전|변경\s*전|기존|과거|Before)\s*[:：]\s*/i, "").trim();
        if (content) beforeItems.push(content);
      } else if (/^(?:이후|변경\s*후|개선|현재|After)\s*[:：]/i.test(line)) {
        currentSection = "after";
        var content = line.replace(/^(?:이후|변경\s*후|개선|현재|After)\s*[:：]\s*/i, "").trim();
        if (content) afterItems.push(content);
      } else if (currentSection === "before") {
        beforeItems.push(line);
      } else if (currentSection === "after") {
        afterItems.push(line);
      }
    }
    if (beforeItems.length === 0 && afterItems.length === 0) {
      var timelineItems = steps.length > 0 ? steps.filter(function (s) { return s && s.trim(); }) : [];
      if (timelineItems.length >= 4) {
        var mid = Math.ceil(timelineItems.length / 2);
        beforeItems = timelineItems.slice(0, mid);
        afterItems = timelineItems.slice(mid);
      }
    }
    if (beforeItems.length === 0 && afterItems.length === 0) return;
    var html =
      '<div class="before-after-comparison"><h4 class="before-after-title">Before / After 비교</h4>' +
      '<div class="before-after-panels"><div class="ba-panel ba-before"><div class="ba-panel-header">이전 (Before)</div><div class="ba-panel-body">';
    beforeItems.forEach(function (item) { html += '<div class="ba-item">' + esc(item) + "</div>"; });
    html += '</div></div><div class="ba-arrow-col"><span class="ba-arrow-icon">→</span></div>' +
      '<div class="ba-panel ba-after"><div class="ba-panel-header">이후 (After)</div><div class="ba-panel-body">';
    afterItems.forEach(function (item) { html += '<div class="ba-item">' + esc(item) + "</div>"; });
    html += "</div></div></div></div>";
    container.insertAdjacentHTML("beforeend", html);
  }

  function clearModeViz() {
    var container = document.getElementById("mode-viz-container");
    if (container) container.style.display = "none";
    ["viz-design-explain", "viz-risk-review", "viz-next-steps", "viz-history-trace"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) { el.innerHTML = ""; el.style.display = "none"; }
    });
    if (window.__riskReviewChart) {
      try { window.__riskReviewChart.destroy(); } catch (e) {}
      window.__riskReviewChart = null;
    }
  }

  window.ReasonRenderViz = {
    renderModeViz: renderModeViz,
    clearModeViz: clearModeViz,
  };
})();
