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

        complexities = sorted(
            {
                node.complexity
                for node in nodes
                if node.complexity is not None
            },
            reverse=True,
        )

        for complexity in complexities:
            complexity_nodes = [
                node
                for node in nodes
                if node.complexity == complexity
            ]

            if complexity == max_complexity:
                self._place_core(
                    complexity_nodes,
                    positions,
                )
                continue

            self._place_outer_nodes(
                complexity_nodes,
                positions,
                complexity,
            )

        return positions

    def _place_core(
        self,
        nodes: list,
        positions: dict[str, NodePosition],
    ) -> None:
        """Place the most complex nodes in the centre layer."""

        import math

        ordered_nodes = sorted(
            nodes,
            key=lambda node: node.name.lower(),
        )

        radius = max(
            self.grid_size,
            len(ordered_nodes) * self.grid_size / (2.0 * math.pi),
        )

        for index, node in enumerate(ordered_nodes):
            angle = (
                2.0
                * math.pi
                * index
                / len(ordered_nodes)
            )

            positions[node.id] = NodePosition(
                x=radius * math.cos(angle),
                y=radius * math.sin(angle),
                layout_layer=1,
            )


    def _place_outer_nodes(
        self,
        nodes: list,
        positions: dict[str, NodePosition],
        complexity: int,
    ) -> None:
        """Place the next complexity level outside the existing nodes."""

        import math

        ordered_nodes = sorted(
            nodes,
            key=lambda node: node.name.lower(),
        )

        existing_layers = [
            position.layout_layer
            for position in positions.values()
        ]

        outer_layer = max(existing_layers, default=1)

        radius = outer_layer * self.grid_size * 2.0

        angle_offset = (
            complexity * math.pi / 4.0
        )

        for index, node in enumerate(ordered_nodes):
            angle = (
                angle_offset
                + 2.0
                * math.pi
                * index
                / len(ordered_nodes)
            )

            positions[node.id] = NodePosition(
                x=radius * math.cos(angle),
                y=radius * math.sin(angle),
                layout_layer=outer_layer,
            )

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

