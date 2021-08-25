import numpy as np

import stad as sd

dist = np.array([0.1, 0.3, 0.4])
s_dist = sd.sparse.from_condensed(dist)
lens_mask = np.array([True, True, True])


class TestMasks:
  def test_distance_mask(self):
    mask = sd.masks.distances(dist, 0.2)
    assert (mask == np.array([True, False, False])).all()
  
  def test_edge_mask(self):
    mask, threshold = sd.masks.edges(dist, 1)
    assert (mask == np.array([True, False, False])).all()
    assert threshold == 0.3
  
  def test_mst_mask(self):
    mask = sd.masks.mst(s_dist, lens_mask)
    assert (mask == np.array([True, True, False])).all()
    assert np.allclose(s_dist.data, np.array([0.1, 0.3, 0.4]))
  
  def test_mst_mask_with_lens(self):
    mask = sd.masks.mst(s_dist, np.array([False, True, True]))
    assert (mask == np.array([False, True, True])).all()
    assert np.allclose(s_dist.data, np.array([0.1, 0.3, 0.4]))
