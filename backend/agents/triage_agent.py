import time
from typing import Dict, Any

class TriageAgent:
    """
    Agent 1: Triage & Intent Classifier.
    Analyzes incoming questions, alarms, or incident logs.
    Inspects FalkorDB episodic and semantic memory to detect whether a learned
    ':HISTORICAL_CASCADE' shortcut exists (Two-Run Learning Loop).
    """
    def __init__(self, mcp_server, memory_managers):
        self.mcp = mcp_server
        self.episodic = memory_managers["episodic"]
        self.semantic = memory_managers["semantic"]

    def run(self, user_query: str, session_id: str, context: Dict[str, Any] = None, tenant_id: str = "nexus_corp") -> Dict[str, Any]:
        thought_log = []
        q_lower = user_query.lower()

        thought_log.append(f"Received query: '{user_query}' in session {session_id}")
        
        # Check episodic memory for prior session context
        past_episodes = self.episodic.recall_recent_episodes(session_id, limit=3, tenant_id=tenant_id)
        if past_episodes:
            thought_log.append(f"Recalled {len(past_episodes)} prior episodes from session memory.")

        # Determine target entity & intent
        if any(w in q_lower for w in ["outage", "500", "spike", "error", "failing", "degraded", "sev-1", "incident", "alarm"]):
            intent = "OUTAGE_TRIAGE"
            target_entity = "service_payment_gw" if "payment" in q_lower else ("service_auth" if "auth" in q_lower else "inc_804")
            thought_log.append(f"Classified as critical OUTAGE_TRIAGE. Primary target entity: {target_entity}")
        elif any(w in q_lower for w in ["why", "rfc", "decision", "decide", "adr", "migrate", "chose"]):
            intent = "DECISION_PROVENANCE"
            target_entity = "rfc_104" if "104" in q_lower or "falkor" in q_lower or "session" in q_lower else "rfc_112"
            thought_log.append(f"Classified as DECISION_PROVENANCE. Tracing decision source for: {target_entity}")
        elif any(w in q_lower for w in ["who owns", "who knows", "expert", "on-call", "team", "engineer"]):
            intent = "EXPERTISE_DISCOVERY"
            target_entity = "service_auth" if "auth" in q_lower else ("service_payment_gw" if "payment" in q_lower else "service_ledger")
            thought_log.append(f"Classified as EXPERTISE_DISCOVERY for entity: {target_entity}")
        elif any(w in q_lower for w in ["blast", "breaks", "impact", "downstream", "pagerank", "centrality"]):
            intent = "BLAST_RADIUS_AUDIT"
            target_entity = "service_auth" if "auth" in q_lower else "service_payment_gw"
            thought_log.append(f"Classified as BLAST_RADIUS_AUDIT for entity: {target_entity}")
        else:
            intent = "COMPANY_INTELLIGENCE"
            target_entity = None
            thought_log.append("Classified as general COMPANY_INTELLIGENCE graph search.")

        # Check for Two-Run Learning Loop shortcut edge: :HISTORICAL_CASCADE
        is_memory_accelerated = False
        learned_shortcut = None

        if intent == "OUTAGE_TRIAGE" and target_entity == "service_payment_gw":
            graph = self.mcp.engine.get_or_create_graph(f"tenant_{tenant_id}_brain")
            for e in graph.edges:
                if e["source"] == "service_payment_gw" and e["type"] == "HISTORICAL_CASCADE":
                    is_memory_accelerated = True
                    learned_shortcut = {
                        "target_service": e["target"],
                        "confidence": e.get("properties", {}).get("confidence", 0.94),
                        "last_incident": e.get("properties", {}).get("last_incident", "INC-804")
                    }
                    thought_log.append(
                        f"🧠 MEMORY HIT (Two-Run Loop)! Discovered learned shortcut edge :HISTORICAL_CASCADE "
                        f"from PaymentGateway -> {e['target']} (confidence: {learned_shortcut['confidence']}). "
                        f"Bypassing 5-hop exploration, resolving in 1 direct hop!"
                    )
                    break

        handoff_payload = {
            "query": user_query,
            "session_id": session_id,
            "intent": intent,
            "target_entity": target_entity,
            "is_memory_accelerated": is_memory_accelerated,
            "learned_shortcut": learned_shortcut,
            "past_episodes_count": len(past_episodes),
            "triage_notes": f"Triage complete. Delegating to Graph Investigator Agent with intent {intent}."
        }

        return {
            "agent": "TriageAgent",
            "status": "HANDOFF",
            "handoff_to": "InvestigatorAgent",
            "thoughts": thought_log,
            "payload": handoff_payload
        }
