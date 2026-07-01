import typer
from rich import print

from tag import __version__
from tag.transition_model import TransitionModel, InterfaceDirection, TransferType
from tag.reader import DrawioReader
from tag.classifier import CellClassifier
from tag.builder import TransitionModelBuilder
from tag.catalog import CatalogWriter
from tag.pipeline import Pipeline

app = typer.Typer(
    help="Transition Architecture Generator"
)

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
