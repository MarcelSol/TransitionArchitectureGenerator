from tag.drawio import DrawioDocument
from tag.transition_model import (
    TransitionModel,
    TransitionNode,
    TransitionInterface,
    InterfaceDirection,
    TransferType,
)
from tag.label_normalizer import LabelNormalizer


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

                #
                # Ignore unnamed vertices.
                #

                name = LabelNormalizer.normalize(cell.value or "")

                if not name:
                    continue

                if cell.value and cell.value != name:
                    print(f'"{cell.value}"')
                    print(" -> ")
                    print(f'"{name}"')
                    print()

                #
                # Existing node?
                #

                node = model.nodes.get(name)

                if node is None:

                    node = TransitionNode(
                        id=cell.id,
                        name=name,

                        width=cell.width,
                        height=cell.height,
                    )

                    model.nodes[name] = node

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
