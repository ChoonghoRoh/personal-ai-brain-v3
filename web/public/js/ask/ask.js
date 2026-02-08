/**
 * 로딩 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 메시지 (기본값: "로딩 중...")
 */
function showLoading(elementId, message = "로딩 중...") {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="loading">${escapeHtml(message)}</div>`;
  }
}

/**
 * 에러 메시지 표시
 * @param {string} elementId - 요소 ID
 * @param {string} message - 에러 메시지
 */
function showError(elementId, message) {
  const element = document.getElementById(elementId);
  if (element) {
    element.innerHTML = `<div class="loading" style="color: #ef4444;">${escapeHtml(message)}</div>`;
  }
}

// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "🤖 Personal AI Brain - AI Ask",
      subtitle: "AI 질의 및 응답",
      currentPath: "/ask",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }

  // 저장된 대화 기록 복원
  loadChatHistoryFromStorage();
});

let chatHistory = [];

// 로컬 스토리지 키
const CHAT_HISTORY_KEY = "ai_ask_chat_history";
const MAX_HISTORY_ITEMS = 50; // 최대 저장할 대화 기록 수

/**
 * 저장된 대화 기록 복원
 * 로컬 스토리지에서 대화 기록을 불러와서 표시
 */
function loadChatHistoryFromStorage() {
  try {
    const stored = localStorage.getItem(CHAT_HISTORY_KEY);
    if (stored) {
      chatHistory = JSON.parse(stored);
      // 최대 개수 제한
      if (chatHistory.length > MAX_HISTORY_ITEMS) {
        chatHistory = chatHistory.slice(-MAX_HISTORY_ITEMS);
        saveChatHistoryToStorage();
      }
      displayChatHistory();
    }
  } catch (error) {
    console.error("대화 기록 로드 실패:", error);
    chatHistory = [];
  }
}

/**
 * 대화 기록을 로컬 스토리지에 저장
 * 현재 대화 기록을 로컬 스토리지에 저장하여 다음 접속 시 복원
 */
function saveChatHistoryToStorage() {
  try {
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory));
  } catch (error) {
    console.error("대화 기록 저장 실패:", error);
    // 로컬 스토리지 용량 초과 시 오래된 항목 삭제
    if (error.name === "QuotaExceededError") {
      if (chatHistory.length > 10) {
        chatHistory = chatHistory.slice(-10);
        try {
          localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory));
        } catch (e) {
          console.error("대화 기록 저장 재시도 실패:", e);
        }
      }
    }
  }
}

/**
 * 대화 기록 표시
 * 저장된 대화 기록을 화면에 표시
 */
function displayChatHistory() {
  if (chatHistory.length > 0) {
    document.getElementById("chat-history").style.display = "block";
    const chatItemsHtml = chatHistory
      .slice()
      .reverse()
      .map(
        (item) => `
        <div class="chat-item">
          <div class="chat-question">Q: ${escapeHtml(item.question)}</div>
          <div class="chat-answer">A: ${escapeHtml(item.answer)}</div>
          ${item.sources && item.sources.length > 0 ? `<div class="chat-sources" style="margin-top: 8px; font-size: 12px; color: #666;">참고: ${item.sources.length}개 문서</div>` : ""}
        </div>
      `
      )
      .join("");
    document.getElementById("chat-items").innerHTML = chatItemsHtml;
  } else {
    document.getElementById("chat-history").style.display = "none";
  }
}

// 대화 기록 내보내기
function exportChatHistory(format = "json") {
  if (chatHistory.length === 0) {
    alert("내보낼 대화 기록이 없습니다.");
    return;
  }

  let content = "";
  let filename = "";
  let mimeType = "";

  if (format === "json") {
    content = JSON.stringify(chatHistory, null, 2);
    filename = `chat-history-${new Date().toISOString().split("T")[0]}.json`;
    mimeType = "application/json";
  } else if (format === "markdown") {
    content = chatHistory
      .slice()
      .reverse()
      .map((item, index) => {
        const sourcesText = item.sources && item.sources.length > 0
          ? `\n\n**참고 문서:**\n${item.sources.map(s => `- ${s.file} (유사도: ${(s.score * 100).toFixed(1)}%)`).join("\n")}`
          : "";
        return `## 대화 ${index + 1}\n\n**질문:**\n${item.question}\n\n**답변:**\n${item.answer}${sourcesText}\n\n---\n`;
      })
      .join("\n");
    filename = `chat-history-${new Date().toISOString().split("T")[0]}.md`;
    mimeType = "text/markdown";
  }

  // 파일 다운로드
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * 대화 기록 삭제
 * 모든 대화 기록을 삭제하고 로컬 스토리지에서도 제거
 */
function clearChatHistory() {
  if (!confirm("모든 대화 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
    return;
  }

  chatHistory = [];
  saveChatHistoryToStorage();
  displayChatHistory();
  alert("대화 기록이 삭제되었습니다.");
}

/**
 * 질문 요청 데이터 준비
 * @returns {Object|null} 요청 데이터 또는 null (검증 실패 시)
 */
function prepareQuestionRequest() {
  const question = document.getElementById("question-input").value.trim();
  const contextEnabled = document.getElementById("context-enabled").checked;

  if (!question) {
    alert("질문을 입력하세요.");
    return null;
  }

  return {
    question: question,
    context_enabled: contextEnabled,
    top_k: 5,
    max_tokens: 500,
    temperature: 0.7,
  };
}

/**
 * UI 초기화
 */
function initializeAskUI() {
  const askButton = document.getElementById("ask-button");
  const responsePanel = document.getElementById("response-panel");

  askButton.disabled = true;
  askButton.textContent = "처리 중...";
  responsePanel.style.display = "block";
  showLoading("answer-box", "답변을 생성하는 중...");
  document.getElementById("sources-list").innerHTML = "";
}

/**
 * 질문 API 호출
 * @param {Object} requestData - 요청 데이터
 * @returns {Promise<Object>} API 응답 데이터
 */
async function executeQuestion(requestData) {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestData),
  });

  const data = await response.json();
  return data;
}

/**
 * 답변 표시
 * @param {Object} data - API 응답 데이터
 */
function displayAnswer(data) {
  const answerBox = document.getElementById("answer-box");
  answerBox.innerHTML = ""; // 기존 내용 초기화
  
  const answerText = document.createElement("div");
  answerText.style.cssText = "white-space: pre-wrap; line-height: 1.8;";
  answerText.textContent = data.answer || "답변을 생성할 수 없습니다.";
  answerBox.appendChild(answerText);
  
  // 모델 정보 및 오류 표시
  if (data.error) {
    const errorInfo = document.createElement("div");
    errorInfo.style.cssText = "margin-top: 15px; padding: 12px; background: #fef3c7; border-radius: 6px; font-size: 13px; color: #92400e; border-left: 4px solid #f59e0b;";
    errorInfo.innerHTML = `<strong>⚠️ 주의:</strong> ${escapeHtml(data.error)}`;
    answerBox.appendChild(errorInfo);
  } else if (data.model_used) {
    const modelInfo = document.createElement("div");
    modelInfo.style.cssText = "margin-top: 15px; padding: 12px; background: #dbeafe; border-radius: 6px; font-size: 13px; color: #1e40af; border-left: 4px solid #2563eb;";
    modelInfo.innerHTML = `<strong>✅ AI 모델 사용:</strong> ${escapeHtml(data.model_used)} (추론적 답변 생성됨)`;
    answerBox.appendChild(modelInfo);
  }
}

/**
 * 참고 문서 표시
 * @param {Array} sources - 참고 문서 배열
 */
function displaySources(sources) {
  if (sources && sources.length > 0) {
    const sourcesHtml = sources
      .map(
        (source) => `
      <li class="source-item">
        <div class="source-header">
          <div class="source-file">${escapeHtml(source.file || "Unknown")}</div>
          <div class="source-score">유사도: ${(source.score * 100).toFixed(1)}%</div>
        </div>
        <div class="source-snippet">${escapeHtml(source.snippet || "")}</div>
      </li>
    `
      )
      .join("");
    document.getElementById("sources-list").innerHTML = sourcesHtml;
  }
}

/**
 * 대화 기록 업데이트
 * @param {string} question - 질문
 * @param {Object} data - API 응답 데이터
 */
async function updateConversationHistory(question, data) {
  const chatItem = {
    question: question,
    answer: data.answer,
    sources: data.sources,
    timestamp: new Date().toISOString(),
  };
  chatHistory.push(chatItem);

  // 최대 개수 제한
  if (chatHistory.length > MAX_HISTORY_ITEMS) {
    chatHistory = chatHistory.slice(-MAX_HISTORY_ITEMS);
  }

  // 로컬 스토리지에 저장
  saveChatHistoryToStorage();

  // 서버에 저장 (선택적, 오류 발생해도 계속 진행)
  try {
    const sessionId = getSessionId();
    await fetch("/api/conversations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        answer: data.answer,
        sources: data.sources,
        model_used: data.model_used,
        session_id: sessionId
      })
    });
  } catch (error) {
    console.warn("서버에 대화 기록 저장 실패 (로컬 스토리지는 저장됨):", error);
  }

  // 대화 기록 표시
  displayChatHistory();
}

/**
 * 세션 ID 생성/가져오기
 */
function getSessionId() {
  let sessionId = sessionStorage.getItem("conversation_session_id");
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem("conversation_session_id", sessionId);
  }
  return sessionId;
}

/**
 * UI 상태 복원
 */
function restoreAskUI() {
  const askButton = document.getElementById("ask-button");
  askButton.disabled = false;
  askButton.textContent = "질문하기";
}

/**
 * 질문하기 (메인 함수)
 */
async function askQuestion() {
  // 요청 데이터 준비
  const requestData = prepareQuestionRequest();
  if (!requestData) {
    return;
  }

  // UI 초기화
  initializeAskUI();

  try {
    // 질문 실행
    const data = await executeQuestion(requestData);

    // 답변 표시
    displayAnswer(data);

    // 참고 문서 표시
    displaySources(data.sources);

    // 대화 기록 업데이트
    updateConversationHistory(requestData.question, data);
  } catch (error) {
    console.error("질의 오류:", error);
    showError("answer-box", error.message);
  } finally {
    restoreAskUI();
  }
}
