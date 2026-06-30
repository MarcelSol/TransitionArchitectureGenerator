import typer
from tag.reader import DrawioReader
from rich import print
from tag.model import TransitionModel
from tag import __version__

app = typer.Typer(
    help="Transition Architecture Generator"
)


@app.command()
def analyse(file: str):
    reader = DrawioReader(file)

    tree = reader.load()
        
    root = tree.getroot()
        
    print()
    
    diagram_count = len(root.findall("diagram"))

    print()
    print(f"Pages : {diagram_count}")
    for diagram in root.findall("diagram"):
        print(
            f"Name: {diagram.get('name')}, "
            f"ID: {diagram.get('id')}"
    )

@app.command()
def version():
    print(__version__)
