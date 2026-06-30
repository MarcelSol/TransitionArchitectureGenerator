import typer
from rich import print

from tag import __version__

app = typer.Typer(
    help="Transition Architecture Generator"
)


@app.command()
def analyse(file: str):
    """
    Analyse a draw.io file.
    """

    print(f"[green]TAG[/green] version {__version__}")
    print(f"Analysing {file}")
    print("")
    print("Parser not implemented yet.")


@app.command()
def version():
    print(__version__)
