import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from cryptoshred.app.business.map import from_list_in_file


app = typer.Typer()
console = Console()


@app.command()
def list(
    ctx: typer.Context,
    input: Path = typer.Argument(
        ..., help="The file containing the list of crytpocontainers."
    ),
    out: Optional[Path] = typer.Option(
        None, help="The output file. Defaults to stdout."
    ),
) -> None:
    """
    This function generates a mapping between subject IDs ans the PII found
    in a given list of crytpocontainers for that PII. This is usefull if for example
    you need to find the ``sid`` given the PII in a deletion request.
    It will return a json object. See :ref:`Mapping FAQ<faq/map:Map Subject ID to PII>` for
    more info.
    """
    res = from_list_in_file(input, ctx.obj["key_backend"])
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
    else:
        console.print(json.dumps(res, indent=2))
