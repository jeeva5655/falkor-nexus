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

    print("\n--- OUT-OF-THE-BOX CLINCHERS: RISK GATE, TENANT ISOLATION & GRAPHRAG ---")
    # 1. Pre-Merge CI/CD Risk Gate Test (Track 01 Counterfactual Prevention)
    gate_res = mcp.call_tool("falkordb_premerge_risk_gate", {"service_id": "service_auth", "tenant_id": "test_corp"})
    assert gate_res["status"] == "success"
    assert gate_res["verdict"] == "BLOCKED_MISSING_CIRCUIT_BREAKER"
    assert gate_res["risk_score"] >= 70
    assert len(gate_res["unguarded_dependencies"]) > 0
    print(f"[PASS] Pre-Merge Risk Gate verified: Blocked risky PR with risk_score={gate_res['risk_score']}.")

    # Auto-heal gate via endpoint
    heal_resp = client.post("/api/graph/premerge_gate", json={"service_id": "service_auth", "tenant_id": "test_corp", "auto_heal": True})
    assert heal_resp.status_code == 200
    assert heal_resp.json()["verdict"] == "APPROVED_PROTECTED"
    print("[PASS] Pre-Merge Auto-Heal verified: Circuit breaker injected live into FalkorDB.")

    # 2. Key-Level Multigraph Tenant Isolation Test (Track 02 Clincher)
    cyber_graph = engine.get_or_create_graph("tenant_aegis_cyber_brain")
    from backend.seeds.enterprise_data import seed_cyber_defense_graph
    seed_cyber_defense_graph(cyber_graph)
    assert "service_waf_gateway" in cyber_graph.nodes
    assert "cve_2026_9901" in cyber_graph.nodes
    nexus_graph = engine.get_or_create_graph("tenant_nexus_corp_brain")
    assert "cve_2026_9901" not in nexus_graph.nodes, "Zero-leakage: aegis_cyber CVE must NOT exist in nexus_corp!"
    print("[PASS] Multigraph Tenant Isolation verified: Zero cross-tenant leakage between nexus_corp and aegis_cyber.")

    # 3. Live GraphRAG Unstructured Text -> Graph Extractor Test (Track 03 Clincher)
    rag_extract_resp = client.post("/api/ingest/graphrag_extract", json={
        "raw_text": "Postmortem SEV-1: INC-904 outage in service_auth caused by PR #612 authored by Sarah Chen affecting service_payment_gw.",
        "tenant_id": "test_corp"
    })
    assert rag_extract_resp.status_code == 200
    rag_extract_data = rag_extract_resp.json()
    assert rag_extract_data["status"] == "success"
    assert rag_extract_data["entities_extracted_count"] >= 3
    assert rag_extract_data["relationships_extracted_count"] >= 2
    test_corp_g = engine.get_or_create_graph("tenant_test_corp_brain")
    assert "inc_904" in test_corp_g.nodes
    assert "pr_612" in test_corp_g.nodes
    print(f"[PASS] GraphRAG Extractor verified: {rag_extract_data['entities_extracted_count']} nodes & {rag_extract_data['relationships_extracted_count']} edges extracted to FalkorDB.")

    print("\n--- GRAND FINALE ADDITIONS: COMMUNITY DETECTION, CONCURRENCY & BUS-FACTOR ---")
    # 4. Community Detection MCP Tool #10 (Track 01 Spec)
    comm_res = mcp.call_tool("falkordb_community_detection", {"tenant_id": "test_corp"})
    assert comm_res["status"] == "success"
    assert comm_res["total_communities"] > 0
    print(f"[PASS] Community Detection verified: Partitioned graph into {comm_res['total_communities']} modularity clusters.")

    # 5. Concurrency Stress Test Benchmark (Track 02 Spec)
    bench_resp = client.post("/api/graph/concurrency_benchmark", json={"tenant_id": "test_corp", "operations": 20})
    assert bench_resp.status_code == 200
    bench_data = bench_resp.json()
    assert bench_data["successful_operations"] == 20
    assert bench_data["ops_per_sec"] > 0
    assert bench_data["write_conflicts"] == 0
    print(f"[PASS] Concurrency Benchmark verified: {bench_data['ops_per_sec']} ops/sec, avg latency {bench_data['avg_latency_ms']}ms across isolated multigraphs.")

    # 6. Bus-Factor & Knowledge Silo Simulator (Track 03 Spec)
    bus_resp = client.get("/api/graph/bus_factor?tenant_id=test_corp&unavailable_person_id=sarah_chen")
    assert bus_resp.status_code == 200
    bus_data = bus_resp.json()
    assert bus_data["status"] == "success"
    assert len(bus_data["services"]) > 0
    assert bus_data["recommended_failover_responder"] is not None
    assert len(bus_data["failover_path"]) > 0
    print(f"[PASS] Bus-Factor Simulator verified: Sarah Chen offline -> Rerouted to {bus_data['recommended_failover_responder']['name']} ({bus_data['recommended_failover_responder']['role']}) via {bus_data['failover_path']}.")

    print("\n========================================================")
    print("ALL 3 TRACKS + CLINCHERS + GRAND FINALE 100% VERIFIED!")
    print("========================================================")

if __name__ == "__main__":
    test_full_system_across_all_tracks()
