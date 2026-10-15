import time
from typing import Dict, List, Any, Optional

class SemanticMemoryManager:
    """
    Manages semantic memory (conceptual knowledge, entity relations, organizational facts).
    Allows agents to recall definitions, architectural guidelines, and relationships.
    """
    def __init__(self, graph_engine):
        self.engine = graph_engine

    def add_concept(self, concept_id: str, name: str, description: str, category: str, tenant_id: str = "nexus_corp"):
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)
        data = {
            "id": concept_id,
            "name": name,
            "description": description,
            "category": category,
            "updated_at": time.time()
        }
        return graph.add_node(concept_id, "Concept", data)

    def link_concepts(self, source_id: str, target_id: str, relation: str, properties: Dict[str, Any] = None, tenant_id: str = "nexus_corp"):
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)
        return graph.add_edge(source_id, target_id, relation, properties or {})

    def query_semantic_context(self, term: str, tenant_id: str = "nexus_corp") -> List[Dict[str, Any]]:
        """
        Retrieves nodes whose names, properties, or labels match the semantic search query.
        """
        graph_name = f"tenant_{tenant_id}_brain"
        graph = self.engine.get_or_create_graph(graph_name)
        term_lower = term.lower()
        matches = []

        for nid, n in graph.nodes.items():
            props = n.get("properties", {})
            name = str(props.get("name", "")).lower()
            title = str(props.get("title", "")).lower()
            desc = str(props.get("description", "")).lower()
            summary = str(props.get("summary", "")).lower()
            skills = " ".join(props.get("skills", [])).lower() if isinstance(props.get("skills"), list) else ""

            if term_lower in name or term_lower in title or term_lower in desc or term_lower in summary or term_lower in skills or term_lower in nid.lower():
                matches.append({
                    "id": nid,
                    "label": n.get("label"),
                    "properties": props
                })

        return matches
