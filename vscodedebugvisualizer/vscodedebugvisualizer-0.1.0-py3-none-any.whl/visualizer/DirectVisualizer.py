import json


class DirectVisualizer:
    def checkType(self, obj):
        return isinstance(obj, dict) and "kind" in obj

    def visualize(self, d):
        return json.dumps(d)
