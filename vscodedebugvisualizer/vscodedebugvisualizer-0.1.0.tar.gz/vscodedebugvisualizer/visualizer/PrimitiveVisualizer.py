import json


class PrimitiveVisualizer:
    def checkType(self, t):
        return isinstance(t, str) or isinstance(t, int) or isinstance(t, float) or isinstance(t, dict)

    def visualize(self, text):
        value = str(text)
        d = {
            "kind": {"text": True},
            "text": value,
        }
        return json.dumps(d)
