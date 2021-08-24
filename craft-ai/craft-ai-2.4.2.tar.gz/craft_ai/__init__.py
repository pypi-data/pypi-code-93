__version__ = "2.4.2"

from . import errors
from .client import Client
from .interpreter import Interpreter
from .time import Time
from .formatters import format_property, format_decision_rules
from .reducer import reduce_decision_rules
from .tree_utils import (
    extract_decision_paths_from_tree,
    extract_decision_path_neighbors,
    extract_output_tree,
)
import nest_asyncio

# this is to patch asyncio to allow a nested asyncio loop
# nested asyncio loop allow the client to use websocket call inside jupyter
# and other webbrowser based IDE
nest_asyncio.apply()

# Defining what will be imported when doing `from craft_ai import *`

__all__ = [
    "Client",
    "errors",
    "Interpreter",
    "Time",
    "format_property",
    "format_decision_rules",
    "reduce_decision_rules",
    "extract_output_tree",
    "extract_decision_paths_from_tree",
    "extract_decision_path_neighbors",
]
