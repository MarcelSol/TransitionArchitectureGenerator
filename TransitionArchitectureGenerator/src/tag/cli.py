import typer
from tag.importer import DrawioImporter
from rich import print
from tag.model import TransitionModel
from tag import __version__

app = typer.Typer(
    help="Transition Architecture Generator"
)


@app.command()
def analyse(file: str):
    importer = DrawioImporter(file)

    tree = importer.load()
        
    root = tree.getroot()
        
    print()
    
    diagram_count = len(root.findall("diagram"))

    print()
    print(f"Pages : {diagram_count}")

@app.command()
def version():
    print(__version__)
