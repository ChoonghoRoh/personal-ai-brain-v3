// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🔍 Personal AI Brain - Search",
      subtitle: "의미 기반 문서 검색",
      currentPath: "/search",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }

  // 검색 모드 토글 이벤트
  document.querySelectorAll(".mode-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".mode-btn").forEach(function (b) { b.classList.remove("active"); });
      btn.classList.add("active");
      currentSearchMode = btn.dataset.mode;
    });
  });
});

let searchHistory = JSON.parse(localStorage.getItem("searchHistory") || "[]");
let currentQuery = "";
let currentSearchMode = "hybrid";
let allDocuments = [];

/**
 * 검색 히스토리 표시
 * 로컬 스토리지에 저장된 검색 히스토리를 최대 10개까지 표시
 */
function displayHistory() {
  if (searchHistory.length > 0) {
    document.getElementById("search-history").style.display = "block";
    const historyHtml = searchHistory
      .slice()
      .reverse()
      .slice(0, 10)
      .map(
        (item) => `
      <span class="history-item" onclick="searchFromHistory('${item.replace(/'/g, "\\'")}')">${escapeHtml(item)}</span>
    `
      )
      .join("");
    document.getElementById("history-items").innerHTML = historyHtml;
  }
}

/**
 * 검색 히스토리에서 검색 실행
 * @param {string} query - 검색어
 */
function searchFromHistory(query) {
  document.getElementById("search-input").value = query;
  search();
}

/**
 * 텍스트 하이라이팅
 * 검색어를 찾아 하이라이트 처리 (XSS 방지를 위해 escapeHtml 사용)
 * @param {string} text - 원본 텍스트
 * @param {string} query - 검색어
 * @returns {string} 하이라이트된 HTML 문자열
 */
function highlightText(text, query) {
  if (!query) return escapeHtml(text);
  // 먼저 텍스트를 이스케이프 처리
  const escapedText = escapeHtml(text);
  // 이스케이프된 텍스트에서 쿼리를 찾기 위해 쿼리도 이스케이프
  const escapedQuery = escapeHtml(query);
  const regex = new RegExp(`(${escapedQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, "gi");
  return escapedText.replace(regex, '<span class="highlight">$1</span>');
}

/**
 * 검색 모드 배지 HTML 생성
 * @param {string} mode - 검색 모드 (semantic|keyword|hybrid)
 * @returns {string} 배지 HTML
 */
function buildModeBadge(mode) {
  var config = {
    semantic: { cls: "badge-semantic", label: "의미" },
    keyword:  { cls: "badge-keyword",  label: "키워드" },
    hybrid:   { cls: "badge-hybrid",   label: "하이브리드" },
  };
  var c = config[mode] || config.hybrid;
  return '<span class="result-badge ' + c.cls + '">' + c.label + '</span>';
}

/**
 * 점수 의미 배지 HTML 생성
 * @param {number} score - 유사도 점수 (0~1)
 * @returns {string} 배지 HTML
 */
function buildScoreBadge(score) {
  var label, cls;
  if (score >= 0.8) { label = "매우 관련"; cls = "score-high"; }
  else if (score >= 0.6) { label = "관련"; cls = "score-mid"; }
  else if (score >= 0.4) { label = "참고"; cls = "score-low"; }
  else { label = "낮음"; cls = "score-none"; }
  var pct = (score * 100).toFixed(1);
  return '<span class="result-score ' + cls + '">' + label + ' ' + pct + '%</span>';
}

/**
 * 점수 프로그레스 바 HTML 생성
 * @param {number} score - 유사도 점수 (0~1)
 * @returns {string} 프로그레스 바 HTML
 */
function buildScoreBar(score) {
  var pct = Math.min(Math.round(score * 100), 100);
  var cls;
  if (score >= 0.8) cls = "bar-high";
  else if (score >= 0.6) cls = "bar-mid";
  else if (score >= 0.4) cls = "bar-low";
  else cls = "bar-none";
  return '<div class="score-bar"><div class="score-bar-fill ' + cls + '" style="width:' + pct + '%"></div></div>';
}

/**
 * 문서 status 배지 HTML 생성
 * @param {string|undefined} status - 문서 상태 (approved|draft|rejected)
 * @returns {string} 배지 HTML (상태 없으면 빈 문자열)
 */
function buildStatusBadge(status) {
  if (!status) return "";
  var config = {
    approved: { cls: "status-approved", label: "승인" },
    draft:    { cls: "status-draft",    label: "초안" },
    rejected: { cls: "status-rejected", label: "거절" },
  };
  var c = config[status];
  if (!c) return "";
  return '<span class="result-badge ' + c.cls + '">' + c.label + '</span>';
}

/**
 * 추천 문서 로드 (전체 목록 fetch 후 클라이언트사이드 필터링)
 */
async function loadRecommended() {
  try {
    const response = await fetch("/api/documents");
    const docs = await response.json();
    allDocuments = docs;
    if (docs.length > 0) {
      document.getElementById("recommended").style.display = "block";
      populateFolderFilter(docs);
      filterRecommended();
    }
  } catch (error) {
    console.error("추천 문서 로드 오류:", error);
  }
}

/**
 * 폴더 필터 드롭다운 생성
 * @param {Array} docs - 문서 목록
 */
function populateFolderFilter(docs) {
  var folders = new Set();
  docs.forEach(function (doc) {
    var parts = (doc.file_path || "").split("/");
    if (parts.length > 1) {
      folders.add(parts[0]);
    }
  });
  var select = document.getElementById("rec-folder");
  var sorted = Array.from(folders).sort();
  sorted.forEach(function (folder) {
    var opt = document.createElement("option");
    opt.value = folder;
    opt.textContent = folder + "/";
    select.appendChild(opt);
  });
}

/**
 * 추천 문서 필터/정렬/렌더링
 */
function filterRecommended() {
  var searchText = (document.getElementById("rec-search").value || "").toLowerCase();
  var folder = document.getElementById("rec-folder").value;
  var sortBy = document.getElementById("rec-sort").value;
  var limit = parseInt(document.getElementById("rec-limit").value, 10);

  var filtered = allDocuments.filter(function (doc) {
    var name = (doc.name || "").toLowerCase();
    var path = (doc.file_path || "").toLowerCase();
    if (searchText && name.indexOf(searchText) === -1 && path.indexOf(searchText) === -1) {
      return false;
    }
    if (folder && !path.startsWith(folder.toLowerCase() + "/")) {
      return false;
    }
    return true;
  });

  // 정렬
  filtered.sort(function (a, b) {
    if (sortBy === "name") {
      return (a.name || "").localeCompare(b.name || "");
    } else if (sortBy === "size") {
      return (b.size || 0) - (a.size || 0);
    }
    // newest (기본)
    return (b.modified || 0) - (a.modified || 0);
  });

  // 슬라이스
  var sliced = filtered.slice(0, limit);

  renderRecommendedCards(sliced);
}

/**
 * 추천 문서를 그리드 카드로 렌더링
 * @param {Array} docs - 문서 목록
 */
function renderRecommendedCards(docs) {
  var container = document.getElementById("recommended-items");
  if (docs.length === 0) {
    container.innerHTML = '<div class="no-results">조건에 맞는 문서가 없습니다.</div>';
    return;
  }
  var html = docs.map(function (doc) {
    var name = escapeHtml(doc.name || doc.file_path);
    var pathParts = (doc.file_path || "").split("/");
    var folderPath = pathParts.length > 1 ? escapeHtml(pathParts.slice(0, -1).join("/")) : "";
    var sizeKB = doc.size ? (doc.size / 1024).toFixed(1) + " KB" : "";
    var dateStr = "";
    if (doc.modified) {
      var d = new Date(doc.modified * 1000);
      dateStr = d.toLocaleDateString("ko-KR", { year: "numeric", month: "2-digit", day: "2-digit" });
    }
    var fp = (doc.file_path || "").replace(/'/g, "\\'");
    return '<div class="rec-card" onclick="openDocument(\'' + fp + '\')">' +
      '<div class="rec-card-title">' + name + '</div>' +
      (folderPath ? '<div class="rec-card-path">' + folderPath + '</div>' : '') +
      '<div class="rec-card-meta">' +
        (sizeKB ? '<span>' + sizeKB + '</span>' : '') +
        (dateStr ? '<span>' + dateStr + '</span>' : '') +
      '</div>' +
    '</div>';
  }).join("");
  container.innerHTML = html;
}

/**
 * 검색 실행
 * 검색어를 입력받아 API를 호출하고 결과를 표시
 * 검색 히스토리에 자동으로 추가
 */
async function search() {
  const query = document.getElementById("search-input").value.trim();
  const resultsDiv = document.getElementById("results");
  const searchButton = document.getElementById("search-button");

  if (!query) {
    resultsDiv.innerHTML = '<div class="no-results">검색어를 입력하세요.</div>';
    return;
  }

  // 검색 히스토리에 추가
  if (!searchHistory.includes(query)) {
    searchHistory.push(query);
    if (searchHistory.length > 20) {
      searchHistory.shift();
    }
    localStorage.setItem("searchHistory", JSON.stringify(searchHistory));
    displayHistory();
  }

  currentQuery = query;

  // 로딩 상태
  searchButton.disabled = true;
  searchButton.textContent = "검색 중...";
  resultsDiv.innerHTML = '<div class="loading">검색 중...</div>';

  try {
    const url = `/api/search?q=${encodeURIComponent(query)}&limit=10&search_mode=${encodeURIComponent(currentSearchMode)}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // API 응답이 객체인 경우 results 속성 사용, 배열인 경우 직접 사용
    let results = [];
    if (Array.isArray(data)) {
      results = data;
    } else if (data && typeof data === 'object') {
      results = Array.isArray(data.results) ? data.results : [];
    }

    // results가 배열인지 최종 확인
    if (!Array.isArray(results)) {
      console.error("검색 결과가 배열이 아닙니다:", typeof results, results);
      resultsDiv.innerHTML = '<div class="no-results">검색 결과 형식 오류가 발생했습니다.</div>';
      return;
    }

    if (results.length === 0) {
      resultsDiv.innerHTML = '<div class="no-results">검색 결과가 없습니다.</div>';
    } else {
      const resultsHtml = results
        .map((result, idx) => {
          // BE highlighted_snippet 우선 사용 (이미 <mark> 태그 포함, sanitized)
          const hasHighlighted = result.highlighted_snippet;
          const snippetHtml = hasHighlighted
            ? result.highlighted_snippet
            : highlightText(result.snippet || result.content || "", query);
          const fullContentHtml = highlightText(result.content || "", query);
          const showToggle = (result.content || "").length > 300;
          const score = result.score || 0;
          const modeBadge = buildModeBadge(currentSearchMode);
          const scoreBadge = buildScoreBadge(score);
          const scoreBar = buildScoreBar(score);
          const statusBadge = buildStatusBadge(result.status);
          return `
                    <div class="result-item" onclick="openDocument('${result.file.replace(/'/g, "\\'")}')">
                        <div class="result-badges">
                            ${modeBadge}${statusBadge}
                        </div>
                        <div class="result-header">
                            <div class="result-file">${escapeHtml(result.file || "Unknown")}</div>
                            <div class="result-score-group">
                                ${scoreBadge}
                            </div>
                        </div>
                        ${scoreBar}
                        <div class="result-snippet" id="snippet-${idx}">${snippetHtml}</div>
                        ${showToggle ? `<div class="result-full-content" id="full-${idx}" style="display:none;">${fullContentHtml}</div>
                        <button class="snippet-toggle-btn" data-idx="${idx}" onclick="event.stopPropagation(); toggleFullContent(${idx})">전체 보기</button>` : ''}
                    </div>
                `;
        })
        .join("");
      resultsDiv.innerHTML = resultsHtml;
    }
  } catch (error) {
    console.error("검색 오류:", error);
    resultsDiv.innerHTML = '<div class="no-results">검색 중 오류가 발생했습니다: ' + escapeHtml(error.message) + '</div>';
  } finally {
    searchButton.disabled = false;
    searchButton.textContent = "검색";
  }
}

/**
 * snippet/전체 보기 토글
 * @param {number} idx - 결과 인덱스
 */
function toggleFullContent(idx) {
  var snippetEl = document.getElementById("snippet-" + idx);
  var fullEl = document.getElementById("full-" + idx);
  var btn = document.querySelector('.snippet-toggle-btn[data-idx="' + idx + '"]');
  if (!snippetEl || !fullEl || !btn) return;

  if (fullEl.style.display === "none") {
    snippetEl.style.display = "none";
    fullEl.style.display = "block";
    btn.textContent = "간략히 보기";
  } else {
    snippetEl.style.display = "block";
    fullEl.style.display = "none";
    btn.textContent = "전체 보기";
  }
}

/**
 * 관계 추천 패널 로드 (Phase 18-4-5)
 * @param {number} chunkId - 소스 청크 ID
 * @param {HTMLElement} container - 추천 패널을 삽입할 컨테이너
 */
async function loadRelationRecommendations(chunkId, container) {
  if (!chunkId || !container) return;
  container.innerHTML = '<div class="loading">추천 로딩 중...</div>';
  try {
    var url = "/api/relations/recommendations?chunk_id=" + chunkId + "&top_k=5&cross_document_only=true";
    var resp = await fetch(url);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    var data = await resp.json();
    var recs = data.recommendations || [];
    if (recs.length === 0) {
      container.innerHTML = '<div class="no-results">추천 관계가 없습니다.</div>';
      return;
    }
    var typeIcons = { similar: "~", prerequisite: "->", extends: "+" };
    var html = recs.map(function (rec) {
      var icon = typeIcons[rec.suggested_type] || "~";
      var simPct = (rec.similarity * 100).toFixed(1);
      var relatedTag = rec.already_related ? '<span class="rec-tag rec-tag-exists">연결됨</span>' : '';
      return '<div class="rec-relation-card">' +
        '<div class="rec-relation-header">' +
          '<span class="rec-type-icon" title="' + escapeHtml(rec.suggested_type) + '">[' + icon + ']</span>' +
          '<span class="rec-doc-name">' + escapeHtml(rec.document_name) + '</span>' +
          relatedTag +
        '</div>' +
        '<div class="rec-sim-bar"><div class="rec-sim-fill" style="width:' + simPct + '%"></div><span>' + simPct + '%</span></div>' +
        '<div class="rec-relation-snippet">' + escapeHtml(rec.content_snippet) + '</div>' +
        (!rec.already_related ? '<button class="rec-add-btn" onclick="event.stopPropagation(); addRelation(' + data.source_chunk_id + ',' + rec.chunk_id + ',\'' + escapeHtml(rec.suggested_type) + '\',' + rec.similarity + ', this)">관계 추가</button>' : '') +
      '</div>';
    }).join("");
    container.innerHTML = html;
  } catch (err) {
    console.error("관계 추천 로드 오류:", err);
    container.innerHTML = '<div class="no-results">추천 로드 실패</div>';
  }
}

/**
 * 관계 추가 (POST /api/relations)
 */
async function addRelation(sourceChunkId, targetChunkId, relationType, score, btnEl) {
  if (btnEl) btnEl.disabled = true;
  try {
    var resp = await fetch("/api/relations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source_chunk_id: sourceChunkId,
        target_chunk_id: targetChunkId,
        relation_type: relationType,
        confidence: score,
      }),
    });
    if (!resp.ok) {
      var errData = await resp.json().catch(function () { return {}; });
      throw new Error(errData.detail || "HTTP " + resp.status);
    }
    if (btnEl) {
      btnEl.textContent = "추가됨";
      btnEl.classList.add("rec-added");
    }
  } catch (err) {
    console.error("관계 추가 실패:", err);
    if (btnEl) {
      btnEl.disabled = false;
      btnEl.textContent = "실패 - 재시도";
    }
  }
}

// 페이지 로드 시 실행
displayHistory();
loadRecommended();
