"""
reader.py

Reads a draw.io document and converts it into the internal
DrawioDocument representation.

The reader is the only component in TAG that understands the
native draw.io XML structure.
"""

from pathlib import Path

from lxml import etree

from tag.drawio import DrawioDocument, DrawioPage
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

            document.pages.append(page)

        logger.info(
            "Read %d page(s)",
            document.page_count
        )

        return document
