"""
Comprehensive test suite verifying all 3 tracks for FalkorNexus.
"""
import pytest
from backend.graph_engine import engine
from backend.seeds.enterprise_data import seed_enterprise_graph
from backend.mcp_server import FalkorMCPServer
from backend.memory.episodic import EpisodicMemoryManager
from backend.memory.semantic import SemanticMemoryManager
from backend.memory.procedural import ProceduralMemoryManager
from backend.agents.orchestrator import AgentOrchestrator

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
    # 1. Shortest Path from Incident to Engineer
    path_res = mcp.call_tool("falkordb_shortest_path", {"source_id": "inc_804", "target_id": "sarah_chen", "tenant_id": "test_corp"})
    assert path_res["status"] == "success"
    assert path_res["data"]["found"] is True
    print(f"[PASS] Shortest Path verified: {path_res['explainability']}")

    # 2. Blast Radius
    blast_res = mcp.call_tool("falkordb_blast_radius", {"node_id": "service_auth", "max_depth": 3, "tenant_id": "test_corp"})
    assert blast_res["status"] == "success"
    assert blast_res["data"]["impact_count"] > 0
    print(f"[PASS] Blast Radius verified: {blast_res['explainability']}")

    # 3. PageRank
    pr_res = mcp.call_tool("falkordb_pagerank", {"top_k": 3, "tenant_id": "test_corp"})
    assert pr_res["status"] == "success"
    assert len(pr_res["data"]) == 3
    print(f"[PASS] PageRank verified: Top systemic hub = {pr_res['data'][0]['name']}")

    # 4. Centrality (Bottlenecks)
    cent_res = mcp.call_tool("falkordb_centrality", {"tenant_id": "test_corp"})
    assert cent_res["status"] == "success"
    print(f"[PASS] Centrality verified: Found {len(cent_res['data']['betweenness_bottlenecks'])} bottleneck candidates.")

    print("\n--- TRACK 02: AGENT MEMORY & COORDINATION ---")
    # 1. Run full 4-agent coordination pipeline
    query = "Critical alert: PaymentGateway error rate spike and 500 cascade! Triage and mitigate."
    session_id = "test_sess_42"
    result = orchestrator.process_query(query, session_id=session_id, tenant_id="test_corp")
    assert len(result["agent_steps"]) == 4, "Should execute exactly 4 agents in coordination."
    assert result["agent_steps"][0]["agent"] == "TriageAgent"
    assert result["agent_steps"][1]["agent"] == "InvestigatorAgent"
    assert result["agent_steps"][2]["agent"] == "ActionAgent"
    assert result["agent_steps"][3]["agent"] == "MemoryAgent"
    print(f"[PASS] 4-Agent Pipeline executed in {result['duration_ms']}ms with handoff state tracking.")

    # 2. Check Episodic Memory Persistence
    recalled_episodes = episodic_mgr.recall_recent_episodes(session_id, limit=5, tenant_id="test_corp")
    assert len(recalled_episodes) >= 1
    assert recalled_episodes[0]["intent"] == "OUTAGE_TRIAGE"
    print(f"[PASS] Episodic Memory verified: Successfully recalled {len(recalled_episodes)} persistent episodes.")

    # 3. Check Procedural Memory Playbook Chain
    wf = procedural_mgr.get_playbook_workflow("plb_sev1_triage", tenant_id="test_corp")
    assert wf is not None
    assert len(wf["steps"]) == 4
    print(f"[PASS] Procedural Memory verified: Loaded playbook '{wf['playbook']['name']}' with {len(wf['steps'])} chained steps.")

    print("\n--- TRACK 03: COMPANY BRAIN & DECISION PROVENANCE ---")
    # 1. Tracing Decision Lineage
    lineage_res = mcp.call_tool("falkordb_decision_lineage", {"identifier": "RFC-104", "tenant_id": "test_corp"})
    assert lineage_res["status"] == "success"
    assert "FalkorDB" in lineage_res["entity"]["properties"]["title"]
    print(f"[PASS] Decision Lineage verified: {lineage_res['explainability']}")

    # 2. Expert Finder
    expert_res = mcp.call_tool("falkordb_find_expert", {"service_id": "service_auth", "tenant_id": "test_corp"})
    assert expert_res["status"] == "success"
    assert len(expert_res["experts"]) >= 1
    print(f"[PASS] Expert Finder verified: Found {len(expert_res['experts'])} SMEs for AuthService.")

    print("\n==========================================")
    print("ALL 3 HACKATHON TRACKS VERIFIED 100% PASS!")
    print("==========================================")

if __name__ == "__main__":
    test_full_system_across_all_tracks()
