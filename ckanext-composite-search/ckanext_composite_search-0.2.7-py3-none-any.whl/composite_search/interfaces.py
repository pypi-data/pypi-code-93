from __future__ import annotations
from typing import Any
import ckan.plugins as plugins

from .utils import SearchParam

class ICompositeSearch(plugins.Interface):
    def before_composite_search(
        self, search_params: dict[str, Any], params: list[SearchParam]
    ) -> tuple[dict[str, Any], list[SearchParam]]:

        return search_params, params
