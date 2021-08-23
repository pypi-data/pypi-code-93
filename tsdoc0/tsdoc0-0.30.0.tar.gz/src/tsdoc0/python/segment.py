from dataclasses import dataclass
from textx.model import get_model
from typing import cast
from typing import Optional


class Segment:
    @dataclass
    class LineCol:
        line: int
        col: int

    @property
    def linecol(self) -> Optional[LineCol]:
        model = get_model(self)

        if not hasattr(model, "_tx_parser"):
            return None

        tx_parser = model._tx_parser

        # Silence the error about a missing attribute because it already exists inside
        # of all textX model classes
        tx_position = self._tx_position  # type: ignore[attr-defined]

        return Segment.LineCol(*tx_parser.pos_to_linecol(tx_position))

    @property
    def line(self) -> Optional[int]:
        if (linecol := self.linecol) is None:
            return None

        return linecol.line

    @property
    def col(self) -> Optional[int]:
        if (linecol := self.linecol) is None:
            return None

        return linecol.col

    @property
    def filename(self) -> Optional[str]:
        model = get_model(self)

        if not hasattr(model, "_tx_filename"):
            return None

        return cast(str, model._tx_filename)
