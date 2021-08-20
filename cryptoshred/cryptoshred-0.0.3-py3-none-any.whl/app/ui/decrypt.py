import typer
from rich.console import Console
from pathlib import Path

from cryptoshred.app.business.decrypt import (
    from_dict_in_file,
    from_json_string,
    from_list_in_file,
)


app = typer.Typer()
console = Console()


@app.command()
def file(ctx: typer.Context, path: Path) -> None:
    """
    Will take a file containing valid json and replace any cryptocontainer
    it can find within that file with the value of that container.
    Be aware that this can take quite some time for long fact streams or deeply
    nested structures as the decryptor has to check every entry in the structure.
    """
    res = from_dict_in_file(path=path, key_backend=ctx.obj["key_backend"])
    console.print(res)


@app.command()
def list(ctx: typer.Context, path: Path) -> None:
    """
    Takes a file containing a list of cryptocontainers and will decrypt them.
    """
    res = from_list_in_file(path=path, key_backend=ctx.obj["key_backend"])
    console.print(res)


@app.command()
def container(ctx: typer.Context, input: str) -> None:
    """
    Takes a cryptocontainer as string and will decrypt it.
    """
    console.print(from_json_string(input, ctx.obj["key_backend"]))
