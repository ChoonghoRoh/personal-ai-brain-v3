/**
 * Reasoning Lab — Render 레이어
 * 결과·추천 등 화면 그리기. 시각화는 reason-render-viz.js 참조
 * 의존성: reason-model(MODE_VIZ_TITLES), utils(escapeHtml), reason-render-viz.js
 */
(function () {
  "use strict";

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
  function renderSummaryText(result) {
    var briefEl = document.getElementById("result-summary-text");
    if (!briefEl) return;
    var answer = (result.answer || "").trim();
    if (!answer) { briefEl.style.display = "none"; return; }
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
    if (answerDiv) answerDiv.textContent = result.answer || "답변을 생성할 수 없습니다.";
  }

  function renderContextChunks(chunks) {
    var contextChunksDiv = document.getElementById("context-chunks");
    if (!contextChunksDiv) return;
    if (chunks.length > 0) {
      contextChunksDiv.innerHTML = chunks.map(function (chunk) {
        var metaParts = [];
        if (chunk.project) metaParts.push("<strong>" + esc(chunk.project) + "</strong>");
        if (chunk.project_id != null) metaParts.push("프로젝트 ID: " + chunk.project_id);
        metaParts.push(esc(chunk.document || "알 수 없음"));
        metaParts.push("청크 ID: " + (chunk.id || "N/A"));
        var labels = chunk.labels && chunk.labels.length ? chunk.labels : [];
        var labelsHtml = labels.length
          ? ' <span class="chunk-labels">' + labels.map(function (l) { return '<span class="chunk-label-tag">' + esc(l) + "</span>"; }).join(" ") + "</span>"
          : "";
        return '<div class="chunk-item"><div class="chunk-meta">' + metaParts.join(" / ") + labelsHtml + '</div><div class="chunk-content">' + esc(chunk.content || "내용 없음") + "</div></div>";
      }).join("");
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
      if (chunk.document) documentMap.get(chunk.document).chunks.push(chunk);
    });
    if (documentMap.size > 0) {
      contextDocumentsDiv.innerHTML = Array.from(documentMap.values()).map(function (doc) {
        var docPath = doc.name.indexOf("brain/") === 0 ? doc.name : "brain/" + doc.name;
        return '<div class="document-item"><div class="doc-info"><div class="doc-name">' + esc(doc.name) + '</div><div class="doc-meta">' + (doc.project ? "프로젝트: " + esc(doc.project) + " / " : "") + doc.chunks.length + '개 청크 사용됨</div></div><a href="/document/' + encodeURIComponent(docPath) + '" class="doc-btn" target="_blank">문서 열기 →</a></div>';
      }).join("");
    } else {
      contextDocumentsDiv.innerHTML = '<p style="color: #999;">사용된 문서가 없습니다.</p>';
    }
  }

  function renderContext(chunks) { renderContextChunks(chunks); renderContextDocuments(chunks); }

  function renderSteps(steps) {
    var stepsDiv = document.getElementById("reasoning-steps");
    if (!stepsDiv) return;
    if (steps && steps.length > 0) {
      stepsDiv.innerHTML = "<ol>" + steps.map(function (step) { return "<li>" + esc(step || "단계 정보 없음") + "</li>"; }).join("") + "</ol>";
    } else {
      stepsDiv.innerHTML = '<p style="color: #999;">Reasoning 단계 정보가 없습니다.</p>';
    }
  }

  // ---------- 메인 진입: displayResults ----------
  function displayResults(result) {
    if (!result) { console.error("displayResults: result가 없습니다"); return; }
    var chunks = result.context_chunks || [];
    var modeEl = document.getElementById("mode");
    var mode = (modeEl && modeEl.value) || "design_explain";
    renderSummary(result);
    if (window.ReasonRenderViz) window.ReasonRenderViz.renderModeViz(result, mode);
    renderConclusion(result);
    renderContext(chunks);
    renderSteps(result.reasoning_steps);
    if (result.recommendations) displayRecommendations(result.recommendations);
    else hideRecommendationsSection();
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
          section.querySelectorAll(".rec-toggle").forEach(function (b) { b.classList.remove("active"); b.setAttribute("aria-selected", "false"); });
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
    if (!chunks.length) { el.innerHTML = '<p class="rec-empty">관련 청크 추천이 없습니다.</p>'; return; }
    el.innerHTML = chunks.map(function (c) {
      return '<div class="rec-card rec-card-chunk"><div class="rec-card-header"><span class="rec-card-title">' + esc(c.title || "제목 없음") + '</span><span class="rec-card-meta">' + esc(c.document_name || "") + " · " + ((c.similarity_score || 0) * 100).toFixed(0) + '%</span></div><div class="rec-card-body">' + esc((c.content_preview || "").substring(0, 150)) + ((c.content_preview || "").length > 150 ? "…" : "") + '</div><a href="/knowledge-detail?chunk_id=' + (c.chunk_id || "") + '" class="rec-card-link" target="_blank">청크 보기 →</a></div>';
    }).join("");
  }

  function displaySuggestedLabels(labels) {
    var el = document.getElementById("suggested-labels");
    if (!el) return;
    if (!labels.length) { el.innerHTML = '<p class="rec-empty">추천 라벨이 없습니다.</p>'; return; }
    el.innerHTML = labels.map(function (l) {
      return '<span class="label-tag" title="' + esc(l.label_type || "") + " · " + ((l.confidence || 0) * 100).toFixed(0) + '%">' + esc(l.name || "") + "</span>";
    }).join("");
  }

  function displaySampleQuestions(questions) {
    var el = document.getElementById("sample-questions");
    if (!el) return;
    if (!questions.length) { el.innerHTML = '<p class="rec-empty">샘플 질문이 없습니다.</p>'; return; }
    window.__lastSampleQuestions = questions;
    el.innerHTML = questions.map(function (q, i) {
      return '<button type="button" class="sample-question-btn" data-index="' + i + '" data-mode="' + esc(q.suggested_mode || "design_explain") + '">' + esc((q.question || "").substring(0, 60)) + ((q.question || "").length > 60 ? "…" : "") + "</button>";
    }).join("");
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
    if (!items.length) { el.innerHTML = '<p class="rec-empty">추가 탐색 제안이 없습니다.</p>'; return; }
    el.innerHTML = items.map(function (it) {
      var typeLabel = it.type === "project" ? "프로젝트" : it.type === "label" ? "라벨" : "질문";
      var href = it.type === "project" ? "#" : it.type === "label" ? "/admin/labels" : "#";
      return '<div class="explore-item"><span class="explore-type">' + esc(typeLabel) + '</span><span class="explore-name">' + esc(it.name || "") + '</span><span class="explore-desc">' + esc((it.description || "").substring(0, 50)) + ((it.description || "").length > 50 ? "…" : "") + "</span>" + (href !== "#" ? '<a href="' + href + '" class="explore-link">보기 →</a>' : "") + "</div>";
    }).join("");
  }

  // ---------- 화면 비우기 ----------
  function clearReasoningResults() {
    var els = {
      docCount: document.getElementById("summary-docs-count"),
      chunkCount: document.getElementById("summary-chunks-count"),
      relCount: document.getElementById("summary-relations-count"),
      brief: document.getElementById("result-summary-text"),
      answer: document.getElementById("answer"),
      contextChunks: document.getElementById("context-chunks"),
      contextDocs: document.getElementById("context-documents"),
      steps: document.getElementById("reasoning-steps"),
    };
    if (els.docCount) els.docCount.textContent = "-";
    if (els.chunkCount) els.chunkCount.textContent = "-";
    if (els.relCount) els.relCount.textContent = "-";
    if (els.brief) { els.brief.textContent = ""; els.brief.style.display = "none"; }
    if (els.answer) els.answer.textContent = "";
    if (els.contextChunks) els.contextChunks.innerHTML = "";
    if (els.contextDocs) els.contextDocs.innerHTML = "";
    if (els.steps) els.steps.innerHTML = "";
    hideRecommendationsSection();
    ["related-chunks", "suggested-labels", "sample-questions", "explore-more"].forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.innerHTML = "";
    });
    if (window.ReasonRenderViz) window.ReasonRenderViz.clearModeViz();
  }

  window.ReasonRender = {
    switchContextTab: switchContextTab,
    displayResults: displayResults,
    clearReasoningResults: clearReasoningResults,
    clearModeViz: function () { if (window.ReasonRenderViz) window.ReasonRenderViz.clearModeViz(); },
    hideRecommendationsSection: hideRecommendationsSection,
  };
})();
