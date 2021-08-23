
import numpy as np
import pandas as pd

from pandas_ml_common import dummy_splitter
from pandas_ml_utils import Model, FittingParameter
from pandas_ml_utils.constants import *

def create_line_data(n=300, slope=1):
    np.random.seed(32)
    x = np.linspace(0, 1, n)
    y = slope * x + np.random.normal(0, 0.05, n)
    return x, y


def create_sine_data(n=300):
    np.random.seed(32)
    x = np.linspace(0, 1 * 2 * np.pi, n)
    y1 = 3 * np.sin(x)
    y1 = np.concatenate((np.zeros(60), y1 + np.random.normal(0, 0.15 * np.abs(y1), n), np.zeros(60)))
    x = np.concatenate((np.linspace(-3, 0, 60), np.linspace(0, 3 * 2 * np.pi, n),
                        np.linspace(3 * 2 * np.pi, 3 * 2 * np.pi + 3, 60)))
    y2 = 0.1 * x + 1
    y = (y1 + y2) + 2
    return x, y


if __name__ == '__main__':

    df = pd.DataFrame(np.array(create_line_data(300)).T, columns=["x", "y"])

    with df.model() as m:
        from pandas_ml_utils.ml.callback.live_loss_plot import NbLiveLossPlot
        from pandas_ml_utils_torch import PytorchModel, PytorchNN
        from pandas_ml_utils import FeaturesAndLabels
        from torch.optim import Adam
        from torch import nn
        import torch as t

        class Net(PytorchNN):

            def __init__(self):
                super(Net, self).__init__()
                self.net = nn.Sequential(
                    nn.Linear(1, 200),
                    nn.ReLU(),
                    nn.Linear(200, 200),
                    nn.ReLU(),
                    nn.Linear(200, 1),
                    nn.ReLU()
                )

            def forward_training(self, *input) -> t.Tensor:
                return self.net(input[0])

        fit = m.fit(
            PytorchModel(Net, FeaturesAndLabels(["x"], ["y"]), nn.MSELoss, Adam),
            FittingParameter(splitter=dummy_splitter, epochs=100),
            callbacks=[NbLiveLossPlot(backend='pgf')]
        )




