import json

import plotly


class PlotlyVisualizer:
    def checkType(self, t):
        return isinstance(t, plotly.graph_objs._figure.Figure)

    def visualize(self, figure):
        figureDict = json.loads(figure.to_json())
        figureDict["kind"] = {"plotly": True}

        # let the client decide, about the template, if its not specified within the data itself
        del figureDict["layout"]["template"]
        return json.dumps(figureDict)
