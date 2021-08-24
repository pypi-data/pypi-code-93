import numpy as np
import pandas as pd
import pytest
from scipy.optimize import shgo
from scipy.sparse import isspmatrix
from scipy.spatial.distance import pdist

import stad as sd

data = pd.read_csv('../examples/data/horse.csv')
idx = np.random.choice(data.shape[0], 200, replace=False)
data = data.iloc[idx, :]
dist = pdist(data, 'euclidean')
dist /= dist.max()


def custom_optimiser(fun, args, bounds, maxiter, **kwargs):
  return shgo(fun, bounds, args=args, options={
    'maxiter': maxiter,
    **kwargs
  }
              )


class TestSweep:
  def test_edge_threshold_default(self):
    sweep = sd.ThresholdEdges()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.edge_factor == 0.1
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edge_threshold_custom(self):
    sweep = sd.ThresholdEdges(edge_factor=0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.edge_factor == 0.3
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edge_threshold_clamp_upper(self):
    sweep = sd.ThresholdEdges(edge_factor=1.2)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.edge_factor == 1.0
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edge_threshold_clamp_lower(self):
    sweep = sd.ThresholdEdges(edge_factor=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.edge_factor == 0
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_threshold_default(self):
    sweep = sd.ThresholdDistance()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.distance == 0.2
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_threshold_custom(self):
    sweep = sd.ThresholdDistance(distance=0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.distance == 0.3
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_threshold_clamp_upper(self):
    sweep = sd.ThresholdDistance(distance=1.2)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.distance == 1.0
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_threshold_clamp_lower(self):
    sweep = sd.ThresholdDistance(distance=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.distance == 0
    assert sweep.n_steps == 1
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx == 0
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_default(self):
    sweep = sd.SweepEdgesLogarithmic()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_start_custom(self):
    sweep = sd.SweepEdgesLogarithmic(start=0.1)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.1
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_start_higher_than_stop(self):
    with pytest.raises(AssertionError):
      sd.SweepEdgesLogarithmic(start=0.4)
  
  def test_edges_logarithmic_sweep_start_clamp_lower(self):
    sweep = sd.SweepEdgesLogarithmic(start=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_stop_custom(self):
    sweep = sd.SweepEdgesLogarithmic(stop=0.4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.4
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_stop_lower_than_start(self):
    with pytest.raises(AssertionError):
      sd.SweepEdgesLogarithmic(stop=0.005)
  
  def test_edges_logarithmic_sweep_stop_clamp_upper(self):
    sweep = sd.SweepEdgesLogarithmic(stop=1.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 1
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_logarithmic_sweep_nstep_custom(self):
    sweep = sd.SweepEdgesLogarithmic(n_steps=15)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 15
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_default(self):
    sweep = sd.SweepDistanceLogarithmic()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_start_custom(self):
    sweep = sd.SweepDistanceLogarithmic(start=0.1)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.1
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_start_higher_than_stop(self):
    with pytest.raises(AssertionError):
      sd.SweepDistanceLogarithmic(start=0.4)
  
  def test_distance_logarithmic_sweep_start_clamp_lower(self):
    sweep = sd.SweepDistanceLogarithmic(start=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_stop_custom(self):
    sweep = sd.SweepDistanceLogarithmic(stop=0.4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.4
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_stop_lower_than_start(self):
    with pytest.raises(AssertionError):
      sd.SweepDistanceLogarithmic(stop=0.005)
  
  def test_distance_logarithmic_sweep_stop_clamp_upper(self):
    sweep = sd.SweepDistanceLogarithmic(stop=1.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 1
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_logarithmic_sweep_nstep_custom(self):
    sweep = sd.SweepDistanceLogarithmic(n_steps=15)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 15
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_default(self):
    sweep = sd.SweepEdgesLinear()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_start_custom(self):
    sweep = sd.SweepEdgesLinear(start=0.1)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.1
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_start_higher_than_stop(self):
    with pytest.raises(AssertionError):
      sd.SweepEdgesLinear(start=0.4)
  
  def test_edges_linear_sweep_start_clamp_lower(self):
    sweep = sd.SweepEdgesLinear(start=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_stop_custom(self):
    sweep = sd.SweepEdgesLinear(stop=0.4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.4
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_stop_lower_than_start(self):
    with pytest.raises(AssertionError):
      sd.SweepEdgesLinear(stop=0.005)
  
  def test_edges_linear_sweep_stop_clamp_upper(self):
    sweep = sd.SweepEdgesLinear(stop=1.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 1
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_edges_linear_sweep_nstep_custom(self):
    sweep = sd.SweepEdgesLinear(n_steps=15)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 15
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_default(self):
    sweep = sd.SweepDistanceLinear()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_start_custom(self):
    sweep = sd.SweepDistanceLinear(start=0.1)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.1
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_start_higher_than_stop(self):
    with pytest.raises(AssertionError):
      sd.SweepDistanceLinear(start=0.4)
  
  def test_distance_linear_sweep_start_clamp_lower(self):
    sweep = sd.SweepDistanceLinear(start=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0
    assert sweep.stop == 0.3
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_stop_custom(self):
    sweep = sd.SweepDistanceLinear(stop=0.4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.4
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_stop_lower_than_start(self):
    with pytest.raises(AssertionError):
      sd.SweepDistanceLinear(stop=0.005)
  
  def test_distance_linear_sweep_stop_clamp_upper(self):
    sweep = sd.SweepDistanceLinear(stop=1.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 1
    assert sweep.n_steps == 10
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_distance_linear_sweep_nstep_custom(self):
    sweep = sd.SweepDistanceLinear(n_steps=15)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 15
    assert len(sweep.objective_trace) == sweep.n_steps
    assert len(sweep.correlation_trace) == sweep.n_steps
    assert len(sweep.penalty_trace) == sweep.n_steps
    assert len(sweep.ratio_trace) == sweep.n_steps
    assert len(sweep.distance_trace) == sweep.n_steps
    assert len(sweep.added_edges_trace) == sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < sweep.n_steps
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_default(self):
    sweep = sd.OptimizerFunction()
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_start_custom(self):
    sweep = sd.OptimizerFunction(start=0.1)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.1
    assert sweep.stop == 0.3
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_start_higher_than_stop(self):
    with pytest.raises(AssertionError):
      sd.OptimizerFunction(start=0.4)
  
  def test_optimizer_start_clamp_lower(self):
    sweep = sd.OptimizerFunction(start=-0.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0
    assert sweep.stop == 0.3
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_stop_custom(self):
    sweep = sd.OptimizerFunction(stop=0.4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.4
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_stop_lower_than_start(self):
    with pytest.raises(AssertionError):
      sd.OptimizerFunction(stop=0.005)
  
  def test_optimizer_stop_clamp_upper(self):
    sweep = sd.OptimizerFunction(stop=1.3)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 1
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_nstep_custom(self):
    sweep = sd.OptimizerFunction(n_steps=15)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 15
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_optimizer_kwargs_custom(self):
    sweep = sd.OptimizerFunction(initial_temp=100, no_local_search=True)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 100
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
  
  def test_custom_optimizer_custom(self):
    sweep = sd.OptimizerFunction(function=custom_optimiser, n_steps=8, n=4)
    (network, s) = sd.stad(dist, sweep=sweep)
    assert isspmatrix(network)
    assert s == sweep # just to check sis a _SweepBase
    assert sweep.start == 0.01
    assert sweep.stop == 0.3
    assert sweep.n_steps == 8
    assert len(sweep.objective_trace) >= sweep.n_steps
    assert len(sweep.correlation_trace) >= sweep.n_steps
    assert len(sweep.penalty_trace) >= sweep.n_steps
    assert len(sweep.ratio_trace) >= sweep.n_steps
    assert len(sweep.distance_trace) >= sweep.n_steps
    assert len(sweep.added_edges_trace) >= sweep.n_steps
    assert sweep.best_trace_idx >= 0 and sweep.best_trace_idx < len(
      sweep.objective_trace)
    assert not np.isnan(sweep.best_objective)
    assert not np.isnan(sweep.best_correlation)
    assert not np.isnan(sweep.best_penalty)
    assert not np.isnan(sweep.best_distance)
    assert not np.isnan(sweep.best_added_edges)
    # best_ratio is nan because ratio is disabled in default mode
    assert sweep.mst_mask.sum() == 199
    assert len(sweep.mst_mask) == len(dist)
    assert len(sweep.lens_mask) == len(dist)
    assert len(sweep.network_mask) == len(dist)
    assert sweep.lens_mask.all()
