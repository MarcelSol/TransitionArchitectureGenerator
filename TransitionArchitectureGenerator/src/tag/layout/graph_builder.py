"""
Builds a layout graph from a TransitionModel.
"""

from tag.transition_model import TransitionModel

from .graph import LayoutGraph


class LayoutGraphBuilder:

    @staticmethod
    def build(
        model: TransitionModel,
    ) -> LayoutGraph:

        graph = LayoutGraph()

        #
        # Add every semantic node.
        #
        for node in model.nodes.values():

            graph.add_node(
                node.id,
                node.name,
            )

        #
        # Build the union graph.
        #
        for interface in model.interfaces.values():

            graph.add_edge(
                interface.source,
                interface.target,
            )

        #
        # Build the neighbours for every individual milestone.
        #
        for milestone in model.milestones:

            #
            # Temporary neighbour sets for this milestone.
            #
            page_neighbours = {
                node_id: set()
                for node_id in graph.nodes.keys()
            }

            #
            # Collect every visible interface.
            #
            for interface in model.interfaces.values():

                if milestone not in interface.visible_on:
                    continue

                page_neighbours[interface.source].add(
                    interface.target
                )

                page_neighbours[interface.target].add(
                    interface.source
                )

            #
            # Store the page neighbours.
            #
            for node_id, neighbours in page_neighbours.items():

                graph.nodes[node_id].page_neighbours[
                    milestone
                ] = frozenset(neighbours)

        return graph
