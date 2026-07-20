from tag.layout.graph_builder import LayoutGraphBuilder, LayoutGraph

from tag.transition_model import (
    TransitionModel,
    TransitionNode,
    TransitionInterface,
    InterfaceDirection,
    TransferType,
    InterfaceKey,
)


def test_duplicate_interfaces():

    graph = LayoutGraph()

    graph.add_edge("A", "B")
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")

    assert graph.edge_count == 1
    assert graph.nodes["A"].neighbours == {"B"}
    assert graph.nodes["B"].neighbours == {"A"}
    print(graph)


def test_graph_builder():

    model = TransitionModel()

    #
    # Nodes
    #

    model.nodes["A"] = TransitionNode(
        id="A",
        name="A",
    )

    model.nodes["B"] = TransitionNode(
        id="B",
        name="B",
    )

    model.nodes["C"] = TransitionNode(
        id="C",
        name="C",
    )

    #
    # Interfaces
    #

    interface = TransitionInterface(
        id="IF-A-B",
        source="A",
        target="B",
        direction=InterfaceDirection.ONE_WAY,
        transfer_type=TransferType.AUTOMATED,
    )

    key = InterfaceKey(
        source="A",
        target="B",
        direction=InterfaceDirection.ONE_WAY,
        transfer_type=TransferType.AUTOMATED,
    )

    model.interfaces[key] = interface

    #
    # Build graph
    #

    graph = LayoutGraphBuilder.build(model)

    #
    # Verify nodes
    #

    assert graph.node_count == 3

    assert "A" in graph.nodes
    assert "B" in graph.nodes
    assert "C" in graph.nodes

    #
    # Verify edge
    #

    assert graph.edge_count == 1

    assert graph.nodes["A"].neighbours == {"B"}
    assert graph.nodes["B"].neighbours == {"A"}
    assert graph.nodes["C"].neighbours == set()
    print(model)
    print(graph)


test_duplicate_interfaces()
test_graph_builder()
