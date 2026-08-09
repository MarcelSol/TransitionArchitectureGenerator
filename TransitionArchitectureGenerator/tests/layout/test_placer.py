from tag.layout.graph import LayoutGraph, LayoutNode
from tag.layout.placer import LayoutPlacer


def test_places_core_nodes():
    graph = LayoutGraph(
        nodes={
            "A": LayoutNode(
                id="A",
                name="A",
                neighbours={"B"},
                complexity=3,
            ),
            "B": LayoutNode(
                id="B",
                name="B",
                neighbours={"A"},
                complexity=3,
            ),
            "C": LayoutNode(
                id="C",
                name="C",
                neighbours={"A"},
                complexity=2,
            ),
        }
    )

    print("Restuld")
    print( graph)
    placer = LayoutPlacer()
    positions = placer.place(graph)

    assert set(positions) == {"A", "B"}
    assert positions["A"].layout_layer == 1
    assert positions["B"].layout_layer == 1

    print("PASS: core nodes were placed")

    for node_id, position in positions.items():
        print(
            f"{node_id}: "
            f"x={position.x:.1f}, "
            f"y={position.y:.1f}, "
            f"layer={position.layout_layer}"
        )


test_places_core_nodes()
