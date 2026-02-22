/**
 * 키워드 그룹 트리뷰 모듈
 * 트리 구조 표시, 접기/펼치기, 폴더형 UI, 우클릭 메뉴 기반 노드 이동
 */
class KeywordGroupTreeView {
  constructor(manager) {
    this.manager = manager;
    this.treeData = [];
    this.expandedNodes = new Set();
    this.selectedNodeId = null;
    this.contextMenu = new KeywordGroupContextMenu(this);
  }

  /** 트리 데이터 로드 */
  async loadTree() {
    const depthEl = document.getElementById("kg-tree-max-depth");
    const maxDepth = depthEl ? (depthEl.value || "5") : "5";
    try {
      const response = await fetch("/api/labels/tree?max_depth=" + encodeURIComponent(maxDepth));
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "HTTP " + response.status }));
        throw new Error(errorData.detail || "트리 로드 실패 (" + response.status + ")");
      }
      var data = await response.json();
      // API가 단일 루트 객체 또는 배열을 반환할 수 있음
      var rawData = Array.isArray(data) ? data : [data];
      this.treeData = this._filterGroupsOnly(rawData);
      // manager.selectedGroupId와 트리 선택 상태 동기화
      if (this.manager && this.manager.selectedGroupId) {
        this.selectedNodeId = this.manager.selectedGroupId;
      }
      this.renderTree(this.treeData);
    } catch (error) {
      console.error("트리 로드 실패:", error);
      const container = document.getElementById("groups-tree");
      if (container) {
        container.innerHTML = '<div class="detail-empty-state"><p>트리를 불러올 수 없습니다</p></div>';
      }
    }
  }

  /** 그룹 노드만 필터링 */
  _filterGroupsOnly(nodes) {
    if (!nodes) return [];
    return nodes
      .filter(function (node) { return node.label_type !== "keyword"; })
      .map(function (node) {
        return Object.assign({}, node, {
          children: this._filterGroupsOnly(node.children)
        });
      }.bind(this));
  }

  /** 트리 렌더링 */
  renderTree(treeData) {
    const container = document.getElementById("groups-tree");
    if (!container) return;
    container.innerHTML = "";

    if (!treeData || treeData.length === 0) {
      container.innerHTML = '<div class="detail-empty-state"><p>그룹이 없습니다</p></div>';
      return;
    }

    const ul = document.createElement("ul");
    ul.className = "tree-container";
    treeData.forEach(function (node) {
      ul.appendChild(this._renderNode(node, 0));
    }.bind(this));
    container.appendChild(ul);
  }

  /** 단일 노드 렌더링 */
  _renderNode(node, depth) {
    var self = this;
    var hasChildren = node.children && node.children.length > 0;
    var isExpanded = this.expandedNodes.has(node.id);

    var li = document.createElement("li");
    li.className = "tree-node";
    li.dataset.nodeId = node.id;

    // 노드 내용 컨테이너
    var content = document.createElement("div");
    content.className = "tree-node-content";
    if (this.selectedNodeId === node.id) {
      content.classList.add("selected");
    }

    // 토글 아이콘
    var toggle = document.createElement("span");
    toggle.className = "tree-toggle";
    if (hasChildren) {
      toggle.textContent = isExpanded ? "\u25BC" : "\u25B6";
      toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        self.toggleNode(node.id);
      });
    } else {
      toggle.innerHTML = "&nbsp;";
    }
    content.appendChild(toggle);

    // 폴더 아이콘
    if (hasChildren) {
      var folderIcon = document.createElement("span");
      folderIcon.className = "tree-folder-icon";
      folderIcon.textContent = isExpanded ? "\uD83D\uDCC2" : "\uD83D\uDCC1"; // 📂 or 📁
      content.appendChild(folderIcon);
    }

    // 노드 이름
    var name = document.createElement("span");
    name.className = "tree-name";
    name.textContent = node.name;
    name.addEventListener("click", function (e) {
      e.stopPropagation();
      self.selectNode(node.id);
    });
    content.appendChild(name);

    // 키워드 수 표시 (있으면)
    if (typeof node.keyword_count === "number") {
      var count = document.createElement("span");
      count.className = "tree-count";
      count.textContent = "(" + node.keyword_count + ")";
      content.appendChild(count);
    }

    // 우클릭 컨텍스트 메뉴
    content.addEventListener("contextmenu", function (e) {
      e.preventDefault();
      e.stopPropagation();
      self.contextMenu.show(e, node);
    });

    li.appendChild(content);

    // 자식 노드 (재귀)
    if (hasChildren) {
      var childrenUl = document.createElement("ul");
      childrenUl.className = "tree-children" + (isExpanded ? "" : " collapsed");
      node.children.forEach(function (child) {
        childrenUl.appendChild(self._renderNode(child, depth + 1));
      });
      li.appendChild(childrenUl);
    }

    return li;
  }

  /** 노드 접기/펼치기 */
  toggleNode(nodeId) {
    if (this.expandedNodes.has(nodeId)) {
      this.expandedNodes.delete(nodeId);
    } else {
      this.expandedNodes.add(nodeId);
    }
    this.renderTree(this.treeData);
  }

  /** 노드 선택 */
  selectNode(nodeId) {
    this.selectedNodeId = nodeId;

    // 기존 그룹 선택과 연동 (2단 상세 패널 업데이트)
    if (this.manager && this.manager.matching) {
      this.manager.matching.selectGroup(nodeId);
    }

    // 트리 내 선택 표시 갱신
    var allContents = document.querySelectorAll("#groups-tree .tree-node-content");
    allContents.forEach(function (el) {
      el.classList.remove("selected");
    });
    var selectedNode = document.querySelector('#groups-tree .tree-node[data-node-id="' + nodeId + '"] > .tree-node-content');
    if (selectedNode) {
      selectedNode.classList.add("selected");
      // 선택된 노드로 자동 스크롤
      selectedNode.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }

    // Breadcrumb 렌더링
    this.renderBreadcrumb(nodeId);
  }

  /** 노드 이동 (낙관적 UI) */
  async moveNode(sourceId, targetId) {
    var sourceEl = document.querySelector('[data-node-id="' + sourceId + '"] > .tree-node-content');

    // 1. 로딩 스피너 표시
    if (sourceEl) sourceEl.classList.add("loading");

    // 2. 백업 (딥카피)
    var backup = JSON.parse(JSON.stringify(this.treeData));

    // 3. 낙관적 UI: 클라이언트 즉시 이동
    var moved = this._moveNodeLocal(sourceId, targetId);
    if (!moved) {
      if (sourceEl) sourceEl.classList.remove("loading");
      showError("노드를 찾을 수 없습니다.");
      return;
    }

    // 이동된 트리 즉시 렌더링
    this.renderTree(this.treeData);

    // 4. API 호출
    try {
      var response = await fetch("/api/labels/" + sourceId + "/move", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_parent_id: targetId }),
      });

      if (!response.ok) {
        var errorData = await response.json().catch(function () { return {}; });
        throw new Error(errorData.detail || "노드 이동 실패");
      }

      showSuccess("노드가 이동되었습니다.");

      // API 성공 시 전체 트리 리로드 (서버 상태와 동기화)
      await this.loadTree();

      if (this.manager && this.manager.matching && this.manager.selectedGroupId) {
        await this.manager.matching.loadKeywords();
      }
    } catch (error) {
      console.error("노드 이동 실패:", error);

      // 5. 실패 시 백업 복구
      this.treeData = backup;
      this.renderTree(this.treeData);

      showError(error.message || "노드 이동 중 오류가 발생했습니다.");
    } finally {
      // 6. 로딩 스피너 제거
      if (sourceEl) sourceEl.classList.remove("loading");
    }
  }

  /** 로컬 노드 이동 */
  _moveNodeLocal(sourceId, targetId) {
    var sourceNode = this._removeNodeById(sourceId, this.treeData);
    if (!sourceNode) return false;

    if (targetId === null) {
      this.treeData.push(sourceNode);
      return true;
    }

    var targetNode = this._findNode(targetId);
    if (!targetNode) {
      this.treeData.push(sourceNode);
      return false;
    }

    if (!targetNode.children) targetNode.children = [];
    targetNode.children.push(sourceNode);
    return true;
  }

  /** 노드 제거 */
  _removeNodeById(nodeId, nodes) {
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].id === nodeId) {
        return nodes.splice(i, 1)[0];
      }
      if (nodes[i].children && nodes[i].children.length > 0) {
        var found = this._removeNodeById(nodeId, nodes[i].children);
        if (found) return found;
      }
    }
    return null;
  }

  /** Breadcrumb 렌더링 */
  async renderBreadcrumb(labelId) {
    var container = document.getElementById("tree-breadcrumb");
    if (!container) return;

    try {
      var response = await fetch("/api/labels/" + labelId + "/breadcrumb");
      if (!response.ok) {
        container.style.display = "none";
        return;
      }

      var path = await response.json();
      if (!path || path.length === 0) {
        container.style.display = "none";
        return;
      }

      var self = this;
      container.innerHTML = "";

      path.forEach(function (item, index) {
        if (index > 0) {
          var sep = document.createElement("span");
          sep.className = "separator";
          sep.textContent = "/";
          container.appendChild(sep);
        }

        if (index < path.length - 1) {
          var link = document.createElement("a");
          link.href = "#";
          link.textContent = item.name;
          link.addEventListener("click", function (e) {
            e.preventDefault();
            self.selectNode(item.id);
          });
          container.appendChild(link);
        } else {
          var current = document.createElement("span");
          current.textContent = item.name;
          container.appendChild(current);
        }
      });

      container.style.display = "block";
    } catch (error) {
      console.error("Breadcrumb 로드 실패:", error);
      container.style.display = "none";
    }
  }

  /** 검색 결과 하이라이트 */
  highlightSearchResults(query) {
    this.clearHighlight();
    if (!query || !query.trim()) return;

    var lowerQuery = query.toLowerCase().trim();
    var matchedNodeIds = [];

    // 재귀적으로 매칭 노드 찾기
    this._findMatchingNodes(this.treeData, lowerQuery, matchedNodeIds);

    // 매칭 노드의 부모 모두 펼치기
    var self = this;
    matchedNodeIds.forEach(function (nodeId) {
      self._expandParents(nodeId);
    });

    // 트리 다시 렌더링 (펼침 상태 반영)
    if (matchedNodeIds.length > 0) {
      this.renderTree(this.treeData);
    }

    // 하이라이트 클래스 추가
    matchedNodeIds.forEach(function (nodeId) {
      var nodeContent = document.querySelector('#groups-tree .tree-node[data-node-id="' + nodeId + '"] > .tree-node-content');
      if (nodeContent) {
        nodeContent.classList.add("highlight");
      }
    });
  }

  /** 매칭 노드 검색 */
  _findMatchingNodes(nodes, lowerQuery, result) {
    if (!nodes) return;
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].name && nodes[i].name.toLowerCase().indexOf(lowerQuery) !== -1) {
        result.push(nodes[i].id);
      }
      if (nodes[i].children && nodes[i].children.length > 0) {
        this._findMatchingNodes(nodes[i].children, lowerQuery, result);
      }
    }
  }

  /** 하이라이트 제거 */
  clearHighlight() {
    var highlighted = document.querySelectorAll("#groups-tree .tree-node-content.highlight");
    highlighted.forEach(function (el) {
      el.classList.remove("highlight");
    });
  }

  /** 노드 ID로 찾기 */
  _findNode(nodeId, nodes) {
    if (!nodes) nodes = this.treeData;
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].id === nodeId) return nodes[i];
      if (nodes[i].children && nodes[i].children.length > 0) {
        var found = this._findNode(nodeId, nodes[i].children);
        if (found) return found;
      }
    }
    return null;
  }

  /** 부모 노드 펼치기 */
  _expandParents(nodeId, nodes, parentChain) {
    if (!nodes) nodes = this.treeData;
    if (!parentChain) parentChain = [];

    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].id === nodeId) {
        parentChain.forEach(function (pid) {
          this.expandedNodes.add(pid);
        }.bind(this));
        return true;
      }
      if (nodes[i].children && nodes[i].children.length > 0) {
        var newChain = parentChain.concat([nodes[i].id]);
        if (this._expandParents(nodeId, nodes[i].children, newChain)) {
          return true;
        }
      }
    }
    return false;
  }


  /** 부모 ID 찾기 */
  _findParentId(nodeId, nodes, parentId) {
    if (!nodes) nodes = this.treeData;
    if (parentId === undefined) parentId = null;
    for (var i = 0; i < nodes.length; i++) {
      if (nodes[i].id === nodeId) return parentId;
      if (nodes[i].children && nodes[i].children.length > 0) {
        var found = this._findParentId(nodeId, nodes[i].children, nodes[i].id);
        if (found !== undefined) return found;
      }
    }
    return undefined;
  }
}

/**
 * 뷰 전환 (파일관리형에서는 트리 단일 뷰 — 호환용 no-op)
 */
function switchView(view) {
  var listView = document.getElementById("list-view");
  var treeView = document.getElementById("tree-view");
  if (!listView && !treeView) return;

  var viewTabs = document.querySelectorAll(".view-mode-tabs .view-tab");
  viewTabs.forEach(function (btn) {
    btn.style.borderBottom = "";
    btn.style.color = "#6b7280";
    btn.style.fontWeight = "500";
    if (btn.dataset.view === view) {
      btn.style.borderBottom = "2px solid #2563eb";
      btn.style.color = "#2563eb";
      btn.style.fontWeight = "600";
    }
  });

  if (view === "tree") {
    if (listView) listView.style.display = "none";
    if (treeView) treeView.style.display = "block";
    if (window.groupManager && window.groupManager.treeView) {
      window.groupManager.treeView.loadTree();
    }
  } else {
    if (listView) listView.style.display = "";
    if (treeView) treeView.style.display = "none";
  }
}

/**
 * 현재 활성 뷰가 트리인지 확인 (파일관리형에서는 항상 트리)
 */
function isTreeViewActive() {
  return true;
}
