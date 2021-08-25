import numpy as np
import pandas as pd
from scipy.sparse import isspmatrix
from scipy.spatial.distance import pdist

import stad as sd

data = pd.read_csv('../examples/data/horse.csv')
idx = np.random.choice(data.shape[0], 200, replace=False)
data = data.iloc[idx, :]
dist = pdist(data, 'euclidean')
dist /= dist.max()


class TestStad:
  def test_stad(self):
    network, sweep = sd.stad(dist)
    assert isspmatrix(network)
    assert sweep.n_steps == 10 # just to check sweep is a _SweepBase
    assert network.shape == (200, 200)

  def test_stad_repeated(self):
    network, sweep = sd.stad(dist)
    network, sweep2 = sd.stad(dist)
    assert not (sweep is sweep2)

