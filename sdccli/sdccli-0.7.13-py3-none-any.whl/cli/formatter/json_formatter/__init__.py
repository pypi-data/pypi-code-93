import json


class JsonFormatter:
    def format(self, response, format_type):
        print(json.dumps(response, indent=4, default=str))
