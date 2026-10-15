import time
import uuid
from typing import Dict, List, Any, Optional

class ProceduralMemoryManager:
    """
    Manages procedural memory (playbooks, executable SOP workflows, operational recipes).
    Workflows are stored as directed linked graph chains:
    (Playbook)-[:FIRST_STEP]->(PlaybookStep)-[:NEXT_STEP]->(PlaybookStep)
    """
    def __init__(self, graph_engine):
        self.engine = graph_engine

    def get_playbook_workflow(self, playbook_id: str, tenant_id: str = "nexus_corp") -> Optional[Dict[str, Any]]:
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)

        pb_node = graph.get_node(playbook_id)
        if not pb_node:
            return None

        # Find first step
        first_step_id = None
        for e in graph.edges:
            if e["source"] == playbook_id and e["type"] == "FIRST_STEP":
                first_step_id = e["target"]
                break

        steps_chain = []
        curr_step_id = first_step_id
        visited = set()

        while curr_step_id and curr_step_id not in visited:
            visited.add(curr_step_id)
            step_node = graph.get_node(curr_step_id)
            if not step_node:
                break
            steps_chain.append(step_node["properties"])

            # Find next step
            next_id = None
            for e in graph.edges:
                if e["source"] == curr_step_id and e["type"] == "NEXT_STEP":
                    next_id = e["target"]
                    break
            curr_step_id = next_id

        return {
            "playbook": pb_node["properties"],
            "steps": steps_chain,
            "total_steps": len(steps_chain)
        }

    def list_all_playbooks(self, tenant_id: str = "nexus_corp") -> List[Dict[str, Any]]:
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)

        playbooks = []
        for nid in graph.labels.get("Playbook", set()):
            node = graph.get_node(nid)
            if node:
                wf = self.get_playbook_workflow(nid, tenant_id)
                playbooks.append({
                    "id": nid,
                    "properties": node["properties"],
                    "steps_count": len(wf["steps"]) if wf else 0
                })
        return playbooks

    def learn_new_playbook(
        self,
        name: str,
        domain: str,
        trigger_condition: str,
        steps: List[Dict[str, Any]],
        tenant_id: str = "nexus_corp"
    ) -> Dict[str, Any]:
        """
        Dynamically learns and stores a new procedural graph in FalkorDB
        based on a successful incident resolution or operator instruction.
        """
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)

        pb_id = f"plb_{uuid.uuid4().hex[:6]}"
        pb_props = {
            "id": pb_id,
            "name": name,
            "domain": domain,
            "trigger_condition": trigger_condition,
            "created_at": time.time(),
            "learned_by_agent": True,
            "steps_count": len(steps)
        }
        graph.add_node(pb_id, "Playbook", pb_props)

        prev_step_id = None
        step_nodes = []
        for idx, stp in enumerate(steps):
            stp_id = f"step_{pb_id}_{idx+1}"
            step_data = {
                "id": stp_id,
                "step_number": idx + 1,
                "action_name": stp.get("action_name", f"Step {idx+1}"),
                "command": stp.get("command", ""),
                "description": stp.get("description", "")
            }
            graph.add_node(stp_id, "PlaybookStep", step_data)
            step_nodes.append(step_data)

            if idx == 0:
                graph.add_edge(pb_id, stp_id, "FIRST_STEP", {})
            else:
                graph.add_edge(prev_step_id, stp_id, "NEXT_STEP", {})
            prev_step_id = stp_id

        return {
            "status": "learned",
            "playbook_id": pb_id,
            "playbook": pb_props,
            "steps": step_nodes
        }
