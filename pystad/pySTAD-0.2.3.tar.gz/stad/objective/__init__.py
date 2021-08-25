"""
A module containing the functions used to evaluate the networks.

STAD optimizes a network representation of a dataset by maximising the
correlation of the distances in the network with the distances in the data.
Several options are included to fine-tune this optimization process.

Functions
---------
network distances :
  Compute the shortest-paths in the network using breadth-first search.
  Supports parallel evaluation using OpenMP, starts a thread for each core by
  default.
objective :
  Computes the correlation, edge-penalty, ratio, and their combination in the
  objective score for a single network.
"""

try:
  from ._impl_fast import network_distances
except ImportError:
  from ._impl_slow import network_distances
  from sys import stderr
  print("Falling back to slow stad.objective implementation", file=stderr)

from .objective import objective
