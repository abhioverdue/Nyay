"""
Graph RAG: builds a directed citation graph where nodes are judgments
and edges represent "cites" relationships.

When a query retrieves a judgment, we traverse its precedent chain
(ancestors = cases it relies on) and include them in the context window.
The LLM now reasons over the full legal lineage, not just one document.

This is the key architectural differentiator from standard RAG.
"""

import networkx as nx
from backend.models import Judgment, GraphNode

class PrecedentGraph:
    def __init__(self):
        self.G = nx.DiGraph()
        self._judgments: dict[str, Judgment] = {}

    def build(self, judgments: list[Judgment], citation_map: dict[str, list[str]]):
        """
        citation_map: {case_id: [list of case_ids it cites]}
        Edge direction: citing → cited (follows legal precedent direction)
        """
        self._judgments = {j.case_id: j for j in judgments}

        for j in judgments:
            self.G.add_node(j.case_id, judgment=j)

        for case_id, cited_ids in citation_map.items():
            for cited_id in cited_ids:
                if case_id in self.G and cited_id in self.G:
                    self.G.add_edge(case_id, cited_id)  # case_id cites cited_id

    def get_precedent_chain(self, case_id: str, max_hops: int = 2) -> list[GraphNode]:
        """
        Returns ancestor nodes (cases this judgment relies on), up to max_hops.
        Uses BFS on the directed graph following citation edges.
        """
        if case_id not in self.G:
            return []

        visited = set()
        queue = [(case_id, 0)]
        chain: list[GraphNode] = []

        while queue:
            current_id, depth = queue.pop(0)
            if current_id in visited or depth > max_hops:
                continue
            visited.add(current_id)

            if current_id != case_id:  # don't include the root itself
                j = self._judgments.get(current_id)
                if j:
                    chain.append(GraphNode(
                        case_id=current_id,
                        court=j.court,
                        date=j.date,
                        outcome=j.outcome,
                        depth=depth
                    ))

            # follow outgoing edges (cases this node cites)
            for successor in self.G.successors(current_id):
                if successor not in visited:
                    queue.append((successor, depth + 1))

        return chain

    def get_citing_cases(self, case_id: str) -> list[str]:
        """Returns cases that cite this judgment (its descendants)."""
        return list(self.G.predecessors(case_id))

    def get_graph_data(self) -> dict:
        """Returns full graph as JSON-serialisable dict for the frontend D3 visualisation."""
        nodes = []
        for node_id in self.G.nodes():
            j = self._judgments.get(node_id)
            if j:
                nodes.append({
                    "id": node_id,
                    "court": j.court,
                    "section": j.section_cited,
                    "outcome": j.outcome,
                    "date": j.date,
                    "state": j.state,
                    "citing_count": len(list(self.G.predecessors(node_id))),
                })
        edges = [{"source": u, "target": v} for u, v in self.G.edges()]
        return {"nodes": nodes, "edges": edges}

    def get_subgraph(self, case_ids: list[str]) -> dict:
        """Returns subgraph for a set of case IDs (used for query-specific visualisation)."""
        relevant = set(case_ids)
        # include their precedents too
        for cid in list(relevant):
            for anc in self.get_precedent_chain(cid, max_hops=2):
                relevant.add(anc.case_id)

        nodes = []
        edges = []
        for node_id in relevant:
            if node_id in self.G:
                j = self._judgments.get(node_id)
                if j:
                    nodes.append({
                        "id": node_id,
                        "court": j.court,
                        "section": j.section_cited,
                        "outcome": j.outcome,
                        "date": j.date,
                        "state": j.state,
                        "is_query_result": node_id in case_ids,
                    })
        for u, v in self.G.edges():
            if u in relevant and v in relevant:
                edges.append({"source": u, "target": v})

        return {"nodes": nodes, "edges": edges}


_graph = PrecedentGraph()

def get_graph() -> PrecedentGraph:
    return _graph
