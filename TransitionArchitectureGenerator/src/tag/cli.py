import typer
from rich import print

from tag import __version__
from tag.model import TransitionModel
from tag.reader import DrawioReader

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

    print(f"Pages       : {document.page_count}")
    print(f"Cells       : {document.cell_count}")

    for page in document.pages:
        print(f"  {page.name}")


@app.command()
def version():
    print(__version__)
