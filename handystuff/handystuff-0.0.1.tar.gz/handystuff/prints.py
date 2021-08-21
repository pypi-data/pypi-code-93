from typing import Dict, Any
from handystuff.loaders import json


#
# try:
#     import click
# except ImportError:
#     raise ImportError("Install handystuff with prints options: \n\n pip install handystuff[prints]")
#
#
# def highlight(text, colors: Dict[str, str]):
#     result = []
#     for t in text.split():
#         if t in colors.keys():
#             result.append(click.style(t, fg=colors[t]))
#         else:
#             result.append(t)
#     return " ".join(result)


def format_dict(config: Dict[str, Any]) -> str:
    """Formats the config in a more-or-less readable way.

    Args:
      config: Dict[str:
      Any]:

    Returns:

    """
    return json.dumps(config, indent=4)
