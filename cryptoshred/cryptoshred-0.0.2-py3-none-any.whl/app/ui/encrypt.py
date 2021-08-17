from typing import Optional
from uuid import UUID
import typer
from rich.console import Console
from cryptoshred.app.business.encrypt import encrypt_value
from cryptoshred.exceptions import KeyNotFoundException


app = typer.Typer()
console = Console()


@app.command()
def value(
    ctx: typer.Context,
    sid: Optional[UUID] = typer.Option(
        None, help="The id of the subject to use for encryption."
    ),
    value: str = typer.Argument(..., help="The value to encrypt"),
) -> None:
    """
    Takes a value and returns the cryptocontainer representing that value.
    If you provide a subject id it will use the key for that subject id if it exists
    or error out otherwise. If you do not provide an ID a new one will be created.
    """
    try:
        cc = encrypt_value(value=value, sid=sid, key_backend=ctx.obj["key_backend"])
    except KeyNotFoundException:
        console.print(
            "Could not find key for provided ID please enter a valid ID or no id at all if you want to generate one.",
            style="red",
        )
        raise typer.Abort()

    console.print(cc.json())
