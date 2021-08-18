import os.path
from pathlib import Path
from typing import Any, Optional

from jinja2 import BaseLoader, Environment


class Env(Environment):
    def __init__(
        self,
        loader: Optional[BaseLoader],
        trim_blocks: bool = True,
        lstrip_blocks: bool = True,
        enable_async: bool = True,
        keep_trailing_newline: bool = True,
    ) -> None:
        super().__init__(
            trim_blocks=trim_blocks,
            lstrip_blocks=lstrip_blocks,
            keep_trailing_newline=keep_trailing_newline,
            autoescape=False,
            loader=loader,
            enable_async=enable_async,
        )

    async def save(self, name: str, output: str, **kwargs: Any):
        Path(os.path.dirname(output)).mkdir(parents=True, exist_ok=True)
        template = self.get_template(name)
        text = await template.render_async(**kwargs)  # type: ignore
        with open(output, "w") as f:
            f.write(text)
