import time
import uuid
from typing import Dict, Any, List, Generator
from backend.agents.triage_agent import TriageAgent
from backend.agents.investigator_agent import InvestigatorAgent
from backend.agents.action_agent import ActionAgent
from backend.agents.memory_agent import MemoryAgent

class AgentOrchestrator:
    """
    Coordinates multi-agent workflows, managing shared state machine,
    persisting agent handoffs into the graph, and providing event streams for the UI.
    """
    def __init__(self, mcp_server, memory_managers, graph_engine):
        self.mcp = mcp_server
        self.memory_managers = memory_managers
        self.engine = graph_engine

        # Initialize agents
        self.triage = TriageAgent(mcp_server, memory_managers)
        self.investigator = InvestigatorAgent(mcp_server, memory_managers)
        self.action = ActionAgent(mcp_server, memory_managers)
        self.memory = MemoryAgent(mcp_server, memory_managers)

    def _record_state_handoff(self, session_id: str, from_agent: str, to_agent: str, payload: Dict[str, Any], tenant_id: str):
        graph_name = f"tenant_{tenant_id}_memory"
        graph = self.engine.get_or_create_graph(graph_name)

        state_id = f"state_{uuid.uuid4().hex[:6]}"
        state_data = {
            "id": state_id,
            "session_id": session_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "timestamp": time.time(),
            "status": "HANDED_OFF"
        }
        graph.add_node(state_id, "AgentState", state_data)
        graph.add_edge(session_id, state_id, "HAS_STATE_TRANSITION", {})

    def process_query(self, user_query: str, session_id: str, tenant_id: str = "nexus_corp") -> Dict[str, Any]:
        """
        Synchronous end-to-end execution through the 4-agent coordination pipeline.
        """
        start_time = time.time()
        agent_steps = []

        # Ensure session exists in episodic memory
        self.memory_managers["episodic"].create_or_get_session(session_id, user_id="operator_user", tenant_id=tenant_id)

        # 1. Triage Agent
        triage_out = self.triage.run(user_query, session_id)
        agent_steps.append(triage_out)
        self._record_state_handoff(session_id, "User", "TriageAgent", triage_out["payload"], tenant_id)

        # 2. Investigator Agent
        self._record_state_handoff(session_id, "TriageAgent", "InvestigatorAgent", triage_out["payload"], tenant_id)
        invest_out = self.investigator.run(triage_out, tenant_id=tenant_id)
        agent_steps.append(invest_out)

        # 3. Action Agent
        self._record_state_handoff(session_id, "InvestigatorAgent", "ActionAgent", invest_out["payload"], tenant_id)
        action_out = self.action.run(invest_out, tenant_id=tenant_id)
        agent_steps.append(action_out)

        # 4. Memory Agent
        self._record_state_handoff(session_id, "ActionAgent", "MemoryAgent", action_out["payload"], tenant_id)
        mem_out = self.memory.run(action_out, tenant_id=tenant_id)
        agent_steps.append(mem_out)

        total_duration = round((time.time() - start_time) * 1000, 2)

        return {
            "session_id": session_id,
            "tenant_id": tenant_id,
            "duration_ms": total_duration,
            "agent_steps": agent_steps,
            "result": mem_out["response"]
        }
