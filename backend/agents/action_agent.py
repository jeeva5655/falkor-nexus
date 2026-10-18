import time
from typing import Dict, Any, List

class ActionAgent:
    """
    Agent 3: Action & Remediation Agent.
    Translates graph insights into concrete actions:
    executes procedural SOP playbooks, isolates degraded dependencies,
    dispatches on-call alerts, creates rollback branches, and formats clear citations.
    """
    def __init__(self, mcp_server, memory_managers):
        self.mcp = mcp_server
        self.procedural = memory_managers["procedural"]

    def run(self, handoff_data: Dict[str, Any], tenant_id: str = "nexus_corp") -> Dict[str, Any]:
        payload = handoff_data.get("payload", {})
        intent = payload.get("intent")
        evidence = payload.get("evidence", {})
        synthesis = payload.get("investigation_synthesis", "")

        thought_log = []
        executed_actions = []
        citations = []

        thought_log.append(f"Action Agent activated. Synthesizing response and checking procedural playbooks for intent: {intent}")

        if intent == "OUTAGE_TRIAGE":
            # 1. Retrieve Procedural SOP Playbook from procedural memory
            thought_log.append("Consulting Procedural Memory for Playbook: 'plb_sev1_triage'")
            playbook_wf = self.procedural.get_playbook_workflow("plb_sev1_triage", tenant_id=tenant_id)
            if playbook_wf:
                thought_log.append(f"Loaded playbook '{playbook_wf['playbook']['name']}' with {playbook_wf['total_steps']} executable steps.")

            # 2. Execute Action 1: Circuit breaker isolation
            thought_log.append("Executing Action: Enable Circuit-Breaker on AuthService (Prevent cascading 504 timeouts)")
            act1 = self.mcp.call_tool("falkordb_execute_action", {
                "action_type": "isolate_service",
                "target_id": "service_auth",
                "parameters": {"fallback": "token_cache_stale_allow"}
            })
            executed_actions.append(act1.get("action_record", {}))

            # 3. Execute Action 2: Page On-Call SME
            thought_log.append("Executing Action: Page Sarah Chen (On-Call Lead Architect for AuthService)")
            act2 = self.mcp.call_tool("falkordb_execute_action", {
                "action_type": "page_on_call",
                "target_id": "sarah_chen",
                "parameters": {"severity": "SEV-1", "incident": "INC-804"}
            })
            executed_actions.append(act2.get("action_record", {}))

            # 4. Execute Action 3: Rollback PR
            thought_log.append("Executing Action: Generate Automated Rollback Branch for PR #482 (commit c3b8f19)")
            act3 = self.mcp.call_tool("falkordb_execute_action", {
                "action_type": "revert_pr",
                "target_id": "pr_482",
                "parameters": {"commit": "c3b8f19"}
            })
            executed_actions.append(act3.get("action_record", {}))

            citations = [
                {"label": "Incident", "id": "inc_804", "title": "INC-804: PaymentGateway 500 Spike"},
                {"label": "Degraded Dependency", "id": "service_auth", "title": "AuthService (Tier-1, Critical)"},
                {"label": "Culprit Pull Request", "id": "pr_482", "title": "PR #482: feat(auth) JWT token cache"},
                {"label": "Root Cause Commit", "id": "commit_c3b8f19", "title": "commit c3b8f19: strict claim verification"},
                {"label": "SME / On-Call", "id": "sarah_chen", "title": "Sarah Chen (Principal Architect)"},
                {"label": "Procedural Playbook", "id": "plb_sev1_triage", "title": "SEV-1 Outage Mitigation SOP"}
            ]

        elif intent == "DECISION_PROVENANCE":
            citations = [
                {"label": "RFC Document", "id": "rfc_104", "title": "RFC-104: FalkorDB Graph Identity & Multi-Tenant Context"},
                {"label": "Architectural Decision", "id": "dec_42", "title": "ADR-42: Adopt FalkorDB Multi-Tenant Topology"},
                {"label": "Historical Incident", "id": "inc_732", "title": "INC-732: Auth Token Revocation Memory Leak (Postmortem)"},
                {"label": "Author & Approver", "id": "sarah_chen", "title": "Sarah Chen (Principal Systems Architect)"}
            ]

        elif intent == "EXPERTISE_DISCOVERY":
            experts = evidence.get("experts", [])
            citations = [
                {
                    "label": exp.get("relation", "Expert"),
                    "id": exp["person"]["id"],
                    "title": f"{exp['person']['name']} ({exp['person'].get('role', 'Engineer')})"
                }
                for exp in experts if exp.get("person")
            ]

        else:
            citations = [
                {"label": "Service", "id": "service_auth", "title": "AuthService"},
                {"label": "Dependent Service", "id": "service_payment_gw", "title": "PaymentGateway"},
                {"label": "Dependent Service", "id": "service_order_proc", "title": "OrderProcessor"}
            ]

        handoff_payload = {
            **payload,
            "actions_executed": executed_actions,
            "citations": citations,
            "final_synthesis": synthesis
        }

        return {
            "agent": "ActionAgent",
            "status": "HANDOFF",
            "handoff_to": "MemoryAgent",
            "thoughts": thought_log,
            "actions_count": len(executed_actions),
            "payload": handoff_payload
        }
