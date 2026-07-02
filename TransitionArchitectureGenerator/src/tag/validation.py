from tag.transition_model import TransitionModel
from tag.transition_model import NodeCategory
from tag.validation_report import ValidationSeverity
from tag.builder import TransitionModelBuilder

from tag.validation_report import (
    ValidationReport,
)


class Validator:

    @staticmethod
    def validate(
        model: TransitionModel,
    ) -> ValidationReport:

        report = ValidationReport()

        #
        # Validation rules
        #

        Validator._validate_node_categories(
            model,
            report,
        )

        Validator._validate_orphan_nodes(
            model,
            report,
        )

        #
        # More validation rules will be added here.
        #

        return report

    # -----------------------------------------------------------------

    @staticmethod
    def _validate_orphan_nodes(
        model: TransitionModel,
        report: ValidationReport,
    ) -> None:

        connected = set()

        for interface in model.interfaces.values():

            connected.add(interface.source)
            connected.add(interface.target)

        for node in model.nodes.values():

            if node.id not in connected:

                report.add(
                    severity=ValidationSeverity.WARNING,
                    rule="V108",
                    object_id=node.id,
                    object_name=node.name,
                    page=TransitionModelBuilder._first_visible(
                        node.visible_on,
                        model.milestones,
                    ),
                    message="Node has no interfaces.",
                )

    # -----------------------------------------------------------------

    @staticmethod
    def _validate_node_categories(
        model: TransitionModel,
        report: ValidationReport,
    ) -> None:

        for node in model.nodes.values():

            if node.category == NodeCategory.UNKNOWN:

                report.add(
                    severity=ValidationSeverity.WARNING,
                        rule="V101",
                        object_id=node.id,
                        object_name=node.name,
                        page=TransitionModelBuilder._first_visible(
                            node.visible_on,
                            model.milestones,
                        ),
                        message="Unknown node category.",
                    )
