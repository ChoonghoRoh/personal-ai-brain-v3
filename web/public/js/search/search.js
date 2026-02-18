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
        .map((result) => {
          const highlightedSnippet = highlightText(result.snippet || result.content || "", query);
          return `
                    <div class="result-item" onclick="openDocument('${result.file.replace(/'/g, "\\'")}')">
                        <div class="result-header">
                            <div class="result-file">${escapeHtml(result.file || "Unknown")}</div>
                            <div class="result-score">유사도: ${(result.score * 100).toFixed(1)}%</div>
                        </div>
                        <div class="result-snippet">${highlightedSnippet}</div>
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

// 페이지 로드 시 실행
displayHistory();
loadRecommended();
