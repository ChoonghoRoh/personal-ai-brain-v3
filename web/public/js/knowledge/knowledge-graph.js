// Phase 15-8-1: D3.js Force-Directed Graph 지식 노드 관계 시각화

const COLORS = [
  '#2563eb', '#dc2626', '#059669', '#d97706', '#7c3aed',
  '#0891b2', '#e11d48', '#4f46e5', '#0d9488', '#ca8a04'
];

function getAuthHeaders() {
  const headers = {};
  const token = localStorage.getItem('auth_token');
  if (token) headers['Authorization'] = 'Bearer ' + token;
  return headers;
}

let simulation = null;

async function loadGraphData() {
  const limit = document.getElementById('node-limit').value;
  const minConf = document.getElementById('min-confidence').value;

  try {
    const res = await fetch(
      `/api/knowledge/graph?limit=${limit}&min_confidence=${minConf}`,
      { headers: getAuthHeaders() }
    );
    if (!res.ok) throw new Error('그래프 데이터 로드 실패');
    const data = await res.json();

    document.getElementById('node-count').textContent = `노드: ${data.total_nodes}`;
    document.getElementById('link-count').textContent = `링크: ${data.total_links}`;

    if (data.nodes.length === 0) {
      document.querySelector('.graph-canvas-wrapper').innerHTML =
        '<div class="graph-empty">관계 데이터가 없습니다. 청크 간 관계를 먼저 생성하세요.</div>';
      return;
    }

    renderGraph(data);
  } catch (err) {
    if (typeof showError === 'function') showError(err.message);
    console.error(err);
  }
}

function renderGraph(data) {
  const wrapper = document.querySelector('.graph-canvas-wrapper');
  wrapper.innerHTML = '<svg id="graph-svg"></svg>';

  const svg = d3.select('#graph-svg');
  const width = wrapper.clientWidth;
  const height = wrapper.clientHeight;

  svg.attr('viewBox', [0, 0, width, height]);

  // 그룹별 색상 매핑
  const groups = [...new Set(data.nodes.map(n => n.group))];
  const colorMap = {};
  groups.forEach((g, i) => { colorMap[g] = COLORS[i % COLORS.length]; });

  // 줌
  const g = svg.append('g');
  svg.call(d3.zoom()
    .scaleExtent([0.2, 5])
    .on('zoom', (event) => g.attr('transform', event.transform))
  );

  // 링크
  const link = g.append('g')
    .selectAll('line')
    .data(data.links)
    .join('line')
    .attr('class', 'link')
    .attr('stroke-width', d => Math.max(1, d.confidence * 3));

  // 노드
  const node = g.append('g')
    .selectAll('g')
    .data(data.nodes)
    .join('g')
    .attr('class', 'node')
    .call(d3.drag()
      .on('start', dragStarted)
      .on('drag', dragged)
      .on('end', dragEnded)
    );

  node.append('circle')
    .attr('r', 8)
    .attr('fill', d => colorMap[d.group] || '#94a3b8')
    .on('click', (event, d) => showNodeDetail(d));

  node.append('text')
    .text(d => d.label.length > 20 ? d.label.substring(0, 20) + '...' : d.label);

  // 시뮬레이션
  if (simulation) simulation.stop();

  simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.links).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(20))
    .on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

  function dragStarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragEnded(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

function showNodeDetail(node) {
  const panel = document.getElementById('node-detail');
  document.getElementById('detail-title').textContent = node.label;
  document.getElementById('detail-document').textContent = `문서: ${node.document_name || '-'}`;
  document.getElementById('detail-group').textContent = `문서 ID: ${node.document_id || '-'}`;
  panel.style.display = 'block';
}

// 이벤트
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('refresh-btn').addEventListener('click', loadGraphData);
  document.getElementById('node-limit').addEventListener('change', loadGraphData);

  const slider = document.getElementById('min-confidence');
  slider.addEventListener('input', () => {
    document.getElementById('confidence-value').textContent = parseFloat(slider.value).toFixed(1);
  });
  slider.addEventListener('change', loadGraphData);

  loadGraphData();
});
