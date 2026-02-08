/**
 * Reasoning Lab — Render 레이어
 * 결과·시각화·추천 등 화면 그리기.
 * 의존성: reason-model(MODE_VIZ_TITLES), utils(escapeHtml)
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

  // ---------- 탭 ----------
  function switchContextTab(tab) {
    document.querySelectorAll(".context-tabs .tab-btn").forEach(function (btn) {
      btn.classList.remove("active");
      btn.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".context-content").forEach(function (content) {
      content.classList.remove("active");
    });
    if (tab === "chunks") {
      var first = document.querySelector(".context-tabs .tab-btn:first-child");
      if (first) { first.classList.add("active"); first.setAttribute("aria-selected", "true"); }
      var chunksEl = document.getElementById("context-chunks");
      if (chunksEl) chunksEl.classList.add("active");
    } else {
      var last = document.querySelector(".context-tabs .tab-btn:last-child");
      if (last) { last.classList.add("active"); last.setAttribute("aria-selected", "true"); }
      var docsEl = document.getElementById("context-documents");
      if (docsEl) docsEl.classList.add("active");
    }
  }

  // ---------- 결과 요약·결론·컨텍스트 ----------
  /** 답변에서 첫 문장(또는 첫 줄)을 추출해 요약 텍스트로 표시 */
  function renderSummaryText(result) {
    var briefEl = document.getElementById("result-summary-text");
    if (!briefEl) return;
    var answer = (result.answer || "").trim();
    if (!answer) { briefEl.style.display = "none"; return; }
    // 첫 문장 추출: 마침표·느낌표·물음표 또는 첫 줄바꿈 기준
    var firstSentence = answer.split(/(?<=[.!?。])\s|\n/)[0] || answer.substring(0, 120);
    if (firstSentence.length > 150) firstSentence = firstSentence.substring(0, 147) + "...";
    briefEl.textContent = firstSentence;
    briefEl.style.display = "block";
  }

  function renderSummary(result) {
    var chunks = result.context_chunks || [];
    var relations = result.relations || [];
    var uniqueDocs = new Set(chunks.map(function (c) { return c.document; }).filter(Boolean));
    var docCountEl = document.getElementById("summary-docs-count");
    var chunkCountEl = document.getElementById("summary-chunks-count");
    var relCountEl = document.getElementById("summary-relations-count");
    if (docCountEl) docCountEl.textContent = uniqueDocs.size;
    if (chunkCountEl) chunkCountEl.textContent = chunks.length;
    if (relCountEl) relCountEl.textContent = relations.length;
    renderSummaryText(result);
  }

  function renderConclusion(result) {
    var answerDiv = document.getElementById("answer");
    if (answerDiv) {
      answerDiv.textContent = result.answer || "답변을 생성할 수 없습니다.";
    }
  }

  function renderContextChunks(chunks) {
    var contextChunksDiv = document.getElementById("context-chunks");
    if (!contextChunksDiv) return;
    if (chunks.length > 0) {
      contextChunksDiv.innerHTML = chunks
        .map(function (chunk) {
          var metaParts = [];
          if (chunk.project) metaParts.push("<strong>" + esc(chunk.project) + "</strong>");
          if (chunk.project_id != null) metaParts.push("프로젝트 ID: " + chunk.project_id);
          metaParts.push(esc(chunk.document || "알 수 없음"));
          metaParts.push("청크 ID: " + (chunk.id || "N/A"));
          var labels = chunk.labels && chunk.labels.length ? chunk.labels : [];
          var labelsHtml = labels.length
            ? ' <span class="chunk-labels">' + labels.map(function (l) { return '<span class="chunk-label-tag">' + esc(l) + "</span>"; }).join(" ") + "</span>"
            : "";
          return (
            '<div class="chunk-item"><div class="chunk-meta">' +
            metaParts.join(" / ") +
            labelsHtml +
            '</div><div class="chunk-content">' +
            esc(chunk.content || "내용 없음") +
            "</div></div>"
          );
        })
        .join("");
    } else {
      contextChunksDiv.innerHTML = '<p style="color: #999;">사용된 컨텍스트 청크가 없습니다.</p>';
    }
  }

  function renderContextDocuments(chunks) {
    var contextDocumentsDiv = document.getElementById("context-documents");
    if (!contextDocumentsDiv) return;
    var documentMap = new Map();
    chunks.forEach(function (chunk) {
      if (chunk.document && !documentMap.has(chunk.document)) {
        documentMap.set(chunk.document, { name: chunk.document, project: chunk.project, chunks: [] });
      }
      if (chunk.document) {
        documentMap.get(chunk.document).chunks.push(chunk);
      }
    });
    if (documentMap.size > 0) {
      contextDocumentsDiv.innerHTML = Array.from(documentMap.values())
        .map(function (doc) {
          var docPath = doc.name.indexOf("brain/") === 0 ? doc.name : "brain/" + doc.name;
          return (
            '<div class="document-item"><div class="doc-info"><div class="doc-name">' +
            esc(doc.name) +
            '</div><div class="doc-meta">' +
            (doc.project ? "프로젝트: " + esc(doc.project) + " / " : "") +
            doc.chunks.length +
            "개 청크 사용됨</div></div>" +
            '<a href="/document/' +
            encodeURIComponent(docPath) +
            '" class="doc-btn" target="_blank">문서 열기 →</a></div>'
          );
        })
        .join("");
    } else {
      contextDocumentsDiv.innerHTML = '<p style="color: #999;">사용된 문서가 없습니다.</p>';
    }
  }

  function renderContext(chunks) {
    renderContextChunks(chunks);
    renderContextDocuments(chunks);
  }

  function renderSteps(steps) {
    var stepsDiv = document.getElementById("reasoning-steps");
    if (!stepsDiv) return;
    if (steps && steps.length > 0) {
      stepsDiv.innerHTML =
        "<ol>" +
        steps.map(function (step) { return "<li>" + esc(step || "단계 정보 없음") + "</li>"; }).join("") +
        "</ol>";
    } else {
      stepsDiv.innerHTML = '<p style="color: #999;">Reasoning 단계 정보가 없습니다.</p>';
    }
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
        if (panel) {
          renderDesignExplainViz(result, panel);
          panel.style.display = "block";
        }
        break;
      case "risk_review":
        panel = document.getElementById("viz-risk-review");
        if (panel) {
          renderRiskReviewViz(result, panel);
          panel.style.display = "block";
        }
        break;
      case "next_steps":
        panel = document.getElementById("viz-next-steps");
        if (panel) {
          renderNextStepsViz(result, panel);
          panel.style.display = "block";
        }
        break;
      case "history_trace":
        panel = document.getElementById("viz-history-trace");
        if (panel) {
          renderHistoryTraceViz(result, panel);
          panel.style.display = "block";
        }
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
      for (var l = 1; l <= 5; l++) {
        var key = (s - 1) * 5 + (l - 1);
        var labels = cellMap[key] || [];
        var riskClass = s >= 4 && l >= 4 ? "high" : s >= 3 && l >= 3 ? "medium" : "low";
        table +=
          '<td class="risk-cell ' +
          riskClass +
          '">' +
          labels.map(function (lb) { return '<span class="risk-item">' + esc(lb) + "</span>"; }).join("") +
          "</td>";
      }
      table += "</tr>";
    }
    table += "</tbody></table>";
    container.innerHTML =
      '<div class="risk-matrix-wrapper"><p class="risk-matrix-caption">심각도(행) × 가능성(열)</p>' + table + "</div>";

    // Phase 10-2-2: 영향 그래프 (선택)
    renderRiskImpactGraph(result, container);
  }

  /** 리스크 간 영향 관계를 Mermaid 그래프로 시각화 */
  function renderRiskImpactGraph(result, container) {
    var relations = result.relations || [];
    if (relations.length === 0) return;

    // Mermaid 노드 ID 매핑
    var nodeMap = {};
    var nodeIdx = 0;
    function nodeId(label) {
      if (!nodeMap[label]) nodeMap[label] = "R" + (nodeIdx++);
      return nodeMap[label];
    }
    function sanitize(s) {
      return (s || "")
        .replace(/["\\]/g, "'")
        .replace(/[\r\n]+/g, " ")
        .replace(/[|[\]{}()#<>]/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .substring(0, 35);
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
      '<div class="risk-impact-graph">' +
      '<h4 class="risk-impact-title">영향 관계 그래프</h4>' +
      '<div class="mermaid-viz-wrapper"><div id="' + id + '" class="mermaid-viz"></div></div>' +
      "</div>";
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
      html +=
        '<div class="roadmap-item"><div class="roadmap-phase">' +
        (i + 1) +
        '</div><div class="roadmap-content">' +
        esc(step || "") +
        "</div></div>";
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
    items.forEach(function (item, i) {
      html +=
        '<div class="history-timeline-item"><div class="history-timeline-marker"></div><div class="history-timeline-content">' +
        esc(String(item).trim()) +
        "</div></div>";
    });
    html += "</div>";
    container.innerHTML = html;

    // Phase 10-2-4: Before/After 비교 (선택)
    renderBeforeAfterComparison(result, container);
  }

  /** 히스토리 기반 Before/After 비교 패널 */
  function renderBeforeAfterComparison(result, container) {
    var text = result.answer || "";
    var steps = result.reasoning_steps || [];
    var combined = text + "\n" + steps.join("\n");
    var lines = combined.split("\n").filter(function (l) { return l.trim(); });

    var beforeItems = [];
    var afterItems = [];
    var currentSection = null;

    // 텍스트에서 Before/After 구간 파싱
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

    // 명시적 구간이 없으면 타임라인 항목을 전후 반으로 분할
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
      '<div class="before-after-comparison">' +
      '<h4 class="before-after-title">Before / After 비교</h4>' +
      '<div class="before-after-panels">' +
      '<div class="ba-panel ba-before"><div class="ba-panel-header">이전 (Before)</div><div class="ba-panel-body">';

    beforeItems.forEach(function (item) {
      html += '<div class="ba-item">' + esc(item) + "</div>";
    });

    html +=
      '</div></div>' +
      '<div class="ba-arrow-col"><span class="ba-arrow-icon">→</span></div>' +
      '<div class="ba-panel ba-after"><div class="ba-panel-header">이후 (After)</div><div class="ba-panel-body">';

    afterItems.forEach(function (item) {
      html += '<div class="ba-item">' + esc(item) + "</div>";
    });

    html += "</div></div></div></div>";
    container.insertAdjacentHTML("beforeend", html);
  }

  // ---------- 메인 진입: displayResults ----------
  function displayResults(result) {
    if (!result) {
      console.error("displayResults: result가 없습니다");
      return;
    }
    var chunks = result.context_chunks || [];
    var modeEl = document.getElementById("mode");
    var mode = (modeEl && modeEl.value) || "design_explain";
    renderSummary(result);
    renderModeViz(result, mode);
    renderConclusion(result);
    renderContext(chunks);
    renderSteps(result.reasoning_steps);
    if (result.recommendations) {
      displayRecommendations(result.recommendations);
    } else {
      hideRecommendationsSection();
    }
  }

  // ---------- 추천 ----------
  function hideRecommendationsSection() {
    var section = document.getElementById("recommendations-section");
    if (section) section.style.display = "none";
  }

  function displayRecommendations(rec) {
    var section = document.getElementById("recommendations-section");
    if (!section) return;
    section.style.display = "block";
    displayRelatedChunks(rec.related_chunks || []);
    displaySuggestedLabels(rec.suggested_labels || []);
    displaySampleQuestions(rec.sample_questions || []);
    displayExploreMore(rec.explore_more || []);
    if (!section.dataset.bound) {
      section.dataset.bound = "1";
      section.querySelectorAll(".rec-toggle").forEach(function (btn) {
        btn.addEventListener("click", function () {
          section.querySelectorAll(".rec-toggle").forEach(function (b) {
            b.classList.remove("active");
            b.setAttribute("aria-selected", "false");
          });
          section.querySelectorAll(".rec-panel").forEach(function (p) { p.classList.remove("active"); });
          this.classList.add("active");
          this.setAttribute("aria-selected", "true");
          var panelId = this.getAttribute("data-panel") + "-panel";
          var panel = document.getElementById(panelId);
          if (panel) panel.classList.add("active");
        });
      });
    }
  }

  function displayRelatedChunks(chunks) {
    var el = document.getElementById("related-chunks");
    if (!el) return;
    if (!chunks.length) {
      el.innerHTML = '<p class="rec-empty">관련 청크 추천이 없습니다.</p>';
      return;
    }
    el.innerHTML = chunks
      .map(function (c) {
        return (
          '<div class="rec-card rec-card-chunk"><div class="rec-card-header">' +
          '<span class="rec-card-title">' + esc(c.title || "제목 없음") + "</span>" +
          '<span class="rec-card-meta">' + esc(c.document_name || "") + " · " + ((c.similarity_score || 0) * 100).toFixed(0) + "%</span>" +
          '</div><div class="rec-card-body">' + esc((c.content_preview || "").substring(0, 150)) + ((c.content_preview || "").length > 150 ? "…" : "") + "</div>" +
          '<a href="/knowledge-detail?chunk_id=' + (c.chunk_id || "") + '" class="rec-card-link" target="_blank">청크 보기 →</a></div>'
        );
      })
      .join("");
  }

  function displaySuggestedLabels(labels) {
    var el = document.getElementById("suggested-labels");
    if (!el) return;
    if (!labels.length) {
      el.innerHTML = '<p class="rec-empty">추천 라벨이 없습니다.</p>';
      return;
    }
    el.innerHTML = labels
      .map(function (l) {
        return (
          '<span class="label-tag" title="' +
          esc(l.label_type || "") +
          " · " +
          ((l.confidence || 0) * 100).toFixed(0) +
          '%">' +
          esc(l.name || "") +
          "</span>"
        );
      })
      .join("");
  }

  function displaySampleQuestions(questions) {
    var el = document.getElementById("sample-questions");
    if (!el) return;
    if (!questions.length) {
      el.innerHTML = '<p class="rec-empty">샘플 질문이 없습니다.</p>';
      return;
    }
    window.__lastSampleQuestions = questions;
    el.innerHTML = questions
      .map(function (q, i) {
        return (
          '<button type="button" class="sample-question-btn" data-index="' +
          i +
          '" data-mode="' +
          esc(q.suggested_mode || "design_explain") +
          '">' +
          esc((q.question || "").substring(0, 60)) +
          ((q.question || "").length > 60 ? "…" : "") +
          "</button>"
        );
      })
      .join("");
    el.querySelectorAll(".sample-question-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var idx = parseInt(this.getAttribute("data-index"), 10);
        var item = window.__lastSampleQuestions && window.__lastSampleQuestions[idx];
        if (item) handleSampleQuestionClick(item);
      });
    });
  }

  function handleSampleQuestionClick(item) {
    var questionEl = document.getElementById("question");
    var modeEl = document.getElementById("mode");
    if (questionEl) questionEl.value = item.question || "";
    if (modeEl && item.suggested_mode) modeEl.value = item.suggested_mode;
  }

  function displayExploreMore(items) {
    var el = document.getElementById("explore-more");
    if (!el) return;
    if (!items.length) {
      el.innerHTML = '<p class="rec-empty">추가 탐색 제안이 없습니다.</p>';
      return;
    }
    el.innerHTML = items
      .map(function (it) {
        var typeLabel = it.type === "project" ? "프로젝트" : it.type === "label" ? "라벨" : "질문";
        var href = it.type === "project" ? "#" : it.type === "label" ? "/admin/labels" : "#";
        return (
          '<div class="explore-item">' +
          '<span class="explore-type">' + esc(typeLabel) + "</span>" +
          '<span class="explore-name">' + esc(it.name || "") + "</span>" +
          '<span class="explore-desc">' + esc((it.description || "").substring(0, 50)) + ((it.description || "").length > 50 ? "…" : "") + "</span>" +
          (href !== "#" ? '<a href="' + href + '" class="explore-link">보기 →</a>' : "") +
          "</div>"
        );
      })
      .join("");
  }

  // ---------- 화면 비우기 (control에서 호출) ----------
  function clearReasoningResults() {
    var docCountEl = document.getElementById("summary-docs-count");
    var chunkCountEl = document.getElementById("summary-chunks-count");
    var relCountEl = document.getElementById("summary-relations-count");
    var briefEl = document.getElementById("result-summary-text");
    var answerDiv = document.getElementById("answer");
    var contextChunksDiv = document.getElementById("context-chunks");
    var contextDocumentsDiv = document.getElementById("context-documents");
    var stepsDiv = document.getElementById("reasoning-steps");
    if (docCountEl) docCountEl.textContent = "-";
    if (chunkCountEl) chunkCountEl.textContent = "-";
    if (relCountEl) relCountEl.textContent = "-";
    if (briefEl) { briefEl.textContent = ""; briefEl.style.display = "none"; }
    if (answerDiv) answerDiv.textContent = "";
    if (contextChunksDiv) contextChunksDiv.innerHTML = "";
    if (contextDocumentsDiv) contextDocumentsDiv.innerHTML = "";
    if (stepsDiv) stepsDiv.innerHTML = "";
    hideRecommendationsSection();
    var recSection = document.getElementById("recommendations-section");
    if (recSection) recSection.style.display = "none";
    ["related-chunks", "suggested-labels", "sample-questions", "explore-more"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.innerHTML = "";
    });
    clearModeViz();
  }

  function clearModeViz() {
    var container = document.getElementById("mode-viz-container");
    if (container) container.style.display = "none";
    ["viz-design-explain", "viz-risk-review", "viz-next-steps", "viz-history-trace"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) {
        el.innerHTML = "";
        el.style.display = "none";
      }
    });
    if (window.__riskReviewChart) {
      try {
        window.__riskReviewChart.destroy();
      } catch (e) {}
      window.__riskReviewChart = null;
    }
  }

  window.ReasonRender = {
    switchContextTab: switchContextTab,
    displayResults: displayResults,
    clearReasoningResults: clearReasoningResults,
    clearModeViz: clearModeViz,
    hideRecommendationsSection: hideRecommendationsSection,
  };
})();
