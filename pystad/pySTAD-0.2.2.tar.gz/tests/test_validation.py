import numpy as np
import pytest
from scipy.sparse import coo_matrix
from scipy.sparse import isspmatrix

import stad as sd

dense = np.array([
  np.array([0, 0.1, 0.3]),
  np.array([0.1, 0, 0.4]),
  np.array([0.3, 0.4, 0])
])
dist = np.array([0.1, 0.3, 0.4])
s_dist = coo_matrix((dist, ([0, 0, 1], [1, 2, 2])), shape=(3, 3))
mask = sd.masks.mst(s_dist, np.array([True, True, True]))
network = sd.sparse.filter(s_dist.copy(), mask)
sweep = sd.sweeps.ThresholdDistance()

class TestValidation:
  def test_validation_distance_dense(self):
    d = sd._validation.distances(dense)
    assert isspmatrix(d)
    assert (d.data == s_dist.data).all()
    assert (d.row == s_dist.row).all()
    assert (d.col == s_dist.col).all()
  
  def test_validation_distance_condensed(self):
    d = sd._validation.distances(dist)
    assert isspmatrix(d)
    assert (d.data == s_dist.data).all()
    assert (d.row == s_dist.row).all()
    assert (d.col == s_dist.col).all()
  
  def test_validation_distance_sparse(self):
    d = sd._validation.distances(s_dist)
    assert isspmatrix(d)
    assert (d.data == s_dist.data).all()
    assert (d.row == s_dist.row).all()
    assert (d.col == s_dist.col).all()
  
  def test_validation_distance_sparse_small(self):
    one_node = coo_matrix(([1], ([0], [0])), shape=(1, 1))
    with pytest.raises(AssertionError):
      d = sd._validation.distances(one_node)
  
  def test_validation_distance_sparse_square(self):
    not_square = coo_matrix((dist, ([0, 0, 1], [1, 2, 2])), shape=(3, 4))
    with pytest.raises(AssertionError):
      d = sd._validation.distances(not_square)
  
  def test_validation_distance_sparse_implicit_zeros(self):
    implicit = coo_matrix(([0.1, 0.4], ([0, 1], [1, 2])), shape=(3, 3))
    with pytest.raises(AssertionError):
      d = sd._validation.distances(implicit)
  
  def test_validation_distance_dense_square(self):
    square = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances(square)
  
  def test_validation_distance_dense_diag(self):
    diag = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 2.0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances(diag)
  
  def test_validation_distance_dense_symmetric(self):
    sym = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.7, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances(sym)
  
  def test_validation_distance_dense_small(self):
    small = np.array([
      np.array([0])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances(small)
  
  def test_validation_distance_length(self):
    length = np.array([0.1, 0.3, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances(length)
  
  def test_validation_distance_short(self):
    short = np.array([])
    with pytest.raises(AssertionError):
      sd._validation.distances(short)
  
  def test_validation_distance_nan(self):
    n = np.array([0.1, np.nan, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances(n)
  
  def test_validation_distance_inf(self):
    i = np.array([0.1, np.inf, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances(i)
  
  def test_validation_distance_negative(self):
    n = np.array([0.1, -0.6, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances(n)
  
  def test_validation_distance_value(self):
    v = np.array([0.1, 0.1, 0.1, 0.1])
    with pytest.raises(AssertionError):
      sd._validation.distances(v)
  
  def test_validation_distance_dense_dense(self):
    d = sd._validation.distances_dense(dense)
    assert isinstance(d, np.ndarray)
    assert d.shape == (3, 3)
    assert np.allclose(d, dense)
  
  def test_validation_distance_dense_condensed(self):
    d = sd._validation.distances_dense(dist)
    assert isinstance(d, np.ndarray)
    assert d.shape == (3, 3)
    assert np.allclose(d, dense)
  
  def test_validation_distance_dense_sparse(self):
    d = sd._validation.distances_dense(s_dist)
    assert isinstance(d, np.ndarray)
    assert d.shape == (3, 3)
    assert np.allclose(d, dense)
  
  def test_validation_distance_dense_sparse_small(self):
    one_node = coo_matrix(([1], ([0], [0])), shape=(1, 1))
    with pytest.raises(AssertionError):
      d = sd._validation.distances_dense(one_node)
  
  def test_validation_distance_dense_sparse_square(self):
    not_square = coo_matrix((dist, ([0, 0, 1], [1, 2, 2])), shape=(3, 4))
    with pytest.raises(AssertionError):
      d = sd._validation.distances_dense(not_square)
  
  def test_validation_distance_dense_sparse_implicit_zeros(self):
    implicit = coo_matrix(([0.1, 0.4], ([0, 1], [1, 2])), shape=(3, 3))
    with pytest.raises(AssertionError):
      d = sd._validation.distances_dense(implicit)
  
  def test_validation_distance_dense_dense_square(self):
    square = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(square)
  
  def test_validation_distance_dense_dense_diag(self):
    diag = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 2.0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(diag)
  
  def test_validation_distance_dense_dense_symmetric(self):
    sym = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.7, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(sym)
  
  def test_validation_distance_dense_dense_small(self):
    small = np.array([
      np.array([0])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(small)
  
  def test_validation_distance_dense_dense_empty(self):
    small = np.array([
      np.array([])
    ])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(small)
  
  def test_validation_distance_dense_length(self):
    length = np.array([0.1, 0.3, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(length)
  
  def test_validation_distance_dense_short(self):
    short = np.array([])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(short)
  
  def test_validation_distance_dense_nan(self):
    n = np.array([0.1, np.nan, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(n)
  
  def test_validation_distance_dense_inf(self):
    i = np.array([0.1, np.inf, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(i)
  
  def test_validation_distance_dense_negative(self):
    n = np.array([0.1, -0.6, 0.4, 0.6])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(n)
  
  def test_validation_distance_dense_value(self):
    v = np.array([0.1, 0.1, 0.1, 0.1])
    with pytest.raises(AssertionError):
      sd._validation.distances_dense(v)
  
  def test_validation_network(self):
    full = coo_matrix(([0.1, 0.3, 0.4], ([0, 0, 1], [1, 2, 2])), shape=(3, 3))
    n = sd._validation.network(full)
    assert isspmatrix(n)
    assert (n.data == full.data).all()
    assert (n.row == full.row).all()
    assert (n.col == full.col).all()

  def test_validation_network_tuple(self):
    n = sd._validation.network((network, sweep))
    assert isspmatrix(n)
    assert (n.data == network.data).all()
    assert (n.row == network.row).all()
    assert (n.col == network.col).all()
  
  def test_validation_network_implicit(self):
    sub = coo_matrix(([0.1, 0.4], ([0, 1], [1, 2])), shape=(3, 3))
    n = sd._validation.network(sub)
    assert isspmatrix(n)
    assert (n.data == sub.data).all()
    assert (n.row == sub.row).all()
    assert (n.col == sub.col).all()
  
  def test_validation_network_nans(self):
    sub = coo_matrix(([0.1, np.nan], ([0, 1], [1, 2])), shape=(3, 3))
    with pytest.raises(AssertionError):
      sd._validation.network(sub)
  
  def test_validation_network_inf(self):
    sub = coo_matrix(([0.1, np.inf], ([0, 1], [1, 2])), shape=(3, 3))
    with pytest.raises(AssertionError):
      sd._validation.network(sub)
  
  def test_validation_network_negative(self):
    sub = coo_matrix(([0.1, -0.1], ([0, 1], [1, 2])), shape=(3, 3))
    with pytest.raises(AssertionError):
      sd._validation.network(sub)
  
  def test_validation_network_mask(self):
    mask = np.array([True, True, False])
    n = sd._validation.network(mask)
    assert isspmatrix(n)
    assert (n.data == np.array([True, True])).all()
    assert (n.row == np.array([0, 0])).all()
    assert (n.col == np.array([1, 2])).all()
  
  def test_validation_network_mask_small(self):
    mask = np.array([])
    with pytest.raises(AssertionError):
      sd._validation.network(mask)
  
  def test_validation_network_mask_length(self):
    mask = np.array([0.1, 0.2, 0.4, 0.5])
    with pytest.raises(AssertionError):
      sd._validation.network(mask)
  
  def test_validation_network_dense(self):
    dense = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.3, 0.4, 0])
    ])
    d = sd._validation.network(dense)
    assert isspmatrix(d)
    assert (d.data == s_dist.data).all()
    assert (d.row == s_dist.row).all()
    assert (d.col == s_dist.col).all()
  
  def test_validation_network_dense_square(self):
    square = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.network(square)
  
  def test_validation_network_dense_diag(self):
    diag = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 2.0, 0.4]),
      np.array([0.3, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.network(diag)
  
  def test_validation_network_dense_symmetric(self):
    sym = np.array([
      np.array([0, 0.1, 0.3]),
      np.array([0.1, 0, 0.4]),
      np.array([0.7, 0.4, 0]),
      np.array([0.4, 0, 1])
    ])
    with pytest.raises(AssertionError):
      sd._validation.network(sym)
  
  def test_validation_network_dense_small(self):
    small = np.array([
      np.array([0])
    ])
    with pytest.raises(AssertionError):
      sd._validation.network(small)
  
  def test_validation_network_dense_empty(self):
    small = np.array([
      np.array([])
    ])
    with pytest.raises(AssertionError):
      sd._validation.network(small)
