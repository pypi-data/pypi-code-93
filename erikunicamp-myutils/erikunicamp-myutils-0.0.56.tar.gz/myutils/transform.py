import os
import numpy as np
from sklearn import preprocessing

##########################################################
def pca(data, normalize=False):
    """Perform Principal Component Analysis on @data. It expects the @data with
    rows as instances and features as columns.
    You may check the contribution of each component by calling
    get_pc_contribution()"""

    x = data.copy()
    if normalize:
        x = preprocessing.normalize(x, axis=0)

    x -= np.mean(x, axis=0) # just centralize
    cov = np.cov(x, rowvar = False)
    evals , evecs = np.linalg.eig(cov)

    idx = np.argsort(evals)[::-1]
    evecs = evecs[:,idx] # each column is a eigenvector
    evals = evals[idx]
    a = np.dot(x, evecs)

    return a, evecs, evals

##########################################################
def get_pc_contribution(evecs):
    """Get the id and calculate the relative contribution of the feature
    with major contribution to the first two components. Notice that the
    values are relative to each component and thus the sum may surpass 1."""
    pcs = []; contribs = []
    for i in range(2): # Just two major components
        evec = np.abs(evecs[:, i])
        contrib = evec / np.sum(evec)
        pcs.append(np.argsort(contrib)[-1])
        contribs.append(np.max(contrib))
    return pcs, contribs
