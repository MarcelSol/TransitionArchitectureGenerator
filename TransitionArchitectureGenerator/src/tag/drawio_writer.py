from pathlib import Path
from xml.etree import ElementTree as ET

from tag.drawio import (
    DrawioDocument,
    DrawioPage,
    DrawioCell,
)
from tag.layout.graph import LayoutGraph
from tag.layout.placer import NodePosition
from tag.config import load_config
from tag.transition_model import (
    InterfaceDirection,
    TransferType,
    TransitionModel,
    TransitionNode,
)


class DrawioWriter:

    PAGE_ID = "TAG_COMPLETE_ARCHITECTURE"
    PAGE_NAME = "Complete Architecture"

    ROOT_ID = "0"
    LAYER_ID = "1"

    GRID_SIZE = 200.0

    CHILD_PADDING = 20.0
    CHILD_HEADER_HEIGHT = 24.0

    # -----------------------------------------------------------------

    @staticmethod
    def write(
        model: TransitionModel,
        graph: LayoutGraph,
        positions: dict[str, NodePosition],
        filename: str,
    ):

        DrawioWriter._validate_inputs(
            model,
            graph,
            positions,
        )

        config = load_config()

        document = DrawioWriter._build_document(
            model,
            graph,
            positions,
            config,
        )

        DrawioWriter._write_xml(
            document,
            filename,
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _validate_inputs(
        model: TransitionModel,
        graph: LayoutGraph,
        positions: dict[str, NodePosition],
    ):

        for node_id in graph.nodes:

            if node_id not in positions:
                raise ValueError(
                    f"No position found for graph node '{node_id}'."
                )

        for node_id in model.nodes:

            if node_id not in graph.nodes:
                raise ValueError(
                    f"Model node '{node_id}' is missing "
                    "from the layout graph."
                )

        for interface in model.interfaces.values():

            if interface.source not in graph.nodes:
                raise ValueError(
                    f"Interface '{interface.id}' references "
                    f"unknown source '{interface.source}'."
                )

            if interface.target not in graph.nodes:
                raise ValueError(
                    f"Interface '{interface.id}' references "
                    f"unknown target '{interface.target}'."
                )

    # -----------------------------------------------------------------

    @staticmethod
    def _build_document(
        model: TransitionModel,
        graph: LayoutGraph,
        positions: dict[str, NodePosition],
        config: dict | None = None,
    ) -> DrawioDocument:

        if config is None:
            config = load_config()

        document = DrawioDocument()

        # The complete architecture is deliberately independent of the
        # milestone lifecycle rules and is always the first page.
        document.pages.append(
            DrawioWriter._build_page(
                model=model,
                graph=graph,
                positions=positions,
                page_id=DrawioWriter.PAGE_ID,
                page_name=DrawioWriter.PAGE_NAME,
                config=config,
                milestone=None,
                milestone_index=None,
            )
        )

        # Add one page per milestone, preserving the input order.
        for index, milestone in enumerate(model.milestones):
            document.pages.append(
                DrawioWriter._build_page(
                    model=model,
                    graph=graph,
                    positions=positions,
                    page_id=f"TAG_MILESTONE_{index + 1:03d}",
                    page_name=milestone,
                    config=config,
                    milestone=milestone,
                    milestone_index=index,
                )
            )

        return document

    # -----------------------------------------------------------------

    @staticmethod
    def _build_page(
        model: TransitionModel,
        graph: LayoutGraph,
        positions: dict[str, NodePosition],
        page_id: str,
        page_name: str,
        config: dict,
        milestone: str | None,
        milestone_index: int | None,
    ) -> DrawioPage:

        page = DrawioPage(
            id=page_id,
            name=page_name,
        )

        page.cells.append(
            DrawioCell(
                id=DrawioWriter.ROOT_ID,
            )
        )

        page.cells.append(
            DrawioCell(
                id=DrawioWriter.LAYER_ID,
                parent=DrawioWriter.ROOT_ID,
            )
        )

        is_complete_page = milestone is None
        default_border = DrawioWriter._default_border(config)
        visible_node_ids = set()

        for node in model.nodes.values():
            if is_complete_page:
                visible_node_ids.add(node.id)
                continue

            if milestone in node.visible_on:
                visible_node_ids.add(node.id)
                continue

            # A composite container must remain visible whenever one or
            # more of its children are visible on this milestone.
            if node.children and any(
                milestone in child.visible_on
                for child in node.children
            ):
                visible_node_ids.add(node.id)

        # -------------------------------------------------------------
        # Nodes and composite children
        # -------------------------------------------------------------

        for node in sorted(
            model.nodes.values(),
            key=lambda item: item.name.lower(),
        ):
            if node.id not in visible_node_ids:
                continue

            position = positions[node.id]
            node_border = default_border

            if not is_complete_page:
                node_border = DrawioWriter._lifecycle_border(
                    visible_on=node.visible_on,
                    milestones=model.milestones,
                    milestone_index=milestone_index,
                    config=config,
                )

            parent_cell = DrawioWriter._build_node_cell(
                node,
                position,
                border_color=node_border,
            )
            page.cells.append(parent_cell)

            if node.children:
                child_offset_x, child_offset_y = (
                    DrawioWriter._child_offsets(node)
                )

                # Keep the original child index in the cell ID on every
                # page. Hidden children therefore do not renumber the rest.
                for index, child in enumerate(node.children):
                    if (
                        not is_complete_page
                        and milestone not in child.visible_on
                    ):
                        continue

                    # Lifecycle highlighting for a composite belongs to
                    # its parent container, not to individual children.
                    child_border = default_border

                    child_cell = DrawioWriter._build_child_cell(
                        node,
                        child,
                        index,
                        child_offset_x,
                        child_offset_y,
                        border_color=child_border,
                    )
                    page.cells.append(child_cell)

        # -------------------------------------------------------------
        # Interfaces
        # -------------------------------------------------------------

        for index, interface in enumerate(
            model.interfaces.values(),
            start=1,
        ):
            if not is_complete_page:
                if milestone not in interface.visible_on:
                    continue

                # Do not emit connectors whose endpoints are hidden on
                # this milestone page.
                if (
                    interface.source not in visible_node_ids
                    or interface.target not in visible_node_ids
                ):
                    continue

            edge_id = (
                f"interface_{index:03d}_"
                f"{interface.id}"
            )
            page.cells.append(
                DrawioWriter._build_interface_cell(
                    interface,
                    edge_id,
                )
            )

        return page

    # -----------------------------------------------------------------

    @staticmethod
    def _default_border(config: dict) -> str:
        milestone_borders = config.get("milestone_borders", {})
        return milestone_borders.get("default", "#000000")

    # -----------------------------------------------------------------

    @staticmethod
    def _lifecycle_border(
        visible_on: set[str],
        milestones: list[str],
        milestone_index: int | None,
        config: dict,
    ) -> str:

        default_border = DrawioWriter._default_border(config)
        if milestone_index is None or not milestones:
            return default_border

        if milestone_index < 0 or milestone_index >= len(milestones):
            return default_border

        current_milestone = milestones[milestone_index]
        if current_milestone not in visible_on:
            return default_border

        borders = config.get("milestone_borders", {})

        # The first milestone cannot have first-appearance highlights.
        if milestone_index > 0:
            previous_milestone = milestones[milestone_index - 1]
            if previous_milestone not in visible_on:
                return borders.get("first_appearance", "#00E600")

        # The last milestone cannot have disappearance highlights.
        if milestone_index < len(milestones) - 1:
            next_milestone = milestones[milestone_index + 1]
            if next_milestone not in visible_on:
                return borders.get("last_appearance", "#FF0000")

        return default_border

    # -----------------------------------------------------------------

    @staticmethod
    def _build_node_cell(
        node: TransitionNode,
        position: NodePosition,
        border_color: str = "#000000",
    ) -> DrawioCell:

        x, y = DrawioWriter._physical_position(
            position
        )

        width = node.width

        height = node.height

        if node.children:

            width, height = (
                DrawioWriter._container_dimensions(
                    node
                )
            )

        else:

            if width <= 0:
                width = 160

            if height <= 0:
                height = 80

        if node.children:

            style = (
                DrawioWriter._container_style(
                    node,
                    border_color,
                )
            )

        else:

            style = (
                DrawioWriter._node_style(
                    node.category.value,
                    node.fill_color,
                    border_color,
                )
            )

        return DrawioCell(
            id=node.id,
            value=node.name,
            style=style,
            vertex=True,
            parent=DrawioWriter.LAYER_ID,
            x=x,
            y=y,
            width=width,
            height=height,
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _build_child_cell(
        parent: TransitionNode,
        child,
        index: int,
        offset_x: float,
        offset_y: float,
        border_color: str = "#000000",
    ) -> DrawioCell:

        child_id = (
            f"{parent.id}"
            f"__child_{index}"
        )

        x = child.x + offset_x
        y = child.y + offset_y

        return DrawioCell(
            id=child_id,
            value=child.name,
            style=DrawioWriter._child_style(
                child.category.value,
                child.fill_color,
                border_color,
            ),
            vertex=True,
            parent=parent.id,
            x=x,
            y=y,
            width=child.width,
            height=child.height,
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _container_dimensions(
        node: TransitionNode,
    ) -> tuple[float, float]:

        if not node.children:

            width = node.width

            height = node.height

            if width <= 0:
                width = 160

            if height <= 0:
                height = 80

            return width, height

        max_x = max(
            child.x + child.width
            for child in node.children
        )

        max_y = max(
            child.y + child.height
            for child in node.children
        )

        min_x = min(
            child.x
            for child in node.children
        )

        min_y = min(
            child.y
            for child in node.children
        )

        offset_x = (
            DrawioWriter.CHILD_PADDING
            - min_x
        )

        offset_y = (
            DrawioWriter.CHILD_HEADER_HEIGHT
            + DrawioWriter.CHILD_PADDING
            - min_y
        )

        width = (
            max_x
            + offset_x
            + DrawioWriter.CHILD_PADDING
        )

        height = (
            max_y
            + offset_y
            + DrawioWriter.CHILD_PADDING
        )

        return width, height

    # -----------------------------------------------------------------

    @staticmethod
    def _child_offsets(
        node: TransitionNode,
    ) -> tuple[float, float]:

        min_x = min(
            child.x
            for child in node.children
        )

        min_y = min(
            child.y
            for child in node.children
        )

        offset_x = (
            DrawioWriter.CHILD_PADDING
            - min_x
        )

        offset_y = (
            DrawioWriter.CHILD_HEADER_HEIGHT
            + DrawioWriter.CHILD_PADDING
            - min_y
        )

        return offset_x, offset_y

    # -----------------------------------------------------------------

    @staticmethod
    def _physical_position(
        position: NodePosition,
    ) -> tuple[float, float]:

        return (
            position.x
            * DrawioWriter.GRID_SIZE,
            position.y
            * DrawioWriter.GRID_SIZE,
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _node_style(
        category: str,
        fill_color: str,
        border_color: str = "#000000",
    ) -> dict[str, str]:

        stroke_width = "4" if border_color.upper() in {"#00E600", "#FF0000"} else "1"

        return {
            "rounded": "0",
            "whiteSpace": "wrap",
            "html": "1",
            "fillColor": fill_color,
            "strokeColor": border_color,
            "strokeWidth": stroke_width,
            "fontColor": "#000000",
            "align": "center",
            "verticalAlign": "middle",
            "fontSize": "12",
        }

    # -----------------------------------------------------------------

    @staticmethod
    def _container_style(
        node: TransitionNode,
        border_color: str = "#000000",
    ) -> dict[str, str]:

        stroke_width = "4" if border_color.upper() in {"#00E600", "#FF0000"} else "1"

        return {
            "shape": "swimlane",
            "horizontal": "1",
            "startSize": str(
                int(
                    DrawioWriter.CHILD_HEADER_HEIGHT
                )
            ),
            "container": "1",
            "collapsible": "0",
            "recursiveResize": "0",
            "html": "1",
            "whiteSpace": "wrap",
            "rounded": "0",
            "fillColor": "#FFFFFF",
            "swimlaneFillColor": "#FFFFFF",
            "strokeColor": border_color,
            "strokeWidth": stroke_width,
            "fontColor": "#000000",
            "fontSize": "12",
            "fontStyle": "1",
            "align": "center",
            "verticalAlign": "middle",
            "spacingLeft": "8",
        }

    # -----------------------------------------------------------------

    @staticmethod
    def _child_style(
        category: str,
        fill_color: str,
        border_color: str = "#000000",
    ) -> dict[str, str]:

        stroke_width = "4" if border_color.upper() in {"#00E600", "#FF0000"} else "1"

        return {
            "rounded": "0",
            "whiteSpace": "wrap",
            "html": "1",
            "fillColor": fill_color,
            "strokeColor": border_color,
            "strokeWidth": stroke_width,
            "fontColor": "#000000",
            "align": "center",
            "verticalAlign": "middle",
            "fontSize": "10",
        }

    # -----------------------------------------------------------------

    @staticmethod
    def _build_interface_cell(
        interface,
        edge_id: str,
    ) -> DrawioCell:

        return DrawioCell(
            id=edge_id,
            value="",
            style=DrawioWriter._interface_style(
                interface.direction,
                interface.transfer_type,
            ),
            edge=True,
            parent=DrawioWriter.LAYER_ID,
            source=interface.source,
            target=interface.target,
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _interface_style(
        direction: InterfaceDirection,
        transfer_type: TransferType,
    ) -> dict[str, str]:

        style = {
            "edgeStyle": "orthogonalEdgeStyle",
            "rounded": "0",
            "orthogonalLoop": "1",
            "jettySize": "auto",
            "html": "1",
            "strokeColor": "#000000",
            "strokeWidth": "1",
            "endArrow": "block",
        }

        if direction == InterfaceDirection.TWO_WAY:

            style["startArrow"] = "block"

        else:

            style["startArrow"] = "none"

        if transfer_type == TransferType.MANUAL:

            style["dashed"] = "1"

        else:

            style["dashed"] = "0"

        return style

    # -----------------------------------------------------------------

    @staticmethod
    def _write_xml(
        document: DrawioDocument,
        filename: str,
    ):

        root = ET.Element(
            "mxfile"
        )

        for page in document.pages:

            diagram = ET.SubElement(
                root,
                "diagram",
                {
                    "id": page.id,
                    "name": page.name,
                },
            )

            graph_model = ET.SubElement(
                diagram,
                "mxGraphModel",
                {
                    "dx": "1422",
                    "dy": "794",
                    "grid": "1",
                    "gridSize": "10",
                    "guides": "1",
                    "tooltips": "1",
                    "connect": "1",
                    "arrows": "1",
                    "fold": "1",
                    "page": "1",
                    "pageScale": "1",
                    "pageWidth": "850",
                    "pageHeight": "1100",
                    "math": "0",
                    "shadow": "0",
                },
            )

            mx_root = ET.SubElement(
                graph_model,
                "root",
            )

            for cell in page.cells:

                attributes = {
                    "id": cell.id,
                }

                if cell.value:
                    attributes["value"] = cell.value

                if cell.style:
                    attributes["style"] = (
                        ";".join(
                            f"{key}={value}"
                            for key, value
                            in cell.style.items()
                        )
                        + ";"
                    )

                if cell.vertex:
                    attributes["vertex"] = "1"

                if cell.edge:
                    attributes["edge"] = "1"

                if cell.parent is not None:
                    attributes["parent"] = cell.parent

                if cell.source is not None:
                    attributes["source"] = cell.source

                if cell.target is not None:
                    attributes["target"] = cell.target

                mx_cell = ET.SubElement(
                    mx_root,
                    "mxCell",
                    attributes,
                )

                if cell.vertex:

                    ET.SubElement(
                        mx_cell,
                        "mxGeometry",
                        {
                            "x": str(cell.x),
                            "y": str(cell.y),
                            "width": str(cell.width),
                            "height": str(cell.height),
                            "as": "geometry",
                        },
                    )

                elif cell.edge:

                    ET.SubElement(
                        mx_cell,
                        "mxGeometry",
                        {
                            "relative": "1",
                            "as": "geometry",
                        },
                    )

        tree = ET.ElementTree(
            root
        )

        ET.indent(
            tree,
            space="  ",
        )

        output_path = Path(
            filename
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        tree.write(
            output_path,
            encoding="utf-8",
            xml_declaration=True,
        )
