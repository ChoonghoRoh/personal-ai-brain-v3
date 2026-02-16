/**
 * Reasoning Lab — Common 레이어
 * 데이터 로드·페이지 공통 유틸 (옵션/시드).
 * 의존성: reason-model(필요 시), utils(escapeHtml)
 */
(function () {
  "use strict";

  /**
   * 로딩 메시지 표시 (reason 전용)
   * @param {string} elementId - 대상 요소 ID
   * @param {string} message - 메시지
   * @param {string} style - 인라인 스타일 (선택)
   */
  function showLoading(elementId, message, style) {
    if (message === undefined) message = "로딩 중...";
    if (style === undefined) style = "";
    var element = document.getElementById(elementId);
    if (element) {
      element.innerHTML =
        '<div class="loading" ' +
        (style ? 'style="' + style + '"' : "") +
        ">" +
        (typeof escapeHtml === "function" ? escapeHtml(message) : message) +
        "</div>";
    }
  }

  /**
   * Reasoning 보조 옵션 로드 (프로젝트, 라벨 목록)
   */
  async function loadReasoningOptions() {
    try {
      var projectsRes = await fetch("/api/knowledge/projects");
      var labelsRes = await fetch("/api/labels");
      var projects = projectsRes.ok ? await projectsRes.json() : [];
      var labels = [];
      if (labelsRes.ok) {
        var labelsData = await labelsRes.json();
        labels = Array.isArray(labelsData) ? labelsData : labelsData.items || [];
      }
      var projectsSelect = document.getElementById("projects-select");
      var labelsSelect = document.getElementById("labels-select");
      if (projectsSelect) {
        projectsSelect.innerHTML = (projects || [])
          .map(function (p) {
            return (
              '<option value="' +
              Number(p.id) +
              '">' +
              (typeof escapeHtml === "function" ? escapeHtml(p.name || "") : p.name || "") +
              "</option>"
            );
          })
          .join("");
      }
      if (labelsSelect) {
        labelsSelect.innerHTML = (labels || [])
          .map(function (l) {
            var id = l.id != null ? l.id : l.label_id;
            var name = l.name != null ? l.name : l.label_name || "";
            return (
              '<option value="' +
              (typeof escapeHtml === "function" ? escapeHtml(String(name)) : String(name)) +
              '">' +
              (typeof escapeHtml === "function" ? escapeHtml(name) : name) +
              "</option>"
            );
          })
          .join("");
      }
    } catch (e) {
      console.warn("Reasoning 옵션 로드 실패:", e);
    }
  }

  /**
   * 시드 청크 로드 후 question 필드에 설정
   * @param {string} chunkId - 청크 ID
   */
  async function loadSeedChunk(chunkId) {
    try {
      var response = await fetch("/api/knowledge/chunks/" + chunkId);
      var chunk = await response.json();
      var questionEl = document.getElementById("question");
      if (questionEl) {
        questionEl.value =
          "다음 청크를 기반으로 Reasoning을 시작합니다:\n\n" + (chunk.content || "").substring(0, 200) + "...";
      }
    } catch (error) {
      console.error("Seed chunk 로드 실패:", error);
    }
  }

  /**
   * 문서 컨텍스트 로드 (Phase 15-3)
   * @param {string} documentId - 문서 ID
   */
  async function loadDocumentContext(documentId) {
    try {
      var response = await fetch("/api/knowledge/documents/" + documentId);
      if (!response.ok) throw new Error("문서 정보 로드 실패");
      var doc = await response.json();
      var questionEl = document.getElementById("question");
      if (questionEl && !questionEl.value.trim()) {
        questionEl.placeholder =
          "'" + (doc.file_name || "문서") + "' 문서에 대해 질문하세요";
      }
      showDocumentBadge(doc);
      window.__reasonDocumentIds = [parseInt(documentId, 10)];
      return doc;
    } catch (error) {
      console.error("문서 컨텍스트 로드 실패:", error);
      return null;
    }
  }

  /**
   * 문서 정보 뱃지 표시 (Phase 15-3)
   * @param {object} doc - 문서 정보 객체
   */
  function showDocumentBadge(doc) {
    var existing = document.getElementById("document-context-badge");
    if (existing) existing.remove();

    var escapeFn = typeof escapeHtml === "function" ? escapeHtml : function (s) { return String(s); };
    var fileName = escapeFn(doc.file_name || "문서");

    var badge = document.createElement("div");
    badge.id = "document-context-badge";
    badge.className = "document-context-badge";
    badge.innerHTML =
      '<span class="doc-badge">' +
      '<span class="doc-badge-icon">📄</span>' +
      '<span>' + fileName + '</span>' +
      '<button type="button" class="doc-badge-close" title="문서 필터 해제">&times;</button>' +
      '</span>';

    badge.querySelector(".doc-badge-close").addEventListener("click", function () {
      clearDocumentContext();
    });

    var form = document.querySelector(".reasoning-form");
    if (form) {
      var firstFormGroup = form.querySelector(".form-group");
      if (firstFormGroup) {
        form.insertBefore(badge, firstFormGroup);
      } else {
        form.prepend(badge);
      }
    }
  }

  /**
   * 문서 컨텍스트 초기화 (Phase 15-3)
   */
  function clearDocumentContext() {
    window.__reasonDocumentIds = null;
    var badge = document.getElementById("document-context-badge");
    if (badge) badge.remove();
    var questionEl = document.getElementById("question");
    if (questionEl) {
      questionEl.placeholder = "질문을 입력하세요 (선택사항)";
    }
  }

  /**
   * URL 쿼리에서 seed_chunk / document_id 파라미터를 읽어 처리 (Phase 15-3 확장)
   */
  function initSeedFromUrl() {
    var urlParams = new URLSearchParams(window.location.search);
    var seedChunkId = urlParams.get("seed_chunk");
    if (seedChunkId) {
      loadSeedChunk(seedChunkId);
      return;
    }
    var documentId = urlParams.get("document_id");
    if (documentId) {
      loadDocumentContext(documentId);
    }
  }

  window.ReasonCommon = {
    showLoading: showLoading,
    loadReasoningOptions: loadReasoningOptions,
    loadSeedChunk: loadSeedChunk,
    initSeedFromUrl: initSeedFromUrl,
    loadDocumentContext: loadDocumentContext,
    showDocumentBadge: showDocumentBadge,
    clearDocumentContext: clearDocumentContext,
  };
})();
