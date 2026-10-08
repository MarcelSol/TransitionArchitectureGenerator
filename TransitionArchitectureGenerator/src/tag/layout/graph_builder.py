"""
Builds a layout graph from a TransitionModel.
"""

import math

from tag.transition_model import TransitionModel

from .graph import LayoutGraph


class LayoutGraphBuilder:

    #
    # These values must match the corresponding rendering
    # dimensions used by DrawioWriter.
    #
    GRID_SIZE = 200.0
    CHILD_PADDING = 20.0
    CHILD_HEADER_HEIGHT = 30.0

    @staticmethod
    def build(
        model: TransitionModel,
    ) -> LayoutGraph:
        """
        Build a LayoutGraph from a transition model.
        """

        graph = LayoutGraph()

        #
        # Add every semantic node.
        #
        for node in model.nodes.values():

            width, height = (
                LayoutGraphBuilder._node_footprint(node)
            )

            graph.add_node(
                node.id,
                node.name,
            )

            graph.nodes[node.id].category = (
                node.category.value
            )

            graph.nodes[node.id].width = width
            graph.nodes[node.id].height = height

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

                page_neighbours[
                    interface.source
                ].add(
                    interface.target
                )

                page_neighbours[
                    interface.target
                ].add(
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

    @staticmethod
    def _node_footprint(
        node,
    ) -> tuple[int, int]:
        """
        Return the logical grid footprint of a model node.

        Ordinary nodes occupy one grid cell.

        Composite nodes derive their footprint from the actual
        physical bounding box of their children, including the
        container padding and header.
        """

        if not node.children:
            return 1, 1

        #
        # Determine the physical bounding box of the children.
        #
        min_x = min(
            child.x
            for child in node.children
        )

        min_y = min(
            child.y
            for child in node.children
        )

        max_x = max(
            child.x + child.width
            for child in node.children
        )

        max_y = max(
            child.y + child.height
            for child in node.children
        )

        #
        # Apply the same offsets used by DrawioWriter.
        #
        offset_x = (
            LayoutGraphBuilder.CHILD_PADDING
            - min_x
        )

        offset_y = (
            LayoutGraphBuilder.CHILD_HEADER_HEIGHT
            + LayoutGraphBuilder.CHILD_PADDING
            - min_y
        )

        #
        # Calculate the physical container dimensions.
        #
        physical_width = (
            max_x
            + offset_x
            + LayoutGraphBuilder.CHILD_PADDING
        )

        physical_height = (
            max_y
            + offset_y
            + LayoutGraphBuilder.CHILD_PADDING
        )

        #
        # Convert physical dimensions into logical grid cells.
        #
        logical_width = max(
            1,
            math.ceil(
                physical_width
                / LayoutGraphBuilder.GRID_SIZE
            ),
        )

        logical_height = max(
            1,
            math.ceil(
                physical_height
                / LayoutGraphBuilder.GRID_SIZE
            ),
        )

        return logical_width, logical_height
