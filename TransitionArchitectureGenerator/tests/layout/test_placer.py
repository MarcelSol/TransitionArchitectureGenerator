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
            neighbours={"A", "B", "D"},
            complexity=4,
        ),
        "D": LayoutNode(
            id="D",
            name="D",
            neighbours={"C"},
            complexity=3,
        ),
        "E": LayoutNode(
            id="E",
            name="E",
            neighbours={"C"},
            complexity=2,
        ),
    }
    )

    placer = LayoutPlacer()
    positions = placer.place(graph)

    assert set(positions) == {"A", "B", "C", "D", "E"}
    
    assert positions["A"].layout_layer == 1
    assert positions["B"].layout_layer == 1
    assert positions["C"].layout_layer == 1
    assert positions["D"].layout_layer == 1
    assert positions["E"].layout_layer == 1

    print("PASS: core nodes were placed")

    for node_id, position in positions.items():
        print(
            f"{node_id}: "
            f"x={position.x:.1f}, "
            f"y={position.y:.1f}, "
            f"layer={position.layout_layer}"
        )


if __name__ == "__main__":
    test_places_nodes_by_complexity()
