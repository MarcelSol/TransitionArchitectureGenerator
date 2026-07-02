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
from pathlib import Path

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

app = typer.Typer(
    help="Transition Architecture Generator"
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
    builder = TransitionModelBuilder()
    transition = builder.build(document)

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
