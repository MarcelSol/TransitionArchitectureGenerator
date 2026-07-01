from tag.transition_model import (
    TransitionModel,
    InterfaceDirection,
    TransferType,
)


class CatalogWriter:

    @staticmethod
    def print(model: TransitionModel):

        CatalogWriter.print_nodes(model)

        print()

        CatalogWriter.print_interfaces(model)

    @staticmethod
    def print_nodes(model: TransitionModel):

        print()
        print("Node Catalog")
        print("============")
        print()

        for node in sorted(
            model.nodes.values(),
            key=lambda n: n.name.lower()
        ):

            pages = ", ".join(
                sorted(node.visible_on)
            )

            print(f"{node.name:<40} {pages}")

    @staticmethod
    def _node_lookup(model):

        return {
            node.id: node
            for node in model.nodes.values()
        }
    @staticmethod
    def print_interfaces(model: TransitionModel):
        print()
        print("Interface Catalog")
        print("=================")
        print()

        node_lookup = CatalogWriter._node_lookup(model)
        
        for interface in sorted(
            model.interfaces.values(),
            key=lambda i: (
                node_lookup[i.source].name,
                node_lookup[i.target].name,
            )
        ):
            pages = ", ".join(sorted(interface.visible_on))

            direction = (
                "<->"
                if interface.direction == InterfaceDirection.TWO_WAY
                else "->"
            )

            transfer = (
                "Manual"
                if interface.transfer_type == TransferType.MANUAL
                else "Automatic"
            )

            source = node_lookup[interface.source].name
            target = node_lookup[interface.target].name

            print(
                f"{source:<40} "
                f"{direction:^5} "
                f"{target:<40} "
                f"{transfer:<10} "
                f"{pages}"
            )

