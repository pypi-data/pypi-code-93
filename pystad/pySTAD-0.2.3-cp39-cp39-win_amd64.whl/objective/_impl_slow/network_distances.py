from scipy.sparse.csgraph import shortest_path

from stad import sparse


def network_distances(sparse_adjacency_matrix, num_threads: int = None,
                      chunk_size: int =None):
    """ Computes distance of unweighted undirected networks

    Computes node distances for undirected unweighted networks containing 
    a single connected component. Implements a parallel breadth-first search
    using MPI. MPI's interface can be used to specify the number of cores
    to use.

    Parameters
    ----------
    sparse_adjacency_matrix : scipy sparse matrix
        A sparse matrix containing only the edges of the objective to evaluate.
    num_threads : integer
        This parameter is ignored.
    chunk_size : unsigned integer
        This parameter is ignored.
    Returns
    -------
    a condensed distance matrix (1d numpy array)
    """
    distances = shortest_path(sparse_adjacency_matrix.tocsr(), directed=False, unweighted=True)
    return sparse.squareform(distances)
