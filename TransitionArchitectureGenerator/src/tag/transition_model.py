from __future__ import annotations

from tag.validation_report import ValidationReport
from dataclasses import dataclass, field
from enum import Enum


class NodeCategory(Enum):
    UNKNOWN = "Unknown"
    EXTERNAL = "External"
    INTEGRATION = "Integration"
    TRANSACTIONAL = "Transactional"
    MASTER_DATA = "Master Data"

class InterfaceDirection(Enum):
    ONE_WAY = "one_way"
    TWO_WAY = "two_way"


class TransferType(Enum):
    AUTOMATED = "automated"
    MANUAL = "manual"

@dataclass(frozen=True, slots=True)
class InterfaceKey:
    source: str
    target: str

    direction: InterfaceDirection
    transfer_type: TransferType

@dataclass(slots=True)
class TransitionChild:

    id: str

    name: str

    category: NodeCategory

    x: float        # relative to container

    y: float

    width: float

    height: float

    visible_on: set[str] = field(default_factory=set)

@dataclass(slots=True)
class TransitionNode:

    id: str

    name: str

    category: NodeCategory = NodeCategory.UNKNOWN

    width: float = 0.0
    height: float = 0.0

    visible_on: set[str] = field(default_factory=set)

    first_appears: str = ""

    retired_in: str = ""

    children: list[TransitionChild] = field(default_factory=list)

@dataclass(slots=True)
class TransitionInterface:
    id: str

    source: str
    target: str

    direction: InterfaceDirection

    transfer_type: TransferType

    visible_on: set[str] = field(default_factory=set)

    first_appears: str = ""

    retired_in: str = ""

    label: str | None = None

@dataclass(slots=True)
class TransitionModel:

    #
    # Ordered list of milestones (Draw.io pages).
    # The order is significant and is preserved from the input file.
    #
    milestones: list[str] = field(default_factory=list)

    nodes: dict[str, TransitionNode] = field(default_factory=dict)

    interfaces: dict[
        InterfaceKey,
        TransitionInterface
    ] = field(default_factory=dict)

    report: ValidationReport = field(
        default_factory=ValidationReport
    )
