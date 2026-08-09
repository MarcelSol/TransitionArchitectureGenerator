from dataclasses import dataclass

from tag.layout.graph import LayoutGraph


@dataclass
class NodePosition:
    x: float
    y: float
    layout_layer: int


class LayoutPlacer:
    """Place nodes according to their complexity and graph relationships."""

    def __init__(
        self,
        grid_size: float = 200.0,
        node_spacing: float = 80.0,
    ) -> None:
        self.grid_size = grid_size
        self.node_spacing = node_spacing

    def place(self, graph: LayoutGraph) -> dict[str, NodePosition]:
        """Calculate a position for every node in the layout graph."""

        positions: dict[str, NodePosition] = {}

        nodes = list(graph.nodes.values())

        if not nodes:
            return positions

        max_complexity = max(
            node.complexity or 0
            for node in nodes
        )

        core_nodes = [
            node
            for node in nodes
            if node.complexity == max_complexity
        ]

        if not core_nodes:
            return positions

        # First version: arrange the most complex nodes
        # evenly around the centre.
        import math

        centre_x = 0.0
        centre_y = 0.0

        radius = max(
            self.grid_size,
            len(core_nodes) * self.grid_size / (2 * math.pi),
        )

        for index, node in enumerate(
            sorted(core_nodes, key=lambda n: n.id)
        ):
            angle = (
                2.0 * math.pi * index / len(core_nodes)
            )

            x = centre_x + radius * math.cos(angle)
            y = centre_y + radius * math.sin(angle)

            positions[node.id] = NodePosition(
                x=x,
                y=y,
                layout_layer=1,
            )

        return positions
