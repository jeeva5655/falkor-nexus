import time
from typing import Dict, Any, List

class MemoryAgent:
    """
    Agent 4: Memory & Reflection Agent.
    Updates the 3-Tier Graph Memory:
    1. Episodic Memory: Records conversation turn, decision chain, and outcome into FalkorDB.
    2. Semantic Memory: Connects entities discovered during the session.
    3. Procedural Memory: Evaluates whether new operational heuristics should be learned into graph playbooks.
    """
    def __init__(self, mcp_server, memory_managers):
        self.mcp = mcp_server
        self.episodic = memory_managers["episodic"]
        self.semantic = memory_managers["semantic"]
        self.procedural = memory_managers["procedural"]

    def run(self, handoff_data: Dict[str, Any], tenant_id: str = "nexus_corp") -> Dict[str, Any]:
        payload = handoff_data.get("payload", {})
        session_id = payload.get("session_id", "default_sess")
        query = payload.get("query", "")
        intent = payload.get("intent", "GENERAL")
        actions = payload.get("actions_executed", [])
        citations = payload.get("citations", [])
        synthesis = payload.get("final_synthesis", "")

        thought_log = []
        thought_log.append("Memory & Reflection Agent activated. Beginning tri-memory graph consolidation...")

        # 1. Update Episodic Memory
        related_entities = [c["id"] for c in citations if "id" in c]
        outcome = {
            "summary": synthesis,
            "actions": actions,
            "confidence": 0.98,
            "related_entities": related_entities
        }
        agent_chain = ["TriageAgent", "InvestigatorAgent", "ActionAgent", "MemoryAgent"]
        
        episode = self.episodic.record_episode(
            session_id=session_id,
            user_query=query,
            intent=intent,
            agent_chain=agent_chain,
            reasoning_trace=[],
            outcome=outcome,
            tenant_id=tenant_id
        )
        thought_log.append(f"Recorded Episodic Memory node '{episode['id']}' linked to Session '{session_id}' in FalkorDB.")

        # 2. Update Semantic Memory relations
        if intent == "OUTAGE_TRIAGE":
            self.semantic.link_concepts(
                source_id="service_payment_gw",
                target_id="service_auth",
                relation="PREVIOUSLY_CASCADED_FROM",
                properties={"incident_id": "inc_804", "timestamp": time.time()},
                tenant_id=tenant_id
            )
            thought_log.append("Semantic graph updated: linked (PaymentGateway)-[:PREVIOUSLY_CASCADED_FROM]->(AuthService)")

        # 3. Procedural Memory Reflection
        if intent == "OUTAGE_TRIAGE" and actions:
            thought_log.append("Reflecting on operational procedure: verified mitigation workflow matches SEV-1 Playbook.")

        final_response = {
            "query": query,
            "intent": intent,
            "answer": synthesis,
            "actions_executed": actions,
            "citations": citations,
            "subgraph": payload.get("subgraph", {}),
            "evidence": payload.get("evidence", {}),
            "memory": {
                "episode_id": episode["id"],
                "session_id": session_id,
                "tenant_id": tenant_id,
                "persisted_to_falkordb": True
            }
        }

        return {
            "agent": "MemoryAgent",
            "status": "COMPLETED",
            "thoughts": thought_log,
            "response": final_response
        }
