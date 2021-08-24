"""Storage filter module."""
import typing as t

from fw_utils import (
    ExpressionFilter,
    Filter,
    Filters,
    SizeFilter,
    StringFilter,
    TimeFilter,
)

__all__ = ["create_filter", "DirFilter", "Filters"]


FACTORY = {
    "path": StringFilter,
    "size": SizeFilter,
    "created": TimeFilter,
    "modified": TimeFilter,
}


def create_filter(
    include: Filters = None,
    exclude: Filters = None,
    factory: t.Optional[t.Dict[str, t.Type[ExpressionFilter]]] = None,
) -> Filter:
    """Create storage filter and optionally extend common factory."""
    factory_ = FACTORY.copy()
    factory_.update(factory or {})
    return Filter(factory_, include=include, exclude=exclude)


class DirFilter(StringFilter):
    """Local storage directory filter."""

    def match(self, value: t.Union[str, t.Any]) -> bool:
        """Match str with the filter's regex pattern."""
        if not isinstance(value, str):
            value = getattr(value, self.key, getattr(value, "path"))
        return super().match(value)
