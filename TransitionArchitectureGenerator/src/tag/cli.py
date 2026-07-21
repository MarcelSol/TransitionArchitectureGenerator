import typer
from rich import print

from tag import __version__
from tag.transition_model import TransitionModel, InterfaceDirection, TransferType
from tag.reader import DrawioReader
from tag.excel_exporter import ExcelExporter
from tag.classifier import CellClassifier
from tag.builder import TransitionModelBuilder
from tag.catalog import CatalogWriter
from tag.pipeline import Pipeline
from tag.validation import Validator
from tag.validation_report import ValidationSeverity
from tag.layout.graph_builder import LayoutGraphBuilder
from pathlib import Path

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

app = typer.Typer(
    help="Transition Architecture Generator"
)

@app.command()
def validate(input: str):

    print(f"[green]TAG[/green] version {__version__}")
    print()

    model = Pipeline.load(input)

    report = Validator.validate(model)

    if report.error_count == 0 and report.warning_count == 0:

        print("Validation passed.")
        return

    print()

    print("Errors")

    for issue in report.issues:

        if issue.severity != ValidationSeverity.ERROR:
            continue

        print(
            f"{issue.rule:<6}"
            f"{issue.object_id:<50}"
            f"{issue.page:<35}"
            f"{issue.message}"
        )

    print()

    print("Warnings")

    for issue in report.issues:

        if issue.severity != ValidationSeverity.WARNING:
            continue

        print(
            f"{issue.rule:<6}"
            f"{issue.object_id:<50}"
            f"{issue.page:<35}"
            f"{issue.message}"
        )

    print()

    print("Info")

    for issue in report.issues:

        if issue.severity != ValidationSeverity.INFO:
            continue

        print(
            f"{issue.rule:<6}"
            f"{issue.object_id:<50}"
            f"{issue.page:<35}"
            f"{issue.message}"
        )

    print()

    print(
        f"{report.error_count} error(s), "
        f"{report.warning_count} warning(s), "
        f"{report.info_count} info(s)"
    )

@app.command()
def export(input: str):
    """
    Export the transition model to an Excel workbook.
    """

    print(f"[green]TAG[/green] version {__version__}")
    print()

    model = Pipeline.load(input)

    input_path = Path(input)

    #
    # The output directory is a sister directory of the input directory.
    #
    output_dir = input_path.parent.parent / OUTPUT_FOLDER

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = output_dir / (
        input_path.stem + ".xlsx"
    )

    ExcelExporter.export(
        model,
        str(output_file),
    )

    print()
    print(f"Workbook written to {output_file}")

@app.command()
def catalog(file: str):

    print(f"[green]TAG[/green] version {__version__}")
    print()

    model = Pipeline.load(file)

    CatalogWriter.print(model)

@app.command()
def analyze(file: str):

    print(f"[green]TAG[/green] version {__version__}")
    print()

    reader = DrawioReader(file)

    document = reader.read()

    transition = Pipeline.load(file)
    graph = LayoutGraphBuilder.build(transition)

    print()
    print("Transition Model")
    print("----------------")

    print(f"Nodes       : {len(transition.nodes)}")
    print(f"Interfaces  : {len(transition.interfaces)}")    

    print()
    print(f"Nodes      : {len(document.nodes)}")

    print(f"Input file : {file}")
    print()

    print(f"Pages      : {document.page_count}")
    print(f"Cells      : {document.cell_count}")
    print(f"Interfaces : {len(document.interfaces)}")

    print()
    print(graph.dump())

    for page in document.pages:
        nodes = sum(
            CellClassifier.is_node(cell)
            for cell in page.cells
        )

        interfaces = sum(
            CellClassifier.is_interface(cell)
            for cell in page.cells
        )

        groups = sum(
            CellClassifier.is_group(cell)
            for cell in page.cells
        )

        print()

        print(page.name)

        print(f"Nodes       : {nodes}")
        print(f"Interfaces  : {interfaces}")
        print(f"Groups      : {groups}")


@app.command()
def version():
    print(__version__)
