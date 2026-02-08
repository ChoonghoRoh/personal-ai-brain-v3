// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "💡 라벨 매칭",
      subtitle: "AI 추천 라벨을 연결하세요",
      currentPath: "/knowledge-label-matching",
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

// 상세 페이지로 돌아가기
function goBackToDetail() {
  if (currentChunkId) {
    window.location.href = `/knowledge-detail?id=${currentChunkId}`;
  } else {
    window.location.href = "/knowledge";
  }
}

// 청크 정보 및 라벨 매칭 패널 로드
async function loadLabelMatching(chunkId) {
  const contentDiv = document.getElementById("label-matching-content-wrapper");
  if (!contentDiv) {
    console.error("라벨 매칭 컨텐츠 요소를 찾을 수 없습니다.");
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

    // 헤더 제목 업데이트
    const headerTitle = document.getElementById("chunk-title-header");
    if (headerTitle) {
      const chunkTitle = chunk.title || chunk.content.substring(0, 50).replace(/\n/g, " ").trim() + (chunk.content.length > 50 ? "..." : "") || "제목 없음";
      headerTitle.textContent = chunkTitle;
    }

    contentDiv.innerHTML = `
      <div class="chunk-detail-section">
        <div class="chunk-meta">
          ${chunk.project_name ? `<span><strong>${chunk.project_name}</strong></span><span>/</span>` : ""}
          <span>${chunk.document_name || "알 수 없음"}</span>
          <span>(청크 #${chunk.chunk_index})</span>
        </div>
        <div class="chunk-content">${formatTextWithLineBreaks(chunk.content.substring(0, 300))}${chunk.content.length > 300 ? "..." : ""}</div>
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
      
      <!-- 라벨 매칭 패널 -->
      <div class="chunk-detail-section">
        <div class="label-matching-panel">
          <div class="label-matching-tabs">
            <button class="matching-tab active" onclick="switchLabelMatchingTab('keywords', ${chunk.id}, event)">추천 키워드</button>
            <button class="matching-tab" onclick="switchLabelMatchingTab('groups', ${chunk.id}, event)">추천 그룹</button>
          </div>
          <div id="label-matching-content" class="label-matching-content">
            <div class="loading">추천 라벨을 불러오는 중...</div>
          </div>
        </div>
      </div>
    `;

    // 첫 번째 탭 자동 로드
    setTimeout(() => {
      switchLabelMatchingTab("keywords", chunkId, null);
    }, 100);
  } catch (error) {
    console.error("라벨 매칭 로드 실패:", error);
    contentDiv.innerHTML = '<div class="empty-state"><h3>오류 발생</h3><p>라벨 매칭 정보를 불러올 수 없습니다.</p></div>';
  }
}

// 라벨 매칭 탭 전환
async function switchLabelMatchingTab(tabType, chunkId, event) {
  // 탭 버튼 활성화
  document.querySelectorAll(".matching-tab").forEach((btn) => btn.classList.remove("active"));
  if (event && event.target) {
    event.target.classList.add("active");
  } else {
    // event가 없으면 첫 번째 탭을 활성화
    const tabs = document.querySelectorAll(".matching-tab");
    if (tabs.length > 0) {
      const activeIndex = tabType === "keywords" ? 0 : 1;
      if (tabs[activeIndex]) tabs[activeIndex].classList.add("active");
    }
  }

  const contentDiv = document.getElementById("label-matching-content");
  if (!contentDiv) return;

  contentDiv.innerHTML = '<div class="loading">추천 라벨을 불러오는 중...</div>';

  try {
    // 추천 라벨 가져오기
    const response = await fetch(`/api/knowledge/labels/suggest?chunk_id=${chunkId}`);
    if (!response.ok) throw new Error("추천 라벨을 불러올 수 없습니다.");

    const data = await response.json();
    const suggestions = data.suggestions || [];

    // 현재 연결된 라벨 ID 목록 가져오기
    const chunkResponse = await fetch(`/api/knowledge/chunks/${chunkId}`);
    const chunkData = await chunkResponse.json();
    const connectedLabelIds = (chunkData.labels || []).map((l) => l.id);

    // 탭 타입에 따라 필터링
    const filtered = suggestions.filter((s) => {
      if (tabType === "keywords") {
        return s.label_type === "keyword";
      } else if (tabType === "groups") {
        return s.label_type === "keyword_group";
      }
      return true;
    });

    if (filtered.length === 0) {
      contentDiv.innerHTML = `<div class="empty-state"><p>추천 ${tabType === "keywords" ? "키워드" : "그룹"}가 없습니다.</p></div>`;
      return;
    }

    // 카드 목록 생성
    contentDiv.innerHTML = filtered
      .map((suggestion) => {
        const isConnected = connectedLabelIds.includes(suggestion.label_id);
        return `
          <div class="label-suggestion-card ${isConnected ? "disabled" : ""}">
            <div class="label-suggestion-info">
              <div class="label-suggestion-name">${suggestion.label_name}</div>
              <div class="label-suggestion-meta">
                타입: ${suggestion.label_type} · 신뢰도: ${(suggestion.confidence * 100).toFixed(0)}%
              </div>
            </div>
            <div class="label-suggestion-action">
              ${
                isConnected
                  ? '<button class="btn-add-label" disabled>연결됨</button>'
                  : `<button class="btn-add-label" onclick="addSuggestedLabel(${chunkId}, ${suggestion.label_id}, ${suggestion.confidence})">추가</button>`
              }
            </div>
          </div>
        `;
      })
      .join("");
  } catch (error) {
    console.error("추천 라벨 로드 실패:", error);
    contentDiv.innerHTML = `<div class="empty-state"><p>추천 라벨을 불러올 수 없습니다.</p></div>`;
  }
}

// 추천 라벨 추가
async function addSuggestedLabel(chunkId, labelId, confidence) {
  try {
    const response = await fetch(`/api/knowledge/chunks/${chunkId}/labels`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        label_ids: [labelId],
        status: "confirmed",
        source: "human",
      }),
    });

    if (!response.ok) throw new Error("라벨 추가 실패");

    // 성공 메시지
    alert("라벨이 추가되었습니다.");

    // 라벨 매칭 정보 새로고침
    loadLabelMatching(chunkId);
  } catch (error) {
    console.error("라벨 추가 실패:", error);
    alert("라벨 추가 중 오류가 발생했습니다.");
  }
}

// 라벨 제거
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

    // 라벨 매칭 정보 새로고침
    loadLabelMatching(chunkId);
  } catch (error) {
    console.error("라벨 제거 실패:", error);
    alert("라벨 제거 중 오류가 발생했습니다.");
  }
}

// 초기화
if (currentChunkId) {
  loadLabelMatching(currentChunkId);
} else {
  document.getElementById("label-matching-content-wrapper").innerHTML = `
    <div class="empty-state">
      <h3>❌ 청크 ID가 없습니다</h3>
      <p>올바른 URL로 접근해주세요.</p>
      <button class="btn btn-primary" onclick="window.location.href='/knowledge'" style="margin-top: 15px;">
        목록으로 돌아가기
      </button>
    </div>
  `;
}
