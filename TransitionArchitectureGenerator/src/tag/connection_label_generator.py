from dataclasses import dataclass

from tag.config import load_config
from tag.transition_model import TransitionInterface, TransitionModel


@dataclass(frozen=True, slots=True)
class ConnectionPriority:
    value: str
    code: str


class ConnectionLabelGenerator:
    """
    Generate connection labels based on the semantic categories
    of the source and target nodes.

    Node category is semantic information.
    Visual properties such as colour are not used here.
    """

    def __init__(self) -> None:

        settings = load_config()

        configuration = settings.get(
            "connection_labels",
            {},
        )

        classification = configuration.get(
            "node_classification",
            {},
        )

        self.attribute = classification.get(
            "attribute",
            "category",
        )

        self.priority = [
            ConnectionPriority(
                value=str(item["value"]),
                code=str(item["code"]),
            )
            for item in classification.get(
                "priority",
                [],
            )
        ]

        sequence = configuration.get(
            "sequence",
            {},
        )

        self.sequence_width = int(
            sequence.get(
                "width",
                3,
            )
        )

        self.sequence_start = int(
            sequence.get(
                "start",
                1,
            )
        )

        self._validate_configuration()

    def generate(
        self,
        model: TransitionModel,
    ) -> None:
        """
        Generate labels for interfaces that do not already have one.

        Existing labels are preserved.
        """

        reserved_labels = {
            interface.label.strip()
            for interface in model.interfaces.values()
            if interface.label
            and interface.label.strip()
        }

        next_sequence = self.sequence_start

        for interface in model.interfaces.values():

            if interface.label is not None:
                if interface.label.strip():
                    continue

            prefix = self._connection_prefix(
                interface,
                model,
            )

            label = self._next_available_label(
                prefix=prefix,
                reserved_labels=reserved_labels,
                next_sequence=next_sequence,
            )

            interface.label = label

            reserved_labels.add(label)

            next_sequence = self._next_sequence(
                label=label,
                current_sequence=next_sequence,
            )

    def _connection_prefix(
        self,
        interface: TransitionInterface,
        model: TransitionModel,
    ) -> str:

        source = model.nodes.get(
            interface.source
        )

        target = model.nodes.get(
            interface.target
        )

        if source is None:
            raise ValueError(
                f"Interface '{interface.id}' references "
                f"unknown source node '{interface.source}'"
            )

        if target is None:
            raise ValueError(
                f"Interface '{interface.id}' references "
                f"unknown target node '{interface.target}'"
            )

        source_value = self._node_classification(
            source
        )

        target_value = self._node_classification(
            target
        )

        source_priority = self._priority_index(
            source_value
        )

        target_priority = self._priority_index(
            target_value
        )

        if (
            source_priority is None
            and target_priority is None
        ):
            raise ValueError(
                f"Neither endpoint of interface "
                f"'{interface.id}' has a configured "
                f"connection classification: "
                f"'{source_value}' / '{target_value}'"
            )

        if source_priority is None:
            return self.priority[
                target_priority
            ].code

        if target_priority is None:
            return self.priority[
                source_priority
            ].code

        if source_priority <= target_priority:
            return self.priority[
                source_priority
            ].code

        return self.priority[
            target_priority
        ].code

    def _node_classification(
        self,
        node,
    ) -> str:

        attribute_value = getattr(
            node,
            self.attribute,
            None,
        )

        if attribute_value is None:
            raise ValueError(
                f"Node has no attribute "
                f"'{self.attribute}'"
            )

        if hasattr(
            attribute_value,
            "value",
        ):
            return str(
                attribute_value.value
            )

        return str(
            attribute_value
        )

    def _priority_index(
        self,
        value: str,
    ) -> int | None:

        value = value.strip().lower()

        for index, priority in enumerate(
            self.priority
        ):
            if (
                priority.value.strip().lower()
                == value
            ):
                return index

        return None

    def _next_available_label(
        self,
        prefix: str,
        reserved_labels: set[str],
        next_sequence: int,
    ) -> str:

        sequence = next_sequence

        while True:

            label = (
                f"{prefix}"
                f"{sequence:0{self.sequence_width}d}"
            )

            if label not in reserved_labels:
                return label

            sequence += 1

    def _next_sequence(
        self,
        label: str,
        current_sequence: int,
    ) -> int:

        suffix = label[
            -self.sequence_width:
        ]

        if (
            len(suffix) == self.sequence_width
            and suffix.isdigit()
        ):
            number = int(suffix)

            if number >= current_sequence:
                return number + 1

        return current_sequence + 1

    def _validate_configuration(
        self,
    ) -> None:

        if not self.priority:
            raise ValueError(
                "connection_labels.node_classification.priority "
                "must contain at least one entry"
            )

        if self.sequence_width < 1:
            raise ValueError(
                "connection_labels.sequence.width "
                "must be at least 1"
            )

        if self.sequence_start < 0:
            raise ValueError(
                "connection_labels.sequence.start "
                "must be zero or greater"
            )

        values = [
            item.value.strip().lower()
            for item in self.priority
        ]

        if len(values) != len(set(values)):
            raise ValueError(
                "connection_labels.node_classification.priority "
                "contains duplicate values"
            )

        codes = [
            item.code.strip()
            for item in self.priority
        ]

        if len(codes) != len(set(codes)):
            raise ValueError(
                "connection_labels.node_classification.priority "
                "contains duplicate codes"
            )
