from dataclasses import dataclass, field


@dataclass(slots=True)
class DrawioCell:
    id: str
    value: str = ""
    style: str = ""

    vertex: bool = False
    edge: bool = False

    source: str | None = None
    target: str | None = None

    parent: str | None = None

    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


@dataclass(slots=True)
class DrawioPage:
    id: str
    name: str

    cells: list[DrawioCell] = field(default_factory=list)


@dataclass(slots=True)
class DrawioDocument:
    pages: list[DrawioPage] = field(default_factory=list)

    @property
    def page_count(self):
        return len(self.pages)

    @property
    def cell_count(self):
        return sum(len(p.cells) for p in self.pages)
