import math

from tag.drawio import DrawioDocument
from tag.validation_report import ValidationSeverity
from tag.transition_model import (
    TransitionModel,
    TransitionNode,
    TransitionChild,
    TransitionInterface,
    InterfaceDirection,
    TransferType,
    InterfaceKey,
)
from tag.label_normalizer import LabelNormalizer
from tag.color_classifier import ColorClassifier
from tag.identifier_generator import IdentifierGenerator

SNAP_DISTANCE = 10.0

class TransitionModelBuilder:

    @staticmethod
    def _find_container(
        cell: DrawioCell,
        page: DrawioPage,
    ) -> DrawioCell | None:

        lookup = {c.id: c for c in page.cells}
        parent = lookup.get(cell.parent)

        if (
            parent is not None
            and parent.vertex
            and parent.value
        ):
            return parent

        largest = None
        largest_area = -1.0

        for other in page.cells:

            if other.id == cell.id:
                continue

            if not other.vertex:
                continue

            #
            # Groups are only used for positioning.
            #
            if "group" in other.style:
                continue

            if TransitionModelBuilder._distance_to_node(
                cell.x,
                cell.y,
                other,
            ) != 0:
                continue

            if TransitionModelBuilder._distance_to_node(
                cell.x + cell.width,
                cell.y + cell.height,
                other,
            ) != 0:
                continue

            area = other.width * other.height

            if area > largest_area:
                largest = other
                largest_area = area

        return largest

    # -----------------------------------------------------------------

    @staticmethod
    def _attach_interface_labels(
        page: DrawioPage,
    ):

        #
        # Build a lookup by Draw.io id.
        #

        lookup = {
            cell.id: cell
            for cell in page.cells
        }

        #
        # Copy the label text to the parent edge.
        #

        for cell in page.cells:

            if not cell.is_interface_label:
                continue

            edge = lookup.get(cell.parent)

            if edge is None:
                continue

            edge.interface_label = cell.value


    @staticmethod
    def _is_interface_label(
        cell: DrawioCell,
    ) -> bool:

        return (
            cell.vertex
            and "edgeLabel" in cell.style
        )

    # -----------------------------------------------------------------
    @staticmethod
    def _contains(
        parent: TransitionNode,
        child: TransitionNode,
    ) -> bool:

        if parent.id == child.id:
            return False

        if (
            parent.width <= child.width
            or
            parent.height <= child.height
        ):
            return False

        return (
            TransitionModelBuilder._distance_to_node(
                child.x,
                child.y,
                parent,
            ) == 0
            and
            TransitionModelBuilder._distance_to_node(
                child.x + child.width,
                child.y + child.height,
                parent,
            ) == 0
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _distance_to_node(
        x: float,
        y: float,
        node: DrawioCell,
    ) -> float:

        #
        # Find the nearest point on the node rectangle.
        #

        if x < node.x:
            nearest_x = node.x
        elif x > node.x + node.width:
            nearest_x = node.x + node.width
        else:
            nearest_x = x

        if y < node.y:
            nearest_y = node.y
        elif y > node.y + node.height:
            nearest_y = node.y + node.height
        else:
            nearest_y = y

        dx = x - nearest_x
        dy = y - nearest_y

        return math.hypot(dx, dy)

    # -----------------------------------------------------------------

    @staticmethod
    def _find_nearest_node(
        x: float,
        y: float,
        cells: list[DrawioCell],
        drawio_to_tag,
    ) -> tuple[DrawioCell | None, float]:

        nearest_node = None
        nearest_distance = float("inf")

        for node in cells:
            if not node.vertex:
                continue

            #
            # Only consider nodes that actually became TAG nodes.
            #
            if node.id not in drawio_to_tag:
                continue

            distance = (
                TransitionModelBuilder._distance_to_node(
                    x,
                    y,
                    node,
                )
            )

            if distance < nearest_distance:

                nearest_distance = distance
                nearest_node = node

        return nearest_node, nearest_distance

    # -----------------------------------------------------------------

    @staticmethod
    def _compute_lifecycle(
        model: TransitionModel,
    ) -> None:

        milestones = model.milestones

        #
        # Nodes
        #
        for node in model.nodes.values():

            node.first_appears = TransitionModelBuilder._first_visible(
                node.visible_on,
                milestones,
            )

            node.retired_in = TransitionModelBuilder._retired_in(
                node.visible_on,
                milestones,
            )

        #
        # Interfaces
        #
        for interface in model.interfaces.values():

            interface.first_appears = TransitionModelBuilder._first_visible(
                interface.visible_on,
                milestones,
            )

            interface.retired_in = TransitionModelBuilder._retired_in(
                interface.visible_on,
                milestones,
            )

    # ---------------------------------------------------------------------

    @staticmethod
    def _first_visible(
        visible_on: set[str],
        milestones: list[str],
    ) -> str:

        for milestone in milestones:

            if milestone in visible_on:
                return milestone

        return ""

    # ---------------------------------------------------------------------

    @staticmethod
    def _last_visible(
        visible_on: set[str],
        milestones: list[str],
    ) -> str:

        last = ""

        for milestone in milestones:

            if milestone in visible_on:
                last = milestone

        return last


    @staticmethod
    def _retired_in(
        visible_on: set[str],
        milestones: list[str],
    ) -> str:

        seen = False

        for milestone in milestones:

            if milestone in visible_on:
                seen = True

            elif seen:
                return milestone

        return ""


    def build(
        self,
        document: DrawioDocument,
    ) -> TransitionModel:

        model = TransitionModel()
        drawio_to_tag = {}
        child_owner = {}

        for page in document.pages:
            #
            # Add the interface lablel if it exist,
            #
            TransitionModelBuilder._attach_interface_labels(
                page
            )

            #
            # Preserve milestone order.
            #
            model.milestones.append(page.name)


            #
            # Nodes
            #

            for cell in page.cells:
                if not cell.vertex:
                    continue

                #
                # Ignore unnamed vertices.
                #

                name = LabelNormalizer.normalize(cell.value or "")

                if not name:
                    continue

                if cell.is_interface_label:
                    continue

                container = TransitionModelBuilder._find_container(
                    cell,
                    page,
                )

                node_id = IdentifierGenerator.node_id(name)

                drawio_to_tag[cell.id] = node_id

                #
                # Already known?
                #

                if node_id in child_owner:
                    continue

                node = model.nodes.get(node_id)

                if node is not None:
                    node.visible_on.add(page.name)
                    continue

                if container is None:

                    node = TransitionNode(
                        id=node_id,
                        name=name,
                        category=ColorClassifier.classify(cell.style),
                    )

                    model.nodes[node_id] = node

                else:

                    container_id = IdentifierGenerator.node_id(
                        LabelNormalizer.normalize(container.value)
                    )

                    owner = model.nodes.get(container_id)

                    if owner is None:

                        owner = TransitionNode(
                            id=container_id,
                            name=LabelNormalizer.normalize(container.value),
                            category=ColorClassifier.classify(container.style),
                        )

                        model.nodes[container_id] = owner

                    owner.children.append(
                        TransitionChild(
                            id=node_id,
                            name=name,
                            category=ColorClassifier.classify(cell.style),
                            x=cell.x - container.x,
                            y=cell.y - container.y,
                            width=cell.width,
                            height=cell.height,
                        )
                    )

                    child_owner[node_id] = container_id

                    continue

            #
            # Interfaces
            #
            for cell in page.cells:

                if not cell.edge:
                    continue

                #
                # Ignore incomplete interfaces.
                # But report the error.
                #
                source_id = drawio_to_tag.get(cell.source, "")
                target_id = drawio_to_tag.get(cell.target, "")
                source_id = child_owner.get(source_id, source_id)
                target_id = child_owner.get(target_id, target_id)
                incomplete = False

                if not cell.source or cell.source not in drawio_to_tag:

                    source_node, distance = (
                        TransitionModelBuilder._find_nearest_node(
                            cell.source_point.x,
                            cell.source_point.y,
                            page.cells,
                            drawio_to_tag,
                        )
                    )

                    if (
                        source_node is not None
                        and distance <= SNAP_DISTANCE
                    ):

                        source_id = drawio_to_tag[source_node.id]
                        source_id = child_owner.get(source_id, source_id)

                        model.report.add(
                            severity=ValidationSeverity.INFO,
                            rule="V010",
                            object_id=cell.id,
                            object_name="",
                            page=page.name,
                            message=(
                                f"Source snapped to "
                                f"{source_id} "
                                f"({distance:.1f}px)"
                            ),
                        )

                    else:

                        model.report.add(
                            severity=ValidationSeverity.ERROR,
                            rule="V001",
                            object_id=cell.id,
                            object_name="",
                            page=page.name,
                            message="Connector has no source node.",
                        )

                        incomplete = True

                if not cell.target or cell.target not in drawio_to_tag:

                    target_node, distance = (
                        TransitionModelBuilder._find_nearest_node(
                            cell.target_point.x,
                            cell.target_point.y,
                            page.cells,
                            drawio_to_tag,
                        )
                    )

                    if (
                        target_node is not None
                        and distance <= SNAP_DISTANCE
                    ):

                        target_id = drawio_to_tag[target_node.id]
                        target_id = child_owner.get(target_id, target_id)


                        model.report.add(
                            severity=ValidationSeverity.INFO,
                            rule="V011",
                            object_id=cell.id,
                            object_name="",
                            page=page.name,
                            message=(
                                f"target snapped to "
                                f"{target_id} "
                                f"({distance:.1f}px)"
                            ),
                        )

                    else:

                        model.report.add(
                            severity=ValidationSeverity.ERROR,
                            rule="V002",
                            object_id=cell.id,
                            object_name="",
                            page=page.name,
                            message="Connector has no target node.",
                        )

                        incomplete = True

                if incomplete:
                    continue


                #
                # Direction
                #

                if cell.style.get("startArrow", "none") != "none":
                    direction = InterfaceDirection.TWO_WAY
                else:
                    direction = InterfaceDirection.ONE_WAY

                #
                # Transfer type
                #

                if cell.style.get("dashed", "0") == "1":
                    transfer_type = TransferType.MANUAL
                else:
                    transfer_type = TransferType.AUTOMATED

                #
                # Build the key.
                #
                key = InterfaceKey(
                    source=source_id,
                    target=target_id,
                    direction=direction,
                    transfer_type=transfer_type,
                )

                #
                # Existing interface?
                #

                interface = model.interfaces.get(key)

                if interface is None:

                    interface = TransitionInterface(
                        id=IdentifierGenerator.interface_id(
                            source_id,
                            target_id,
                        ),
                        source=source_id,
                        target=target_id,
                        direction=direction,
                        transfer_type=transfer_type,
                        label=cell.interface_label,
                    )

                    model.interfaces[key] = interface

                interface.visible_on.add(page.name)


        TransitionModelBuilder._compute_lifecycle(model)
        return model
