// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🔗 관계 매칭",
      subtitle: "AI 추천 관계를 연결하세요",
      currentPath: "/knowledge-relation-matching",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

let currentChunkId = null;

// 관계 변경 후 리로드 콜백 설정
window._relationReloadFn = function (chunkId) {
  loadRelationMatching(chunkId);
};

// URL 파라미터에서 id 확인
const urlParams = new URLSearchParams(window.location.search);
const chunkIdParam = urlParams.get("id");
if (chunkIdParam) {
  currentChunkId = parseInt(chunkIdParam);
}

// 상세 페이지로 돌아가기
function goBackToDetail() {
  if (currentChunkId) {
    window.location.href = `/knowledge-detail?id=${currentChunkId}`;
  } else {
    window.location.href = "/knowledge";
  }
}

// 관계 매칭 보드 로드
async function loadRelationMatching(chunkId) {
  const contentDiv = document.getElementById("relation-matching-content-wrapper");
  if (!contentDiv) {
    console.error("관계 매칭 컨텐츠 요소를 찾을 수 없습니다.");
    return;
  }

  contentDiv.innerHTML = '<div class="loading">⏳ 청크 정보를 불러오는 중...</div>';

  try {
    // 청크 기본 정보 가져오기
    const chunkResponse = await fetch(`/api/knowledge/chunks/${chunkId}`);
    if (!chunkResponse.ok) throw new Error("청크 정보를 불러올 수 없습니다.");
    const chunk = await chunkResponse.json();

    // 배열 데이터 기본값 설정
    if (!chunk.labels) chunk.labels = [];
    if (!chunk.outgoing_relations) chunk.outgoing_relations = [];
    if (!chunk.incoming_relations) chunk.incoming_relations = [];

    contentDiv.innerHTML = `
      <div class="relation-matching-board">
        <div class="relation-matching-layout">
          <!-- 좌측: 기준 청크 카드 -->
          <div class="relation-matching-left">
            <h4>기준 청크</h4>
            <div class="chunk-card-preview">
              <div class="chunk-preview-content">${formatTextWithLineBreaks(chunk.content.substring(0, 200))}${chunk.content.length > 200 ? "..." : ""}</div>
              <div class="chunk-preview-meta">
                ${chunk.document_name || "알 수 없음"} (청크 #${chunk.chunk_index})
              </div>
            </div>
          </div>

          <!-- 중앙: 기존 관계 카드 리스트 -->
          <div class="relation-matching-center">
            <div class="relation-section-header">
              <h4>연결된 관계 (${chunk.outgoing_relations.length + chunk.incoming_relations.length})</h4>
              <div class="relation-type-filters" id="existing-relations-filters">
                <button class="filter-btn filter-btn-all active" onclick="toggleRelationFilter('all', 'existing', event)">전체</button>
                <button class="filter-btn" data-type="similar" onclick="toggleRelationFilter('similar', 'existing', event)">유사</button>
                <button class="filter-btn" data-type="explains" onclick="toggleRelationFilter('explains', 'existing', event)">설명</button>
                <button class="filter-btn" data-type="result_of" onclick="toggleRelationFilter('result_of', 'existing', event)">결과</button>
                <button class="filter-btn" data-type="cause_of" onclick="toggleRelationFilter('cause_of', 'existing', event)">원인</button>
                <button class="filter-btn" data-type="refers_to" onclick="toggleRelationFilter('refers_to', 'existing', event)">참조</button>
              </div>
            </div>
            <div id="existing-relations-list" class="relations-list">
              ${generateExistingRelationsHTML(chunk.outgoing_relations, chunk.incoming_relations, chunk.id)}
            </div>
          </div>

          <!-- 우측: AI 추천 관계 카드 리스트 -->
          <div class="relation-matching-right">
            <div class="relation-section-header">
              <h4>추천 관계</h4>
              <div class="relation-type-filters" id="suggested-relations-filters">
                <button class="filter-btn filter-btn-all active" onclick="toggleRelationFilter('all', 'suggested', event)">전체</button>
                <button class="filter-btn" data-type="similar" onclick="toggleRelationFilter('similar', 'suggested', event)">유사</button>
                <button class="filter-btn" data-type="explains" onclick="toggleRelationFilter('explains', 'suggested', event)">설명</button>
                <button class="filter-btn" data-type="result_of" onclick="toggleRelationFilter('result_of', 'suggested', event)">결과</button>
                <button class="filter-btn" data-type="cause_of" onclick="toggleRelationFilter('cause_of', 'suggested', event)">원인</button>
                <button class="filter-btn" data-type="refers_to" onclick="toggleRelationFilter('refers_to', 'suggested', event)">참조</button>
              </div>
            </div>
            <div id="suggested-relations-list" class="relations-list">
              <div class="loading">추천 관계를 불러오는 중...</div>
            </div>
          </div>
        </div>

        <!-- 하단: 선택된 추천 관계 요약 + 한 번에 연결 버튼 -->
        <div id="relation-matching-summary" class="relation-matching-summary" style="display: none;">
          <div class="summary-text">
            <span id="selected-relations-count">0</span>개의 관계가 선택되었습니다.
          </div>
          <div class="summary-actions">
            <button class="btn btn-primary" onclick="applySelectedRelations(${chunk.id})">선택한 관계 연결</button>
            <button class="btn btn-secondary" onclick="clearSelectedRelations()">선택 취소</button>
          </div>
        </div>
      </div>
    `;

    // 관계 매칭 보드 초기화
    initializeRelationMatchingBoard(chunkId);

    // 추천 관계 로드
    loadSuggestedRelations(chunkId);

    // 기존 관계 필터 적용
    setTimeout(() => {
      applyRelationFilters("existing");
    }, 100);
  } catch (error) {
    console.error("관계 매칭 로드 실패:", error);
    contentDiv.innerHTML = '<div class="empty-state"><h3>오류 발생</h3><p>관계 매칭 정보를 불러올 수 없습니다.</p></div>';
  }
}

// 초기화
if (currentChunkId) {
  loadRelationMatching(currentChunkId);
} else {
  document.getElementById("relation-matching-content-wrapper").innerHTML = `
    <div class="empty-state">
      <h3>❌ 청크 ID가 없습니다</h3>
      <p>올바른 URL로 접근해주세요.</p>
      <button class="btn btn-primary" onclick="window.location.href='/knowledge'" style="margin-top: 15px;">
        목록으로 돌아가기
      </button>
    </div>
  `;
}
