from typing import Any
from flask.json import JSONEncoder as FlaskJSONEncoder


class JSJSONEncoder(FlaskJSONEncoder):

    def default(self, o: Any) -> Any:
        if hasattr(o.__class__, '__is_jsonclass__'):
            return o.tojson()
        return super().default(o)
