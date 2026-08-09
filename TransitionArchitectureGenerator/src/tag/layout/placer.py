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

        import math

        centre_x = 0.0
        centre_y = 0.0

        radius = max(
            self.grid_size,
            len(core_nodes) * self.grid_size / (2.0 * math.pi),
        )

        ordered_nodes = sorted(
            core_nodes,
            key=lambda node: node.name.lower(),
        )

        for index, node in enumerate(ordered_nodes):
            angle = (
                2.0
                * math.pi
                * index
                / len(ordered_nodes)
            )

            positions[node.id] = NodePosition(
                x=centre_x + radius * math.cos(angle),
                y=centre_y + radius * math.sin(angle),
                layout_layer=1,
            )

        return positions

    def dump(self, graph: LayoutGraph) -> None:
        """Print the current placement to the console."""

        positions = self.place(graph)

        print()
        print("Node Placement")
        print("==============")

        for node_id in sorted(
            positions,
            key=lambda node_id: graph.nodes[node_id].name.lower(),
        ):
            node = graph.nodes[node_id]
            position = positions[node_id]

            print(
                f"{node.name}"
                f"    Complexity : {node.complexity}"
                f"    Layer : {position.layout_layer}"
                f"    x={position.x:.1f}"
                f"    y={position.y:.1f}"
            )

