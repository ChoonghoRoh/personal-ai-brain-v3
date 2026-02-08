// Layout 초기화
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  // Header 렌더링
  if (typeof renderHeader === "function") {
    renderHeader({
      title: "📄 Personal AI Brain - Document Viewer",
      subtitle: "문서 뷰어",
      currentPath: "/document",
    });
  } else {
    console.error("renderHeader 함수를 찾을 수 없습니다.");
  }
});

// URL에서 document_id 가져오기
// window.location.pathname은 이미 디코딩된 값을 반환함
const path = window.location.pathname;
let documentId = path.replace(/^\/document\//, "");

// 이중 인코딩 방지: 이미 인코딩된 경우 디코딩
try {
  const decoded = decodeURIComponent(documentId);
  // 디코딩 결과가 원본과 다르면 이미 인코딩된 것으로 간주
  if (decoded !== documentId && !decoded.includes('%')) {
    documentId = decoded;
  }
} catch (e) {
  // 디코딩 실패 시 원본 사용
}

// 이미 디코딩된 경로이므로 그대로 사용 (추가 인코딩 불필요)
// API 호출 시에는 한 번만 인코딩

async function loadDocument() {
  // 빈 문자열 체크 (함수 내부로 이동)
  if (!documentId) {
    document.getElementById("document-viewer").innerHTML = `
      <div class="error">
        <h2>문서 ID가 없습니다</h2>
        <p>올바른 문서 경로를 입력하세요.</p>
      </div>
    `;
    return;
  }

  try {
    // window.location.pathname은 이미 디코딩된 값을 반환하므로
    // documentId는 일반 경로 (예: brain/projects/alpha-project/roadmap.md)
    // FastAPI의 {document_id:path}는 슬래시를 포함한 경로를 자동으로 처리하므로
    // encodeURIComponent를 사용하여 인코딩 (슬래시는 %2F로 변환됨)
    const encodedId = encodeURIComponent(documentId);
    console.log("Loading document:", documentId, "-> encoded:", encodedId);
    const response = await fetch(`/api/documents/${encodedId}`);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }));
      const errorMsg = errorData.detail || `HTTP ${response.status}`;
      
      // 404 오류인 경우 경로 동기화 시도
      if (response.status === 404) {
        console.log("문서를 찾을 수 없습니다. 경로 동기화 시도...", documentId);
        try {
          // 경로 동기화 API 호출
          const syncResponse = await fetch(`/api/documents/sync/${encodeURIComponent(documentId)}`, {
            method: 'POST'
          });
          
          if (syncResponse.ok) {
            const syncData = await syncResponse.json();
            console.log("경로 동기화 완료:", syncData);
            
            // 동기화 후 다시 문서 로드 시도
            const retryResponse = await fetch(`/api/documents/${encodeURIComponent(documentId)}`);
            if (retryResponse.ok) {
              const retryData = await retryResponse.json();
              // 성공적으로 로드된 경우 정상 처리
              documentId = retryData.file_path || documentId;
              // 재귀 호출로 다시 로드
              return loadDocument();
            }
          }
        } catch (syncError) {
          console.error("경로 동기화 오류:", syncError);
        }
      }
      
      console.error("Document load error:", {
        status: response.status,
        statusText: response.statusText,
        error: errorMsg,
        url: `/api/documents/${encodeURIComponent(documentId)}`,
        documentId: documentId,
      });
      throw new Error(errorMsg);
    }

    const data = await response.json();

    const viewer = document.getElementById("document-viewer");

    // type이 없는 경우 처리
    if (!data.type) {
      viewer.innerHTML = `
        <div class="error">
          <h2>문서 형식을 확인할 수 없습니다</h2>
          <p>파일 경로: ${data.file_path || documentId}</p>
          <p>서버 응답에 파일 형식 정보가 없습니다.</p>
        </div>
      `;
      return;
    }

    if (data.type === "markdown") {
      // Markdown 렌더링
      // marked.parse() 결과에서 <script> 태그 제거하여 XSS 및 실행 오류 방지
      let html = marked.parse(data.content || "");

      // <script> 태그 제거 (보안 및 실행 오류 방지)
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = html;
      const scripts = tempDiv.querySelectorAll("script");
      scripts.forEach((script) => script.remove());
      html = tempDiv.innerHTML;

      viewer.innerHTML = `
        <div class="document-header">
          <div class="document-title">${data.name || data.file_path || documentId}</div>
          <div class="document-path">${data.file_path || documentId}</div>
          <div style="margin-top: 15px;">
            <button onclick="viewKnowledgeStructure(${
              data.id ? data.id : "null"
            })" style="padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 10px;">
              📊 지식 구조 보기
            </button>
          </div>
        </div>
        <div class="document-content">${html}</div>
      `;
    } else if (data.type === "text") {
      // 일반 텍스트 파일
      const content = (data.content || "").replace(/\n/g, "<br>");
      viewer.innerHTML = `
        <div class="document-header">
          <div class="document-title">${data.name || data.file_path || documentId}</div>
          <div class="document-path">${data.file_path || documentId}</div>
          <div style="margin-top: 15px;">
            <button onclick="viewKnowledgeStructure(${
              data.id ? data.id : "null"
            })" style="padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; margin-right: 10px;">
              📊 지식 구조 보기
            </button>
          </div>
        </div>
        <div class="document-content">
          <pre style="white-space: pre-wrap; font-family: inherit;">${content}</pre>
        </div>
      `;
    } else if (data.type === "pdf") {
      // PDF 뷰어
      viewer.innerHTML = `
        <div class="document-header">
          <div class="document-title">${data.name || data.file_path || documentId}</div>
          <div class="document-path">${data.file_path || documentId}</div>
        </div>
        <iframe class="pdf-viewer" src="/api/documents/${encodeURIComponent(documentId)}?format=pdf" type="application/pdf"></iframe>
      `;
    } else if (data.type === "docx") {
      // DOCX 파일 안내
      viewer.innerHTML = `
        <div class="document-header">
          <div class="document-title">${data.name || data.file_path || documentId}</div>
          <div class="document-path">${data.file_path || documentId}</div>
        </div>
        <div class="error">
          <h2>DOCX 파일</h2>
          <p>DOCX 파일은 아직 웹에서 직접 볼 수 없습니다.</p>
          <p>파일을 다운로드하여 열어주세요.</p>
        </div>
      `;
    } else {
      viewer.innerHTML = `
        <div class="error">
          <h2>지원하지 않는 파일 형식</h2>
          <p>파일 형식: ${data.type || "알 수 없음"}</p>
          <p>파일 경로: ${data.file_path || documentId}</p>
          <p>이 형식은 아직 지원하지 않습니다.</p>
        </div>
      `;
    }
  } catch (error) {
    console.error("문서 로드 오류:", error);
    document.getElementById("document-viewer").innerHTML = `
      <div class="error">
        <h2>문서를 불러올 수 없습니다</h2>
        <p>${error.message || "알 수 없는 오류가 발생했습니다."}</p>
        <p style="margin-top: 10px; font-size: 12px; color: #666;">문서 ID: ${documentId}</p>
      </div>
    `;
  }
}

// 지식 구조 보기
function viewKnowledgeStructure(documentId) {
  if (!documentId || documentId === "null" || (typeof documentId === "string" && isNaN(documentId))) {
    console.error("viewKnowledgeStructure: 유효하지 않은 documentId:", documentId);
    return;
  }
  window.location.href = `/knowledge?document_id=${documentId}`;
}

// 페이지 로드 시 실행
if (documentId) {
  loadDocument();
} else {
  document.getElementById("document-viewer").innerHTML = `
    <div class="error">
      <h2>문서 ID가 없습니다</h2>
      <p>올바른 문서 경로를 입력하세요.</p>
    </div>
  `;
}
