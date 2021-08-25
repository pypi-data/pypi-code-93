"""
A module containing masking functions.

These functions are used to extract edges from the complete distance matrix that
satisfy several criteria.

Functions
---------
distances :
  Returns a mask for all edges with a distance below the given threshold.
edges :
  Returns the k smallest edges.
mst :
  Returns the edges of the minimum spanning tree.
"""
from .distances import distances
from .edges import edges
from .mst import mst
