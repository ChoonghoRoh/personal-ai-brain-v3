/**
 * 문서 뷰어 공통 유틸리티
 * 모든 페이지에서 문서 링크를 일관되게 처리하기 위한 공통 함수
 */

/**
 * 문서 경로를 안전하게 인코딩하여 문서 뷰어 URL 생성
 * 이미 인코딩된 경로는 디코딩 후 재인코딩하여 이중 인코딩 방지
 * @param {string} filePath - 문서 파일 경로 (인코딩되거나 인코딩되지 않은 상태)
 * @returns {string} 문서 뷰어 URL
 */
function getDocumentUrl(filePath) {
  if (!filePath) {
    console.error('getDocumentUrl: filePath가 없습니다');
    return '#';
  }
  
  // 이미 인코딩된 경로인지 확인 (디코딩 시도)
  let decodedPath = filePath;
  try {
    // 한 번 디코딩 시도
    decodedPath = decodeURIComponent(filePath);
    // 디코딩 후 원본과 다르면 이미 인코딩된 것으로 간주
    if (decodedPath !== filePath) {
      // 이미 인코딩된 경우, 디코딩된 값을 사용
      filePath = decodedPath;
    }
  } catch (e) {
    // 디코딩 실패 시 원본 사용 (이미 디코딩된 상태이거나 잘못된 인코딩)
  }
  
  // 최종적으로 한 번만 인코딩
  return `/document/${encodeURIComponent(filePath)}`;
}

/**
 * 문서 링크 클릭 핸들러
 * @param {string} filePath - 문서 파일 경로
 */
function openDocument(filePath) {
  if (!filePath) {
    console.error('openDocument: filePath가 없습니다');
    return;
  }
  window.location.href = getDocumentUrl(filePath);
}

/**
 * 문서 링크 HTML 생성
 * @param {string} filePath - 문서 파일 경로
 * @param {string} displayText - 표시할 텍스트 (기본값: filePath)
 * @param {object} options - 추가 옵션
 * @returns {string} HTML 문자열
 */
function createDocumentLink(filePath, displayText = null, options = {}) {
  if (!filePath) {
    return displayText || '문서 없음';
  }
  
  const text = displayText || filePath;
  const url = getDocumentUrl(filePath);
  const className = options.className || '';
  const style = options.style || '';
  const onClick = options.onClick || `openDocument('${filePath.replace(/'/g, "\\'")}')`;
  
  if (options.asButton) {
    return `<button onclick="${onClick}" class="${className}" style="${style}">${text}</button>`;
  }
  
  return `<a href="${url}" onclick="event.preventDefault(); ${onClick}" class="${className}" style="${style}">${text}</a>`;
}

/**
 * 문서 아이템 HTML 생성 (카드 형태)
 * @param {object} doc - 문서 객체 (file_path, name 등 포함)
 * @param {object} options - 추가 옵션
 * @returns {string} HTML 문자열
 */
function createDocumentCard(doc, options = {}) {
  if (!doc || !doc.file_path) {
    return '';
  }
  
  const filePath = doc.file_path;
  const name = doc.name || doc.file_path;
  const sizeKB = doc.size ? (doc.size / 1024).toFixed(1) : null;
  const date = doc.modified ? new Date(doc.modified * 1000) : null;
  const dateStr = date ? date.toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }) : null;
  const timeStr = date ? date.toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
  }) : null;
  
  const metaHtml = sizeKB || dateStr 
    ? `<div style="font-size: 12px; color: #666; margin-top: 5px;">
        ${sizeKB ? `<span>${sizeKB} KB</span>` : ''}
        ${dateStr ? `<span style="margin-left: 10px;">${dateStr} ${timeStr}</span>` : ''}
      </div>`
    : '';
  
  const className = options.className || 'document-item';
  const style = options.style || '';
  
  return `
    <div class="${className}" onclick="openDocument('${filePath.replace(/'/g, "\\'")}')" style="cursor: pointer; ${style}">
      <div class="document-info">
        <div class="document-name">${name}</div>
        <div class="document-path">${filePath}</div>
        ${metaHtml}
      </div>
    </div>
  `;
}

/**
 * 문서 목록 HTML 생성
 * @param {Array} documents - 문서 객체 배열
 * @param {object} options - 추가 옵션
 * @returns {string} HTML 문자열
 */
function createDocumentList(documents, options = {}) {
  if (!documents || documents.length === 0) {
    return '<div class="loading">문서가 없습니다.</div>';
  }
  
  const grouped = options.groupByFolder !== false ? {} : null;
  const items = [];
  
  if (grouped) {
    // 폴더별로 그룹화
    documents.forEach((doc) => {
      const pathParts = doc.file_path.split("/");
      const folder = pathParts.slice(0, -1).join("/") || "루트";
      if (!grouped[folder]) {
        grouped[folder] = [];
      }
      grouped[folder].push(doc);
    });
    
    const sortedFolders = Object.keys(grouped).sort();
    sortedFolders.forEach((folder) => {
      items.push(`<div class="folder-group"><div class="folder-header">📁 ${folder}</div>`);
      grouped[folder].forEach((doc) => {
        items.push(createDocumentCard(doc, options));
      });
      items.push('</div>');
    });
  } else {
    // 그룹화 없이 리스트
    documents.forEach((doc) => {
      items.push(createDocumentCard(doc, options));
    });
  }
  
  return `<div class="documents-list">${items.join('')}</div>`;
}

// 전역으로 export (브라우저 환경)
if (typeof window !== 'undefined') {
  window.getDocumentUrl = getDocumentUrl;
  window.openDocument = openDocument;
  window.createDocumentLink = createDocumentLink;
  window.createDocumentCard = createDocumentCard;
  window.createDocumentList = createDocumentList;
}

