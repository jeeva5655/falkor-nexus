"""
FalkorNexus Dynamic LLM Agent Reasoner.
Enables true autonomous tool selection over FalkorDB Model Context Protocol (MCP) tools.
Supports OpenAI, Gemini, Ollama, and local models.
Provides both synchronous (for agent pipeline) and async execution methods.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
import httpx

from backend.config import settings

logger = logging.getLogger("llm_reasoner")

class DynamicLLMReasoner:
    def __init__(self, mcp_server):
        self.mcp = mcp_server
        self.tools = self._format_tools_for_llm()

    def _format_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Formats FalkorDB MCP tools into standard tool-calling schemas.
        """
        mcp_tools = self.mcp.list_tools()
        formatted = []
        for t in mcp_tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["inputSchema"]
                }
            })
        return formatted

    def get_graph_schema_prompt(self, tenant_id: str) -> str:
        """
        Extracts active schema directly from FalkorDB graph to anchor LLM reasoning.
        """
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.mcp.engine.get_or_create_graph(graph_name)
        labels = list(graph.labels.keys())
        edge_types = list(set(e["type"] for e in graph.edges))

        return f"""You are the FalkorNexus Autonomous Operations Commander powered by FalkorDB.
You reason over a connected enterprise graph to investigate outages, discover ownership, and trace decisions.

Active FalkorDB Graph Schema:
- Node Labels: {', '.join(labels)}
- Relationship Types: {', '.join(edge_types)}
- Native GraphBLAS Algorithms available: PageRank, Betweenness Centrality, ShortestPath, Blast Radius.

Instructions:
1. When presented with an incident or question, choose the most appropriate MCP graph tools dynamically.
2. For service outages, compute blast radius and shortest path to culprit code changes/authors.
3. For architecture questions, trace decision provenance back to RFCs and historical incidents.
4. Always provide an explainable decision trace with citations referencing exact Node IDs.
"""

    def get_api_config(self) -> Optional[Dict[str, str]]:
        if settings.OPENAI_API_KEY:
            return {
                "url": f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
                "key": settings.OPENAI_API_KEY,
                "model": settings.OPENAI_MODEL
            }
        if settings.GEMINI_API_KEY:
            return {
                "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                "key": settings.GEMINI_API_KEY,
                "model": "gemini-2.5-flash"
            }
        # Check if Ollama is accessible
        if settings.OLLAMA_HOST:
            return {
                "url": f"{settings.OLLAMA_HOST.rstrip('/')}/v1/chat/completions",
                "key": "ollama",
                "model": settings.OLLAMA_MODEL
            }
        return None

    def is_llm_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)

    def run_sync_if_configured(self, user_query: str, tenant_id: str = "nexus_corp") -> Optional[Dict[str, Any]]:
        """
        Synchronous autonomous tool-calling loop for the InvestigatorAgent.
        Returns None if no LLM API is configured or available, triggering native planner fallback.
        """
        cfg = self.get_api_config()
        if not cfg or not (settings.OPENAI_API_KEY or settings.GEMINI_API_KEY):
            return None

        thoughts = [f"Dispatched prompt to LLM ({cfg['model']}) with {len(self.tools)} FalkorDB MCP tools."]
        tools_called = []
        messages = [
            {"role": "system", "content": self.get_graph_schema_prompt(tenant_id)},
            {"role": "user", "content": user_query}
        ]
        headers = {
            "Authorization": f"Bearer {cfg['key']}",
            "Content-Type": "application/json"
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                for turn in range(4):
                    resp = client.post(cfg["url"], headers=headers, json={
                        "model": cfg["model"],
                        "messages": messages,
                        "tools": self.tools,
                        "tool_choice": "auto",
                        "temperature": 0.1
                    })
                    if resp.status_code != 200:
                        logger.warning(f"LLM API returned status {resp.status_code}: {resp.text[:120]}")
                        return None

                    choice = resp.json()["choices"][0]
                    msg = choice["message"]
                    messages.append(msg)

                    if msg.get("tool_calls"):
                        for tc in msg["tool_calls"]:
                            fn_name = tc["function"]["name"]
                            fn_args = json.loads(tc["function"].get("arguments", "{}"))
                            fn_args["tenant_id"] = tenant_id
                            thoughts.append(f"🤖 LLM Dynamic MCP Tool Selection: {fn_name}({json.dumps(fn_args, separators=(',', ':'))})")
                            res = self.mcp.call_tool(fn_name, fn_args)
                            tools_called.append(res)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc["id"],
                                "name": fn_name,
                                "content": json.dumps(res.get("data", res), default=str)
                            })
                    else:
                        return {
                            "answer": msg.get("content", ""),
                            "thoughts": thoughts,
                            "tools_called": tools_called,
                            "llm_powered": True
                        }
        except Exception as e:
            logger.warning(f"LLM sync reasoner fallback: {e}")

        return None
