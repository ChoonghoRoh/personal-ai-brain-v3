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

// Phase 7.7: 기존 관계 HTML 생성 헬퍼 함수
function generateExistingRelationsHTML(outgoingRelations, incomingRelations, chunkId) {
  const allRelations = [];

  // 나가는 관계
  (outgoingRelations || []).forEach((rel) => {
    allRelations.push({
      ...rel,
      direction: "outgoing",
      target_chunk_id: rel.target_chunk_id,
      content: rel.target_content || "내용 없음",
      relation_id: rel.id,
    });
  });

  // 들어오는 관계
  (incomingRelations || []).forEach((rel) => {
    allRelations.push({
      ...rel,
      direction: "incoming",
      source_chunk_id: rel.source_chunk_id,
      content: rel.source_content || "내용 없음",
      relation_id: rel.id,
    });
  });

  if (allRelations.length === 0) {
    return '<p style="color: #999; text-align: center; padding: 20px;">연결된 관계가 없습니다</p>';
  }

  return allRelations
    .map((rel) => {
      const confirmed = rel.confirmed === true || rel.confirmed === "true" || rel.confirmed === true;
      const confirmedBadge = confirmed ? '<span class="relation-confirmed-badge">✔ 확정</span>' : '<span class="relation-suggested-badge">⏳ 제안</span>';

      const relationId = rel.relation_id || rel.id || (rel.direction === "outgoing" ? rel.target_chunk_id : rel.source_chunk_id);

      return `
        <div class="relation-card" data-relation-id="${relationId}" data-direction="${rel.direction}" data-confirmed="${confirmed}" data-relation-type="${(
        rel.relation_type || ""
      )
        .toLowerCase()
        .replace(/\s+/g, "_")}">
          <div class="relation-card-header">
            <span class="relation-type-badge">${rel.relation_type || "관계 없음"}</span>
            ${confirmedBadge}
          </div>
          <div class="relation-card-content">${rel.content.substring(0, 150)}${rel.content.length > 150 ? "..." : ""}</div>
          <div class="relation-card-actions">
            <button class="btn-relation btn-relation-remove" onclick="removeRelation(${chunkId}, ${relationId}, '${rel.direction}', ${confirmed}, this)">
              해제
            </button>
          </div>
        </div>
      `;
    })
    .join("");
}

// Phase 7.7: 관계 매칭 보드 초기화
function initializeRelationMatchingBoard(chunkId) {
  // 선택된 관계 추적을 위한 Set 초기화
  if (!window.selectedRelations) {
    window.selectedRelations = new Set();
  }
  window.selectedRelations.clear();

  // Phase 7.9.3: 필터 상태 초기화
  if (!window.relationTypeFilters) {
    window.relationTypeFilters = {
      existing: new Set(["all"]),
      suggested: new Set(["all"]),
    };
  } else {
    window.relationTypeFilters.existing = new Set(["all"]);
    window.relationTypeFilters.suggested = new Set(["all"]);
  }
}

// Phase 7.9.3: 관계 타입 필터 토글
function toggleRelationFilter(relationType, area, event) {
  if (!window.relationTypeFilters) {
    window.relationTypeFilters = {
      existing: new Set(["all"]),
      suggested: new Set(["all"]),
    };
  }

  const filters = window.relationTypeFilters[area];
  const button = event.target;

  if (relationType === "all") {
    // "전체" 선택 시 모든 필터 해제하고 "전체"만 활성화
    filters.clear();
    filters.add("all");

    // 모든 필터 버튼 비활성화
    const filterContainer = area === "existing" ? document.getElementById("existing-relations-filters") : document.getElementById("suggested-relations-filters");
    filterContainer.querySelectorAll(".filter-btn").forEach((btn) => {
      btn.classList.remove("active");
    });
    button.classList.add("active");
  } else {
    // "전체" 해제
    filters.delete("all");

    // 선택한 타입 토글
    if (filters.has(relationType)) {
      filters.delete(relationType);
      button.classList.remove("active");
    } else {
      filters.add(relationType);
      button.classList.add("active");
    }

    // "전체" 버튼 비활성화
    const filterContainer = area === "existing" ? document.getElementById("existing-relations-filters") : document.getElementById("suggested-relations-filters");
    const allButton = filterContainer.querySelector(".filter-btn-all");
    if (allButton) {
      allButton.classList.remove("active");
    }

    // 필터가 모두 해제되면 "전체" 활성화
    if (filters.size === 0) {
      filters.add("all");
      if (allButton) {
        allButton.classList.add("active");
      }
    }
  }

  // 필터링 적용
  applyRelationFilters(area);
}

// Phase 7.9.3: 관계 필터 적용
function applyRelationFilters(area) {
  if (!window.relationTypeFilters) return;

  const filters = window.relationTypeFilters[area];
  const showAll = filters.has("all") || filters.size === 0;

  if (area === "existing") {
    // 기존 관계 필터링
    const relationCards = document.querySelectorAll("#existing-relations-list .relation-card");
    relationCards.forEach((card) => {
      const relationType = card.querySelector(".relation-type-badge")?.textContent.trim() || "";
      const normalizedType = relationType.toLowerCase().replace(/\s+/g, "_");

      if (showAll || filters.has(normalizedType)) {
        card.style.display = "block";
      } else {
        card.style.display = "none";
      }
    });
  } else if (area === "suggested") {
    // 추천 관계 필터링
    const relationCards = document.querySelectorAll("#suggested-relations-list .relation-card");
    relationCards.forEach((card) => {
      const relationType = card.querySelector(".relation-type-badge")?.textContent.trim() || "similar";
      const normalizedType = relationType.toLowerCase().replace(/\s+/g, "_");

      if (showAll || filters.has(normalizedType)) {
        card.style.display = "block";
      } else {
        card.style.display = "none";
      }
    });
  }
}

// Phase 7.9.1: 유사도 점수에 따른 색상 계산
function getScoreColor(score) {
  if (score >= 0.9) return "#059669"; // 진한 초록
  if (score >= 0.7) return "#10b981"; // 초록
  if (score >= 0.5) return "#f59e0b"; // 노랑
  return "#ef4444"; // 빨강
}

// Phase 7.9.1: 추천 관계 로드 (공유 키워드/그룹 표시 포함)
async function loadSuggestedRelations(chunkId) {
  const suggestedList = document.getElementById("suggested-relations-list");
  if (!suggestedList) return;

  suggestedList.innerHTML = '<div class="loading">추천 관계를 불러오는 중...</div>';

  try {
    // 기준 청크 정보 가져오기 (라벨 포함)
    const chunkResponse = await fetch(`/api/knowledge/chunks/${chunkId}`);
    if (!chunkResponse.ok) throw new Error("기준 청크를 불러올 수 없습니다.");
    const chunkData = await chunkResponse.json();
    const sourceLabels = (chunkData.labels || []).map((l) => ({ id: l.id, name: l.name, label_type: l.label_type }));

    // 추천 관계 가져오기
    const response = await fetch(`/api/knowledge/relations/suggest?chunk_id=${chunkId}&limit=10`);
    if (!response.ok) throw new Error("추천 관계를 불러올 수 없습니다.");

    const data = await response.json();
    const suggestions = data.suggestions || [];

    if (suggestions.length === 0) {
      suggestedList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">추천 관계가 없습니다</p>';
      return;
    }

    // 현재 연결된 관계 ID 목록 가져오기
    const existingRelationIds = new Set();
    (chunkData.outgoing_relations || []).forEach((rel) => {
      if (rel.target_chunk_id) existingRelationIds.add(rel.target_chunk_id);
    });
    (chunkData.incoming_relations || []).forEach((rel) => {
      if (rel.source_chunk_id) existingRelationIds.add(rel.source_chunk_id);
    });

    // 각 추천 청크의 라벨 정보 가져오기 및 공유 라벨 찾기
    const suggestionsWithSharedLabels = await Promise.all(
      suggestions.map(async (suggestion) => {
        try {
          const targetChunkResponse = await fetch(`/api/knowledge/chunks/${suggestion.target_chunk_id}`);
          if (!targetChunkResponse.ok) return { ...suggestion, sharedLabels: [] };
          const targetChunkData = await targetChunkResponse.json();
          const targetLabels = (targetChunkData.labels || []).map((l) => ({ id: l.id, name: l.name, label_type: l.label_type }));

          // 공유 라벨 찾기 (ID 기준)
          const sharedLabels = sourceLabels.filter((sl) => targetLabels.some((tl) => tl.id === sl.id));
          return { ...suggestion, sharedLabels: sharedLabels.slice(0, 3) }; // 최대 3개
        } catch (error) {
          console.error(`추천 청크 ${suggestion.target_chunk_id} 라벨 로드 실패:`, error);
          return { ...suggestion, sharedLabels: [] };
        }
      })
    );

    suggestedList.innerHTML = suggestionsWithSharedLabels
      .map((suggestion) => {
        const isConnected = existingRelationIds.has(suggestion.target_chunk_id);
        const scorePercent = Math.round((suggestion.score || 0) * 100);
        const sharedLabels = suggestion.sharedLabels || [];
        const sharedLabelsHTML =
          sharedLabels.length > 0
            ? `
              <div class="shared-labels">
                ${sharedLabels.map((label) => `<span class="shared-label-badge">${label.name}</span>`).join("")}
              </div>
            `
            : "";

        const relationType = suggestion.relation_type || "similar";
        const normalizedType = relationType.toLowerCase().replace(/\s+/g, "_");

        return `
          <div class="relation-card ${isConnected ? "disabled" : ""}" 
               data-suggestion-id="${suggestion.target_chunk_id}"
               data-relation-type="${normalizedType}"
               onclick="${isConnected ? "" : `toggleRelationSelection(${suggestion.target_chunk_id}, this)`}">
            <div class="relation-card-header">
              <span class="relation-type-badge">${relationType}</span>
              ${isConnected ? '<span class="relation-confirmed-badge">연결됨</span>' : ""}
            </div>
            <div class="relation-card-content">${suggestion.target_content_preview || "내용 없음"}</div>
            ${sharedLabelsHTML}
            <div class="relation-card-meta">
              <span style="font-size: 11px; color: ${getScoreColor(suggestion.score || 0)}; font-weight: 600;">유사도: ${scorePercent}%</span>
            </div>
            <div class="relation-score-bar">
              <div class="relation-score-fill" style="width: ${scorePercent}%; background: ${getScoreColor(suggestion.score || 0)};"></div>
            </div>
            ${
              !isConnected
                ? `
              <div class="relation-card-actions">
                <button class="btn-relation btn-relation-connect" onclick="event.stopPropagation(); connectRelation(${chunkId}, ${
                    suggestion.target_chunk_id
                  }, '${relationType}', ${suggestion.score || 0.7})">
                  연결
                </button>
                <button class="btn-relation btn-relation-ignore" onclick="event.stopPropagation(); ignoreRelation(${suggestion.target_chunk_id})">
                  무시
                </button>
              </div>
            `
                : ""
            }
          </div>
        `;
      })
      .join("");

    // Phase 7.9.3: 추천 관계 로드 후 필터 적용
    setTimeout(() => {
      applyRelationFilters("suggested");
    }, 100);
  } catch (error) {
    console.error("추천 관계 로드 실패:", error);
    suggestedList.innerHTML = '<p style="color: #dc2626; text-align: center; padding: 20px;">추천 관계를 불러올 수 없습니다</p>';
  }
}

// Phase 7.7: 관계 선택 토글
function toggleRelationSelection(targetChunkId, cardElement) {
  if (!window.selectedRelations) {
    window.selectedRelations = new Set();
  }

  if (window.selectedRelations.has(targetChunkId)) {
    window.selectedRelations.delete(targetChunkId);
    cardElement.classList.remove("selected");
  } else {
    window.selectedRelations.add(targetChunkId);
    cardElement.classList.add("selected");
  }

  updateRelationMatchingSummary();
}

// Phase 7.7: 관계 매칭 요약 업데이트
function updateRelationMatchingSummary() {
  const summary = document.getElementById("relation-matching-summary");
  const countSpan = document.getElementById("selected-relations-count");

  if (!summary || !countSpan) return;

  if (!window.selectedRelations || window.selectedRelations.size === 0) {
    summary.style.display = "none";
  } else {
    summary.style.display = "flex";
    countSpan.textContent = window.selectedRelations.size;
  }
}

// Phase 7.7: 선택한 관계 일괄 연결
async function applySelectedRelations(chunkId) {
  if (!window.selectedRelations || window.selectedRelations.size === 0) {
    alert("선택한 관계가 없습니다.");
    return;
  }

  try {
    const relations = Array.from(window.selectedRelations);
    let successCount = 0;
    let failCount = 0;

    for (const targetChunkId of relations) {
      try {
        const response = await fetch(`/api/knowledge/relations/suggest/${chunkId}/apply?target_chunk_id=${targetChunkId}&relation_type=similar&score=0.7`, {
          method: "POST",
        });

        if (response.ok) {
          successCount++;
        } else {
          failCount++;
        }
      } catch (error) {
        failCount++;
      }
    }

    alert(`${successCount}개의 관계가 연결되었습니다.${failCount > 0 ? ` (${failCount}개 실패)` : ""}`);

    // 청크 상세 정보 새로고침
    loadChunkDetail(chunkId);
    if (window.selectedRelations) {
      window.selectedRelations.clear();
    }
    updateRelationMatchingSummary();
  } catch (error) {
    console.error("관계 연결 실패:", error);
    alert("관계 연결 중 오류가 발생했습니다.");
  }
}

// Phase 7.7: 선택 취소
function clearSelectedRelations() {
  if (window.selectedRelations) {
    window.selectedRelations.clear();
  }
  document.querySelectorAll(".relation-card.selected").forEach((card) => {
    card.classList.remove("selected");
  });
  updateRelationMatchingSummary();
}

// Phase 7.7: 단일 관계 연결
async function connectRelation(chunkId, targetChunkId, relationType, score) {
  try {
    const response = await fetch(`/api/knowledge/relations/suggest/${chunkId}/apply?target_chunk_id=${targetChunkId}&relation_type=${relationType}&score=${score}`, {
      method: "POST",
    });

    if (!response.ok) throw new Error("관계 연결 실패");

    alert("관계가 연결되었습니다.");
    loadChunkDetail(chunkId);
  } catch (error) {
    console.error("관계 연결 실패:", error);
    alert("관계 연결 중 오류가 발생했습니다.");
  }
}

// Phase 7.7: 관계 무시
function ignoreRelation(targetChunkId) {
  // 선택에서 제거
  if (window.selectedRelations) {
    window.selectedRelations.delete(targetChunkId);
  }

  // 카드 숨기기
  const card = document.querySelector(`[data-suggestion-id="${targetChunkId}"]`);
  if (card) {
    card.style.display = "none";
  }

  updateRelationMatchingSummary();
}

// Phase 7.9.1: 관계 해제 (확정/제안 구분)
async function removeRelation(chunkId, relationId, direction, isConfirmed, buttonElement) {
  // 확정 관계인 경우 더 강한 확인 메시지
  const confirmMessage = isConfirmed ? "이 관계는 확정된 관계입니다. 정말 해제하시겠습니까?" : "이 관계를 해제하시겠습니까?";

  if (!confirm(confirmMessage)) return;

  try {
    const response = await fetch(`/api/relations/${relationId}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("관계 해제 실패");

    alert("관계가 해제되었습니다.");
    loadChunkDetail(chunkId);
  } catch (error) {
    console.error("관계 해제 실패:", error);
    alert("관계 해제 중 오류가 발생했습니다.");
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
