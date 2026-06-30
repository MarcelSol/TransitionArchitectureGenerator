from pathlib import Path
from lxml import etree

from tag.logger import logger


class DrawioImporter:
    """
    Imports a draw.io document.

    This class understands the draw.io XML format and converts it into
    the internal TransitionModel.

    At this stage (Commit 3) it only counts objects.
    """

    def __init__(self, filename: str):

        self.filename = Path(filename)

        self.tree = None

    def load(self):

        logger.info("Reading %s", self.filename)

        self.tree = etree.parse(str(self.filename))

        return self.tree
