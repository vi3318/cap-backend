import json
from typing import Any, Dict, List, Optional, Tuple
import networkx as nx


class KnowledgeGraphBuilder:
    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()

    def reset_graph(self) -> None:
        self.graph = nx.MultiDiGraph()

    def add_entities(self, entities: Dict[str, List[Dict[str, Any]]]) -> None:
        for entity_type, items in entities.items():
            for item in items:
                name = item.get("text") or item.get("name")
                if not name:
                    continue
                node_id = self._node_id(name, entity_type)
                if not self.graph.has_node(node_id):
                    self.graph.add_node(
                        node_id,
                        label=name,
                        type=entity_type,
                        meta={k: v for k, v in item.items() if k not in {"text", "name"}},
                    )

    def add_relations(self, relations: List[Tuple[str, str, str]]) -> None:
        for source, target, relation_type in relations:
            self.graph.add_edge(source, target, type=relation_type)

    def infer_relations_from_entities(self, entities: Dict[str, List[Dict[str, Any]]]) -> None:
        statutes = entities.get("statutes", [])
        cases = entities.get("cases", [])
        parties = entities.get("parties", [])
        courts = entities.get("courts", [])
        dates = entities.get("dates", [])

        for case in cases:
            case_node = self._node_id(case.get("text") or case.get("name"), "case")
            for statute in statutes:
                statute_node = self._node_id(statute.get("text") or statute.get("name"), "statute")
                self.graph.add_edge(case_node, statute_node, type="cites")

            for court in courts:
                court_node = self._node_id(court.get("text") or court.get("name"), "court")
                self.graph.add_edge(case_node, court_node, type="heard_by")

            for party in parties:
                party_node = self._node_id(party.get("text") or party.get("name"), "party")
                self.graph.add_edge(party_node, case_node, type="party_in")

            for date in dates:
                date_node = self._node_id(date.get("text") or date.get("name"), "date")
                self.graph.add_edge(case_node, date_node, type="decided_on")

    def build_from_document(self, document_id: str, entities: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        self.reset_graph()
        self.add_entities(entities)
        self.infer_relations_from_entities(entities)
        return self.to_json()

    def get_subgraph(self, center_node_label: str, node_type: Optional[str] = None, depth: int = 2) -> Dict[str, Any]:
        center_candidates = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("label") == center_node_label and (node_type is None or d.get("type") == node_type)
        ]
        if not center_candidates:
            return {"nodes": [], "links": []}

        center = center_candidates[0]
        nodes = {center}
        frontier = {center}
        for _ in range(depth):
            next_frontier = set()
            for node in frontier:
                neighbors = set(self.graph.predecessors(node)) | set(self.graph.successors(node))
                next_frontier |= neighbors
            nodes |= next_frontier
            frontier = next_frontier

        subgraph = self.graph.subgraph(nodes).copy()
        return self.to_json(subgraph)

    def stats(self) -> Dict[str, Any]:
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "by_type": self._nodes_by_type(),
        }

    def to_json(self, g: Optional[nx.MultiDiGraph] = None) -> Dict[str, Any]:
        graph = g or self.graph
        nodes = []
        node_index = {}
        for idx, (node_id, data) in enumerate(graph.nodes(data=True)):
            node_index[node_id] = idx
            nodes.append({
                "id": node_id,
                "label": data.get("label"),
                "type": data.get("type"),
                "meta": data.get("meta", {}),
            })

        links = []
        for source, target, data in graph.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "type": data.get("type"),
            })

        return {"nodes": nodes, "links": links}

    def _node_id(self, label: str, node_type: str) -> str:
        return f"{node_type}:{label}".strip()

    def _nodes_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for _, data in self.graph.nodes(data=True):
            t = data.get("type", "unknown")
            counts[t] = counts.get(t, 0) + 1
        return counts

