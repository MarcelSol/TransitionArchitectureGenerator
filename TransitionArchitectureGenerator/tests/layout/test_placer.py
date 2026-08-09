from tag.layout.graph import LayoutGraph, LayoutNode
from tag.layout.placer import LayoutPlacer


def test_places_nodes_by_complexity():

    graph = LayoutGraph(
    nodes={
        "A": LayoutNode(
            id="A",
            name="A",
            neighbours={"B", "C"},
            complexity=4,
        ),
        "B": LayoutNode(
            id="B",
            name="B",
            neighbours={"A", "C"},
            complexity=4,
        ),
        "C": LayoutNode(
            id="C",
            name="C",
            neighbours={"A", "B"},
            complexity=4,
        ),
        "D": LayoutNode(
            id="D",
            name="D",
            neighbours={"A"},
            complexity=3,
        ),
        "E": LayoutNode(
            id="E",
            name="E",
            neighbours={"B"},
            complexity=3,
        ),
        "F": LayoutNode(
            id="F",
            name="F",
            neighbours={"C"},
            complexity=3,
        ),
    }
    )

    placer = LayoutPlacer(
        grid_size=100.0,
        node_spacing=150.0,
    )


    positions = placer.place(graph)

    assert set(positions) == {
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
    }

    assert positions["A"].layout_layer == 1
    assert positions["B"].layout_layer == 1
    assert positions["C"].layout_layer == 1
    assert positions["D"].layout_layer >= 1
    assert positions["E"].layout_layer >= 1
    assert positions["F"].layout_layer >= 1

    for node_id in ("D", "E", "F"):
        assert positions[node_id].layout_layer >= 1

    print("PASS: core nodes were placed in onion layers")

    for node_id, position in positions.items():
        print(
            f"{node_id}: "
            f"x={position.x:.1f}, "
            f"y={position.y:.1f}, "
            f"layer={position.layout_layer}"
        )


if __name__ == "__main__":
    test_places_nodes_by_complexity()
