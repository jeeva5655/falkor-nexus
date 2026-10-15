"""
FalkorNexus Unified Launcher
Starts the FastAPI application and serves the web dashboard and REST/MCP endpoints.
"""
import uvicorn
from backend.config import settings

def main():
    print("=" * 65)
    print("  FALKORNEXUS: AUTONOMOUS ENTERPRISE BRAIN & OPERATIONS COMMAND")
    print("  Powered by FalkorDB Graph Context")
    print("=" * 65)
    print(f"  Web Dashboard:  http://{settings.HOST}:{settings.PORT}")
    print(f"  API Docs:       http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  MCP Server:     http://{settings.HOST}:{settings.PORT}/api/mcp/tools")
    print(f"  FalkorDB Mode:  Dual-Engine (Live + High-Speed Fallback)")
    print("=" * 65)
    print("  [Track 01] Multi-hop Reasoning, Graph Algorithms (PageRank/SPOFs), MCP")
    print("  [Track 02] Tri-Memory (Episodic, Semantic, Procedural) & 4-Agent Handoffs")
    print("  [Track 03] Company Brain (Who Knows What, Decision Provenance, Ingest)")
    print("=" * 65)

    uvicorn.run(
        "backend.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()
