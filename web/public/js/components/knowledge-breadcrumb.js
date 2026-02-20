/**
 * Knowledge Breadcrumb 컴포넌트 (Phase 18-2, Task 18-2-5)
 * file_path를 파싱하여 경로 배열을 표시하고,
 * 각 항목 클릭 시 지식 트리 페이지에서 해당 폴더를 열 수 있도록 네비게이션.
 *
 * 사용법:
 *   renderKnowledgeBreadcrumb("backend/routers/knowledge.py", containerEl);
 */

/**
 * Breadcrumb HTML을 생성하여 container에 삽입
 * @param {string} filePath - 문서 file_path (예: "backend/routers/knowledge.py")
 * @param {HTMLElement|string} container - DOM 요소 또는 셀렉터
 */
function renderKnowledgeBreadcrumb(filePath, container) {
  var el =
    typeof container === "string"
      ? document.querySelector(container)
      : container;
  if (!el || !filePath) return;

  var parts = filePath.split("/").filter(function (p) {
    return p.length > 0;
  });
  if (parts.length === 0) return;

  var nav = document.createElement("nav");
  nav.className = "kb-breadcrumb";
  nav.setAttribute("aria-label", "파일 경로");

  // 루트(홈) 아이콘
  var homeLink = document.createElement("a");
  homeLink.className = "kb-crumb kb-home";
  homeLink.href = "/knowledge";
  homeLink.textContent = "🌳";
  homeLink.title = "지식 구조 트리";
  nav.appendChild(homeLink);

  for (var i = 0; i < parts.length; i++) {
    // 구분자
    var sep = document.createElement("span");
    sep.className = "kb-sep";
    sep.textContent = "/";
    nav.appendChild(sep);

    var isLast = i === parts.length - 1;
    var crumb = document.createElement(isLast ? "span" : "a");
    crumb.className = "kb-crumb";

    // escapeHtml 사용 (utils.js에서 로드)
    crumb.textContent = parts[i];

    if (!isLast) {
      // 폴더 경로: 클릭 시 knowledge 트리로 이동 (향후 폴더 열기 파라미터 지원 가능)
      var folderPath = parts.slice(0, i + 1).join("/");
      crumb.href = "/knowledge?folder=" + encodeURIComponent(folderPath);
      crumb.title = folderPath;
    } else {
      crumb.classList.add("kb-current");
      crumb.title = filePath;
    }

    nav.appendChild(crumb);
  }

  el.insertBefore(nav, el.firstChild);

  // 스타일 주입 (1회만)
  _injectBreadcrumbStyles();
}

/**
 * Breadcrumb 스타일 CSS 주입
 */
var _breadcrumbStylesInjected = false;
function _injectBreadcrumbStyles() {
  if (_breadcrumbStylesInjected) return;
  _breadcrumbStylesInjected = true;

  var css =
    ".kb-breadcrumb {" +
    "  display: flex;" +
    "  align-items: center;" +
    "  gap: 4px;" +
    "  padding: 8px 0;" +
    "  margin-bottom: 12px;" +
    "  font-size: 13px;" +
    "  flex-wrap: wrap;" +
    "}" +
    ".kb-breadcrumb .kb-crumb {" +
    "  color: #1e40af;" +
    "  text-decoration: none;" +
    "  padding: 2px 4px;" +
    "  border-radius: 3px;" +
    "  transition: background 0.12s;" +
    "}" +
    ".kb-breadcrumb a.kb-crumb:hover {" +
    "  background: #eff6ff;" +
    "  text-decoration: underline;" +
    "}" +
    ".kb-breadcrumb .kb-current {" +
    "  color: #1e293b;" +
    "  font-weight: 600;" +
    "}" +
    ".kb-breadcrumb .kb-sep {" +
    "  color: #94a3b8;" +
    "  font-size: 12px;" +
    "}" +
    ".kb-breadcrumb .kb-home {" +
    "  font-size: 15px;" +
    "  text-decoration: none;" +
    "}";

  var style = document.createElement("style");
  style.id = "kb-breadcrumb-styles";
  style.textContent = css;
  document.head.appendChild(style);
}

// 전역 export
if (typeof window !== "undefined") {
  window.renderKnowledgeBreadcrumb = renderKnowledgeBreadcrumb;
}
