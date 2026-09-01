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
    name: str

    #
    # Union of all neighbours across every page.
    #
    neighbours: set[str] = field(default_factory=set)

    #
    # Neighbours visible on each individual milestone.
    #
    # Key:
    #     milestone name
    #
    # Value:
    #     immutable set of neighbouring node ids
    #
    page_neighbours: dict[str, frozenset[str]] = field(default_factory=dict)

    #
    # Complexity level assigned by the graph peeler.
    #
    # Complexity 1 represents leaves.
    # Higher values represent increasingly central nodes.
    #
    complexity: int | None = None

    #
    # Order in which the node was peeled within its complexity level.
    #
    peel_round: int | None = None

    #
    # Footprint of the node on the integer layout grid.
    #
    # A normal node occupies one cell.
    # Composite nodes may occupy multiple cells.
    #
    width: int = 1
    height: int = 1

    @property
    def level(self) -> str | None:
        """
        Return the hierarchical level of the node.

        Examples:
            1.1
            2.3
            3.5

        Returns None if the node has not yet been analysed.
        """

        if self.complexity is None or self.peel_round is None:
            return None

        return f"{self.complexity}.{self.peel_round + 1}"


@dataclass(slots=True)
class LayoutGraph:
    """
    Undirected graph used by the layout engine.
    """

    nodes: dict[str, LayoutNode] = field(default_factory=dict)

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return (
            sum(
                len(node.neighbours)
                for node in self.nodes.values()
            )
            // 2
        )

    @property
    def max_complexity(self) -> int:
        complexities = [
            node.complexity
            for node in self.nodes.values()
            if node.complexity is not None
        ]

        if not complexities:
            return 0

        return max(complexities)

    def __str__(self) -> str:
        return (
            f"LayoutGraph("
            f"nodes={self.node_count}, "
            f"edges={self.edge_count})"
        )

    def add_node(
        self,
        node_id: str,
        name: str,
    ) -> None:

        if node_id not in self.nodes:
            self.nodes[node_id] = LayoutNode(
                id=node_id,
                name=name,
            )

    def add_edge(
        self,
        source: str,
        target: str,
    ) -> None:

        if source == target:
            return

        self.nodes[source].neighbours.add(target)
        self.nodes[target].neighbours.add(source)

    def dump(self) -> str:
        """
        Return a human-readable representation of the layout graph.
        """

        lines = [
            "Layout Graph",
            "============",
            "",
            f"Nodes           : {self.node_count}",
            f"Edges           : {self.edge_count}",
            f"Max complexity  : {self.max_complexity}",
            "",
        ]

        for complexity in range(1, self.max_complexity + 1):

            nodes = sorted(
                (
                    node
                    for node in self.nodes.values()
                    if node.complexity == complexity
                ),
                key=lambda node: (
                    node.peel_round
                    if node.peel_round is not None
                    else -1,
                    node.name.casefold(),
                ),
            )

            if not nodes:
                continue

            for node in nodes:

                lines.append(
                    f"\t{node.level}\t{node.name}"
                )

                if node.neighbours:

                    for neighbour in sorted(node.neighbours):

                        neighbour_name = (
                            self.nodes[neighbour].name
                        )

                        lines.append(
                            f"\t\t\t{neighbour_name}"
                        )

                else:
                    lines.append("\t\t\t(isolated)")

        return "\n".join(lines)
