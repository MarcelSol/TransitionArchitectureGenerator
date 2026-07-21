"""
Graph representation used by the TAG layout engine.
"""
from dataclasses import dataclass, field


@dataclass(slots=True)
class LayoutNode:
    """
    A semantic node in the layout graph.
    """

    id: str
    neighbours: set[str] = field(default_factory=set)


@dataclass(slots=True)
class LayoutGraph:
    """
    Undirected graph used by the layout engine.
    """
    @property
    def node_count(self) -> int:
        return len(self.nodes)


    @property
    def edge_count(self) -> int:

        return (
            sum(
                len(node.neighbours)
                for node in self.nodes.values()
            ) // 2
        )

    nodes: dict[str, LayoutNode] = field(default_factory=dict)

    def __str__(self) -> str:

        return (
            f"LayoutGraph("
            f"nodes={self.node_count}, "
            f"edges={self.edge_count})"
        )

    def add_node(self, node_id: str) -> None:

        if node_id not in self.nodes:
            self.nodes[node_id] = LayoutNode(id=node_id)

    def add_edge(
        self,
        source: str,
        target: str,
    ) -> None:

        if source == target:
            return

        self.add_node(source)
        self.add_node(target)

        self.nodes[source].neighbours.add(target)
        self.nodes[target].neighbours.add(source)
