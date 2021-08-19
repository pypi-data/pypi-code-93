import os
import numpy as np
from sklearn import preprocessing

##########################################################
def pca(xin, normalize=False):
    x = xin.copy()

    if normalize: x = preprocessing.normalize(x, axis=0)

    x -= np.mean(x, axis=0) # just centralize
    cov = np.cov(x, rowvar = False)
    evals , evecs = np.linalg.eig(cov)

    idx = np.argsort(evals)[::-1]
    evecs = evecs[:,idx] # each column is a eigenvector
    evals = evals[idx]
    a = np.dot(x, evecs)
    return a, evecs, evals
