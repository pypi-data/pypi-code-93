"""Utility functions for gitlabclient
"""
from typing import Any

import json

from .typing import JSON


def pretty_print_json(decorated_func):
    """Decorate a function which returns some JSON data to pretty-print it to stdout

    JSON needs to be python data structures, not serialised strings

    Examples:
      @pretty_print_json
      def function() -> JSON:
          return {"data1": 1, "data2": 2}

      will pretty print the returned dictionary and the pass the returned value to the consumer of function(), to
      continue the control flow of the original code
    """
    def json_pretty_printer(*args, **kwargs) -> Any:
        result = decorated_func(*args, **kwargs)
        ppjson(result)
        return result

    return json_pretty_printer

def ppjson(result: JSON, file=None):
    """pretty-print result using print()
    """
    print(json.dumps(result, indent=2), file=file)
