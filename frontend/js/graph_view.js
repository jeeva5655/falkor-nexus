/**
 * FalkorNexus Force-Directed Knowledge Graph Visualizer
 * High-performance HTML5 Canvas renderer with physics, multi-color node types,
 * path glow highlighting, and blast radius pulse animations.
 */

class GraphVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext('2d');
    
    this.nodes = [];
    this.links = [];
    this.nodeMap = new Map();
    
    // Viewport transform
    this.zoom = 1;
    this.panX = 0;
    this.panY = 0;
    this.isPanning = false;
    this.draggedNode = null;
    this.selectedNode = null;
    this.hoveredNode = null;
    this.startPan = { x: 0, y: 0 };

    // Highlight states
    this.highlightedPath = new Set();
    this.blastRadiusRoot = null;
    this.blastRadiusNodes = new Set();

    // Color Palette
    this.labelColors = {
      Service: '#00f2fe',
      Person: '#10b981',
      Team: '#8a2be2',
      Incident: '#ff4b72',
      PullRequest: '#f59e0b',
      Commit: '#94a3b8',
      RFC: '#38bdf8',
      Decision: '#6366f1',
      Playbook: '#ec4899',
      PlaybookStep: '#d946ef',
      SlackMessage: '#06b6d4',
      MemoryEpisode: '#14b8a6',
      AgentSession: '#8b5cf6',
      Default: '#cbd5e1'
    };

    this.initCanvasSize();
    this.setupEventListeners();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initCanvasSize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.setTransform(1, 0, 0, 1, 0, 0);
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
    this.panX = this.width / 2;
    this.panY = this.height / 2;
  }

  loadData(graphData) {
    this.nodeMap.clear();
    const existingPositions = new Map(this.nodes.map(n => [n.id, { x: n.x, y: n.y, vx: n.vx, vy: n.vy }]));

    this.nodes = graphData.nodes.map((n, i) => {
      const saved = existingPositions.get(n.id);
      const angle = (i / graphData.nodes.length) * 2 * Math.PI;
      const radius = 120 + Math.random() * 160;
      return {
        ...n,
        x: saved ? saved.x : Math.cos(angle) * radius,
        y: saved ? saved.y : Math.sin(angle) * radius,
        vx: saved ? saved.vx : 0,
        vy: saved ? saved.vy : 0,
        radius: n.label === 'Service' ? 14 : (n.label === 'Incident' ? 16 : 11),
        color: this.labelColors[n.label] || this.labelColors.Default
      };
    });

    this.nodes.forEach(n => this.nodeMap.set(n.id, n));

    this.links = graphData.links.map(l => ({
      ...l,
      sourceNode: this.nodeMap.get(typeof l.source === 'object' ? l.source.id : l.source),
      targetNode: this.nodeMap.get(typeof l.target === 'object' ? l.target.id : l.target)
    })).filter(l => l.sourceNode && l.targetNode);
  }

  setupEventListeners() {
    window.addEventListener('resize', () => this.initCanvasSize());

    this.canvas.addEventListener('mousedown', (e) => {
      const pos = this.getMousePos(e);
      const clicked = this.getNodeAt(pos.x, pos.y);
      if (clicked) {
        this.draggedNode = clicked;
        this.selectedNode = clicked;
        if (this.onNodeSelected) this.onNodeSelected(clicked);
      } else {
        this.isPanning = true;
        this.startPan = { x: e.clientX - this.panX, y: e.clientY - this.panY };
      }
    });

    window.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const pos = this.getMousePos(e);

      if (this.draggedNode) {
        this.draggedNode.x = (pos.x - this.panX) / this.zoom;
        this.draggedNode.y = (pos.y - this.panY) / this.zoom;
      } else if (this.isPanning) {
        this.panX = e.clientX - this.startPan.x;
        this.panY = e.clientY - this.startPan.y;
      } else {
        this.hoveredNode = this.getNodeAt(pos.x, pos.y);
        this.canvas.style.cursor = this.hoveredNode ? 'pointer' : 'default';
      }
    });

    window.addEventListener('mouseup', () => {
      this.draggedNode = null;
      this.isPanning = false;
    });

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = 1.1;
      if (e.deltaY < 0) {
        this.zoom = Math.min(this.zoom * zoomFactor, 3.5);
      } else {
        this.zoom = Math.max(this.zoom / zoomFactor, 0.35);
      }
    });
  }

  getMousePos(e) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }

  getNodeAt(screenX, screenY) {
    const worldX = (screenX - this.panX) / this.zoom;
    const worldY = (screenY - this.panY) / this.zoom;

    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const n = this.nodes[i];
      const dx = worldX - n.x;
      const dy = worldY - n.y;
      if (dx * dx + dy * dy < (n.radius + 5) * (n.radius + 5)) {
        return n;
      }
    }
    return null;
  }

  highlightPath(nodeIds) {
    this.highlightedPath = new Set(nodeIds);
  }

  highlightBlastRadius(rootId, impactedIds) {
    this.blastRadiusRoot = rootId;
    this.blastRadiusNodes = new Set(impactedIds);
  }

  clearHighlights() {
    this.highlightedPath.clear();
    this.blastRadiusRoot = null;
    this.blastRadiusNodes.clear();
  }

  applyForces() {
    const kRepel = 1200;
    const kAttract = 0.04;
    const kCenter = 0.015;

    // Node-Node Repulsion
    for (let i = 0; i < this.nodes.length; i++) {
      const n1 = this.nodes[i];
      for (let j = i + 1; j < this.nodes.length; j++) {
        const n2 = this.nodes[j];
        let dx = n2.x - n1.x;
        let dy = n2.y - n1.y;
        let distSq = dx * dx + dy * dy || 1;
        let dist = Math.sqrt(distSq);
        if (dist < 400) {
          let force = kRepel / distSq;
          let fx = (dx / dist) * force;
          let fy = (dy / dist) * force;
          if (n1 !== this.draggedNode) { n1.vx -= fx; n1.vy -= fy; }
          if (n2 !== this.draggedNode) { n2.vx += fx; n2.vy += fy; }
        }
      }

      // Center Gravity
      if (n1 !== this.draggedNode) {
        n1.vx -= n1.x * kCenter;
        n1.vy -= n1.y * kCenter;
      }
    }

    // Link Attraction
    for (let link of this.links) {
      const src = link.sourceNode;
      const tgt = link.targetNode;
      let dx = tgt.x - src.x;
      let dy = tgt.y - src.y;
      let dist = Math.sqrt(dx * dx + dy * dy) || 1;
      let targetDist = 90;
      let force = (dist - targetDist) * kAttract;
      let fx = (dx / dist) * force;
      let fy = (dy / dist) * force;

      if (src !== this.draggedNode) { src.vx += fx; src.vy += fy; }
      if (tgt !== this.draggedNode) { tgt.vx -= fx; tgt.vy -= fy; }
    }

    // Velocity integration & damping
    const damping = 0.82;
    for (let n of this.nodes) {
      if (n === this.draggedNode) continue;
      n.vx *= damping;
      n.vy *= damping;
      n.x += n.vx;
      n.y += n.vy;
    }
  }

  animate() {
    this.applyForces();

    this.ctx.clearRect(0, 0, this.width, this.height);
    this.ctx.save();
    this.ctx.translate(this.panX, this.panY);
    this.ctx.scale(this.zoom, this.zoom);

    // Draw Links
    for (let link of this.links) {
      const src = link.sourceNode;
      const tgt = link.targetNode;
      const isPathLink = this.highlightedPath.has(src.id) && this.highlightedPath.has(tgt.id);
      const isBlastLink = (this.blastRadiusRoot === src.id && this.blastRadiusNodes.has(tgt.id)) ||
                          (this.blastRadiusRoot === tgt.id && this.blastRadiusNodes.has(src.id));

      this.ctx.beginPath();
      this.ctx.moveTo(src.x, src.y);
      this.ctx.lineTo(tgt.x, tgt.y);

      if (isPathLink) {
        this.ctx.strokeStyle = '#00f2fe';
        this.ctx.lineWidth = 3.5;
        this.ctx.shadowColor = '#00f2fe';
        this.ctx.shadowBlur = 12;
      } else if (isBlastLink) {
        this.ctx.strokeStyle = '#ff4b72';
        this.ctx.lineWidth = 2.5;
        this.ctx.shadowColor = '#ff4b72';
        this.ctx.shadowBlur = 8;
      } else {
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
        this.ctx.lineWidth = 1;
        this.ctx.shadowBlur = 0;
      }
      this.ctx.stroke();
      this.ctx.shadowBlur = 0;

      // Draw arrow
      if (isPathLink || this.zoom > 1.2) {
        this.drawArrow(src, tgt, isPathLink ? '#00f2fe' : 'rgba(255, 255, 255, 0.2)');
      }
    }

    // Draw Nodes
    const now = Date.now();
    for (let node of this.nodes) {
      const isSelected = this.selectedNode && this.selectedNode.id === node.id;
      const isHovered = this.hoveredNode && this.hoveredNode.id === node.id;
      const isPathNode = this.highlightedPath.has(node.id);
      const isBlastRoot = this.blastRadiusRoot === node.id;
      const isBlastNode = this.blastRadiusNodes.has(node.id);

      // Pulse ring for blast radius root
      if (isBlastRoot) {
        const pulse = (now % 1500) / 1500;
        this.ctx.beginPath();
        this.ctx.arc(node.x, node.y, node.radius + pulse * 28, 0, Math.PI * 2);
        this.ctx.strokeStyle = `rgba(255, 75, 114, ${1 - pulse})`;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
      }

      // Draw node circle
      this.ctx.beginPath();
      this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);

      if (isPathNode || isSelected || isHovered) {
        this.ctx.shadowColor = node.color;
        this.ctx.shadowBlur = 16;
      } else {
        this.ctx.shadowBlur = 0;
      }

      this.ctx.fillStyle = node.color;
      this.ctx.fill();

      // Inner stroke
      this.ctx.strokeStyle = isSelected ? '#ffffff' : 'rgba(255, 255, 255, 0.3)';
      this.ctx.lineWidth = isSelected ? 2.5 : 1;
      this.ctx.stroke();
      this.ctx.shadowBlur = 0;

      // Node Label text
      if (this.zoom > 0.6 || isSelected || isHovered || isPathNode) {
        this.ctx.font = `${isSelected || isPathNode ? 'bold 11px' : '9px'} Outfit, sans-serif`;
        this.ctx.fillStyle = isSelected || isPathNode ? '#ffffff' : '#94a3b8';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(node.name || node.id, node.x, node.y + node.radius + 12);
      }
    }

    this.ctx.restore();
    requestAnimationFrame(this.animate);
  }

  drawArrow(src, tgt, color) {
    const angle = Math.atan2(tgt.y - src.y, tgt.x - src.x);
    const dist = tgt.radius + 4;
    const arrowX = tgt.x - Math.cos(angle) * dist;
    const arrowY = tgt.y - Math.sin(angle) * dist;

    this.ctx.fillStyle = color;
    this.ctx.beginPath();
    this.ctx.moveTo(arrowX, arrowY);
    this.ctx.lineTo(arrowX - 8 * Math.cos(angle - Math.PI / 7), arrowY - 8 * Math.sin(angle - Math.PI / 7));
    this.ctx.lineTo(arrowX - 8 * Math.cos(angle + Math.PI / 7), arrowY - 8 * Math.sin(angle + Math.PI / 7));
    this.ctx.closePath();
    this.ctx.fill();
  }

  resetView() {
    this.zoom = 1;
    this.panX = this.width / 2;
    this.panY = this.height / 2;
  }
}
