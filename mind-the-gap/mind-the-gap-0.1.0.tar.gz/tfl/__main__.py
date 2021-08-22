import typer

app = typer.Typer(add_completion=False)


@app.command()
def hello(name: str):
    print(f"Hello {name}")


if __name__ == "__main__":
    app()
