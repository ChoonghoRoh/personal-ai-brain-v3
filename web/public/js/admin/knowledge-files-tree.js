// 파일관리 — 트리뷰 모듈
// Phase 16-5: knowledge-files.js에서 분할

import { loadFileList } from './knowledge-files-api.js';

// ── 전역 함수 (utils.js) ──
// esc, getAuthHeaders

/** 현재 선택된 트리 폴더 경로 */
let _selectedTreePath = null;

/**
 * 트리뷰 노드 데이터 로드
 * @param {string} path - 상대 경로
 * @returns {Promise<Array>}
 */
async function loadTreeNode(path) {
  const headers = {};
  const token = localStorage.getItem('auth_token');
  if (token) headers['Authorization'] = 'Bearer ' + token;

  const url = `/api/knowledge/browse-directory?path=${encodeURIComponent(path)}&show_files=false`;
  const res = await fetch(url, { headers });
  if (!res.ok) throw new Error('디렉토리 탐색 실패');
  return await res.json();
}

/**
 * 트리뷰 노드 렌더링
 * @param {HTMLElement} parentEl - 부모 DOM 엘리먼트
 * @param {Array} items - 디렉토리 항목 리스트
 * @param {number} depth - 트리 깊이
 */
function renderTreeNodes(parentEl, items, depth) {
  items.forEach(item => {
    if (item.type !== 'dir') return;

    const node = document.createElement('div');
    node.className = 'kf-tree-node';

    const indent = 12 + depth * 16;
    const hasChildren = item.children_count > 0;
    const arrowClass = hasChildren ? 'kf-tree-arrow' : 'kf-tree-arrow empty';

    const folder = document.createElement('div');
    folder.className = 'kf-tree-folder';
    folder.style.paddingLeft = indent + 'px';
    folder.dataset.path = item.path;
    folder.innerHTML =
      `<span class="${arrowClass}">&#9654;</span>` +
      `<span class="kf-tree-icon">📁</span>` +
      `<span class="kf-tree-name" title="${esc(item.path)}">${esc(item.name)}</span>`;

    const childrenContainer = document.createElement('div');
    childrenContainer.className = 'kf-tree-children';

    // 폴더 클릭 → 선택 + 토글
    folder.addEventListener('click', async (e) => {
      e.stopPropagation();
      // 선택 표시
      selectTreeFolder(item.path, folder);

      // 하위 로드 (lazy)
      if (hasChildren && !childrenContainer.dataset.loaded) {
        try {
          const data = await loadTreeNode(item.path);
          renderTreeNodes(childrenContainer, data.items, depth + 1);
          childrenContainer.dataset.loaded = 'true';
        } catch (err) {
          console.error('트리 노드 로드 실패:', err);
        }
      }

      // 펼침/접힘 토글
      if (hasChildren) {
        const arrow = folder.querySelector('.kf-tree-arrow');
        childrenContainer.classList.toggle('expanded');
        if (arrow) arrow.classList.toggle('expanded');
      }
    });

    node.appendChild(folder);
    node.appendChild(childrenContainer);
    parentEl.appendChild(node);
  });
}

/**
 * 트리 폴더 선택 처리
 * @param {string} folderPath - 선택된 폴더의 상대 경로
 * @param {HTMLElement} folderEl - 선택된 폴더 DOM 엘리먼트
 */
async function selectTreeFolder(folderPath, folderEl) {
  // 이전 선택 해제
  document.querySelectorAll('.kf-tree-folder.selected').forEach(el => {
    el.classList.remove('selected');
  });
  folderEl.classList.add('selected');
  _selectedTreePath = folderPath;

  // 현재 폴더 배지 업데이트
  const badge = document.getElementById('current-folder-display');
  if (badge) badge.textContent = folderPath || '(프로젝트 루트)';

  // PUT /api/knowledge/folder-config 호출하여 폴더 경로 설정
  try {
    const headers = getAuthHeaders();
    await fetch('/api/knowledge/folder-config', {
      method: 'PUT',
      headers,
      body: JSON.stringify({ folder_path: folderPath })
    });

    // 탭2의 폴더 경로 입력창도 업데이트
    const folderInput = document.getElementById('folder-path-input');
    if (folderInput) folderInput.value = folderPath;

    // 파일 목록 갱신
    await loadFileList();
  } catch (err) {
    console.error('폴더 선택 실패:', err);
  }
}

/**
 * 트리뷰 초기화 (루트 로드)
 */
export async function initTreeView() {
  const treeBody = document.getElementById('kf-tree-body');
  if (!treeBody) return;

  try {
    const data = await loadTreeNode('');
    treeBody.innerHTML = '';
    renderTreeNodes(treeBody, data.items, 0);
  } catch (err) {
    console.error('트리뷰 초기화 실패:', err);
    treeBody.innerHTML = '<div class="kf-tree-loading">폴더를 불러올 수 없습니다.</div>';
  }
}
