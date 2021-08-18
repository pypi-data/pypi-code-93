import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from vscodedebugvisualizer.visualizer.PlotlyVisualizer import PlotlyVisualizer


class NumpyVisualizer(PlotlyVisualizer):
    def __init__(self) -> None:
        self.transposed = False
        super().__init__()

    def checkType(self, t):

        return isinstance(t, np.ndarray)

    def selectAndTailorData(self, data: np.ndarray):
        maxLength = 1000
        maxChannels = 100
        shape = data.shape
        numDim = len(shape)

        # only last 2 dimensions
        if numDim > 2:
            data = data[-2]
            shape = data.shape

        self.transposed = False
        # select longest dimension as X
        if numDim == 2:
            if shape[0] > shape[1]:
                self.transposed = True
                data = data.transpose()
                shape = data.shape
        else:
            # create a second dimension
            data = data.reshape(1, -1)
            shape = data.shape

        factor = 1
        # downsample by length
        if shape[1] > maxLength:
            factor = shape[1] // maxLength

        xValues = np.arange(0, shape[1], factor)

        data = data[0:maxChannels, ::factor]

        return data, xValues

    def graphTableView(self, data, xValues, metaData):
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=False,
            vertical_spacing=0.1,
            specs=[
                [{"type": "scatter"}],
                [{"type": "histogram"}],
                [{"type": "table"}],
            ],
        )
        lineName = "[:, %i]" if self.transposed else "[%i, :]"
        lineNameDist = lineName + " dist"
        for i, y in enumerate(data):
            fig.add_trace(
                go.Scatter(
                    x=xValues,
                    y=y,
                    mode="lines",
                    name=lineName % i,
                    legendgrouptitle={"text": "y[%i]" % i},
                    legendgroup="%i" % i,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Histogram(
                    x=y,
                    name=lineNameDist % i,
                    legendgroup="%i" % i,
                ),
                row=2,
                col=1,
            )

        fig.add_trace(
            go.Table(
                header=dict(
                    values=[[name] for name in metaData],
                ),
                cells=dict(
                    values=[[metaData[name]] for name in metaData],
                ),
            ),
            row=3,
            col=1,
        )

        return fig

    def getMetaData(self, data):
        return {
            "shape": str(data.shape),
            "mean": data.mean(),
            "max": data.max(),
            "min": data.min(),
        }

    def visualize(self, data):
        # only use last 2 dimensions
        metaData = self.getMetaData(data)
        data, xValues = self.selectAndTailorData(data)

        fig = self.graphTableView(data, xValues, metaData)

        return super().visualize(fig)
