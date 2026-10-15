import time
import uuid
from typing import Dict, List, Any, Optional

class EpisodicMemoryManager:
    """
    Manages episodic memory for multi-agent systems and persistent user sessions.
    Stores session context, conversational turns, intent classifications,
    actions taken, and outcomes directly in the FalkorDB graph.
    """
    def __init__(self, graph_engine):
        self.engine = graph_engine

    def create_or_get_session(self, session_id: str, user_id: str, tenant_id: str = "nexus_corp") -> Dict[str, Any]:
        graph_name = f"tenant_{tenant_id}_memory"
        graph = self.engine.get_or_create_graph(graph_name)

        existing = graph.get_node(session_id)
        if existing:
            return existing

        session_node = {
            "id": session_id,
            "user_id": user_id,
            "created_at": time.time(),
            "last_active": time.time(),
            "episodes_count": 0,
            "state": "ACTIVE"
        }
        graph.add_node(session_id, "AgentSession", session_node)
        return session_node

    def record_episode(
        self,
        session_id: str,
        user_query: str,
        intent: str,
        agent_chain: List[str],
        reasoning_trace: List[Dict[str, Any]],
        outcome: Dict[str, Any],
        tenant_id: str = "nexus_corp"
    ) -> Dict[str, Any]:
        """
        Stores an episodic memory unit linked to the current session,
        retaining what happened, which tools were used, and what was decided.
        """
        graph_name = f"tenant_{tenant_id}_memory"
        graph = self.engine.get_or_create_graph(graph_name)

        episode_id = f"ep_{uuid.uuid4().hex[:8]}"
        episode_data = {
            "id": episode_id,
            "session_id": session_id,
            "timestamp": time.time(),
            "user_query": user_query,
            "intent": intent,
            "agents_involved": agent_chain,
            "outcome_summary": outcome.get("summary", ""),
            "confidence": outcome.get("confidence", 0.95),
            "actions_executed": outcome.get("actions", [])
        }
        graph.add_node(episode_id, "MemoryEpisode", episode_data)
        graph.add_edge(session_id, episode_id, "CONTAINS_EPISODE", {"created_at": time.time()})

        # Link relevant entities mentioned in the episode
        for entity_id in outcome.get("related_entities", []):
            graph.add_edge(episode_id, entity_id, "REFERENCED", {})

        return episode_data

    def recall_recent_episodes(self, session_id: str, limit: int = 5, tenant_id: str = "nexus_corp") -> List[Dict[str, Any]]:
        """
        Recalls historical episodes from earlier in the session or past sessions
        to restore complete agent context.
        """
        graph_name = f"tenant_{tenant_id}_memory"
        graph = self.engine.get_or_create_graph(graph_name)

        episodes = []
        for e in graph.edges:
            if e["source"] == session_id and e["type"] == "CONTAINS_EPISODE":
                node = graph.get_node(e["target"])
                if node:
                    episodes.append(node["properties"])

        episodes.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return episodes[:limit]
