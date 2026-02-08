/**
 * 관리자 페이지 공통 JavaScript 함수
 */

/**
 * 에러 메시지 표시
 * @param {string} message - 에러 메시지
 * @param {object} [options] - 옵션. persist: true 이면 자동 숨김 없음
 */
function showError(message, options) {
  const errorDiv = document.getElementById("error-message");
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
    errorDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
    const persist = (options && options.persist === true) || (window.ADMIN_MESSAGES_PERSIST === true);
    if (!persist) {
      setTimeout(() => {
        errorDiv.style.display = "none";
      }, 5000);
    }
  } else {
    console.error("Error:", message);
    alert("오류: " + message);
  }
}

/**
 * 성공 메시지 표시
 * @param {string} message - 성공 메시지
 * @param {object} [options] - 옵션. persist: true 이면 자동 숨김 없음
 */
function showSuccess(message, options) {
  const successDiv = document.getElementById("success-message");
  if (successDiv) {
    successDiv.textContent = message;
    successDiv.style.display = "block";
    successDiv.scrollIntoView({ behavior: "smooth", block: "nearest" });
    const persist = (options && options.persist === true) || (window.ADMIN_MESSAGES_PERSIST === true);
    if (!persist) {
      setTimeout(() => {
        successDiv.style.display = "none";
      }, 3000);
    }
  } else {
    console.log("Success:", message);
  }
}

/**
 * 관리자 페이지 공통 초기화 함수
 * @param {object} options - 초기화 옵션
 * @param {string} options.title - 페이지 제목
 * @param {string} options.subtitle - 페이지 부제목
 * @param {string} options.currentPath - 현재 경로
 */
function initializeAdminPage(options = {}) {
  const {
    title = "⚙️ Knowledge Admin",
    subtitle = "지식 구조 관리",
    currentPath = window.location.pathname,
  } = options;

  // Layout 초기화
  if (typeof initLayout === "function") {
    initLayout();
  } else {
    console.error("initLayout 함수를 찾을 수 없습니다. layout-component.js가 로드되었는지 확인하세요.");
  }

  // Header 렌더링 - 스크립트 로드 확인
  const headerPlaceholder = document.getElementById("header-placeholder");
  const container = document.querySelector(".container");

  // renderHeader 함수가 로드될 때까지 대기
  function tryRenderHeader(attempts = 0) {
    if (typeof renderHeader === "function" || typeof window.renderHeader === "function") {
      const renderFn = renderHeader || window.renderHeader;

      // header-placeholder 제거
      if (headerPlaceholder) {
        headerPlaceholder.remove();
      }

      // Header 렌더링
      renderFn({
        title: title,
        subtitle: subtitle,
        currentPath: currentPath,
        containerSelector: ".container",
        insertPosition: "afterbegin",
      });
    } else if (attempts < 10) {
      // 최대 10번까지 재시도 (1초)
      setTimeout(() => tryRenderHeader(attempts + 1), 100);
    } else {
      console.error("renderHeader 함수를 찾을 수 없습니다. header-component.js가 로드되었는지 확인하세요.");
      // 폴백: 간단한 header 표시
      if (headerPlaceholder) {
        headerPlaceholder.innerHTML = `
          <header>
            <h1>${title}</h1>
            <p>${subtitle}</p>
            <nav>
              <a href="/dashboard">대시보드</a>
              <a href="/knowledge">Knowledge Studio</a>
              <a href="/reason">Reasoning Lab</a>
            </nav>
          </header>
        `;
      }
    }
  }

  tryRenderHeader();
}


