import os.path

import typer
from jinja2 import FileSystemLoader

from ..asyncio import coro
from .env import Env
from .scheme import Field, Scheme, Type


@coro
async def generate(name: str, output: str):
    root_path = os.path.realpath(os.path.join(__file__, os.path.pardir, "templates"))
    env = Env(loader=FileSystemLoader(root_path))
    s = Scheme(name=name, fields=[Field(name="id", type=Type.int)])
    await s.generate(env, os.path.join(output, name, "models"))


if __name__ == "__main__":
    typer.run(generate)
