/**
 * 키워드 그룹 트리 컨텍스트 메뉴 모듈
 * 우클릭 메뉴 생성 및 노드 이동/추가 다이얼로그 관리
 */
class KeywordGroupContextMenu {
  constructor(treeView) {
    this.treeView = treeView;
    this._contextMenuCloseHandler = null;
  }

  /**
   * 노드 우클릭 컨텍스트 메뉴 표시
   */
  show(event, node) {
    this.remove();

    var self = this;
    var isRootNode = !this.treeView._findParentId(node.id);

    var menu = document.createElement("div");
    menu.className = "tree-context-menu";
    menu.style.cssText = "position:fixed;z-index:9999;background:white;border:1px solid #e5e7eb;border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:4px 0;min-width:160px;";
    menu.style.left = event.clientX + "px";
    menu.style.top = event.clientY + "px";

    // 1. 루트로 이동 (루트 노드이면 비활성)
    if (!isRootNode) {
      var moveToRootItem = this._createMenuItem("루트로 이동", false);
      moveToRootItem.addEventListener("click", function () {
        self.remove();
        if (confirm('"' + node.name + '"을(를) 루트로 이동하시겠습니까?')) {
          self.treeView.moveNode(node.id, null);
        }
      });
      menu.appendChild(moveToRootItem);
    }

    // 2. 부모 변경
    var changeParentItem = this._createMenuItem("부모 변경", false);
    changeParentItem.addEventListener("click", function () {
      self.remove();
      self._showChangeParentDialog(node);
    });
    menu.appendChild(changeParentItem);

    // 3. 하위 그룹 추가
    var addChildItem = this._createMenuItem("하위 그룹 추가", false);
    addChildItem.addEventListener("click", function () {
      self.remove();
      self._showAddChildGroupDialog(node);
    });
    menu.appendChild(addChildItem);

    document.body.appendChild(menu);

    // 화면 밖으로 나가지 않도록 위치 보정
    var rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) {
      menu.style.left = (window.innerWidth - rect.width - 8) + "px";
    }
    if (rect.bottom > window.innerHeight) {
      menu.style.top = (window.innerHeight - rect.height - 8) + "px";
    }

    // 외부 클릭 시 닫기
    setTimeout(function () {
      document.addEventListener("click", self._contextMenuCloseHandler = function () {
        self.remove();
      }, { once: true });
    }, 0);
  }

  /**
   * 컨텍스트 메뉴 제거
   */
  remove() {
    var existing = document.querySelector(".tree-context-menu");
    if (existing) existing.remove();
    if (this._contextMenuCloseHandler) {
      document.removeEventListener("click", this._contextMenuCloseHandler);
      this._contextMenuCloseHandler = null;
    }
  }

  /**
   * 컨텍스트 메뉴 아이템 생성 헬퍼
   */
  _createMenuItem(text, disabled) {
    var item = document.createElement("div");
    item.style.cssText = "padding:8px 16px;cursor:" + (disabled ? "not-allowed" : "pointer") + ";font-size:13px;color:" + (disabled ? "#9ca3af" : "#374151") + ";";
    item.textContent = text;
    if (!disabled) {
      item.addEventListener("mouseenter", function () {
        item.style.background = "#f3f4f6";
      });
      item.addEventListener("mouseleave", function () {
        item.style.background = "";
      });
    }
    return item;
  }

  /**
   * 부모 변경 다이얼로그 (가능한 부모 목록 선택)
   */
  _showChangeParentDialog(node) {
    var self = this;
    var possibleParents = this._getValidParentNodes(node.id);

    if (possibleParents.length === 0) {
      alert("이동 가능한 부모 그룹이 없습니다.");
      return;
    }

    var dialog = document.createElement("div");
    dialog.style.cssText = "position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:10000;background:white;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.2);padding:20px;min-width:300px;max-width:500px;max-height:400px;overflow-y:auto;";

    var title = document.createElement("h4");
    title.textContent = "부모 그룹 선택";
    title.style.cssText = "margin:0 0 16px 0;color:#1f2937;font-size:16px;";
    dialog.appendChild(title);

    var info = document.createElement("p");
    info.textContent = '"' + node.name + '"의 새 부모를 선택하세요:';
    info.style.cssText = "margin:0 0 12px 0;font-size:13px;color:#6b7280;";
    dialog.appendChild(info);

    var listContainer = document.createElement("div");
    listContainer.style.cssText = "margin-bottom:16px;max-height:200px;overflow-y:auto;border:1px solid #e5e7eb;border-radius:6px;";

    possibleParents.forEach(function (parent) {
      var item = document.createElement("div");
      item.style.cssText = "padding:10px 12px;cursor:pointer;font-size:13px;border-bottom:1px solid #f3f4f6;";
      item.textContent = parent.path + " (" + parent.name + ")";
      item.addEventListener("mouseenter", function () {
        item.style.background = "#f3f4f6";
      });
      item.addEventListener("mouseleave", function () {
        item.style.background = "";
      });
      item.addEventListener("click", function () {
        document.body.removeChild(dialog);
        if (confirm('"' + node.name + '"을(를) "' + parent.name + '" 하위로 이동하시겠습니까?')) {
          self.treeView.moveNode(node.id, parent.id);
        }
      });
      listContainer.appendChild(item);
    });
    dialog.appendChild(listContainer);

    var cancelBtn = document.createElement("button");
    cancelBtn.textContent = "취소";
    cancelBtn.className = "btn btn-secondary";
    cancelBtn.style.cssText = "width:100%;padding:8px;";
    cancelBtn.addEventListener("click", function () {
      document.body.removeChild(dialog);
    });
    dialog.appendChild(cancelBtn);

    document.body.appendChild(dialog);
  }

  /**
   * 하위 그룹 추가 다이얼로그
   */
  _showAddChildGroupDialog(parentNode) {
    var self = this;

    var dialog = document.createElement("div");
    dialog.style.cssText = "position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:10000;background:white;border:1px solid #e5e7eb;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,0.2);padding:20px;min-width:320px;";

    var title = document.createElement("h4");
    title.textContent = "하위 그룹 추가";
    title.style.cssText = "margin:0 0 16px 0;color:#1f2937;font-size:16px;";
    dialog.appendChild(title);

    var info = document.createElement("p");
    info.textContent = '"' + parentNode.name + '" 하위에 새 그룹을 생성합니다.';
    info.style.cssText = "margin:0 0 12px 0;font-size:13px;color:#6b7280;";
    dialog.appendChild(info);

    var nameLabel = document.createElement("label");
    nameLabel.textContent = "그룹 이름";
    nameLabel.style.cssText = "display:block;margin-bottom:4px;font-size:13px;font-weight:600;color:#374151;";
    dialog.appendChild(nameLabel);

    var nameInput = document.createElement("input");
    nameInput.type = "text";
    nameInput.placeholder = "새 그룹 이름";
    nameInput.style.cssText = "width:100%;padding:8px 10px;border:1px solid #e5e7eb;border-radius:6px;font-size:14px;margin-bottom:12px;box-sizing:border-box;";
    dialog.appendChild(nameInput);

    var descLabel = document.createElement("label");
    descLabel.textContent = "설명 (선택)";
    descLabel.style.cssText = "display:block;margin-bottom:4px;font-size:13px;font-weight:600;color:#374151;";
    dialog.appendChild(descLabel);

    var descInput = document.createElement("textarea");
    descInput.placeholder = "그룹 설명";
    descInput.style.cssText = "width:100%;padding:8px 10px;border:1px solid #e5e7eb;border-radius:6px;font-size:14px;margin-bottom:16px;box-sizing:border-box;min-height:60px;";
    dialog.appendChild(descInput);

    var btnContainer = document.createElement("div");
    btnContainer.style.cssText = "display:flex;gap:8px;";

    var createBtn = document.createElement("button");
    createBtn.textContent = "생성";
    createBtn.className = "btn btn-primary";
    createBtn.style.cssText = "flex:1;padding:8px;";
    createBtn.addEventListener("click", async function () {
      var name = nameInput.value.trim();
      if (!name) {
        alert("그룹 이름을 입력하세요.");
        return;
      }
      document.body.removeChild(dialog);
      await self._createChildGroup(parentNode.id, name, descInput.value.trim());
    });
    btnContainer.appendChild(createBtn);

    var cancelBtn = document.createElement("button");
    cancelBtn.textContent = "취소";
    cancelBtn.className = "btn btn-secondary";
    cancelBtn.style.cssText = "flex:1;padding:8px;";
    cancelBtn.addEventListener("click", function () {
      document.body.removeChild(dialog);
    });
    btnContainer.appendChild(cancelBtn);

    dialog.appendChild(btnContainer);
    document.body.appendChild(dialog);

    nameInput.focus();
  }

  /**
   * 하위 그룹 생성 API 호출
   */
  async _createChildGroup(parentId, name, description) {
    try {
      var response = await fetch("/api/labels", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name,
          description: description || "",
          parent_id: parentId,
          label_type: "group"
        })
      });

      if (!response.ok) {
        var errorData = await response.json().catch(function () { return {}; });
        throw new Error(errorData.detail || "그룹 생성 실패");
      }

      showSuccess("하위 그룹이 생성되었습니다.");

      // 부모 노드를 펼친 상태로 설정
      this.treeView.expandedNodes.add(parentId);

      await this.treeView.loadTree();
    } catch (error) {
      console.error("하위 그룹 생성 실패:", error);
      showError(error.message || "그룹 생성 중 오류가 발생했습니다.");
    }
  }

  /**
   * 유효한 부모 노드 목록 반환 (현재 노드와 그 하위 노드 제외)
   */
  _getValidParentNodes(nodeId) {
    var result = [];
    var excludeIds = new Set([nodeId]);
    this._collectDescendantIds(nodeId, excludeIds);
    this._collectValidParents(this.treeView.treeData, excludeIds, result, "");
    return result;
  }

  /**
   * 하위 노드 ID 수집
   */
  _collectDescendantIds(nodeId, result) {
    var node = this.treeView._findNode(nodeId);
    if (node && node.children) {
      for (var i = 0; i < node.children.length; i++) {
        result.add(node.children[i].id);
        this._collectDescendantIds(node.children[i].id, result);
      }
    }
  }

  /**
   * 유효한 부모 노드 수집 (경로 포함)
   */
  _collectValidParents(nodes, excludeIds, result, pathPrefix) {
    for (var i = 0; i < nodes.length; i++) {
      var node = nodes[i];
      if (!excludeIds.has(node.id)) {
        var currentPath = pathPrefix ? pathPrefix + " > " + node.name : node.name;
        result.push({
          id: node.id,
          name: node.name,
          path: currentPath
        });
        if (node.children && node.children.length > 0) {
          this._collectValidParents(node.children, excludeIds, result, currentPath);
        }
      }
    }
  }
}
