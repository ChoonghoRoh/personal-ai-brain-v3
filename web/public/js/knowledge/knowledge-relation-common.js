/**
 * 관계 매칭 공통 함수 모듈
 * knowledge-detail.js와 knowledge-relation-matching.js에서 공유하는 함수들
 *
 * 사용 전 각 페이지에서 window._relationReloadFn을 설정해야 합니다.
 * 예: window._relationReloadFn = loadChunkDetail;
 */

// 기존 관계 HTML 생성 헬퍼 함수
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

// 관계 매칭 보드 초기화
function initializeRelationMatchingBoard(chunkId) {
  // 선택된 관계 추적을 위한 Set 초기화
  if (!window.selectedRelations) {
    window.selectedRelations = new Set();
  }
  window.selectedRelations.clear();

  // 필터 상태 초기화
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

// 관계 타입 필터 토글
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

// 관계 필터 적용
function applyRelationFilters(area) {
  if (!window.relationTypeFilters) return;

  const filters = window.relationTypeFilters[area];
  const showAll = filters.has("all") || filters.size === 0;

  if (area === "existing") {
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

// 유사도 점수에 따른 색상 계산
function getScoreColor(score) {
  if (score >= 0.9) return "#059669";
  if (score >= 0.7) return "#10b981";
  if (score >= 0.5) return "#f59e0b";
  return "#ef4444";
}

// 추천 관계 로드 (공유 키워드/그룹 표시 포함)
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
          return { ...suggestion, sharedLabels: sharedLabels.slice(0, 3) };
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

    // 추천 관계 로드 후 필터 적용
    setTimeout(() => {
      applyRelationFilters("suggested");
    }, 100);
  } catch (error) {
    console.error("추천 관계 로드 실패:", error);
    suggestedList.innerHTML = '<p style="color: #dc2626; text-align: center; padding: 20px;">추천 관계를 불러올 수 없습니다</p>';
  }
}

// 관계 선택 토글
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

// 관계 매칭 요약 업데이트
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

// 선택한 관계 일괄 연결 (리로드는 window._relationReloadFn 사용)
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

    // 페이지별 리로드 함수 호출
    if (window._relationReloadFn) {
      window._relationReloadFn(chunkId);
    }
    if (window.selectedRelations) {
      window.selectedRelations.clear();
    }
    updateRelationMatchingSummary();
  } catch (error) {
    console.error("관계 연결 실패:", error);
    alert("관계 연결 중 오류가 발생했습니다.");
  }
}

// 선택 취소
function clearSelectedRelations() {
  if (window.selectedRelations) {
    window.selectedRelations.clear();
  }
  document.querySelectorAll(".relation-card.selected").forEach((card) => {
    card.classList.remove("selected");
  });
  updateRelationMatchingSummary();
}

// 단일 관계 연결 (리로드는 window._relationReloadFn 사용)
async function connectRelation(chunkId, targetChunkId, relationType, score) {
  try {
    const response = await fetch(`/api/knowledge/relations/suggest/${chunkId}/apply?target_chunk_id=${targetChunkId}&relation_type=${relationType}&score=${score}`, {
      method: "POST",
    });

    if (!response.ok) throw new Error("관계 연결 실패");

    alert("관계가 연결되었습니다.");
    if (window._relationReloadFn) {
      window._relationReloadFn(chunkId);
    }
  } catch (error) {
    console.error("관계 연결 실패:", error);
    alert("관계 연결 중 오류가 발생했습니다.");
  }
}

// 관계 무시
function ignoreRelation(targetChunkId) {
  if (window.selectedRelations) {
    window.selectedRelations.delete(targetChunkId);
  }

  const card = document.querySelector(`[data-suggestion-id="${targetChunkId}"]`);
  if (card) {
    card.style.display = "none";
  }

  updateRelationMatchingSummary();
}

// 관계 해제 (리로드는 window._relationReloadFn 사용)
async function removeRelation(chunkId, relationId, direction, isConfirmed, buttonElement) {
  const confirmMessage = isConfirmed ? "이 관계는 확정된 관계입니다. 정말 해제하시겠습니까?" : "이 관계를 해제하시겠습니까?";

  if (!confirm(confirmMessage)) return;

  try {
    const response = await fetch(`/api/relations/${relationId}`, {
      method: "DELETE",
    });

    if (!response.ok) throw new Error("관계 해제 실패");

    alert("관계가 해제되었습니다.");
    if (window._relationReloadFn) {
      window._relationReloadFn(chunkId);
    }
  } catch (error) {
    console.error("관계 해제 실패:", error);
    alert("관계 해제 중 오류가 발생했습니다.");
  }
}
