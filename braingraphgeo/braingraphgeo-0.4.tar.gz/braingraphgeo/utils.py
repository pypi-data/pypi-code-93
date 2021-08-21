import os
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def load_connectivity_matrix(path, return_both_hemispheres=True):
    '''
    Utility function to load graph connectivity matrices.

    Parameters
    __________
    path : str
        Path to data file. Must be .csv
    return_both_hemispheres : bool
        Bool. If false, only returns the first half of the rows, assuming
        the matrix was constructed with hemispheric symmetry.

    Returns
    _______
    df : DataFrame
        Adjacency matrix with node labels as pandas DataFrame
    '''
    if os.path.splitext(path)[1] != '.csv':
        raise ValueError('Please enter the path to a .csv file')

    df = pd.read_csv(path, index_col=0)

    if return_both_hemispheres:
        return df
    else:
        n = df.shape[0]//2
        return df.iloc[:n]


def build_spearman_correlation_matrix(mat1, mat2, parcellation):
    '''
    Takes two connectivity matrices and generates a matrix
    of spearman correlation coefficients between the 12 major brain
    divisions.

    Parameters
    __________
    mat1 : ndarray
        2D connectivity matrix. Assumes hemispheric symmetry with "sources"
        as rows, and ipsi- and contralateral "targets" as columns,
        respectively.
    mat2 : ndarray
        2D connectivity matrix. Assumes hemispheric symmetry with "sources"
        as rows, and ipsi- and contralateral "targets" as columns,
        respectively.
    parcellation : pandas DataFrame
        Must contain a row for every node and a "Brain Division" column
        with strings matching the names of one of the 12 major brain
        divisions listed in the Allen atlas.

    Returns
    _______
    corr : ndarray
        2D matrix of shape (12,24) corresponding to spearman correlations
        between 12 major brain divisions. corr[:,:12] corresponds to
        ipsilateral connections and cprr[:,12:] corresponds to contralateral
        connections. Hemispheric symmetry is assumed.
    '''

    # Check inputs
    check_parcellation(parcellation)

    if mat1.shape != mat2.shape:
        raise ValueError('mat1 and mat2 do not have the same shape')
    N_nodes = mat1.shape[1]
    N_per_hemi = N_nodes//2

    brain_divisions = np.unique(parcellation['Brain Division'])
    N_div = len(brain_divisions)

    # Maps nodes to brain divisions
    masks = {}
    for division in brain_divisions:
        masks[division] = np.array(parcellation['Brain Division'] == division)

    corr = np.zeros((N_div, N_div*2))
    for i, div_i in enumerate(brain_divisions):
        for j, div_j in enumerate(brain_divisions):
            mask = np.outer(masks[div_i], masks[div_j])  # per hemisphere

            # ipsilateral on left
            corr[i, j] = spearmanr(mat1[:, :N_per_hemi]
                                   [mask], mat2[:, :N_per_hemi][mask])[0]
            # contralateral on right
            corr[i, j+N_div] = spearmanr(mat1[:, N_per_hemi:]
                                         [mask], mat2[:, N_per_hemi:][mask])[0]
    return corr


def check_parcellation(parcellation):
    '''
    Utility function to check that the user-supplied parcellation data
    is compatible with the Allen brain divisions.

    Parameters
    __________
    parcellation : pandas DataFrame
        Must contain a row for every node and a "Brain Division" column
        with strings matching the names of one of the 12 major brain
        divisions listed in the Allen atlas.

    Raises
    _______
    ValueError
        If `parcellation` contains a brain division label that is not one
        of the 12 major brain divisions from the Allen atlas
    '''

    brain_divisions = ['Isocortex', 'OLF', 'HPF', 'CTXsp', 'STR',
                       'PAL', 'TH', 'HY', 'MB', 'P', 'MY', 'CB']
    # Brain division acronyms in parcellation
    parcel_acros = parcellation['Brain Division'].unique()
    for parcel_acro in parcel_acros:
        if parcel_acro not in brain_divisions:
            raise ValueError(
                f'Parcellation contains unknown acronym: {parcel_acro}')


def to_density(W, density):
    '''
    Utility function to threshold a connectivity matrix W to a desired
    density.

    Parameters
    __________
    W : ndarray
        Connectivity matrix.
    density : float/int in [0,100]
        Desired network density (as percent)

    Returns
    _______
    W : ndarray
        Input matrix W with low weights set to zero such that the network
        density is `density`
    '''

    offdiag = np.diag(np.ones(W.shape[0])) == 0
    thresh = np.percentile(W[offdiag], 100 - density)
    W_thr = np.zeros_like(W)
    W_thr[W >= thresh] = W[W >= thresh]
    return W_thr


def rescale(a):
    '''
    Utility function to rescale an array from 0-1

    Parameters
    __________
    a : ndarray

    Returns
    _______
    scaled : ndarray
        a scaled to be in 0-1
    '''
    shift = a - a.min()
    scaled = shift / shift.max()
    return scaled
