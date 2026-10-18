# 🏆 FalkorNexus — Official Hackathon Submission Dossier

**Team / Creator:** Jeeva N ([@jeeva5655](https://github.com/jeeva5655))  
**Repository:** [https://github.com/jeeva5655/falkor-nexus](https://github.com/jeeva5655/falkor-nexus)  
**Tracks Entered:**
- ✅ **Track 01: Graph Agents (Connected Data & Graph Tools)**
- ✅ **Track 02: Multi-Agent Systems (Memory, State & Coordination)**
- ✅ **Track 03: Company Brain (Context, Lineage & Operational Graph)**

---

## 📌 Submission Form Copy-Paste Fields

### 1. Project Title
```text
FalkorNexus - Autonomous Multi-Agent Enterprise Operations Command on FalkorDB
```

### 2. Tagline / Elevator Pitch (Under 200 chars)
```text
Autonomous multi-agent operations command on FalkorDB GraphBLAS: Two-Run Self-Healing Learning Loop, proactive CI/CD risk gate, multigraph tenant isolation, and live GraphRAG extraction.
```

### 3. Which Tracks Are You Submitting To?
Select all three:
- [x] Track 01 — Connected Data & Graph Tools
- [x] Track 02 — Multi-Agent Systems & Memory
- [x] Track 03 — Company Brain & Organizational Knowledge

### 4. Links
* **GitHub Repository URL:** `https://github.com/jeeva5655/falkor-nexus`
* **Demo Video File:** Located locally at `falkornexus_demo_walkthrough.mp4` (1m 37s, 1080p Full HD with Audio Narration)
  * *Upload this MP4 to YouTube (as Unlisted) or Loom / Google Drive and paste the public link here.*
* **Blog Post URL (AirPods 5 Side Prize):**
  * `https://dev.to/jeeva5655/how-we-built-a-self-healing-multi-agent-company-brain-on-falkordb-and-why-vector-rag-failed-us-4ana`

---

## 📝 Project Overview & Deep Dive (Ready for Description Box)

### What Inspired FalkorNexus?
Modern AI agents deployed over enterprise infrastructure fail because vector embeddings cannot navigate relational topology. When microservice `PaymentGateway` throws HTTP 500 errors, vector RAG searches for keywords in payment code and hallucinates client retry fixes—unaware that the true culprit is an upstream dependency in `AuthService` introduced by a PR commit merged 90 minutes prior.

FalkorNexus replaces chunk-based vector search with deterministic **FalkorDB GraphBLAS linear algebra**.

### How FalkorDB Powers All 3 Tracks

#### Track 01: Native GraphBLAS Algorithms as MCP Agent Tools
* 10 registered Model Context Protocol (MCP) tools:
  1. `falkordb_cypher_query`: Arbitrary Cypher execution.
  2. `falkordb_shortest_path`: Native `shortestPath()` multi-hop causal exploration.
  3. `falkordb_blast_radius`: Multi-depth upstream/downstream impact analysis.
  4. `falkordb_pagerank`: Native GraphBLAS `CALL algo.pageRank('Service', 'DEPENDS_ON')`.
  5. `falkordb_centrality`: Native Betweenness Centrality single-point-of-failure detection.
  6. `falkordb_find_expert`: Subject-matter expert discovery by graph topology.
  7. `falkordb_decision_lineage`: Architecture decision provenance and RFC tracing.
  8. `falkordb_execute_action`: Automated remediation actions against services.
  9. `falkordb_premerge_risk_gate`: Proactive CI/CD pre-merge blast radius gate & circuit-breaker audit.
  10. `falkordb_community_detection`: Native modularity clustering with visual canvas halos.

#### Track 02: The "Two-Run Learning Loop" & 850+ Ops/Sec Concurrency
* **Two-Run Learning Loop**:
  * **Run 1 (Cold Start)**: 4 coordinated agents (`TriageAgent` $\rightarrow$ `InvestigatorAgent` $\rightarrow$ `ActionAgent` $\rightarrow$ `MemoryAgent`) traverse 5 topological hops in 14.2s to diagnose `AuthService` and commit `c3b8f19`.
  * **Graph Mutation**: `MemoryAgent` writes a learned shortcut edge: `(:Service {id: 'service_payment_gw'})-[:HISTORICAL_CASCADE {confidence: 0.94}]->(:Service {id: 'service_auth'})`.
  * **Run 2 (Memory-Accelerated)**: Resolves the follow-up alert in **1 hop and 1.8s (87% Speedup)**!
* **High-Concurrency Benchmark**: 50 concurrent operations across multigraph namespaces delivering **868 ops/sec** at **1.15ms** latency with 0 write conflicts.

#### Track 03: Company Brain, Bus-Factor Resilience & GraphRAG Extractor
* **Multigraph Tenant Isolation**: Single FalkorDB instance runs isolated multigraphs via `db.select_graph()` (`nexus_corp` Fintech $\leftrightarrow$ `aegis_cyber` SecOps) with zero cross-tenant data leakage.
* **Bus-Factor Simulator**: Detects services with `Bus Factor = 1` and simulates automated failover routing when primary architects like Sarah Chen are unreachable.
* **Live GraphRAG Extractor**: Parses unstructured postmortems into typed nodes and directed relationships committed live to FalkorDB.
* **One-Click Audit Export**: Autonomous download of incident postmortems in Markdown with Cypher provenance.

---

## 🛠️ How to Test & Verify in 30 Seconds

```bash
# Clone
git clone https://github.com/jeeva5655/falkor-nexus.git
cd falkor-nexus

# Run Full Automated Test Suite
python -m backend.tests.test_system

# Launch Web Application
docker-compose up --build
# Or: python run.py
# Open: http://127.0.0.1:8000
```
