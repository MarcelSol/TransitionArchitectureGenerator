import math

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

            if not positions:
                self._place_core(
                    complexity_nodes,
                    positions,
                )
            else:
                self._place_complexity_level(
                    complexity_nodes,
                    positions,
                )

        return positions

    def _place_core(
        self,
        nodes: list,
        positions: dict[str, NodePosition],
    ) -> None:
        """Place the most complex nodes in the centre layer."""

        ordered_nodes = sorted(
            nodes,
            key=lambda node: node.name.lower(),
        )

        radius = max(
            self.grid_size,
            len(ordered_nodes)
            * self.grid_size
            / (2.0 * math.pi),
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

    def _place_complexity_level(
        self,
        nodes: list,
        positions: dict[str, NodePosition],
    ) -> None:
        """Place a complexity level using already-placed neighbours."""

        for node in sorted(
            nodes,
            key=lambda node: node.name.lower(),
        ):

            neighbour_layers = [
                positions[neighbour_id].layout_layer
                for neighbour_id in node.neighbours
                if neighbour_id in positions
            ]

            current_layer = max(
                neighbour_layers,
                default=1,
            )

            candidate = self._find_best_position(
                node,
                current_layer,
                positions,
            )

            if candidate is None:
                current_layer += 1

                candidate = self._find_best_position(
                    node,
                    current_layer,
                    positions,
                )

            if candidate is None:
                raise RuntimeError(
                    f"Could not place node '{node.name}' "
                    f"in layout layer {current_layer}"
                )

            positions[node.id] = candidate


    def _find_best_position(
        self,
        node,
        layer: int,
        positions: dict[str, NodePosition],
    ) -> NodePosition | None:
        """Find the best available position for a node."""

        candidates = self._generate_candidates(
            layer,
        )

        placed_neighbours = [
            positions[neighbour_id]
            for neighbour_id in node.neighbours
            if neighbour_id in positions
        ]

        if not placed_neighbours:
            for candidate in candidates:
                if self._position_is_free(
                    candidate.x,
                    candidate.y,
                    positions,
                ):
                    return candidate

            return None

        best_candidate = None
        best_score = float("inf")

        for candidate in candidates:
            if not self._position_is_free(
                candidate.x,
                candidate.y,
                positions,
            ):
                continue

            score = self._distance_to_neighbours(
                candidate,
                placed_neighbours,
            )

            if score < best_score:
                best_score = score
                best_candidate = candidate

        return best_candidate

    def _generate_candidates(
        self,
        layer: int,
    ) -> list[NodePosition]:
        """Generate possible positions around a layout layer."""

        radius = layer * self.grid_size * 2.0

        circumference = 2.0 * math.pi * radius

        slot_count = max(
            8,
            int(
                circumference
                / self.node_spacing
            ),
        )

        candidates = []

        for slot in range(slot_count):
            angle = (
                2.0
                * math.pi
                * slot
                / slot_count
            )

            candidates.append(
                NodePosition(
                    x=radius * math.cos(angle),
                    y=radius * math.sin(angle),
                    layout_layer=layer,
                )
            )

        return candidates

    def _distance_to_neighbours(
        self,
        candidate: NodePosition,
        neighbours: list[NodePosition],
    ) -> float:
        """Calculate the total distance to a node's neighbours."""

        total_distance = 0.0

        for neighbour in neighbours:
            dx = candidate.x - neighbour.x
            dy = candidate.y - neighbour.y

            total_distance += math.sqrt(
                dx * dx + dy * dy
            )

        return total_distance

    def _try_place_in_layer(
        self,
        node,
        layer: int,
        positions: dict[str, NodePosition],
    ) -> bool:
        """Try to find a free position in the requested layer."""

        radius = layer * self.grid_size * 2.0

        circumference = 2.0 * math.pi * radius

        slot_count = max(
            1,
            int(
                circumference
                / self.node_spacing
            ),
        )

        for slot in range(slot_count):
            angle = (
                2.0
                * math.pi
                * slot
                / slot_count
            )

            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            if self._position_is_free(
                x,
                y,
                positions,
            ):
                positions[node.id] = NodePosition(
                    x=x,
                    y=y,
                    layout_layer=layer,
                )

                return True

        return False

    def _position_is_free(
        self,
        x: float,
        y: float,
        positions: dict[str, NodePosition],
    ) -> bool:
        """Return True when no existing node is too close."""

        for position in positions.values():
            dx = x - position.x
            dy = y - position.y

            distance = math.sqrt(
                dx * dx + dy * dy
            )

            if distance < self.node_spacing:
                return False

        return True
