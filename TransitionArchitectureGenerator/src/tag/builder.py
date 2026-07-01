from tag.drawio import DrawioDocument
from tag.transition_model import (
    TransitionModel,
    TransitionNode,
    TransitionInterface,
    InterfaceDirection,
    TransferType,
)


class TransitionModelBuilder:

    def build(
        self,
        document: DrawioDocument,
    ) -> TransitionModel:

        model = TransitionModel()

        for page in document.pages:

            #
            # Nodes
            #

            for cell in page.cells:

                if not cell.vertex:
                    continue

                node = TransitionNode(
                    id=cell.id,
                    name=cell.value,

                    width=cell.width,
                    height=cell.height,
                )

                node.visible_on.add(page.name)

                model.nodes.append(node)

            #
            # Interfaces
            #

            for cell in page.cells:

                if not cell.edge:
                    continue

                interface = TransitionInterface(
                    id=cell.id,

                    source=cell.source or "",

                    target=cell.target or "",

                    direction=InterfaceDirection.ONE_WAY,

                    transfer_type=TransferType.AUTOMATED,
                )

                interface.visible_on.add(page.name)

                model.interfaces.append(interface)

        return model
