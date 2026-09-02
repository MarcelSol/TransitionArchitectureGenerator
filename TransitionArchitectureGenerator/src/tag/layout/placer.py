"""
Grid-based node placement for the TAG layout engine.
"""

from dataclasses import dataclass

from tag.layout.graph import LayoutGraph, LayoutNode


@dataclass(frozen=True, slots=True)
class NodePosition:
    """
    Position of a node on the integer layout grid.

    x and y identify the top-left cell occupied by the node.

    layout_layer is the minimum onion layer touched by the
    complete node footprint.
    """

    x: int
    y: int
    layout_layer: int


class LayoutPlacer:
    """
    Place nodes on a rectangular onion grid.

    The default core is 4 x 3.

    Each new layer adds four rows in total:
    two rows at the top and two rows at the bottom.

    The width is calculated to keep the layer as close as possible
    to a 4:3 aspect ratio.

    For layer i:

        height = 4 * (i - 1) + 3
        width  = round(4 * height / 3)
    """

    def __init__(
        self,
        core_width: int = 4,
        core_height: int = 3,
        layer_height_expansion: int = 4,
        target_aspect_ratio: float = 4 / 3,
        grid_size: float = 200.0,
        node_spacing: float = 80.0,
    ) -> None:
        if core_width < 1:
            raise ValueError("core_width must be at least 1")

        if core_height < 1:
            raise ValueError("core_height must be at least 1")

        if layer_height_expansion < 1:
            raise ValueError(
                "layer_height_expansion must be at least 1"
            )

        if target_aspect_ratio <= 0:
            raise ValueError(
                "target_aspect_ratio must be positive"
            )

        self.core_width = core_width
        self.core_height = core_height
        self.layer_height_expansion = layer_height_expansion
        self.target_aspect_ratio = target_aspect_ratio

        # Kept for compatibility with the existing CLI and callers.
        # These values belong to the later Draw.io rendering stage.
        self.grid_size = grid_size
        self.node_spacing = node_spacing

    def place(
        self,
        graph: LayoutGraph,
    ) -> dict[str, NodePosition]:
        """
        Calculate a grid position for every node.
        """

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

        minimum_layer = 1

        for complexity in complexities:

            complexity_nodes = [
                node
                for node in nodes
                if node.complexity == complexity
            ]

            ordered_nodes = sorted(
                complexity_nodes,
                key=lambda node: (
                    node.peel_round
                    if node.peel_round is not None
                    else -1,
                    node.name.casefold(),
                ),
            )

            for node in ordered_nodes:

                position = self._find_best_position(
                    node=node,
                    minimum_layer=minimum_layer,
                    positions=positions,
                    graph=graph,
                )

                if position is None:
                    raise RuntimeError(
                        f"Could not place node '{node.name}' "
                        f"with minimum layout layer "
                        f"{minimum_layer}"
                    )

                positions[node.id] = position

            if complexity_nodes:
                minimum_layer = max(
                    positions[node.id].layout_layer
                    for node in complexity_nodes
                )

        return positions

    def _find_best_position(
        self,
        node: LayoutNode,
        minimum_layer: int,
        positions: dict[str, NodePosition],
        graph: LayoutGraph,
    ) -> NodePosition | None:
        """
        Find the best available integer-grid position.

        Already-placed neighbours determine the preferred location.

        The search expands outward until it finds a position where:

        - the complete footprint is free
        - the node's minimum touched layer is permitted
        """

        placed_neighbours = [
            positions[neighbour_id]
            for neighbour_id in node.neighbours
            if neighbour_id in positions
        ]

        if placed_neighbours:

            preferred_x = round(
                sum(
                    position.x
                    for position in placed_neighbours
                )
                / len(placed_neighbours)
            )

            preferred_y = round(
                sum(
                    position.y
                    for position in placed_neighbours
                )
                / len(placed_neighbours)
            )

        else:
            preferred_x = 0
            preferred_y = 0

        max_layer = max(
            minimum_layer,
            self._max_layer(positions),
        )

        search_radius = max(
            2,
            max_layer * self.layer_height_expansion
            + node.width
            + node.height,
        )

        while search_radius <= 1000:

            candidates = self._generate_grid_candidates(
                preferred_x,
                preferred_y,
                search_radius,
            )

            candidates.sort(
                key=lambda coordinate: self._candidate_score(
                    x=coordinate[0],
                    y=coordinate[1],
                    node=node,
                    neighbours=placed_neighbours,
                    minimum_layer=minimum_layer,
                )
            )

            for x, y in candidates:

                layer = self._node_layer(
                    node=node,
                    x=x,
                    y=y,
                )

                if layer < minimum_layer:
                    continue

                if not self._position_is_free(
                    node=node,
                    x=x,
                    y=y,
                    positions=positions,
                    graph=graph,
                ):
                    continue

                return NodePosition(
                    x=x,
                    y=y,
                    layout_layer=layer,
                )

            search_radius *= 2

        return None

    def _generate_grid_candidates(
        self,
        preferred_x: int,
        preferred_y: int,
        radius: int,
    ) -> list[tuple[int, int]]:
        """
        Generate integer grid coordinates around a preferred location.

        Candidates are generated in expanding Manhattan-distance rings.
        """

        candidates: list[tuple[int, int]] = []

        for distance in range(radius + 1):

            for dx in range(-distance, distance + 1):

                dy = distance - abs(dx)

                if dy == 0:

                    candidates.append(
                        (
                            preferred_x + dx,
                            preferred_y,
                        )
                    )

                else:

                    candidates.append(
                        (
                            preferred_x + dx,
                            preferred_y + dy,
                        )
                    )

                    candidates.append(
                        (
                            preferred_x + dx,
                            preferred_y - dy,
                        )
                    )

        return list(dict.fromkeys(candidates))

    def _candidate_score(
        self,
        x: int,
        y: int,
        node: LayoutNode,
        neighbours: list[NodePosition],
        minimum_layer: int,
    ) -> tuple[float, int, int, int]:
        """
        Score a candidate position.

        Connected nodes are preferred to be close together.

        Among otherwise similar candidates, the innermost permitted
        layer is preferred.

        The remaining terms provide deterministic tie-breaking.
        """

        if neighbours:

            distance = sum(
                abs(x - neighbour.x)
                + abs(y - neighbour.y)
                for neighbour in neighbours
            )

        else:

            distance = abs(x) + abs(y)

        layer = self._node_layer(
            node=node,
            x=x,
            y=y,
        )

        if layer < minimum_layer:
            layer_penalty = 1_000_000
        else:
            layer_penalty = 0

        return (
            layer_penalty + distance,
            layer,
            abs(y),
            abs(x),
        )

    def _position_is_free(
        self,
        node: LayoutNode,
        x: int,
        y: int,
        positions: dict[str, NodePosition],
        graph: LayoutGraph,
    ) -> bool:
        """
        Return True when every cell in the node footprint is free.
        """

        occupied = self._occupied_cells(
            node=node,
            x=x,
            y=y,
        )

        for other_id, position in positions.items():

            other_node = graph.nodes[other_id]

            other_occupied = self._occupied_cells(
                node=other_node,
                x=position.x,
                y=position.y,
            )

            if occupied.intersection(other_occupied):
                return False

        return True

    def _occupied_cells(
        self,
        node: LayoutNode,
        x: int,
        y: int,
    ) -> set[tuple[int, int]]:
        """
        Return every logical grid cell occupied by a node.

        x/y represent the top-left cell.

        A node with width=3 and height=2 at (-2, 3)
        occupies:

            (-2, 3) (-1, 3) (0, 3)
            (-2, 2) (-1, 2) (0, 2)
        """

        return {
            (x + dx, y - dy)
            for dx in range(node.width)
            for dy in range(node.height)
        }

    def _node_layer(
        self,
        node: LayoutNode,
        x: int,
        y: int,
    ) -> int:
        """
        Return the minimum onion layer touched by the node footprint.
        """

        cells = self._occupied_cells(
            node=node,
            x=x,
            y=y,
        )

        return min(
            self._cell_layer(
                cell_x,
                cell_y,
            )
            for cell_x, cell_y in cells
        )

    def _cell_layer(
        self,
        x: int,
        y: int,
    ) -> int:
        """
        Return the rectangular onion layer containing a grid cell.

        Layer dimensions are calculated from the configured core
        dimensions and target aspect ratio.

        The first layer is the configured core.
        Each subsequent layer grows outward.
        """

        for layer in range(1, 1001):

            width = self._layer_width(layer)
            height = self._layer_height(layer)

            if self._cell_is_inside_layer(
                x=x,
                y=y,
                width=width,
                height=height,
            ):
                return layer

        raise RuntimeError(
            f"Grid coordinate ({x}, {y}) exceeds the "
            "supported layout layer range"
        )

    def _cell_is_inside_layer(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> bool:
        """
        Return True when a cell lies inside a layer rectangle.

        The rectangle is centred as evenly as possible around (0, 0).

        For an even dimension, the extra cell is consistently placed
        on the positive side.
        """

        min_x = -(width // 2)
        max_x = min_x + width - 1

        min_y = -(height // 2)
        max_y = min_y + height - 1

        return (
            min_x <= x <= max_x
            and min_y <= y <= max_y
        )

    def _layer_width(
        self,
        layer: int,
    ) -> int:
        """
        Return the width of the specified layer.

        The default target ratio is 4:3.

        Examples:

            Layer 1: 4
            Layer 2: 9
            Layer 3: 15
            Layer 4: 20
            Layer 5: 25
        """

        height = self._layer_height(layer)

        return self._round_half_up(
            self.target_aspect_ratio * height
        )

    def _layer_height(
        self,
        layer: int,
    ) -> int:
        """
        Return the height of the specified layer.

        With the default configuration:

            Layer 1: 3
            Layer 2: 7
            Layer 3: 11
            Layer 4: 15
            Layer 5: 19
        """

        return (
            self.core_height
            + (layer - 1)
            * self.layer_height_expansion
        )

    @staticmethod
    def _round_half_up(
        value: float,
    ) -> int:
        """
        Round a positive value using conventional mathematical
        half-up rounding.
        """

        return int(value + 0.5)

    def _max_layer(
        self,
        positions: dict[str, NodePosition],
    ) -> int:
        """
        Return the highest layer currently represented.
        """

        if not positions:
            return 1

        return max(
            position.layout_layer
            for position in positions.values()
        )
