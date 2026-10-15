/**
 * FalkorNexus Application Controller
 * Handles Multi-Agent Streaming, Scenario Orchestration,
 * Track Explorers, Cypher Console, and Real-Time Event Ingestion.
 */

let visualizer = null;
let currentSessionId = 'session_' + Math.random().toString(36).substring(2, 9);
const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', async () => {
  visualizer = new GraphVisualizer('graphCanvas');
  visualizer.onNodeSelected = handleNodeSelection;

  await checkSystemHealth();
  await loadGraphData();
  setupTabNavigation();
  setupScenarioButtons();
  setupCypherConsole();
  setupIngestionForm();
  setupPlaybookForm();
  setupConnectionModal();

  // Send initial chat handler
  document.getElementById('btnSubmitChat').addEventListener('click', handleChatSubmit);
  document.getElementById('chatInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChatSubmit();
    }
  });

  // Reset graph view button
  document.getElementById('btnResetView').addEventListener('click', () => {
    visualizer.resetView();
    visualizer.clearHighlights();
  });
});

// ----------------- System & Graph Loading -----------------
async function checkSystemHealth() {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    const data = await res.json();
    const modeEl = document.getElementById('falkorModeText');
    const badgeEl = document.getElementById('statusBadge');
    
    if (data.falkordb.status === 'connected') {
      modeEl.textContent = 'FalkorDB Live (Port 6379)';
      badgeEl.style.borderColor = 'var(--accent-emerald)';
    } else {
      modeEl.textContent = 'FalkorDB Engine (Dual-Mode Ready)';
      badgeEl.style.borderColor = 'var(--accent-cyan)';
    }
  } catch (e) {
    console.warn('Healthcheck error:', e);
  }
}

async function loadGraphData() {
  try {
    const res = await fetch(`${API_BASE}/api/graph/data`);
    const data = await res.json();
    visualizer.loadData(data);
    document.getElementById('nodeCount').textContent = data.stats.total_nodes;
    document.getElementById('edgeCount').textContent = data.stats.total_links;
  } catch (e) {
    console.error('Failed to load graph data:', e);
  }
}

// ----------------- Multi-Agent Orchestration & Chat -----------------
async function handleChatSubmit() {
  const inputEl = document.getElementById('chatInput');
  const query = inputEl.value.trim();
  if (!query) return;

  const streamContainer = document.getElementById('agentStreamContainer');
  streamContainer.innerHTML = '';
  document.getElementById('btnSubmitChat').disabled = true;
  document.getElementById('btnSubmitChat').innerHTML = '<span>Orchestrating...</span>';

  try {
    const res = await fetch(`${API_BASE}/api/agents/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        session_id: currentSessionId,
        tenant_id: 'nexus_corp'
      })
    });

    const data = await res.json();
    renderAgentPipeline(data.agent_steps, data.result, data.duration_ms);

    // Highlight graph paths if present in result
    if (data.result && data.result.subgraph) {
      const nodeIds = (data.result.subgraph.nodes || []).map(n => n.id);
      if (nodeIds.length > 0) {
        visualizer.highlightPath(nodeIds);
      }
    }
  } catch (e) {
    streamContainer.innerHTML = `<div style="color:var(--accent-rose); font-size:0.8rem;">Error executing agent pipeline: ${e.message}</div>`;
  } finally {
    document.getElementById('btnSubmitChat').disabled = false;
    document.getElementById('btnSubmitChat').innerHTML = '<span>Dispatch Agents</span>';
    inputEl.value = '';
  }
}

function renderAgentPipeline(steps, finalResult, durationMs) {
  const container = document.getElementById('agentStreamContainer');
  container.innerHTML = '';

  const avatarClasses = {
    TriageAgent: 'av-triage',
    InvestigatorAgent: 'av-invest',
    ActionAgent: 'av-action',
    MemoryAgent: 'av-memory'
  };

  steps.forEach((step, idx) => {
    const card = document.createElement('div');
    card.className = 'agent-step-card';
    card.style.animationDelay = `${idx * 0.1}s`;

    const thoughtsHtml = (step.thoughts || []).map(t => `<div class="thought-item">• ${t}</div>`).join('');
    const toolsHtml = (step.tools_executed || []).map(tool => `<span class="tool-badge">⚙ ${tool}</span>`).join(' ');

    card.innerHTML = `
      <div class="agent-step-header">
        <div class="agent-identity">
          <div class="agent-avatar ${avatarClasses[step.agent] || 'av-triage'}">${step.agent[0]}</div>
          <span class="agent-name">${step.agent}</span>
        </div>
        <span class="step-status">${step.status}</span>
      </div>
      <div class="thought-list">${thoughtsHtml}</div>
      ${toolsHtml ? `<div>${toolsHtml}</div>` : ''}
    `;
    container.appendChild(card);
  });

  // Final Action & Synthesis Card
  if (finalResult) {
    const finalCard = document.createElement('div');
    finalCard.className = 'agent-step-card';
    finalCard.style.borderColor = 'var(--border-glow)';
    finalCard.style.background = 'rgba(0, 242, 254, 0.04)';

    const citationsHtml = (finalResult.citations || []).map(c => `
      <span class="citation-chip" onclick="highlightCitation('${c.id}')">
        📌 ${c.label}: ${c.title || c.id}
      </span>
    `).join(' ');

    const actionsHtml = (finalResult.actions_executed || []).map(a => `
      <div style="font-size:0.75rem; color:var(--accent-emerald); font-family:var(--font-mono); margin-top:4px;">
        ✔ [EXECUTED] ${a.action} on ${a.target}: ${a.remediation || a.details}
      </div>
    `).join('');

    finalCard.innerHTML = `
      <div class="agent-step-header">
        <span class="agent-name" style="color:var(--accent-cyan);">🏁 Decision & Remediation Summary</span>
        <span class="panel-badge">${durationMs} ms</span>
      </div>
      <div style="font-size:0.8rem; line-height:1.4; color:var(--text-primary); margin-top:6px;">
        ${finalResult.answer}
      </div>
      ${actionsHtml ? `<div style="margin-top:6px;">${actionsHtml}</div>` : ''}
      ${citationsHtml ? `<div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:8px;">${citationsHtml}</div>` : ''}
    `;
    container.appendChild(finalCard);
  }
}

window.highlightCitation = function(nodeId) {
  const node = visualizer.nodeMap.get(nodeId);
  if (node) {
    visualizer.selectedNode = node;
    visualizer.highlightPath([nodeId]);
    handleNodeSelection(node);
  }
};

// ----------------- Pre-Loaded Scenarios -----------------
function setupScenarioButtons() {
  const scenarios = [
    {
      id: 'sc1',
      prompt: 'Critical alert: PaymentGateway 500 error cascade! Trace upstream dependencies, find recent PRs and culprit commit, identify expert, and execute mitigation.',
      track: 'Track 01 & 03'
    },
    {
      id: 'sc2',
      prompt: 'Retrieve the SEV-1 triage procedural playbook and recall past session episodic memory context.',
      track: 'Track 02'
    },
    {
      id: 'sc3',
      prompt: 'Why did we decide to adopt FalkorDB multi-tenant graph context in RFC-104? Trace architectural provenance and motivating incidents.',
      track: 'Track 03'
    }
  ];

  const cards = document.querySelectorAll('.scenario-card');
  cards.forEach((card, idx) => {
    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const sc = scenarios[idx];
      if (sc) {
        document.getElementById('chatInput').value = sc.prompt;
        handleChatSubmit();
      }
    });
  });
}

// ----------------- Node Inspector -----------------
function handleNodeSelection(node) {
  const drawer = document.getElementById('nodeInspector');
  drawer.style.display = 'flex';
  document.getElementById('inspectTitle').textContent = node.name || node.id;
  document.getElementById('inspectLabel').textContent = node.label;

  const propsEl = document.getElementById('inspectProps');
  propsEl.innerHTML = '';
  const props = node.properties || {};

  for (const [k, v] of Object.entries(props)) {
    const row = document.createElement('div');
    row.className = 'prop-row';
    const displayVal = typeof v === 'object' ? JSON.stringify(v) : v;
    row.innerHTML = `<span class="prop-key">${k}</span><span class="prop-val">${displayVal}</span>`;
    propsEl.appendChild(row);
  }

  // Button: Compute Blast Radius
  document.getElementById('btnInspectBlast').onclick = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/graph/algorithms/blast_radius?node_id=${node.id}&depth=3`);
      const data = await res.json();
      const impactedIds = (data.impacted_nodes || []).map(n => n.id);
      visualizer.highlightBlastRadius(node.id, impactedIds);
    } catch (e) {
      console.error(e);
    }
  };
}

// ----------------- Track Explorer Tabs & Actions -----------------
function setupTabNavigation() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const contents = document.querySelectorAll('.tab-content');

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      contents.forEach(c => c.classList.remove('active'));

      btn.classList.add('active');
      const target = btn.getAttribute('data-tab');
      document.getElementById(target).classList.add('active');

      if (target === 'tabTrack1') loadTrack1Algorithms();
      if (target === 'tabTrack2') loadTrack2Memory();
      if (target === 'tabTrack3') loadTrack3CompanyBrain();
    });
  });
}

// Track 01 Tab: PageRank & Centrality
async function loadTrack1Algorithms() {
  try {
    const prRes = await fetch(`${API_BASE}/api/graph/algorithms/pagerank?top_k=5`);
    const prData = await prRes.json();
    const prList = document.getElementById('pagerankList');
    prList.innerHTML = prData.results.map(r => `
      <div class="algo-item">
        <span>${r.name} (${r.label})</span>
        <span class="algo-score">${r.score}</span>
      </div>
    `).join('');

    const centRes = await fetch(`${API_BASE}/api/graph/algorithms/centrality`);
    const centData = await centRes.json();
    const centList = document.getElementById('centralityList');
    centList.innerHTML = centData.betweenness_bottlenecks.map(b => `
      <div class="algo-item">
        <span>${b.name}</span>
        <span class="algo-score" style="color:var(--accent-rose);">${b.score}</span>
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

// Track 02 Tab: Memory & Procedural Playbooks
async function loadTrack2Memory() {
  try {
    const res = await fetch(`${API_BASE}/api/memory/summary`);
    const data = await res.json();
    document.getElementById('memEpisodicCount').textContent = data.episodic_episodes_count;
    document.getElementById('memSessionsCount').textContent = data.agent_sessions_count;
    document.getElementById('memTransitionsCount').textContent = data.state_transitions_count;
    document.getElementById('memPlaybooksCount').textContent = data.procedural_playbooks_count;

    // Load Playbook Workflow
    const pbRes = await fetch(`${API_BASE}/api/memory/procedural/playbooks/plb_sev1_triage`);
    const pbData = await pbRes.json();
    const chainEl = document.getElementById('playbookChain');
    chainEl.innerHTML = pbData.steps.map(s => `
      <div class="playbook-step-node">
        <div class="step-num-badge">${s.step_number}</div>
        <div class="step-content">
          <div class="step-title">${s.action_name}</div>
          <div class="step-cmd">${s.command}</div>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

// Track 03 Tab: Company Brain Experts
async function loadTrack3CompanyBrain() {
  try {
    const res = await fetch(`${API_BASE}/api/mcp/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: 'falkordb_find_expert',
        arguments: { service_id: 'service_auth' }
      })
    });
    const data = await res.json();
    const expertsList = document.getElementById('expertsList');
    expertsList.innerHTML = (data.experts || []).map(exp => `
      <div class="algo-item">
        <div>
          <div style="font-weight:700; color:var(--text-primary);">${exp.person.name} (${exp.relation})</div>
          <div style="font-size:0.68rem; color:var(--text-muted);">${exp.person.role} • ${exp.person.email}</div>
        </div>
        <span class="panel-badge" style="background:rgba(0,242,254,0.15); color:var(--accent-cyan);">Expert</span>
      </div>
    `).join('');
  } catch (e) {
    console.error(e);
  }
}

// ----------------- Cypher Console -----------------
function setupCypherConsole() {
  document.getElementById('btnRunCypher').addEventListener('click', async () => {
    const query = document.getElementById('cypherInput').value.trim();
    if (!query) return;

    const outEl = document.getElementById('cypherOutput');
    outEl.textContent = 'Executing query...';

    try {
      const res = await fetch(`${API_BASE}/api/graph/cypher`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cypher: query, tenant_id: 'nexus_corp' })
      })
      const data = await res.json();
      outEl.textContent = JSON.stringify(data.results, null, 2);
    } catch (e) {
      outEl.textContent = 'Error: ' + e.message;
    }
  });

  // Query Presets
  const chips = document.querySelectorAll('.preset-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      document.getElementById('cypherInput').value = chip.getAttribute('data-cypher');
      document.getElementById('btnRunCypher').click();
    });
  });
}

// ----------------- Dynamic Ingestion Simulator (Track 03) -----------------
function setupIngestionForm() {
  document.getElementById('btnIngestCommit').addEventListener('click', async () => {
    const hash = 'a' + Math.random().toString(36).substring(2, 7);
    const res = await fetch(`${API_BASE}/api/ingest/event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: 'commit',
        data: {
          hash: hash,
          message: 'hotfix(auth): add rate-limiting token bucket fallback',
          author_id: 'sarah_chen',
          service_id: 'service_auth'
        }
      })
    });
    const data = await res.json();
    alert(`Dynamic Ingestion Success: Node ${data.id} created and linked in FalkorDB graph.`);
    await loadGraphData();
  });
}

// ----------------- Procedural Learning Form (Track 02) -----------------
function setupPlaybookForm() {
  document.getElementById('btnLearnPlaybook').addEventListener('click', async () => {
    const res = await fetch(`${API_BASE}/api/memory/procedural/learn`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: 'Database Failover & High-Availability Resync SOP',
        domain: 'Data Platform',
        trigger_condition: 'db_replica_lag > 5000ms',
        steps: [
          { action_name: 'Check Replica Heartbeat', command: 'CALL falkor.cluster.status()' },
          { action_name: 'Promote Read-Replica to Primary', command: 'EXECUTE cluster.failover(force=True)' },
          { action_name: 'Resync Stale Write Wal', command: 'EXECUTE cluster.resync()' }
        ]
      })
    });
    const data = await res.json();
    alert(`Procedural Memory Learned: Created Playbook '${data.playbook.name}' in FalkorDB!`);
    loadTrack2Memory();
  });
}

// ----------------- FalkorDB Connection Modal -----------------
function setupConnectionModal() {
  const modal = document.getElementById('connectionModal');
  document.getElementById('statusBadge').addEventListener('click', () => {
    modal.style.display = 'flex';
  });
  document.getElementById('btnCloseModal').addEventListener('click', () => {
    modal.style.display = 'none';
  });

  document.getElementById('btnConnectFalkor').addEventListener('click', async () => {
    const url = document.getElementById('falkorUriInput').value.trim();
    const msgEl = document.getElementById('connectMsg');
    msgEl.textContent = 'Connecting...';

    const res = await fetch(`${API_BASE}/api/falkordb/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url || null })
    });
    const data = await res.json();
    if (data.success) {
      msgEl.style.color = 'var(--accent-emerald)';
      msgEl.textContent = data.message;
      await checkSystemHealth();
      await loadGraphData();
    } else {
      msgEl.style.color = 'var(--accent-rose)';
      msgEl.textContent = data.message;
    }
  });
}
