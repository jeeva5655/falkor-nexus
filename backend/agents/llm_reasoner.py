"""
FalkorNexus Dynamic LLM Agent Reasoner.
Enables true autonomous tool selection over FalkorDB Model Context Protocol (MCP) tools.
Works with OpenAI, Ollama, Gemini, or any OpenAI-compatible API.
Features seamless zero-key fallback to native graph reasoning planner.
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

    def is_llm_configured(self) -> bool:
        return bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)

    async def execute_reasoning_loop(
        self,
        user_query: str,
        session_id: str,
        tenant_id: str = "nexus_corp",
        max_turns: int = 5
    ) -> Dict[str, Any]:
        """
        Autonomous ReAct Tool-Calling loop over FalkorDB MCP tools.
        """
        thoughts = []
        tools_executed = []
        messages = [
            {"role": "system", "content": self.get_graph_schema_prompt(tenant_id)},
            {"role": "user", "content": user_query}
        ]

        if not self.is_llm_configured():
            thoughts.append("No external LLM API key detected. Operating in Autonomous Native Graph Planner mode.")
            return None  # Signal to use native planner

        thoughts.append(f"Dispatched prompt to LLM ({settings.OPENAI_MODEL}) with {len(self.tools)} FalkorDB MCP tools.")

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            for turn in range(max_turns):
                payload = {
                    "model": settings.OPENAI_MODEL,
                    "messages": messages,
                    "tools": self.tools,
                    "tool_choice": "auto",
                    "temperature": 0.1
                }

                try:
                    resp = await client.post(f"{settings.OPENAI_BASE_URL}/chat/completions", headers=headers, json=payload)
                    if resp.status_code != 200:
                        thoughts.append(f"LLM API returned {resp.status_code}: {resp.text[:100]}. Falling back to native graph planner.")
                        return None

                    data = resp.json()
                    choice = data["choices"][0]
                    message = choice["message"]
                    messages.append(message)

                    # Check if model wants to call tools
                    if message.get("tool_calls"):
                        for tool_call in message["tool_calls"]:
                            fn = tool_call["function"]
                            fn_name = fn["name"]
                            fn_args = json.loads(fn.get("arguments", "{}"))
                            fn_args["tenant_id"] = tenant_id

                            thoughts.append(f"🤖 LLM dynamic tool selection: {fn_name}({json.dumps(fn_args, separators=(',', ':'))})")
                            tool_result = self.mcp.call_tool(fn_name, fn_args)
                            tools_executed.append(fn_name)

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call["id"],
                                "name": fn_name,
                                "content": json.dumps(tool_result.get("data", tool_result))
                            })
                    else:
                        # LLM generated final answer
                        final_content = message.get("content", "")
                        thoughts.append("LLM completed multi-hop reasoning over FalkorDB context.")
                        return {
                            "answer": final_content,
                            "thoughts": thoughts,
                            "tools_executed": tools_executed,
                            "turns": turn + 1,
                            "llm_powered": True
                        }

                except Exception as e:
                    logger.warning(f"Error during LLM reasoning turn {turn}: {e}")
                    thoughts.append(f"LLM connection error: {e}. Transitioning to native graph planner.")
                    return None

        return None
