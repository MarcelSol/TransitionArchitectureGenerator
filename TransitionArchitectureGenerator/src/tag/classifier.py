from tag.drawio import DrawioCell


class CellClassifier:

    @staticmethod
    def is_node(cell: DrawioCell) -> bool:
        return cell.vertex

    @staticmethod
    def is_interface(cell: DrawioCell) -> bool:
        return cell.edge

    @staticmethod
    def is_group(cell: DrawioCell) -> bool:

        return (
            cell.style.get("group", "0") == "1"
            or cell.style.get("container", "0") == "1"
        )
