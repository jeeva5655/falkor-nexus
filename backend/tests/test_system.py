"""
Comprehensive End-to-End Competition Verification Suite for FalkorNexus.
Tests all 3 Hackathon Tracks + Two-Run Memory Loop + Chaos Webhook + FastAPI Endpoints.
"""
from fastapi.testclient import TestClient
from backend.app import app
from backend.graph_engine import engine
from backend.seeds.enterprise_data import seed_enterprise_graph
from backend.mcp_server import FalkorMCPServer
from backend.memory.episodic import EpisodicMemoryManager
from backend.memory.semantic import SemanticMemoryManager
from backend.memory.procedural import ProceduralMemoryManager
from backend.agents.orchestrator import AgentOrchestrator

client = TestClient(app)

def test_full_system_across_all_tracks():
    # Setup test graph
    test_graph_name = "tenant_test_corp_brain"
    graph = engine.get_or_create_graph(test_graph_name)
    seed_res = seed_enterprise_graph(graph)
    assert seed_res["total_nodes"] > 25, "Graph should have at least 25 nodes seeded."
    assert seed_res["total_edges"] > 35, "Graph should have at least 35 edges seeded."

    # Managers
    episodic_mgr = EpisodicMemoryManager(engine)
    semantic_mgr = SemanticMemoryManager(engine)
    procedural_mgr = ProceduralMemoryManager(engine)
    memory_managers = {
        "episodic": episodic_mgr,
        "semantic": semantic_mgr,
        "procedural": procedural_mgr
    }
    mcp = FalkorMCPServer(engine)
    orchestrator = AgentOrchestrator(mcp, memory_managers, engine)

    print("\n--- TRACK 01: GRAPH TOOLS & ALGORITHMS (MCP) ---")
    path_res = mcp.call_tool("falkordb_shortest_path", {"source_id": "inc_804", "target_id": "sarah_chen", "tenant_id": "test_corp"})
    assert path_res["status"] == "success" and path_res["data"]["found"] is True
    print(f"[PASS] Shortest Path verified: {path_res['explainability']}")

    blast_res = mcp.call_tool("falkordb_blast_radius", {"node_id": "service_auth", "max_depth": 3, "tenant_id": "test_corp"})
    assert blast_res["status"] == "success" and blast_res["data"]["impact_count"] > 0
    print(f"[PASS] Blast Radius verified: {blast_res['explainability']}")

    pr_res = mcp.call_tool("falkordb_pagerank", {"top_k": 3, "tenant_id": "test_corp"})
    assert pr_res["status"] == "success" and len(pr_res["data"]) == 3
    print(f"[PASS] PageRank verified: Top systemic hub = {pr_res['data'][0]['name']}")

    cent_res = mcp.call_tool("falkordb_centrality", {"tenant_id": "test_corp"})
    assert cent_res["status"] == "success"
    print(f"[PASS] Centrality verified: Found {len(cent_res['data']['betweenness_bottlenecks'])} bottleneck candidates.")

    print("\n--- TRACK 02: TWO-RUN LEARNING LOOP & 4-AGENT COORDINATION ---")
    # Reset learning first to guarantee Cold Start
    client.post("/api/agents/reset_learning?tenant_id=test_corp")

    query = "Critical alert: PaymentGateway error rate spike and 500 cascade! Triage and mitigate."
    session_id = "test_sess_42"

    # RUN 1: Cold Start (5 Hops)
    run1 = orchestrator.process_query(query, session_id=session_id, tenant_id="test_corp")
    assert len(run1["agent_steps"]) == 4
    assert run1["result"]["learning_metrics"]["run_type"] == "Cold Start"
    assert run1["result"]["learning_metrics"]["hops_count"] == 5
    assert run1["result"]["learning_metrics"]["memory_shortcut_used"] is False
    print(f"[PASS] Run 1 (Cold Start) executed in {run1['duration_ms']}ms across 5 hops and mutated graph.")

    # RUN 2: Memory-Accelerated (1 Hop via :HISTORICAL_CASCADE)
    run2 = orchestrator.process_query(query, session_id=session_id, tenant_id="test_corp")
    assert run2["result"]["learning_metrics"]["run_type"] == "Memory-Accelerated"
    assert run2["result"]["learning_metrics"]["hops_count"] == 1
    assert run2["result"]["learning_metrics"]["memory_shortcut_used"] is True
    print(f"[PASS] Run 2 (Memory-Accelerated) verified: Resolved in 1 hop via :HISTORICAL_CASCADE shortcut edge!")

    # Episodic & Procedural Memory Checks
    recalled_episodes = episodic_mgr.recall_recent_episodes(session_id, limit=5, tenant_id="test_corp")
    assert len(recalled_episodes) >= 2
    wf = procedural_mgr.get_playbook_workflow("plb_sev1_triage", tenant_id="test_corp")
    assert wf is not None and len(wf["steps"]) == 4
    print(f"[PASS] Tri-Memory verified: {len(recalled_episodes)} episodes + {len(wf['steps'])}-step procedural SOP.")

    print("\n--- TRACK 03: COMPANY BRAIN, LIVE CHAOS WEBHOOK & RAG BENCHMARK ---")
    lineage_res = mcp.call_tool("falkordb_decision_lineage", {"identifier": "RFC-104", "tenant_id": "test_corp"})
    assert lineage_res["status"] == "success"
    print(f"[PASS] Decision Lineage verified: {lineage_res['explainability']}")

    # Live Chaos Webhook Ingestion Test
    chaos_resp = client.post("/api/ingest/chaos?tenant_id=test_corp")
    assert chaos_resp.status_code == 200
    assert chaos_resp.json()["status"] == "chaos_injected"

    expert_res = mcp.call_tool("falkordb_find_expert", {"service_id": "service_ledger", "tenant_id": "test_corp"})
    expert_ids = [e["person"]["id"] for e in expert_res["experts"]]
    assert "alex_rivera" in expert_ids, "Chaos webhook PR #510 author Alex Rivera must be discovered as expert on LedgerDB!"
    print(f"[PASS] Live Chaos Webhook verified: Alex Rivera (PR #510) dynamically linked to LedgerDB.")

    # Vector RAG vs FalkorDB Graph Context Endpoint Test
    rag_resp = client.get("/api/rag/compare")
    assert rag_resp.status_code == 200
    assert rag_resp.json()["falkordb_graph_context"]["root_cause_identified"] is True
    print("[PASS] Vector RAG vs. FalkorDB Graph Context comparison endpoint verified.")

    print("\n========================================================")
    print("ALL 3 TRACKS + LEARNING LOOP + CHAOS WEBHOOK 100% PASS!")
    print("========================================================")

if __name__ == "__main__":
    test_full_system_across_all_tracks()
