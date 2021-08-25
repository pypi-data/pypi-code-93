import numpy as np

import stad as sd

dist = np.array([0.1, 0.3, 0.4])
s_dist = sd.sparse.from_condensed(dist)
mask = sd.masks.mst(s_dist, np.array([True, True, True]))
network = sd.sparse.filter(s_dist.copy(), mask)


class TestObjective:
  def test_network_distances(self):
    dist = sd.objective.network_distances(network)
    assert (dist == np.array([1, 1, 2])).all()
  
  def test_network_distances_threads(self):
    dist = sd.objective.network_distances(network, num_threads=1)
    assert (dist == np.array([1, 1, 2])).all()
  
  def test_network_distances_chunks(self):
    dist = sd.objective.network_distances(network, chunk_size=20)
    assert (dist == np.array([1, 1, 2])).all()
  
  def test_objective(self):
    dist = sd.objective.network_distances(network)
    o, c, p, r, e = sd.objective.objective(s_dist, dist, mask, mask,
                                           np.array([True, True, True]),
                                           0, False)
    assert o > 0
    assert c > 0 and c < 1
    assert p == 0
    assert np.isnan(r)
    assert e == 0
  
  def test_objective_penalty(self):
    dist = sd.objective.network_distances(network)
    o, c, p, r, e = sd.objective.objective(s_dist, dist, mask, mask,
                                           np.array([True, True, True]),
                                           0.2, False)
    assert o > 0
    assert c > 0 and c < 1
    assert p >= 0
    assert np.isnan(r)
    assert e == 0
  
  def test_objective_ratio(self):
    dist = sd.objective.network_distances(network)
    o, c, p, r, e = sd.objective.objective(s_dist, dist, mask, mask,
                                           np.array([True, True, True]),
                                           0.2, True)
    assert o > 0
    assert c > 0 and c < 1
    assert p >= 0
    assert r > 0
    assert e == 0
