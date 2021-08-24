"""
A module containing helper functions to work with sparse matrices

functions
---------
filter :
  Applies a boolean mask to coo matrices.
from_condensed :
  Creates a coo matrix from a condensed distance matrix.
ind2sub :
  Computes the i,j coordinates of an element at a given index in a condensed
  distance matrix.
sub2ind :
  Computes the index in a condensed distance matrix of an element at i, j in a
  dense distance matrix.
is_in :
  Creates a mask indicating which elements of a fully specified coo_matrix
  exist in a sparser coo_matrix. (fully specified is upper triangle with
  explicit zeros).
network_join :
  Implements two-left joins for vertex-value in a network. One for the source
  and one for the target nodes.
squareform :
  Re-export scipy.spatial.distance.squareform. Transforms from dense to condensed
  distance matrices and vice versa.
triu :
  Creates a coo_matrix containing the upper triangle of a dense distance matrix,
  keeping explicit zero values.
"""
from .filter import filter
from .from_condensed import from_condensed
from .is_in import is_in
from .network_join import network_join
from .squareform import squareform
from .triu import triu

try:
  from ._impl_fast import sub2ind, ind2sub
except ImportError:
  from ._impl_slow import sub2ind, ind2sub
  from sys import stderr
  print("Falling back to slow stad.sparse implementation", file=stderr)
