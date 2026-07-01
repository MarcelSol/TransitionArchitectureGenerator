from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class InterfaceDirection(Enum):
    ONE_WAY = "one_way"
    TWO_WAY = "two_way"


class TransferType(Enum):
    AUTOMATED = "automated"
    MANUAL = "manual"


@dataclass(slots=True)
class TransitionNode:
    id: str
    name: str

    width: float
    height: float

    visible_on: set[str] = field(default_factory=set)


@dataclass(slots=True)
class TransitionInterface:
    id: str

    source: str
    target: str

    direction: InterfaceDirection

    transfer_type: TransferType

    visible_on: set[str] = field(default_factory=set)


@dataclass(slots=True)
class TransitionModel:

    nodes: dict[str, TransitionNode] = field(default_factory=dict)

    interfaces: list[TransitionInterface] = field(default_factory=list)
