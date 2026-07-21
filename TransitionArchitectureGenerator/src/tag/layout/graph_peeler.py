"""
Determine node complexity by recursively peeling the layout graph.
"""

from tag.layout.graph import LayoutGraph


class GraphPeeler:
    """
    Determine the complexity of every node in a LayoutGraph.

    Complexity 1 consists of the leaves of the graph.

    Complexity 2 consists of the nodes that only become removable after all
    complexity-1 nodes have disappeared.

    Higher complexities are determined in the same way.

    Within each complexity level, peel_round records the order in which the
    node was removed.
    """

    @staticmethod
    def peel(graph: LayoutGraph) -> None:
        """
        Analyse the graph.

        The graph topology itself is never modified. Instead, a set of
        remaining node ids is maintained while repeatedly recomputing the
        effective degree of every remaining node.
        """

        #
        # Reset previous analysis.
        #
        for node in graph.nodes.values():
            node.complexity = None
            node.peel_round = None

        #
        # Nodes still participating in the current graph.
        #
        remaining = set(graph.nodes.keys())

        complexity = 1
        peel_round = 0

        #
        # Continue until every node has been assigned a complexity.
        #
        while remaining:

            #
            # Continue peeling nodes belonging to the current complexity.
            #
            while True:

                #
                # Determine the current degree of every remaining node.
                #
                degree = GraphPeeler._compute_degrees(
                    graph,
                    remaining,
                )

                #
                # Nothing left?
                #
                if not degree:
                    break

                minimum_degree = min(degree.values())

                #
                # This complexity has finished.
                #
                if minimum_degree > complexity:
                    break

                #
                # Peel every node having the current minimum degree.
                #
                peel = sorted(
                    node_id
                    for node_id, node_degree in degree.items()
                    if node_degree == minimum_degree
                )

                #
                # Record the result.
                #
                for node_id in peel:

                    node = graph.nodes[node_id]

                    node.complexity = complexity
                    node.peel_round = peel_round

                #
                # Remove the peeled nodes.
                #
                remaining.difference_update(peel)

                peel_round += 1

            #
            # Proceed to the next shell.
            #
            complexity += 1
            peel_round = 0

    @staticmethod
    def _compute_degrees(
        graph: LayoutGraph,
        remaining: set[str],
    ) -> dict[str, int]:
        """
        Determine the effective degree of every remaining node.

        Implemented in Part 2.
        """
        raise NotImplementedError

    @staticmethod
    def _compute_degrees(
        graph: LayoutGraph,
        remaining: set[str],
    ) -> dict[str, int]:
        """
        Determine the effective degree of every remaining node.

        The degree of a node is defined as the maximum number of remaining
        neighbours that are simultaneously visible on any single milestone.
        """

        return {
            node_id: GraphPeeler._current_degree(
                graph.nodes[node_id],
                remaining,
            )
            for node_id in remaining
        }

    @staticmethod
    def _current_degree(
        node,
        remaining: set[str],
    ) -> int:
        """
        Determine the current degree of a single node.

        For every milestone we count the remaining neighbours visible on that
        milestone. The node degree is the maximum of those counts.
        """

        max_degree = 0

        for neighbours in node.page_neighbours.values():

            degree = 0

            for neighbour in neighbours:

                if neighbour in remaining:
                    degree += 1

            if degree > max_degree:
                max_degree = degree

        return max_degree

