/**
 * 통합 지식 트리 페이지 (Phase 18-2, Task 18-2-4)
 * GET /api/knowledge/tree?project_id={id}&include_chunks=true 호출 후
 * FolderTree 컴포넌트를 사용하여 렌더링.
 * 노드 클릭 시 우측 상세 정보 패널에 정보 표시.
 */

// ── document_id 파라미터 시 기존 Knowledge Studio로 리다이렉트 ──
(function () {
  var params = new URLSearchParams(window.location.search);
  if (params.get("document_id")) {
    window.location.replace("/knowledge-studio?" + params.toString());
    return;
  }
})();

// ── Layout 초기화 ──
document.addEventListener("DOMContentLoaded", function () {
  initLayout();

  if (typeof renderHeader === "function") {
    renderHeader({
      subtitle: "지식 구조 트리",
      currentPath: "/knowledge",
    });
  }

  _initKnowledgeTreePage();
});

// 트리 인스턴스
let _folderTree = null;
let _currentProjectId = null;

/**
 * 페이지 초기화
 */
async function _initKnowledgeTreePage() {
  const container = document.getElementById("knowledge-tree-container");
  if (!container) return;

  // 페이지 구조 생성
  container.innerHTML = _buildPageHTML();

  // 프로젝트 목록 로드
  await _loadProjects();

  // URL 파라미터에서 project_id 읽기
  var params = new URLSearchParams(window.location.search);
  var projectParam = params.get("project_id");
  if (projectParam) {
    _currentProjectId = parseInt(projectParam);
    var select = document.getElementById("kt-project-select");
    if (select) select.value = _currentProjectId;
  }

  // 트리 컴포넌트 초기화
  var treeBody = document.getElementById("kt-tree-body");
  _folderTree = new FolderTree(treeBody, {
    onFileClick: _onFileClick,
    onFolderClick: _onFolderClick,
    onChunkClick: _onChunkClick,
  });

  // 트리 로드
  await _loadTree();

  // 검색 이벤트 바인딩
  var searchInput = document.getElementById("kt-search-input");
  if (searchInput) {
    var debounceTimer = null;
    searchInput.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        if (_folderTree) {
          _folderTree.filter(searchInput.value);
        }
      }, 250);
    });
  }

  // 프로젝트 변경 이벤트
  var projectSelect = document.getElementById("kt-project-select");
  if (projectSelect) {
    projectSelect.addEventListener("change", function () {
      var val = projectSelect.value;
      _currentProjectId = val ? parseInt(val) : null;
      _loadTree();
    });
  }
}

/**
 * 페이지 HTML 생성
 */
function _buildPageHTML() {
  return (
    '<div class="kt-page">' +
    '  <div class="kt-tree-panel">' +
    '    <div class="kt-tree-header">' +
    "      <h3>지식 트리</h3>" +
    '      <div class="kt-search-box">' +
    '        <input type="text" id="kt-search-input" class="kt-search-input" placeholder="노드 이름 검색..." />' +
    '        <select id="kt-project-select" class="kt-project-select">' +
    '          <option value="">전체 프로젝트</option>' +
    "        </select>" +
    "      </div>" +
    "    </div>" +
    '    <div id="kt-tree-body" class="kt-tree-body"></div>' +
    "  </div>" +
    '  <div id="kt-detail-panel" class="kt-detail-panel">' +
    '    <div class="kt-detail-empty">' +
    '      <span class="kt-icon">🌳</span>' +
    "      <span>노드를 선택하면 상세 정보가 표시됩니다</span>" +
    "    </div>" +
    "  </div>" +
    "</div>"
  );
}

/**
 * 프로젝트 목록 로드
 */
async function _loadProjects() {
  try {
    var headers = typeof getAuthHeaders === "function" ? getAuthHeaders(false) : {};
    var res = await fetch("/api/knowledge/projects", { headers: headers });
    if (!res.ok) return;
    var data = await res.json();
    var select = document.getElementById("kt-project-select");
    if (!select || !data.projects) return;

    for (var i = 0; i < data.projects.length; i++) {
      var p = data.projects[i];
      var opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = p.name;
      select.appendChild(opt);
    }
  } catch (e) {
    console.warn("프로젝트 목록 로드 실패:", e);
  }
}

/**
 * 통합 지식 트리 API 호출
 */
async function _loadTree() {
  if (!_folderTree) return;

  _folderTree.showLoading();
  _showDetailEmpty();

  // 검색어 초기화
  var searchInput = document.getElementById("kt-search-input");
  if (searchInput) searchInput.value = "";

  try {
    var headers = typeof getAuthHeaders === "function" ? getAuthHeaders(false) : {};
    var url = "/api/knowledge/tree?include_chunks=true";
    if (_currentProjectId) {
      url += "&project_id=" + _currentProjectId;
    }

    var res = await fetch(url, { headers: headers });
    if (!res.ok) {
      throw new Error("API 오류: " + res.status);
    }
    var data = await res.json();
    _folderTree.render(data);
  } catch (e) {
    console.error("트리 로드 실패:", e);
    _folderTree.showError("트리를 불러올 수 없습니다: " + e.message);
  }
}

// ── 노드 클릭 핸들러 ──

function _onFolderClick(node) {
  var panel = document.getElementById("kt-detail-panel");
  if (!panel) return;

  var childFiles = 0;
  var childFolders = 0;
  if (node.children) {
    for (var i = 0; i < node.children.length; i++) {
      if (node.children[i].type === "file") childFiles++;
      else if (node.children[i].type === "folder") childFolders++;
    }
  }

  panel.innerHTML =
    '<div class="kt-detail-header">' +
    '  <div class="kt-detail-type">폴더</div>' +
    '  <h2 class="kt-detail-name">' + escapeHtml(node.name) + "</h2>" +
    "</div>" +
    '<ul class="kt-detail-props">' +
    '  <li><span class="prop-label">총 파일 수</span><span class="prop-value">' +
    (node.file_count || 0) +
    "개</span></li>" +
    '  <li><span class="prop-label">직접 하위 폴더</span><span class="prop-value">' +
    childFolders +
    "개</span></li>" +
    '  <li><span class="prop-label">직접 하위 파일</span><span class="prop-value">' +
    childFiles +
    "개</span></li>" +
    "</ul>";
}

function _onFileClick(node) {
  var panel = document.getElementById("kt-detail-panel");
  if (!panel) return;

  var chunkInfo = "";
  if (node.children && node.children.length > 0) {
    chunkInfo =
      '<div class="kt-chunk-preview"><h4>청크 목록 (' +
      node.children.length +
      "개)</h4>" +
      '<ul class="kt-detail-props">';
    for (var i = 0; i < node.children.length; i++) {
      var c = node.children[i];
      var statusClass = c.status || "pending";
      chunkInfo +=
        "<li>" +
        '<span class="prop-label">#' + c.chunk_index + "</span>" +
        '<span class="prop-value">' + escapeHtml(c.name || c.title || "Chunk #" + c.chunk_index) + "</span>" +
        ' <span class="ft-status ' + statusClass + '">' + statusClass + "</span>" +
        "</li>";
    }
    chunkInfo += "</ul></div>";
  }

  panel.innerHTML =
    '<div class="kt-detail-header">' +
    '  <div class="kt-detail-type">파일</div>' +
    '  <h2 class="kt-detail-name">' + escapeHtml(node.name) + "</h2>" +
    "</div>" +
    '<ul class="kt-detail-props">' +
    '  <li><span class="prop-label">문서 ID</span><span class="prop-value">' +
    (node.document_id || "-") +
    "</span></li>" +
    '  <li><span class="prop-label">청크 수</span><span class="prop-value">' +
    (node.chunk_count || 0) +
    "개</span></li>" +
    "</ul>" +
    '<div class="kt-detail-actions">' +
    '  <button class="kt-btn kt-btn-primary" onclick="_navigateToDocument(' +
    node.document_id +
    ')">문서 보기</button>' +
    '  <button class="kt-btn kt-btn-secondary" onclick="_navigateToKnowledge(' +
    node.document_id +
    ')">지식 상세</button>' +
    "</div>" +
    chunkInfo;
}

function _onChunkClick(node) {
  var panel = document.getElementById("kt-detail-panel");
  if (!panel) return;

  var statusClass = node.status || "pending";

  panel.innerHTML =
    '<div class="kt-detail-header">' +
    '  <div class="kt-detail-type">청크</div>' +
    '  <h2 class="kt-detail-name">' +
    escapeHtml(node.name || node.title || "Chunk #" + node.chunk_index) +
    "</h2>" +
    "</div>" +
    '<ul class="kt-detail-props">' +
    '  <li><span class="prop-label">청크 ID</span><span class="prop-value">' +
    (node.chunk_id || "-") +
    "</span></li>" +
    '  <li><span class="prop-label">인덱스</span><span class="prop-value">' +
    (node.chunk_index != null ? node.chunk_index : "-") +
    "</span></li>" +
    '  <li><span class="prop-label">상태</span><span class="prop-value"><span class="ft-status ' +
    statusClass +
    '">' +
    statusClass +
    "</span></span></li>" +
    '  <li><span class="prop-label">라벨 수</span><span class="prop-value">' +
    (node.label_count || 0) +
    "개</span></li>" +
    "</ul>" +
    '<div class="kt-detail-actions">' +
    '  <button class="kt-btn kt-btn-secondary" onclick="_navigateToChunkDetail(' +
    node.chunk_id +
    ')">청크 상세</button>' +
    "</div>";
}

function _showDetailEmpty() {
  var panel = document.getElementById("kt-detail-panel");
  if (!panel) return;
  panel.innerHTML =
    '<div class="kt-detail-empty">' +
    '<span class="kt-icon">🌳</span>' +
    "<span>노드를 선택하면 상세 정보가 표시됩니다</span>" +
    "</div>";
}

// ── 네비게이션 ──

function _navigateToDocument(docId) {
  if (!docId) return;
  window.location.href = "/document/" + docId;
}

function _navigateToKnowledge(docId) {
  if (!docId) return;
  window.location.href = "/knowledge-studio?document_id=" + docId;
}

function _navigateToChunkDetail(chunkId) {
  if (!chunkId) return;
  window.location.href = "/knowledge-detail?chunk_id=" + chunkId;
}

// 전역 export (onclick에서 사용)
if (typeof window !== "undefined") {
  window._navigateToDocument = _navigateToDocument;
  window._navigateToKnowledge = _navigateToKnowledge;
  window._navigateToChunkDetail = _navigateToChunkDetail;
}
