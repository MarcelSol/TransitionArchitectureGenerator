"""
excel_exporter.py

Exports a TransitionModel to an Excel workbook.

The workbook contains the complete model data required for a future
Excel -> TransitionModel import, while deliberately excluding layout
and optimization data.
"""

from openpyxl import Workbook
from openpyxl.styles import Font

from tag.builder import TransitionModelBuilder
from tag.transition_model import (
    TransitionModel,
    InterfaceDirection,
    TransferType,
)

from tag.validation import Validator
from tag.validation_report import (
    ValidationReport,
    ValidationSeverity,
)


class ExcelExporter:

    @staticmethod
    def export(
        model: TransitionModel,
        filename: str,
    ) -> None:

        workbook = Workbook()

        report = Validator.validate(
            model
        )

        #
        # Remove the default worksheet created
        # by openpyxl.
        #
        workbook.remove(
            workbook.active
        )

        #
        # Summary is intentionally first because
        # it is the human-readable overview.
        #
        ExcelExporter._write_summary(
            workbook,
            model,
        )

        ExcelExporter._write_milestones(
            workbook,
            model,
        )

        ExcelExporter._write_nodes(
            workbook,
            model,
        )

        ExcelExporter._write_interfaces(
            workbook,
            model,
        )

        ExcelExporter._write_children(
            workbook,
            model,
        )

        ExcelExporter._write_validation_sheet(
            workbook,
            report,
        )

        workbook.save(
            filename
        )

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------

    @staticmethod
    def _write_summary(
        workbook: Workbook,
        model: TransitionModel,
    ) -> None:

        sheet = workbook.create_sheet(
            "Summary"
        )

        #
        # Title
        #
        sheet.append(
            ["Transition Architecture Model"]
        )

        sheet["A1"].font = Font(
            bold=True,
            size=14,
        )

        sheet.append([])

        #
        # General model information
        #
        sheet.append(
            [
                "Model element",
                "Count",
            ]
        )

        ExcelExporter._format_header(
            sheet,
            row=3,
        )

        sheet.append(
            [
                "Milestones",
                len(model.milestones),
            ]
        )

        sheet.append(
            [
                "Nodes",
                len(model.nodes),
            ]
        )

        sheet.append(
            [
                "Interfaces",
                len(model.interfaces),
            ]
        )

        child_count = sum(
            len(node.children)
            for node in model.nodes.values()
        )

        sheet.append(
            [
                "Children",
                child_count,
            ]
        )

        sheet.append([])

        #
        # Milestone summary
        #
        sheet.append(
            [
                "Milestone",
                "Active Nodes",
                "New Nodes",
                "Retired Nodes",
                "Active Interfaces",
                "New Interfaces",
                "Retired Interfaces",
            ]
        )

        milestone_header_row = (
            sheet.max_row
        )

        ExcelExporter._format_header(
            sheet,
            row=milestone_header_row,
        )

        milestones = model.milestones

        for milestone in milestones:

            new_nodes = 0
            retired_nodes = 0
            active_nodes = 0

            for node in model.nodes.values():

                if milestone in node.visible_on:
                    active_nodes += 1

                if (
                    node.first_appears
                    == milestone
                ):
                    new_nodes += 1

                if (
                    node.retired_in
                    == milestone
                ):
                    retired_nodes += 1

            new_interfaces = 0
            retired_interfaces = 0
            active_interfaces = 0

            for interface in model.interfaces.values():

                if milestone in interface.visible_on:
                    active_interfaces += 1

                if (
                    interface.first_appears
                    == milestone
                ):
                    new_interfaces += 1

                if (
                    interface.retired_in
                    == milestone
                ):
                    retired_interfaces += 1

            sheet.append(
                [
                    milestone,
                    active_nodes,
                    new_nodes,
                    retired_nodes,
                    active_interfaces,
                    new_interfaces,
                    retired_interfaces,
                ]
            )

        ExcelExporter._auto_width(
            sheet
        )

    # -----------------------------------------------------------------
    # Milestones
    # -----------------------------------------------------------------

    @staticmethod
    def _write_milestones(
        workbook: Workbook,
        model: TransitionModel,
    ) -> None:

        sheet = workbook.create_sheet(
            "Milestones"
        )

        sheet.append(
            [
                "Order",
                "Milestone",
            ]
        )

        ExcelExporter._format_header(
            sheet
        )

        for order, milestone in enumerate(
            model.milestones,
            start=1,
        ):

            sheet.append(
                [
                    order,
                    milestone,
                ]
            )

        ExcelExporter._auto_width(
            sheet
        )

    # -----------------------------------------------------------------
    # Nodes
    # -----------------------------------------------------------------

    @staticmethod
    def _write_nodes(
        workbook: Workbook,
        model: TransitionModel,
    ) -> None:

        sheet = workbook.create_sheet(
            "Nodes"
        )

        headers = [
            "ID",
            "Name",
            "Category",
            "Width",
            "Height",
            "First Appears",
            "Retired In",
            "Visible On",
        ]

        sheet.append(
            headers
        )

        ExcelExporter._format_header(
            sheet
        )

        for node in sorted(
            model.nodes.values(),
            key=lambda n: (
                n.name.lower(),
                n.id.lower(),
            ),
        ):

            visible_on = (
                ";".join(
                    milestone
                    for milestone
                    in model.milestones
                    if milestone
                    in node.visible_on
                )
            )

            sheet.append(
                [
                    node.id,
                    node.name,
                    node.category.value,
                    node.width,
                    node.height,
                    node.first_appears,
                    node.retired_in,
                    visible_on,
                ]
            )

        ExcelExporter._auto_width(
            sheet
        )

    # -----------------------------------------------------------------
    # Interfaces
    # -----------------------------------------------------------------

    @staticmethod
    def _write_interfaces(
        workbook: Workbook,
        model: TransitionModel,
    ) -> None:

        sheet = workbook.create_sheet(
            "Interfaces"
        )

        headers = [
            "ID",
            "Label",
            "Source",
            "Target",
            "Direction",
            "Transfer Type",
            "First Appears",
            "Retired In",
            "Visible On",
        ]

        sheet.append(
            headers
        )

        ExcelExporter._format_header(
            sheet
        )

        node_lookup = {
            node.id: node
            for node in model.nodes.values()
        }

        def sort_key(interface):

            source = node_lookup.get(
                interface.source
            )

            target = node_lookup.get(
                interface.target
            )

            source_name = (
                source.name.lower()
                if source is not None
                else interface.source.lower()
            )

            target_name = (
                target.name.lower()
                if target is not None
                else interface.target.lower()
            )

            return (
                source_name,
                target_name,
                interface.id.lower(),
            )

        for interface in sorted(
            model.interfaces.values(),
            key=sort_key,
        ):

            visible_on = (
                ";".join(
                    milestone
                    for milestone
                    in model.milestones
                    if milestone
                    in interface.visible_on
                )
            )

            if (
                interface.direction
                == InterfaceDirection.TWO_WAY
            ):
                direction = "Two-way"
            else:
                direction = "One-way"

            if (
                interface.transfer_type
                == TransferType.MANUAL
            ):
                transfer_type = "Manual"
            else:
                transfer_type = "Automatic"

            sheet.append(
                [
                    interface.id,
                    interface.label or "",
                    interface.source,
                    interface.target,
                    direction,
                    transfer_type,
                    interface.first_appears,
                    interface.retired_in,
                    visible_on,
                ]
            )

        ExcelExporter._auto_width(
            sheet
        )

    # -----------------------------------------------------------------
    # Children
    # -----------------------------------------------------------------

    @staticmethod
    def _write_children(
        workbook: Workbook,
        model: TransitionModel,
    ) -> None:

        sheet = workbook.create_sheet(
            "Children"
        )

        headers = [
            "Parent ID",
            "ID",
            "Name",
            "Category",
            "X",
            "Y",
            "Width",
            "Height",
            "Visible On",
        ]

        sheet.append(
            headers
        )

        ExcelExporter._format_header(
            sheet
        )

        nodes = sorted(
            model.nodes.values(),
            key=lambda n: (
                n.name.lower(),
                n.id.lower(),
            ),
        )

        for parent in nodes:

            children = sorted(
                parent.children,
                key=lambda child: (
                    child.name.lower(),
                    child.id.lower(),
                ),
            )

            for child in children:

                visible_on = (
                    ";".join(
                        milestone
                        for milestone
                        in model.milestones
                        if milestone
                        in child.visible_on
                    )
                )

                sheet.append(
                    [
                        parent.id,
                        child.id,
                        child.name,
                        child.category.value,
                        child.x,
                        child.y,
                        child.width,
                        child.height,
                        visible_on,
                    ]
                )

        ExcelExporter._auto_width(
            sheet
        )

    # -----------------------------------------------------------------
    # Formatting
    # -----------------------------------------------------------------

    @staticmethod
    def _format_header(
        sheet,
        row: int = 1,
    ) -> None:

        bold = Font(
            bold=True
        )

        for cell in sheet[row]:
            cell.font = bold

        sheet.freeze_panes = (
            f"A{row + 1}"
        )

    # -----------------------------------------------------------------

    @staticmethod
    def _auto_width(
        sheet,
    ) -> None:

        for column in sheet.columns:

            length = max(
                len(
                    str(cell.value)
                )
                if cell.value is not None
                else 0
                for cell in column
            )

            #
            # Keep very long validation
            # messages from creating enormous
            # columns.
            #
            width = min(
                length + 2,
                80,
            )

            sheet.column_dimensions[
                column[0].column_letter
            ].width = width

    # -----------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------

    @staticmethod
    def _write_validation_sheet(
        workbook: Workbook,
        report: ValidationReport,
    ) -> None:

        sheet = workbook.create_sheet(
            "Validation"
        )

        #
        # Summary
        #

        sheet.append(
            [
                "Metric",
                "Count",
            ]
        )

        ExcelExporter._format_header(
            sheet
        )

        sheet.append(
            [
                "Errors",
                report.error_count,
            ]
        )

        sheet.append(
            [
                "Warnings",
                report.warning_count,
            ]
        )

        sheet.append(
            [
                "Info",
                report.info_count,
            ]
        )

        sheet.append([])

        #
        # Detail header
        #

        headers = [
            "Severity",
            "Rule",
            "Object ID",
            "Object Name",
            "Page",
            "Message",
        ]

        detail_header_row = (
            sheet.max_row + 1
        )

        sheet.append(
            headers
        )

        ExcelExporter._format_header(
            sheet,
            row=detail_header_row,
        )

        #
        # Sort findings:
        #
        # Errors first,
        # warnings second,
        # info last.
        #
        severity_order = {
            ValidationSeverity.ERROR: 0,
            ValidationSeverity.WARNING: 1,
            ValidationSeverity.INFO: 2,
        }

        issues = sorted(
            report.issues,
            key=lambda issue: (
                severity_order[
                    issue.severity
                ],
                issue.rule,
                issue.object_id,
                issue.page,
            ),
        )

        for issue in issues:

            sheet.append(
                [
                    issue.severity.value,
                    issue.rule,
                    issue.object_id,
                    issue.object_name,
                    issue.page,
                    issue.message,
                ]
            )

        ExcelExporter._auto_width(
            sheet
        )
