from tag.drawio import DrawioDocument
from tag.transition_model import (
    TransitionModel,
    TransitionNode,
    TransitionInterface,
    InterfaceDirection,
    TransferType,
    InterfaceKey,
)
from tag.label_normalizer import LabelNormalizer
from tag.color_classifier import ColorClassifier
from tag.identifier_generator import IdentifierGenerator

class TransitionModelBuilder:


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

        for page in document.pages:
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

                node_id = IdentifierGenerator.node_id(name)
                drawio_to_tag[cell.id] = node_id

                #
                # Existing node?
                #

                node = model.nodes.get(node_id)

                if node is None:

                    node = TransitionNode(
                        id=node_id,
                        name=name,

                        category=ColorClassifier.classify(cell.style),

                        width=cell.width,
                        height=cell.height,
                    )

                    model.nodes[node_id] = node

                #
                # Remember that this node exists on this page.
                #

                node.visible_on.add(page.name)

            #
            # Interfaces
            #

            for cell in page.cells:

                if not cell.edge:
                    continue

                #
                # Ignore incomplete interfaces.
                #

                if (
                    not cell.source
                    or not cell.target
                    or cell.source not in drawio_to_tag
                    or cell.target not in drawio_to_tag
                ):
                    continue


                source_id = drawio_to_tag[cell.source]
                target_id = drawio_to_tag[cell.target]

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
                    )

                    model.interfaces[key] = interface

                interface.visible_on.add(page.name)


        TransitionModelBuilder._compute_lifecycle(model)
        return model
