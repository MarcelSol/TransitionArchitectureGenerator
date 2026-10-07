import typer
from rich import print

from tag import __version__
from tag.transition_model import TransitionModel, InterfaceDirection, TransferType
from tag.excel_exporter import ExcelExporter
from tag.catalog import CatalogWriter
from tag.pipeline import Pipeline
from tag.validation import Validator
from tag.validation_report import ValidationSeverity
from tag.layout.graph_builder import LayoutGraphBuilder
from tag.layout.graph_peeler import GraphPeeler
from tag.layout.placer import LayoutPlacer
from tag.drawio_writer import DrawioWriter
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

    transition = Pipeline.load(file)

    graph = LayoutGraphBuilder.build(
        transition
    )

    GraphPeeler.peel(
        graph
    )

    placer = LayoutPlacer()

    positions = placer.place(
        graph
    )

    print()
    print("Transition Model")
    print("----------------")

    print(
        f"Nodes       : {len(transition.nodes)}"
    )

    print(
        f"Interfaces  : {len(transition.interfaces)}"
    )

    print()

    print(
        f"Input file  : {file}"
    )

    print()

    print(
        f"Milestones  : {len(transition.milestones)}"
    )

    print()

    print(graph.dump())

    print()
    print("Node Placement")
    print("==============")

    for node_id in sorted(
        positions,
        key=lambda node_id:
            graph.nodes[node_id].name.lower(),
    ):

        node = graph.nodes[node_id]
        position = positions[node_id]

        print(
            f"{node.name}"
            f"    Complexity : {node.complexity}"
            f"    Layer : {position.layout_layer}"
            f"    x={position.x:.1f}"
            f"    y={position.y:.1f}"
        )

@app.command()
def generate(
    file: str,
    output: str | None = None,
):
    """
    Generate an optimized Draw.io architecture from an input file.

    The input may be either a .drawio or .xlsx file.
    """

    print(f"[green]TAG[/green] version {__version__}")
    print()

    input_path = Path(file)

    if output is None:
        output = str(
            input_path.with_suffix(".optimized.drawio")
        )

    print(
        f"Input file  : {input_path}"
    )

    print(
        f"Output file : {output}"
    )

    print()

    # -------------------------------------------------------------
    # Load the transition model.
    # -------------------------------------------------------------

    transition = Pipeline.load(
        str(input_path)
    )

    # -------------------------------------------------------------
    # Build the semantic layout graph.
    # -------------------------------------------------------------

    graph = LayoutGraphBuilder.build(
        transition
    )

    # -------------------------------------------------------------
    # Calculate graph complexity.
    # -------------------------------------------------------------

    GraphPeeler.peel(
        graph
    )

    # -------------------------------------------------------------
    # Calculate node positions.
    # -------------------------------------------------------------

    placer = LayoutPlacer()

    positions = placer.place(
        graph
    )

    # -------------------------------------------------------------
    # Generate the Draw.io document.
    # -------------------------------------------------------------

    DrawioWriter.write(
        model=transition,
        graph=graph,
        positions=positions,
        filename=output,
    )

    print(
        f"Generated {len(transition.nodes)} nodes "
        f"and {len(transition.interfaces)} interfaces."
    )

    print()

    print(
        f"[green]Draw.io file written to:[/green] {output}"
    )

@app.command()
def version():
    print(__version__)
