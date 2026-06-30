from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NodeGroup(Enum):
    UNKNOWN = "unknown"
    GREEN = "green"
    WHITE = "white"
    RED = "red"
    GOLD = "gold"


@dataclass(slots=True)
class Geometry:
    x: float
    y: float
    width: float
    height: float


@dataclass(slots=True)
class Node:
    id: str
    name: str

    geometry: Optional[Geometry] = None

    fill_color: str = ""
    line_color: str = ""

    group: NodeGroup = NodeGroup.UNKNOWN

    style: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Connection:
    id: str

    source: str
    target: str

    label: str = ""

    style: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Page:
    id: str
    name: str

    nodes: list[Node] = field(default_factory=list)

    connections: list[Connection] = field(default_factory=list)


@dataclass(slots=True)
class TransitionModel:
    pages: list[Page] = field(default_factory=list)

    def page_count(self) -> int:
        return len(self.pages)

    def node_count(self) -> int:

        return sum(
            len(page.nodes)
            for page in self.pages
        )

    def connection_count(self) -> int:

        return sum(
            len(page.connections)
            for page in self.pages
        )
