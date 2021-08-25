import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist

import stad as sd

data = pd.read_csv('../examples/data/horse.csv')
idx = np.random.choice(data.shape[0], 200, replace=False)
data = data.iloc[idx, :]
dist = pdist(data, 'euclidean')
dist /= dist.max()
(network, sweep) = sd.stad(dist)


class TestLenses:
  def test_boundary_coefficient(self):
    res = sd.lenses.boundary_coefficient(network)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)

  def test_boundary_coefficient_tuple(self):
    res = sd.lenses.boundary_coefficient((network, sweep))
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_boundary_coefficient_custom_dist(self):
    res = sd.lenses.boundary_coefficient(network, distances=dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_density(self):
    res = sd.lenses.density(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_density_sigma(self):
    res = sd.lenses.density(dist, sigma=0.4)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_eccentricity(self):
    res = sd.lenses.eccentricity(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_eccentricity_power(self):
    res = sd.lenses.eccentricity(dist, power=2)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_eccentricity_inf_power(self):
    res = sd.lenses.eccentricity(dist, power=np.inf)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_knn_distance(self):
    res = sd.lenses.knn_distance(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
    assert (res > 0).all()
  
  def test_knn_distance_self(self):
    res = sd.lenses.knn_distance(dist, k=1)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
    assert (res == 0).all()
  
  def test_distance_to_measure(self):
    res = sd.lenses.distance_to_measure(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_distance_to_measure_k(self):
    res = sd.lenses.distance_to_measure(dist, k=10)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian(self):
    res = sd.lenses.graph_laplacian(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_n(self):
    res = sd.lenses.graph_laplacian(dist, n=2)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_sigma(self):
    res = sd.lenses.graph_laplacian(dist, sigma=0.5)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt(self):
    res = sd.lenses.graph_laplacian_alt(dist)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_n(self):
    res = sd.lenses.graph_laplacian_alt(dist, n=2)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_k(self):
    res = sd.lenses.graph_laplacian_alt(dist, k=10)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_weight(self):
    res = sd.lenses.graph_laplacian_alt(dist, weighted_edges=True)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_norm(self):
    res = sd.lenses.graph_laplacian_alt(dist, normalised=False)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_eps(self):
    res = sd.lenses.graph_laplacian_alt(dist, eps=0.4, k=1)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
  
  def test_graph_laplacian_alt_sigma(self):
    res = sd.lenses.graph_laplacian_alt(dist, sigma_eps=0.7)
    assert len(res) == 200
    assert isinstance(res, np.ndarray)
