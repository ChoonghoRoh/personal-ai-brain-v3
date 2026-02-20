/**
 * 폴더 트리뷰 컴포넌트 (Phase 18-2)
 * 재사용 가능한 트리 렌더러 — API 응답 트리를 재귀 렌더링
 *
 * API 응답 구조:
 *   { name, type: "folder"|"file"|"chunk", children, document_id, chunk_count, ... }
 *
 * 사용법:
 *   const tree = new FolderTree(containerEl, { onFileClick, onChunkClick, onFolderClick });
 *   tree.render(apiData);
 */

class FolderTree {
  /**
   * @param {HTMLElement} container - 트리를 렌더링할 DOM 요소
   * @param {object} options
   * @param {function} [options.onFileClick]   - (node) => void
   * @param {function} [options.onChunkClick]  - (node) => void
   * @param {function} [options.onFolderClick] - (node) => void
   * @param {boolean}  [options.expandAll]     - 초기 전체 펼침 (기본 false)
   */
  constructor(container, options = {}) {
    this._container = container;
    this._onFileClick = options.onFileClick || null;
    this._onChunkClick = options.onChunkClick || null;
    this._onFolderClick = options.onFolderClick || null;
    this._expandAll = options.expandAll || false;
    this._selectedEl = null;
    this._data = null;
  }

  /**
   * 트리 데이터를 렌더링한다.
   * @param {object} data - API 응답 트리 루트 노드
   */
  render(data) {
    this._data = data;
    this._container.innerHTML = "";

    if (!data || !data.children || data.children.length === 0) {
      this._container.innerHTML =
        '<div class="ft-empty">표시할 항목이 없습니다.</div>';
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "folder-tree";

    this._renderChildren(wrapper, data.children, 0);
    this._container.appendChild(wrapper);
  }

  /**
   * 로딩 상태 표시
   */
  showLoading() {
    this._container.innerHTML =
      '<div class="folder-tree"><div class="ft-loading">트리를 불러오는 중...</div></div>';
  }

  /**
   * 에러 메시지 표시
   * @param {string} message
   */
  showError(message) {
    this._container.innerHTML =
      '<div class="folder-tree"><div class="ft-error">' +
      escapeHtml(message) +
      "</div></div>";
  }

  /**
   * 검색 필터: 이름에 keyword가 포함된 노드만 표시
   * @param {string} keyword - 검색어 (빈 문자열이면 전체 표시)
   */
  filter(keyword) {
    if (!this._data) return;

    if (!keyword || keyword.trim() === "") {
      this.render(this._data);
      return;
    }

    const lower = keyword.trim().toLowerCase();
    const filtered = this._filterTree(this._data, lower);
    this._container.innerHTML = "";

    if (!filtered || !filtered.children || filtered.children.length === 0) {
      this._container.innerHTML =
        '<div class="folder-tree"><div class="ft-empty">검색 결과가 없습니다.</div></div>';
      return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "folder-tree";
    this._renderChildren(wrapper, filtered.children, 0, true);
    this._container.appendChild(wrapper);
  }

  // -- private --

  _filterTree(node, keyword) {
    if (node.type === "file" || node.type === "chunk") {
      if (node.name && node.name.toLowerCase().includes(keyword)) {
        return Object.assign({}, node);
      }
      return null;
    }

    // folder
    const matchedChildren = [];
    if (node.children) {
      for (const child of node.children) {
        const result = this._filterTree(child, keyword);
        if (result) matchedChildren.push(result);
      }
    }

    const folderNameMatch =
      node.name && node.name.toLowerCase().includes(keyword);
    if (matchedChildren.length > 0 || folderNameMatch) {
      return Object.assign({}, node, {
        children:
          matchedChildren.length > 0 ? matchedChildren : node.children || [],
      });
    }
    return null;
  }

  _renderChildren(parentEl, children, depth, forceExpand) {
    for (const child of children) {
      const nodeEl = this._createNodeEl(child, depth, forceExpand);
      parentEl.appendChild(nodeEl);
    }
  }

  _createNodeEl(node, depth, forceExpand) {
    const wrapper = document.createElement("div");
    wrapper.className = "ft-node";

    const row = document.createElement("div");
    row.className = "ft-row";
    if (node.type === "chunk") row.classList.add("ft-chunk");
    row.style.paddingLeft = 8 + depth * 18 + "px";

    const isFolder = node.type === "folder";
    const hasChildren = node.children && node.children.length > 0;
    const shouldExpand = forceExpand || this._expandAll;

    // 화살표 (폴더만)
    const arrow = document.createElement("span");
    arrow.className = "ft-arrow";
    if (isFolder && hasChildren) {
      arrow.textContent = "\u25B6"; // ▶
      if (shouldExpand) arrow.classList.add("expanded");
    } else {
      arrow.classList.add("empty");
    }
    row.appendChild(arrow);

    // 아이콘
    const icon = document.createElement("span");
    icon.className = "ft-icon";
    if (isFolder) {
      icon.textContent = "\uD83D\uDCC1"; // 📁
    } else if (node.type === "chunk") {
      icon.textContent = "\uD83D\uDCCE"; // 📎
    } else {
      icon.textContent = "\uD83D\uDCC4"; // 📄
    }
    row.appendChild(icon);

    // 이름
    const name = document.createElement("span");
    name.className = "ft-name";
    name.textContent = node.name || "(이름 없음)";
    name.title = node.name || "";
    row.appendChild(name);

    // 배지
    if (isFolder && typeof node.file_count === "number") {
      const badge = document.createElement("span");
      badge.className = "ft-badge";
      badge.textContent = node.file_count + "개 파일";
      row.appendChild(badge);
    } else if (node.type === "file" && typeof node.chunk_count === "number") {
      const badge = document.createElement("span");
      badge.className = "ft-badge";
      badge.textContent = node.chunk_count + "개 청크";
      row.appendChild(badge);
    } else if (node.type === "chunk" && node.status) {
      const status = document.createElement("span");
      status.className = "ft-status " + node.status;
      status.textContent = node.status;
      row.appendChild(status);
    }

    // 클릭 이벤트
    const self = this;
    if (isFolder) {
      row.addEventListener("click", function (e) {
        e.stopPropagation();

        // 접기/펼치기
        if (hasChildren) {
          arrow.classList.toggle("expanded");
          childrenEl.classList.toggle("expanded");
        }

        // 선택 표시
        self._selectRow(row);

        if (self._onFolderClick) {
          self._onFolderClick(node);
        }
      });
    } else if (node.type === "file") {
      row.addEventListener("click", function (e) {
        e.stopPropagation();
        self._selectRow(row);

        if (self._onFileClick) {
          self._onFileClick(node);
        }
      });
    } else if (node.type === "chunk") {
      row.addEventListener("click", function (e) {
        e.stopPropagation();
        self._selectRow(row);

        if (self._onChunkClick) {
          self._onChunkClick(node);
        }
      });
    }

    wrapper.appendChild(row);

    // 하위 노드
    var childrenEl = document.createElement("div");
    childrenEl.className = "ft-children";
    if (shouldExpand && hasChildren) {
      childrenEl.classList.add("expanded");
    }
    if (hasChildren) {
      this._renderChildren(childrenEl, node.children, depth + 1, forceExpand);
    }
    wrapper.appendChild(childrenEl);

    return wrapper;
  }

  _selectRow(rowEl) {
    if (this._selectedEl) {
      this._selectedEl.classList.remove("selected");
    }
    rowEl.classList.add("selected");
    this._selectedEl = rowEl;
  }
}

// escapeHtml fallback (utils.js가 없을 경우 대비)
if (typeof escapeHtml !== "function") {
  function escapeHtml(text) {
    if (text == null) return "";
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}

// 전역 export
if (typeof window !== "undefined") {
  window.FolderTree = FolderTree;
}
