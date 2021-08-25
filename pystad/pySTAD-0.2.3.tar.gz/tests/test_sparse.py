import pytest
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse import isspmatrix

import stad as sd

dist = np.array([0.1, 0.3, 0.4])
labels = ["a", "b", "c"]
network = coo_matrix((dist, ([0, 0, 1], [1, 2, 2])), shape=(3, 3))
sub_network = coo_matrix(([dist[0]], ([0], [1])), shape=(3, 3))


class TestSparse:
  def test_filter(self):
    res = sd.sparse.filter(network.copy(), np.array([True, False, False]))
    assert isspmatrix(res)
    assert len(res.data) == 1
    assert res.data[0] == 0.1
    assert res.row[0] == 0
    assert res.col[0] == 1
    assert len(network.data) == 3
  
  def test_filter_inplace(self):
    net = network.copy()
    res = sd.sparse.filter(net, np.array([True, False, False]))
    assert isspmatrix(res)
    assert len(res.data) == 1
    assert res.data[0] == 0.1
    assert res.row[0] == 0
    assert res.col[0] == 1
    assert len(net.data) == 1
    assert net.data[0] == 0.1
    assert net.row[0] == 0
    assert net.col[0] == 1
  
  def test_from_condensed(self):
    res = sd.sparse.from_condensed(dist)
    assert isspmatrix(res)
    assert (res.data == network.data).all()
    assert (res.row == network.row).all()
    assert (res.col == network.col).all()
  
  def test_is_in(self):
    mask = sd.sparse.is_in(network, sub_network)
    assert (mask == np.array([True, False, False])).all()
  
  def test_network_join(self):
    source, target = sd.sparse.network_join(network, labels)
    assert (source == ["a", "a", "b"]).all()
    assert (target == ["b", "c", "c"]).all()
  
  def test_squareform(self):
    res = sd.sparse.squareform(dist)
    assert res.shape == (3, 3)
    res2 = sd.sparse.squareform(res)
    assert len(res2) == 3
    assert (res2 == dist).all()
  
  def test_triu(self):
    dense = np.array([
      np.array([0, 2, 0]),
      np.array([2, 0, 4]),
      np.array([0, 4, 0])
    ])
    res = sd.sparse.triu(dense)
    assert isspmatrix(res)
    assert (res.data == np.array([2, 0, 4])).all()
    assert (res.row == np.array([0, 0, 1])).all()
    assert (res.col == np.array([1, 2, 2])).all()
  
  def test_sub2ind(self):
    assert sd.sparse.sub2ind(0, 0, 4) == -1
    assert sd.sparse.sub2ind(2, 3, 1) == -1
    assert sd.sparse.sub2ind(0, 1, 4) == 0
    assert sd.sparse.sub2ind(1, 0, 4) == 0
    assert sd.sparse.sub2ind(2, 3, 4) == 5
    assert sd.sparse.sub2ind(2, 3, 9) == 15

  def test_ind2sub(self):
    assert sd.sparse.ind2sub(15, 9) == (2, 3)
    assert sd.sparse.ind2sub(5, 4) == (2, 3)
    assert sd.sparse.ind2sub(0, 4) == (0, 1)
    assert sd.sparse.ind2sub(6, 4) == (-1, -1)
