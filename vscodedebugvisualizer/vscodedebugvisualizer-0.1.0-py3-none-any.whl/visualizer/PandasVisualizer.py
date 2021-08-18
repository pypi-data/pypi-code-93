from vscodedebugvisualizer.visualizer.PlotlyVisualizer import PlotlyVisualizer


class PandasVisualizer(PlotlyVisualizer):
    def checkType(self, t):
        try:
            import pandas
        except ImportError:
            return False
        return isinstance(t, pandas.DataFrame)

    def visualize(self, df):
        from pandas.io import json

        tableDict = {"rows": []}
        for _, row in df.iterrows():
            tableDict["rows"].append(dict(row))

        tableDict["kind"] = {"table": True}
        return json.dumps(tableDict)
