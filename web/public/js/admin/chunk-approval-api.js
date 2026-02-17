/**
 * 청크 승인 관리 API 모듈
 * ChunkApprovalManager에서 사용하는 API fetch 함수들
 * Traditional script 패턴 (전역 함수)
 */

/**
 * 승인 대기 청크 목록 로드
 * @param {string} status - 상태 필터
 * @param {number} limit - 페이지 크기
 * @param {number} offset - 오프셋
 * @returns {Promise<Object>} API 응답 데이터
 */
async function fetchPendingChunksApi(status, limit, offset) {
  let url = `/api/approval/chunks/pending?status=${status}`;
  if (limit != null) url += `&limit=${limit}&offset=${offset || 0}`;
  else url += `&limit=50`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("청크 목록을 불러올 수 없습니다.");
  return response.json();
}

/**
 * 청크 승인
 * @param {number} chunkId - 청크 ID
 * @returns {Promise<void>}
 */
async function approveChunkApi(chunkId) {
  const response = await fetch(`/api/approval/chunks/${chunkId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ approved_by: "admin" }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "청크 승인 실패");
  }
}

/**
 * 청크 일괄 승인
 * @param {number[]} chunkIds - 청크 ID 배열
 * @returns {Promise<Object>} API 응답
 */
async function batchApproveChunksApi(chunkIds) {
  const response = await fetch("/api/approval/chunks/batch/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chunk_ids: chunkIds, approved_by: "admin" }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "일괄 승인 실패");
  }
  return response.json();
}

/**
 * 청크 거절
 * @param {number} chunkId - 청크 ID
 * @param {string|null} reason - 거절 사유
 * @returns {Promise<void>}
 */
async function rejectChunkApi(chunkId, reason) {
  const response = await fetch(`/api/approval/chunks/${chunkId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason: reason || null }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "청크 거절 실패");
  }
}

/**
 * 청크 상세 정보 로드
 * @param {number} chunkId - 청크 ID
 * @returns {Promise<Object>} 청크 데이터
 */
async function fetchChunkDetailApi(chunkId) {
  const chunkResponse = await fetch(`/api/knowledge/chunks/${chunkId}`);
  if (!chunkResponse.ok) throw new Error("청크 정보를 불러올 수 없습니다.");
  return chunkResponse.json();
}

/**
 * 관계 추천 로드
 * @param {number} chunkId - 청크 ID
 * @returns {Promise<Array>} 추천 목록
 */
async function fetchRelationSuggestionsApi(chunkId) {
  try {
    const response = await fetch(`/api/knowledge/relations/suggest?chunk_id=${chunkId}&limit=5`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.suggestions || [];
  } catch (e) {
    console.error("관계 추천 로드 실패:", e);
    return [];
  }
}

/**
 * AI 키워드·라벨 추천 (청크 승인용)
 * @param {number} chunkId - 청크 ID
 * @returns {Promise<Object>} { suggestions, new_keywords, ... }
 */
async function fetchApprovalAiSuggestionsApi(chunkId) {
  const res = await fetch(`/api/knowledge/labels/suggest-llm?chunk_id=${chunkId}&limit=10`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "추천 요청 실패");
  return data;
}

/**
 * 라벨 제안 적용 (폴백용: LabelManager 없을 때)
 * @returns {Promise<void>}
 */
async function applyApprovalLabelSuggestionApi(chunkId, labelId, confidence) {
  const response = await fetch(`/api/knowledge/labels/suggest/${chunkId}/apply/${labelId}?confidence=${confidence}`, {
    method: "POST",
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "라벨 적용 실패");
  }
}

/**
 * 새 키워드를 라벨로 생성 후 청크에 연결 (청크 승인용)
 * @returns {Promise<void>}
 */
async function createApprovalKeywordLabelApi(chunkId, keyword) {
  const createRes = await fetch("/api/labels", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: keyword, label_type: "keyword", description: "" }),
  });
  const createData = await createRes.json();
  if (!createRes.ok) throw new Error(createData.detail || "라벨 생성 실패");
  const labelId = createData.id;
  const linkRes = await fetch(`/api/labels/chunks/${chunkId}/labels/${labelId}`, { method: "POST" });
  if (!linkRes.ok) {
    const err = await linkRes.json().catch(() => ({}));
    throw new Error(err.detail || "청크에 라벨 연결 실패");
  }
}
