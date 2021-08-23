"""Cay: Simple Calculator implementation."""

from . import main


def cli():
    """Run CLI REPL."""
    while True:
        print("cay> ", end="")
        try:
            main.cay_print(main.eval(main.read(input())))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    cli()
