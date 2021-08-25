"""
This module implements several interesting point-cloud measures that can
be used as lenses with STAD. Most of these functions are based on the
documentation of the python implementation of Mapper.

Functions
---------
density :
    Computes the density of each vertex in a point-cloud. Produces high
    values for vertices in regions with many vertices.
eccentricity :
    Computes the eccentricity of each vertex in a point-cloud. Produces high
    values for vertices in regions with few vertices.
knn_distance :
    Computes the distance of the k-th closest neighbour for every vertex.
distance_to_measure :
    Computes the 2-norm of the vector containing the k-th closest neighbours
    for every vertex.
graph_laplacian :
    Computes eigenvectors of the graph laplacian of the distance matrix,
    following the description in section 4.3 from:
        Singh, G., Mémoli, F., & Carlsson, G. (2007). Topological Methods
        for the Analysis of High Dimensional Data Sets and 3D Object
        Recognition. In Eurographics Symposium on Point-Based Graphics.
graph_laplacian_alt :
    Computes eigenvectors of the graph laplacian of the distance matrix,
    following the description in Mapper's documentation:
        http://danifold.net/mapper/filters.html
boundary_coefficient :
    The boundary coefficient uses distances between data-points to estimate
    whether a point is close to the boundary of the point-cloud. Based on:
        Vandaele, R., Saeys, Y., & De Bie, T. (2020). Mining topological
        structure in graphs through forest representations. Journal of
        Machine Learning Research, 21, 1–68.
"""

from .boundary_coefficient import boundary_coefficient
from .density import density
from .distance_to_measure import distance_to_measure
from .eccentricity import eccentricity
from .graph_laplacian import graph_laplacian
from .graph_laplacian_alt import graph_laplacian_alt
from .knn_distance import knn_distance
