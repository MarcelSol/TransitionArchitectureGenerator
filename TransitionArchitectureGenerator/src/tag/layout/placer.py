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

    layout_layer is the minimum onion layer touched by the node's
    complete footprint.
    """

    x: int
    y: int
    layout_layer: int


class LayoutPlacer:
    """
    Place nodes on an integer rectangular onion grid.

    The most complex nodes are placed first in the centre.
    Lower-complexity nodes are placed progressively outward.

    Connectivity determines the preferred position within the
    permitted area. Complexity determines the minimum permitted
    onion layer.
    """

    def __init__(
        self,
        grid_size: float = 200.0,
        node_spacing: float = 80.0,
    ) -> None:
        # Kept for compatibility with the existing CLI and callers.
        #
        # These values are no longer used to determine the logical
        # position. Rendering to Draw.io coordinates is a later step.
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
                        f"with minimum layout layer {minimum_layer}"
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
        The search then examines progressively larger Manhattan
        distances around that location.

        A candidate is valid only if:
        - the complete node footprint is unoccupied
        - the footprint's minimum layer is >= minimum_layer
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

        search_radius = max(
            2,
            self._max_layer(positions)
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
                    node,
                    x,
                    y,
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

        The primary objective is to keep connected nodes close together.

        The next objective is to use the innermost permitted layer.

        The final terms make placement deterministic.
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
            node,
            x,
            y,
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
            node,
            x,
            y,
        )

        for other_id, position in positions.items():

            other_node = graph.nodes[other_id]

            other_occupied = self._occupied_cells(
                other_node,
                position.x,
                position.y,
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
        Return every grid cell occupied by a node.

        x/y represent the top-left cell.

        Therefore a node with width=3 and height=2 at (-2, 3)
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

        A composite node may therefore span several layers.

        For example, if one part of a node touches layer 3 and another
        part touches layer 5, the node's layout layer is 3.
        """

        cells = self._occupied_cells(
            node,
            x,
            y,
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
        Return the rectangular onion layer containing one grid cell.

        The central cell (0, 0) is layer 1.

        Each additional layer expands the rectangle by one cell
        on every side.
        """

        return max(
            abs(x),
            abs(y),
        ) + 1

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
