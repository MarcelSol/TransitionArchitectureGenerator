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
            graph.add_node(node.id)

        #
        # Add every interface.
        #
        for interface in model.interfaces.values():

            graph.add_edge(
                interface.source,
                interface.target,
            )

        return graph
