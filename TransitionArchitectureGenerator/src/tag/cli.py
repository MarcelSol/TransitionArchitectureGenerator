import typer
from rich import print

from tag import __version__
from tag.model import TransitionModel
from tag.reader import DrawioReader
from tag.classifier import CellClassifier

app = typer.Typer(
    help="Transition Architecture Generator"
)


@app.command()
def analyse(file: str):

    print(f"[green]TAG[/green] version {__version__}")
    print()

    reader = DrawioReader(file)

    document = reader.read()

    print(f"Input file : {file}")
    print()

    print(f"Pages      : {document.page_count}")
    print(f"Cells      : {document.cell_count}")

    print(f"Nodes      : {len(document.nodes)}")
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
