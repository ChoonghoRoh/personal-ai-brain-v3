// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "📄 청크 상세",
      subtitle: "청크 상세 정보 및 관계 관리",
      currentPath: "/knowledge-detail",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

let currentChunkId = null;

// 관계 변경 후 리로드 콜백 설정
window._relationReloadFn = function (chunkId) {
  loadChunkDetail(chunkId);
};

// URL 파라미터에서 id 확인
const urlParams = new URLSearchParams(window.location.search);
const chunkIdParam = urlParams.get("id");
if (chunkIdParam) {
  currentChunkId = parseInt(chunkIdParam);
}

// 청크 상세 로드
async function loadChunkDetail(chunkId) {
  // 전역 변수 업데이트
  currentChunkId = chunkId;

  const contentDiv = document.getElementById("chunk-detail-content");
  if (!contentDiv) {
    console.error("청크 상세 요소를 찾을 수 없습니다.");
    return;
  }

  contentDiv.innerHTML = '<div class="loading">⏳ 청크 정보를 불러오는 중...</div>';

  try {
    const response = await fetch(`/api/knowledge/chunks/${chunkId}`);

    // HTTP 오류 처리
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: `HTTP ${response.status}: ${response.statusText}` }));
      throw new Error(errorData.detail || `서버 오류 (${response.status})`);
    }

    const chunk = await response.json();

    // 데이터 유효성 검사
    if (!chunk || !chunk.id) {
      throw new Error("유효하지 않은 청크 데이터입니다.");
    }

    // 배열 데이터 기본값 설정 (undefined 방지)
    if (!chunk.labels) chunk.labels = [];
    if (!chunk.outgoing_relations) chunk.outgoing_relations = [];
    if (!chunk.incoming_relations) chunk.incoming_relations = [];

    // 헤더 업데이트: 청크 제목으로 변경
    const titleElement = document.getElementById("chunk-title");
    if (titleElement) {
      // 제목이 있으면 사용, 없으면 content의 첫 50자 사용
      const titleText = chunk.title || (chunk.content ? chunk.content.substring(0, 50).replace(/\n/g, " ").trim() + (chunk.content.length > 50 ? "..." : "") : "청크 상세");
      titleElement.textContent = titleText;
    }

    // 헤더 버튼 표시 및 이벤트 연결
    const btnLabelMatching = document.getElementById("btn-label-matching");
    const btnRelationMatching = document.getElementById("btn-relation-matching");
    const btnReasoning = document.getElementById("btn-reasoning");

    if (btnLabelMatching) {
      btnLabelMatching.style.display = "inline-block";
      btnLabelMatching.onclick = () => (window.location.href = `/knowledge-label-matching?id=${chunkId}`);
    }
    if (btnRelationMatching) {
      btnRelationMatching.style.display = "inline-block";
      btnRelationMatching.onclick = () => (window.location.href = `/knowledge-relation-matching?id=${chunkId}`);
    }
    if (btnReasoning) {
      btnReasoning.style.display = "inline-block";
      btnReasoning.onclick = () => startReasoning(chunkId);
    }

    contentDiv.innerHTML = `
      <div class="chunk-detail-section">
        <div class="chunk-meta">
          ${chunk.project_name ? `<span><strong>${chunk.project_name}</strong></span><span>/</span>` : ""}
          <span>${chunk.document_name || "알 수 없음"}</span>
          <span>(청크 #${chunk.chunk_index})</span>
        </div>
        <div class="chunk-content">${formatTextWithLineBreaks(chunk.content) || "내용이 없습니다."}</div>
      </div>

      <div class="chunk-detail-section">
        <h4>🏷️ 연결된 라벨</h4>
        <div class="chunk-labels" id="chunk-labels-list">
          ${
            chunk.labels.length > 0
              ? chunk.labels
                  .map(
                    (label) => `
                <span class="label-chip" data-label-id="${label.id}">
                  ${label.name || "이름 없음"}
                  <span class="label-type-badge">${label.label_type || "타입 없음"}</span>
                  <button class="label-chip-remove" onclick="removeLabelFromChunk(${chunk.id}, ${label.id}, this)" title="라벨 제거">×</button>
                </span>
              `
                  )
                  .join("")
              : '<span style="color: #999;">라벨이 없습니다</span>'
          }
        </div>
      </div>

      <!-- 관계 매칭 탭 (임시로 유지, 나중에 제거 예정) -->
      <div id="chunk-detail-tab-relations" class="chunk-detail-tab-content" style="display: none;">
          <div class="relation-matching-board">
            <div class="relation-matching-layout">
              <!-- 좌측: 기준 청크 카드 -->
              <div class="relation-matching-left">
                <h4>기준 청크</h4>
                <div class="chunk-card-preview">
                  <div class="chunk-preview-content">${chunk.content.substring(0, 200)}${chunk.content.length > 200 ? "..." : ""}</div>
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
        </div>
      </div>
    `;

    // 관계 매칭 보드 초기화
    initializeRelationMatchingBoard(chunkId);

    // Phase 7.9.3: 기존 관계 필터 적용
    setTimeout(() => {
      applyRelationFilters("existing");
    }, 100);
  } catch (error) {
    console.error("청크 상세 로드 실패:", error);
    contentDiv.innerHTML = '<div class="empty-state"><h3>오류 발생</h3><p>청크 상세 정보를 불러올 수 없습니다.</p></div>';
  }
}

// Reasoning 시작
function startReasoning(chunkId) {
  window.location.href = `/reason?seed_chunk=${chunkId}`;
}

// Phase 7.7: 라벨 제거
async function removeLabelFromChunk(chunkId, labelId, buttonElement) {
  if (!confirm("이 라벨을 제거하시겠습니까?")) return;

  try {
    const response = await fetch(`/api/knowledge/chunks/${chunkId}/labels`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        label_ids: [labelId],
      }),
    });

    if (!response.ok) throw new Error("라벨 제거 실패");

    // UI에서 제거
    buttonElement.closest(".label-chip").remove();

    // 청크 상세 정보 새로고침
    loadChunkDetail(chunkId);
  } catch (error) {
    console.error("라벨 제거 실패:", error);
    alert("라벨 제거 중 오류가 발생했습니다.");
  }
}

// Phase 7.7: 청크 상세 탭 전환 (관계 매칭용, 임시 유지)
function switchChunkDetailTab(tabType, chunkId, event) {
  // 관계 탭으로 전환 시 추천 관계 로드
  if (tabType === "relations") {
    const relationsTab = document.getElementById("chunk-detail-tab-relations");
    if (relationsTab) {
      relationsTab.style.display = "block";
      loadSuggestedRelations(chunkId);
    }
  }
}

// 초기화
if (currentChunkId) {
  loadChunkDetail(currentChunkId);
} else {
  document.getElementById("chunk-detail-content").innerHTML = `
    <div class="empty-state">
      <h3>❌ 청크 ID가 없습니다</h3>
      <p>올바른 URL로 접근해주세요.</p>
      <button class="btn btn-primary" onclick="window.location.href='/knowledge'" style="margin-top: 15px;">
        목록으로 돌아가기
      </button>
    </div>
  `;
}
