import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.graph_engine import engine
from backend.seeds.enterprise_data import seed_enterprise_graph
from backend.memory.episodic import EpisodicMemoryManager
from backend.memory.semantic import SemanticMemoryManager
from backend.memory.procedural import ProceduralMemoryManager
from backend.mcp_server import FalkorMCPServer
from backend.agents.orchestrator import AgentOrchestrator

# Initialize Managers
episodic_mgr = EpisodicMemoryManager(engine)
semantic_mgr = SemanticMemoryManager(engine)
procedural_mgr = ProceduralMemoryManager(engine)
memory_managers = {
    "episodic": episodic_mgr,
    "semantic": semantic_mgr,
    "procedural": procedural_mgr
}

mcp_server = FalkorMCPServer(engine)
orchestrator = AgentOrchestrator(mcp_server, memory_managers, engine)

# Populate default company graph on startup
default_graph_name = f"tenant_{settings.DEFAULT_TENANT}_brain"
default_graph = engine.get_or_create_graph(default_graph_name)
seed_result = seed_enterprise_graph(default_graph)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Models -----------------
class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "session_live_01"
    tenant_id: Optional[str] = settings.DEFAULT_TENANT

class CypherRequest(BaseModel):
    cypher: str
    tenant_id: Optional[str] = settings.DEFAULT_TENANT
    graph_type: Optional[str] = "brain"

class FalkorConnectRequest(BaseModel):
    url: Optional[str] = None
    host: Optional[str] = "localhost"
    port: Optional[int] = 6379
    password: Optional[str] = None

class IngestEventRequest(BaseModel):
    event_type: str  # "commit", "slack", "ticket", "incident"
    tenant_id: Optional[str] = settings.DEFAULT_TENANT
    data: Dict[str, Any]

class LearnPlaybookRequest(BaseModel):
    name: str
    domain: str
    trigger_condition: str
    steps: List[Dict[str, Any]]
    tenant_id: Optional[str] = settings.DEFAULT_TENANT

class MCPCallRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any]

# ----------------- System & Health -----------------
@app.get("/api/health")
def health_check():
    g = engine.get_or_create_graph(default_graph_name)
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "falkordb": engine.connection_info,
        "default_tenant": settings.DEFAULT_TENANT,
        "nodes_count": len(g.nodes),
        "edges_count": len(g.edges)
    }

@app.post("/api/falkordb/connect")
def connect_falkordb(req: FalkorConnectRequest):
    """
    Connects dynamically to a live FalkorDB instance (Docker or Cloud)
    and syncs the current dataset.
    """
    import falkordb
    try:
        if req.url:
            client = falkordb.FalkorDB.from_url(req.url)
        else:
            client = falkordb.FalkorDB(host=req.host, port=req.port, password=req.password or None)
        
        test = client.select_graph("falkor_ping_test")
        test.query("RETURN 1")

        engine.falkordb_client = client
        engine.is_connected = True
        engine.connection_info = {
            "status": "connected",
            "mode": "falkordb_live",
            "host": req.host,
            "port": req.port,
            "url": req.url
        }

        # Sync current default graph
        sync_res = engine.sync_to_live_falkordb(default_graph_name)

        return {
            "success": True,
            "message": "Successfully connected to FalkorDB and synced graph!",
            "sync_details": sync_res
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Could not connect to live FalkorDB. Retaining high-speed Dual-Mode In-Memory Engine."
        }

@app.post("/api/falkordb/sync")
def sync_to_falkordb():
    return engine.sync_to_live_falkordb(default_graph_name)

# ----------------- Track 01 & 03: Graph Data & Cypher -----------------
@app.get("/api/graph/data")
def get_graph_data(tenant_id: str = settings.DEFAULT_TENANT, graph_type: str = "brain"):
    g_name = f"tenant_{tenant_id}_{graph_type}"
    g = engine.get_or_create_graph(g_name)
    
    # Format for graph visualizer (nodes & links)
    nodes = []
    for nid, ndata in g.nodes.items():
        props = ndata.get("properties", {})
        label = ndata.get("label", "Node")
        name = props.get("name") or props.get("title") or props.get("id") or nid
        nodes.append({
            "id": nid,
            "label": label,
            "name": name,
            "properties": props
        })

    links = []
    for e in g.edges:
        links.append({
            "source": e["source"],
            "target": e["target"],
            "type": e["type"],
            "properties": e.get("properties", {})
        })

    return {
        "tenant_id": tenant_id,
        "graph_name": g_name,
        "nodes": nodes,
        "links": links,
        "stats": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "labels": {k: len(v) for k, v in g.labels.items()}
        }
    }

@app.post("/api/graph/cypher")
def run_cypher(req: CypherRequest):
    g_name = f"tenant_{req.tenant_id}_{req.graph_type}"
    res = engine.execute_cypher(req.cypher, graph_name=g_name)
    return res

# ----------------- Track 01: Graph Algorithms -----------------
@app.get("/api/graph/algorithms/pagerank")
def get_pagerank(tenant_id: str = settings.DEFAULT_TENANT, top_k: int = 10):
    g_name = f"tenant_{tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    scores = g.pagerank()
    top_items = list(scores.items())[:top_k]
    result = []
    for nid, score in top_items:
        node = g.get_node(nid)
        result.append({
            "id": nid,
            "score": round(score, 4),
            "label": node.get("label") if node else "Node",
            "name": node.get("properties", {}).get("name") or node.get("properties", {}).get("title") or nid
        })
    return {"algorithm": "PageRank", "results": result}

@app.get("/api/graph/algorithms/centrality")
def get_centrality(tenant_id: str = settings.DEFAULT_TENANT):
    g_name = f"tenant_{tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    bw = g.betweenness_centrality()
    deg = g.degree_centrality()
    
    top_bw = [{"id": k, "score": round(v, 4), "name": g.get_node(k)["properties"].get("name", k) if g.get_node(k) else k} for k, v in list(bw.items())[:8]]
    top_deg = [{"id": k, "score": round(v, 4), "name": g.get_node(k)["properties"].get("name", k) if g.get_node(k) else k} for k, v in list(deg.items())[:8]]

    return {
        "algorithm": "Centrality",
        "betweenness_bottlenecks": top_bw,
        "degree_hubs": top_deg
    }

@app.get("/api/graph/algorithms/communities")
def get_communities(tenant_id: str = settings.DEFAULT_TENANT):
    g_name = f"tenant_{tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    return {"algorithm": "CommunityDetection", "communities": g.community_detection()}

@app.get("/api/graph/algorithms/shortest_path")
def get_shortest_path(source: str, target: str, tenant_id: str = settings.DEFAULT_TENANT):
    g_name = f"tenant_{tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    return g.shortest_path(source, target)

@app.get("/api/graph/algorithms/blast_radius")
def get_blast_radius(node_id: str, depth: int = 3, tenant_id: str = settings.DEFAULT_TENANT):
    g_name = f"tenant_{tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    return g.blast_radius(node_id, max_depth=depth)

# ----------------- Track 02: Multi-Agent Orchestration & Chat -----------------
@app.post("/api/agents/chat")
def agent_chat(req: QueryRequest):
    """
    Submits a user prompt or incident alert to the 4-Agent Orchestrator.
    Executes TriageAgent -> InvestigatorAgent -> ActionAgent -> MemoryAgent
    with graph-persisted handoff state and returns step-by-step reasoning.
    """
    try:
        res = orchestrator.process_query(
            user_query=req.query,
            session_id=req.session_id,
            tenant_id=req.tenant_id
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/sessions/{session_id}")
def get_session_history(session_id: str, tenant_id: str = settings.DEFAULT_TENANT):
    episodes = episodic_mgr.recall_recent_episodes(session_id, limit=20, tenant_id=tenant_id)
    return {"session_id": session_id, "episodes": episodes}

@app.get("/api/agents/handoffs")
def get_agent_handoffs(tenant_id: str = settings.DEFAULT_TENANT):
    g_name = f"tenant_{tenant_id}_memory"
    g = engine.get_or_create_graph(g_name)
    states = []
    for nid in g.labels.get("AgentState", set()):
        n = g.get_node(nid)
        if n:
            states.append(n["properties"])
    states.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    return {"handoffs": states[:20]}

# ----------------- Track 02: Memory Inspection -----------------
@app.get("/api/memory/summary")
def get_memory_summary(tenant_id: str = settings.DEFAULT_TENANT):
    mem_graph = engine.get_or_create_graph(f"tenant_{tenant_id}_memory")
    brain_graph = engine.get_or_create_graph(f"tenant_{tenant_id}_brain")
    playbooks = procedural_mgr.list_all_playbooks(tenant_id=tenant_id)

    return {
        "tenant_id": tenant_id,
        "episodic_episodes_count": len(mem_graph.labels.get("MemoryEpisode", set())),
        "agent_sessions_count": len(mem_graph.labels.get("AgentSession", set())),
        "state_transitions_count": len(mem_graph.labels.get("AgentState", set())),
        "procedural_playbooks_count": len(playbooks),
        "semantic_nodes_count": len(brain_graph.nodes),
        "playbooks": playbooks
    }

@app.get("/api/memory/procedural/playbooks")
def list_playbooks(tenant_id: str = settings.DEFAULT_TENANT):
    return procedural_mgr.list_all_playbooks(tenant_id=tenant_id)

@app.get("/api/memory/procedural/playbooks/{playbook_id}")
def get_playbook(playbook_id: str, tenant_id: str = settings.DEFAULT_TENANT):
    wf = procedural_mgr.get_playbook_workflow(playbook_id, tenant_id=tenant_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Playbook not found")
    return wf

@app.post("/api/memory/procedural/learn")
def learn_playbook(req: LearnPlaybookRequest):
    return procedural_mgr.learn_new_playbook(
        name=req.name,
        domain=req.domain,
        trigger_condition=req.trigger_condition,
        steps=req.steps,
        tenant_id=req.tenant_id
    )

# ----------------- Track 01: MCP Protocol -----------------
@app.get("/api/mcp/tools")
def list_mcp_tools():
    return {"tools": mcp_server.list_tools()}

@app.post("/api/mcp/call")
def call_mcp_tool(req: MCPCallRequest):
    return mcp_server.call_tool(req.tool, req.arguments)

# ----------------- Track 03: Dynamic Knowledge Ingestion -----------------
@app.post("/api/ingest/event")
def ingest_event(req: IngestEventRequest):
    """
    Real-time dynamic ingestion of Slack messages, GitHub PRs/Commits, or Jira Tickets,
    keeping the company brain fresh and continuously updated!
    """
    g_name = f"tenant_{req.tenant_id}_brain"
    g = engine.get_or_create_graph(g_name)
    event_type = req.event_type.lower()
    data = req.data
    timestamp = time.time()

    if event_type == "commit":
        cid = data.get("id") or f"commit_{data.get('hash', 'new')}"
        g.add_node(cid, "Commit", {
            "id": cid,
            "hash": data.get("hash", cid[:7]),
            "message": data.get("message", "New commit"),
            "author_id": data.get("author_id", "sarah_chen"),
            "timestamp": timestamp
        })
        if data.get("service_id"):
            g.add_edge(data["service_id"], cid, "HAS_COMMIT", {})
        return {"status": "ingested", "type": "Commit", "id": cid}

    elif event_type == "slack":
        mid = data.get("id") or f"msg_{int(timestamp)}"
        g.add_node(mid, "SlackMessage", {
            "id": mid,
            "channel": data.get("channel", "#general"),
            "sender": data.get("sender", "alex_rivera"),
            "text": data.get("text", ""),
            "timestamp": timestamp
        })
        return {"status": "ingested", "type": "SlackMessage", "id": mid}

    elif event_type == "ticket":
        tid = data.get("id") or f"ticket_{int(timestamp)}"
        g.add_node(tid, "Ticket", {
            "id": tid,
            "title": data.get("title", ""),
            "status": data.get("status", "OPEN"),
            "priority": data.get("priority", "HIGH"),
            "assignee_id": data.get("assignee_id", "sarah_chen")
        })
        return {"status": "ingested", "type": "Ticket", "id": tid}

    return {"status": "unknown_event_type"}

# ----------------- Serve Frontend Static Files -----------------
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": f"{settings.PROJECT_NAME} Backend API is Running. Frontend not found."}
