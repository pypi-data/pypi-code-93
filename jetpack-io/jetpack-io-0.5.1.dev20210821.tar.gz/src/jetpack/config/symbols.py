import json
from typing import Dict, Optional


class ModuleNotFoundError(Exception):
    pass


class SymbolMapCache:
    def __init__(self):
        self.cache = None

    def __call__(self) -> Dict[str, str]:
        if not self.cache:
            with open("/var/run/config/jetpack.io/symbol-to-container.json") as f:
                self.cache = json.loads(f.read())
        return self.cache

    def find_image_for_module(self, module: str) -> Optional[str]:
        symbol_map = self()
        if module not in symbol_map:
            raise ModuleNotFoundError("Image for module not fount")
        return symbol_map[module]


_symbol_map_cache = SymbolMapCache()
find_image_for_module = _symbol_map_cache.find_image_for_module
