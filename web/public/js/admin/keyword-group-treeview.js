/**
 * 키워드 그룹 트리뷰 모듈
 * 트리 구조 표시, 접기/펼치기, 드래그 & 드롭 이동 기능
 */
class KeywordGroupTreeView {
  constructor(manager) {
    this.manager = manager;
    this.treeData = [];
    this.expandedNodes = new Set();
    this.selectedNodeId = null;
    this._dragSourceId = null;
  }

  /**
   * 트리 데이터 로드 (GET /api/labels/tree?max_depth=5)
   */
  async loadTree() {
    try {
      const response = await fetch("/api/labels/tree?max_depth=5");
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: "HTTP " + response.status }));
        throw new Error(errorData.detail || "트리 로드 실패 (" + response.status + ")");
      }
      var data = await response.json();
      // API가 단일 루트 객체 또는 배열을 반환할 수 있음
      this.treeData = Array.isArray(data) ? data : [data];
      this.renderTree(this.treeData);
    } catch (error) {
      console.error("트리 로드 실패:", error);
      const container = document.getElementById("groups-tree");
      if (container) {
        container.innerHTML = '<div class="detail-empty-state"><p>트리를 불러올 수 없습니다</p></div>';
      }
    }
  }

  /**
   * 트리 렌더링
   */
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

  /**
   * 단일 노드 HTML 생성 (재귀)
   */
  _renderNode(node, depth) {
    var self = this;
    var hasChildren = node.children && node.children.length > 0;
    var isExpanded = this.expandedNodes.has(node.id);

    var li = document.createElement("li");
    li.className = "tree-node";
    li.dataset.nodeId = node.id;
    li.draggable = true;

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

    li.appendChild(content);

    // D&D 이벤트
    li.addEventListener("dragstart", function (e) {
      e.stopPropagation();
      self._dragSourceId = node.id;
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", String(node.id));
      li.classList.add("dragging");
    });

    li.addEventListener("dragend", function () {
      li.classList.remove("dragging");
      self._dragSourceId = null;
    });

    content.addEventListener("dragover", function (e) {
      e.preventDefault();
      e.stopPropagation();
      e.dataTransfer.dropEffect = "move";
      if (self._dragSourceId && self._dragSourceId !== node.id) {
        content.classList.add("drag-over");
      }
    });

    content.addEventListener("dragleave", function (e) {
      e.stopPropagation();
      content.classList.remove("drag-over");
    });

    content.addEventListener("drop", function (e) {
      e.preventDefault();
      e.stopPropagation();
      content.classList.remove("drag-over");
      var sourceId = parseInt(e.dataTransfer.getData("text/plain"), 10);
      if (sourceId && sourceId !== node.id) {
        self.moveNode(sourceId, node.id);
      }
    });

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

  /**
   * 노드 접기/펼치기 토글
   */
  toggleNode(nodeId) {
    if (this.expandedNodes.has(nodeId)) {
      this.expandedNodes.delete(nodeId);
    } else {
      this.expandedNodes.add(nodeId);
    }
    this.renderTree(this.treeData);
  }

  /**
   * 노드 선택
   */
  selectNode(nodeId) {
    this.selectedNodeId = nodeId;

    // 기존 그룹 선택과 연동
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
    }

    // Breadcrumb 렌더링
    this.renderBreadcrumb(nodeId);
  }

  /**
   * 노드 이동 (PATCH /api/labels/{sourceId}/move)
   */
  async moveNode(sourceId, targetId) {
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
      await this.loadTree();
    } catch (error) {
      console.error("노드 이동 실패:", error);
      showError(error.message || "노드 이동 중 오류가 발생했습니다.");
    }
  }

  /**
   * Breadcrumb 경로 렌더링 (GET /api/labels/{labelId}/breadcrumb)
   */
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

  /**
   * 검색 결과 하이라이트 (트리 노드 중 query 매칭 노드에 .highlight 추가)
   */
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

  /**
   * 매칭 노드 재귀 검색
   */
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

  /**
   * 모든 하이라이트 제거
   */
  clearHighlight() {
    var highlighted = document.querySelectorAll("#groups-tree .tree-node-content.highlight");
    highlighted.forEach(function (el) {
      el.classList.remove("highlight");
    });
  }

  /**
   * 트리에서 특정 노드를 ID로 찾기 (재귀)
   */
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

  /**
   * 노드의 모든 부모를 펼침 상태로 설정
   */
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
}

/**
 * 뷰 전환 (목록 <-> 트리)
 */
function switchView(view) {
  var listContainer = document.getElementById("groups-list");
  var treeContainer = document.getElementById("groups-tree");
  var paginationContainer = document.getElementById("groups-pagination");
  var toggleBtns = document.querySelectorAll(".view-toggle .toggle-btn");

  toggleBtns.forEach(function (btn) {
    btn.classList.remove("active");
    if (btn.dataset.view === view) {
      btn.classList.add("active");
    }
  });

  if (view === "tree") {
    if (listContainer) listContainer.style.display = "none";
    if (paginationContainer) paginationContainer.style.display = "none";
    if (treeContainer) treeContainer.style.display = "block";

    // 트리 데이터 로드
    if (window.groupManager && window.groupManager.treeView) {
      window.groupManager.treeView.loadTree();
    }
  } else {
    if (listContainer) listContainer.style.display = "";
    if (paginationContainer) paginationContainer.style.display = "";
    if (treeContainer) treeContainer.style.display = "none";
  }
}

/**
 * 현재 활성 뷰가 트리인지 확인
 */
function isTreeViewActive() {
  var activeBtn = document.querySelector(".view-toggle .toggle-btn.active");
  return activeBtn && activeBtn.dataset.view === "tree";
}
