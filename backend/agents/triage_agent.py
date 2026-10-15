import time
from typing import Dict, Any

class TriageAgent:
    """
    Agent 1: Triage & Intent Classifier.
    Analyzes incoming questions, alarms, or incident logs,
    determines the operational domain, and establishes shared state for coordination.
    """
    def __init__(self, mcp_server, memory_managers):
        self.mcp = mcp_server
        self.episodic = memory_managers["episodic"]
        self.semantic = memory_managers["semantic"]

    def run(self, user_query: str, session_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        thought_log = []
        q_lower = user_query.lower()

        thought_log.append(f"Received query: '{user_query}' in session {session_id}")
        
        # Check episodic memory for prior session context
        past_episodes = self.episodic.recall_recent_episodes(session_id, limit=3)
        if past_episodes:
            thought_log.append(f"Recalled {len(past_episodes)} prior episodes from session memory.")

        # Intent Classification
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

        handoff_payload = {
            "query": user_query,
            "session_id": session_id,
            "intent": intent,
            "target_entity": target_entity,
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
