import typer
from rich import print
from tag.model import TransitionModel
from tag import __version__

app = typer.Typer(
    help="Transition Architecture Generator"
)


@app.command()
def analyse(file: str):

    model = TransitionModel()

    print(f"[green]TAG[/green] version {__version__}")
    print()

    print(f"Input file : {file}")
    print()

    print(f"Pages       : {model.page_count()}")
    print(f"Nodes       : {model.node_count()}")
    print(f"Connections : {model.connection_count()}")


@app.command()
def version():
    print(__version__)
