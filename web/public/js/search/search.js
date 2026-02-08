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
});

let searchHistory = JSON.parse(localStorage.getItem("searchHistory") || "[]");
let currentQuery = "";

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
 * 추천 문서 로드
 * 최근 업데이트된 문서 5개를 로드하여 표시
 */
async function loadRecommended() {
  try {
    const response = await fetch("/api/documents?limit=5");
    const docs = await response.json();
    if (docs.length > 0) {
      document.getElementById("recommended").style.display = "block";
      const recommendedHtml = docs
        .map(
          (doc) => `
        <div class="recommended-item" onclick="openDocument('${doc.file_path.replace(/'/g, "\\'")}')">
          ${escapeHtml(doc.name || doc.file_path)}
        </div>
      `
        )
        .join("");
      document.getElementById("recommended-items").innerHTML = recommendedHtml;
    }
  } catch (error) {
    console.error("추천 문서 로드 오류:", error);
  }
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
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
    
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
