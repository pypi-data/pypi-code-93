"""
Datetime formatter for AppInspect report formatter
"""

# Python Standard Libraries
import json

# Third-Party Libraries
import datetime

# Custom Libraries
# N/A


class DateTimeEncoder(json.JSONEncoder):
    """A custom JSON encoder created to fix serialization issues."""

    def default(self, obj):  # pylint: disable=E0202,W0221
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)
