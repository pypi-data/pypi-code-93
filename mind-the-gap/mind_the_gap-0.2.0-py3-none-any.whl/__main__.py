import typer

from tfl.cli import cycles

app = typer.Typer()
app.add_typer(cycles.app, name="cycles")

if __name__ == "__main__":
    app()
