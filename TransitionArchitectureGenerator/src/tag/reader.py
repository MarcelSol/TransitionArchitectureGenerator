"""
reader.py

Reads a draw.io document and converts it into the internal
DrawioDocument representation.

The reader is the only component in TAG that understands the
native draw.io XML structure.
"""

from pathlib import Path

from lxml import etree

from tag.drawio import DrawioDocument, DrawioPage, DrawioCell, DrawioPoint
from tag.logger import logger


class DrawioReader:
    """
    Reads a draw.io (.drawio) document.

    At this stage the reader only extracts the pages.
    Later commits will populate each page with DrawioCells.
    """

    def __init__(self, filename: str):

        self.filename = Path(filename)

    def read(self) -> DrawioDocument:

        logger.info("Reading %s", self.filename)

        tree = etree.parse(str(self.filename))
        root = tree.getroot()

        document = DrawioDocument()

        for diagram in root.findall("diagram"):

            page = DrawioPage(
                id=diagram.get("id", ""),
                name=diagram.get("name", "")
            )

            root = diagram[0]

            for cell in root.iter("mxCell"):
            
                drawio_cell = DrawioCell(
                    id=cell.get("id", ""),
                    value=cell.get("value", ""),
                    style=self.parse_style(
                        cell.get("style", "")
                    ),
                    vertex=cell.get("vertex") == "1",
                    edge=cell.get("edge") == "1",
                    source=cell.get("source"),
                    target=cell.get("target"),
                    parent=cell.get("parent")
                )
            
                geometry = cell.find("mxGeometry")
            
                if geometry is not None:
                    drawio_cell.x = float(
                        geometry.get("x", 0)
                    )
            
                    drawio_cell.y = float(
                        geometry.get("y", 0)
                    )
            
                    drawio_cell.width = float(
                        geometry.get("width", 0)
                    )
            
                    drawio_cell.height = float(
                        geometry.get("height", 0)
                    )
            
                    source_point = geometry.find(
                        "mxPoint[@as='sourcePoint']"
                    )

                    if source_point is not None:
                        drawio_cell.source_point = DrawioPoint.from_xml(source_point)

                    target_point = geometry.find(
                        "mxPoint[@as='targetPoint']"
                    )

                    if target_point is not None:
                        drawio_cell.target_point = DrawioPoint.from_xml(target_point)

                page.cells.append(drawio_cell)
            
            document.pages.append(page)

        logger.info(
            "Read %d page(s)",
            document.page_count
        )

        return document

    @staticmethod
    def parse_style(style: str) -> dict[str, str]:

        result = {}

        if not style:
            return result

        for item in style.split(";"):

            if "=" not in item:
                key, value = item, ""
            else:

                key, value = item.split("=", 1)

            result[key] = value

        return result
