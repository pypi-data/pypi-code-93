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


class TestLens:
  def test_lens(self):
    lens = sd.Lens(data['x'], n_bins=10)
    network, sweep = sd.stad(dist, lens=lens)
    assert isspmatrix(network)
    assert sweep.n_steps == 10 # just to check sweep is a _SweepBase
    assert np.allclose(lens.values, data['x'])
    assert len(lens.adjacent_edges) == len(dist)
    assert len(lens.non_adjacent_edges) == len(dist)
    assert len(lens.inner_edges) == len(dist)
    assert len(lens.bins) == 11
    assert lens.non_adjacent_edges.any()
  
  def test_circular_lens(self):
    lens = sd.Lens(data['x'], n_bins=10, circular=True)
    network, sweep = sd.stad(dist, lens = lens)
    assert isspmatrix(network)
    assert sweep.n_steps == 10 # just to check sweep is a _SweepBase
    assert np.allclose(lens.values, data['x'])
    assert len(lens.adjacent_edges) == len(dist)
    assert len(lens.non_adjacent_edges) == len(dist)
    assert len(lens.inner_edges) == len(dist)
    assert len(lens.bins) == 11
    assert lens.non_adjacent_edges.any()
  
  def test_disabled_lens(self):
    lens = sd.Lens(data['x'], n_bins=0)
    network, sweep = sd.stad(dist, lens = lens)
    assert isspmatrix(network)
    assert sweep.n_steps == 10 # just to check sweep is a _SweepBase
    assert np.allclose(lens.values, data['x'])
    assert lens.non_adjacent_edges is None
    assert lens.adjacent_edges is None
    assert lens.non_adjacent_edges is None
    assert lens.inner_edges is None
    assert lens.bins is None
  
  def test_disabled_lens_alt(self):
    lens = sd.Lens(n_bins=10)
    network, sweep = sd.stad(dist, lens = lens)
    assert isspmatrix(network)
    assert sweep.n_steps == 10 # just to check sweep is a _SweepBase
    assert lens.non_adjacent_edges is None
    assert lens.adjacent_edges is None
    assert lens.non_adjacent_edges is None
    assert lens.inner_edges is None
    assert lens.bins is None
