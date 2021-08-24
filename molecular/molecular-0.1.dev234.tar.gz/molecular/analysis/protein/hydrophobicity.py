"""
protein.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

# from molecular import include_dir
# from molecular.geometry import distance
from typelike import ListLike

import numpy as np
import os
import pandas as pd
import sys

# TODO move this to root
include_dir = os.path.abspath(__file__ + '/../../../_include')

# Reference to this module
this = sys.modules[__name__]

# Cache to store data in session
this.cache = {}


# Hydrophobicity scale class
class HydrophobicityScale:
    """
    Store a hydrophobicity scale that can be used for analysis
    """

    # Initialize instance
    def __init__(self, scale=None):
        """
        Initialize instance of ``HydrophobicityScale`` class
        """

        # Initialize data elements
        self.data = None
        self.residue_name_format = None

        # If scale is not None, load
        if scale is not None:
            self.load(scale)

    # Parse the scale
    def __getitem__(self, item):
        # If integer, assume that we're referring to the index
        if isinstance(item, int):
            element = self.data.iloc[item]

        # Otherwise, use the index name
        else:
            element = self.data[item]

        # Return
        return element

    # Load scale
    def load(self, scale):
        """
        Load scale by name

        Parameters
        ----------
        scale : str
            Name of hydrophobicity scale (Default: 'wimley-white')
        """

        # Convert scale to lowercase, convert - to _
        # TODO enable parsing of part of the scale name
        scale = scale.lower().replace('-', '_')

        # Based on scale, get filename
        filename = os.path.join(include_dir, 'protein', 'hydrophobicity_scales', scale + '.csv')

        # Read
        self.data = pd.read_csv(filename).set_index('residue').loc[:, 'hydrophobicity']

        # Get residue name format
        self.residue_name_format = _get_residue_name_format(self.data.index.values[0])


# Convert residue name format
def _convert_residue_name_format(residue, old_format, new_format, squeeze=True):
    """
    Convert ``residue`` from ``old_format`` to ``new_format``

    Parameters
    ----------
    residue : str or ListLike of str
    old_format : str
    new_format : str

    Returns
    -------

    """

    # Make sure residue is list
    if not isinstance(residue, ListLike):
        residue = [residue]

    # Convert residue list to pandas DataFrame
    df = pd.DataFrame({'old_name': residue})

    # Load RCT; filter RCT for old_format and new_format; create local copy; drop columns
    rct = _load_residue_conversions_table()
    x = rct['old_format'] == old_format
    y = rct['new_format'] == new_format
    rct = rct[x & y].copy().drop(columns=['old_format', 'new_format'])

    # Merge df with RCT to get new name
    df = df.merge(rct, how='left', on='old_name', validate='m:1')

    # Return new name
    return df['new_name'].values.squeeze()


# Get the format of the residue name based on length
def _get_residue_name_format(residue):
    # First off, make sure residue is a string, otherwise this will never work
    if not isinstance(residue, str):
        raise AttributeError('residue must be str; received {}'.format(residue))

    # Second, based on the length, assign the format
    n = len(residue)
    if n == 1:
        residue_format = 'letter'
    elif n == 3:
        residue_format = 'abbreviation'
    else:
        residue_format = 'full'

    # Return
    return residue_format


# Helper function to load hydrophobicity scale from cache or file
def _load_hydrophobicity_scale(scale):
    # Key
    key = 'hydrophobicity_scale_' + scale

    # If scale not in cache, add it
    if key not in this.cache:
        this.cache[key] = HydrophobicityScale(scale)

    # Return
    return this.cache[key]


# Helper function to load residue conversions table from cache / file
def _load_residue_conversions_table():
    # If residue_conversions_table has not yet been loaded, load
    if 'residue_conversions_table' not in this.cache:
        # Get filename
        filename = os.path.join(include_dir, 'protein', 'residue_conversions.csv')

        # Read
        this.cache['residue_conversions_table'] = pd.read_csv(filename)

    # Return the table
    return this.cache['residue_conversions_table'].copy()


# Compute hydrophobic moment from sequence
def compute_hydrophobic_moment(sequence, offset=100., scale='wimley-white'):
    """
    Compute the hydrophobic moment from a sequence

    Parameters
    ----------
    sequence : str or list of str
        Amino acid sequence
    offset : float
        Angle (in degrees) between amino acids (Default: 100 degrees)
    scale : str
        Hydrophobicity scale to use (Default: 'wimley-white')

    Returns
    -------
    float
        Hydrophobic moment magnitude
    """

    # Coerce sequence into correct form
    if isinstance(sequence, str):
        sequence = list(sequence)

    # Convert to numpy array for convenience
    sequence = np.array(sequence)

    # Load the right hydrophobicity scale
    if isinstance(scale, str):
        scale = _load_hydrophobicity_scale(scale)

    # At this pint, scale must by an instance of HydrophobicScale
    if not isinstance(scale, HydrophobicityScale):
        raise AttributeError('scale must be a known hydrophobicity scale or HydrophobicScale object')

    # Get the format of sequence entries and scale format
    sequence_format = _get_residue_name_format(sequence[0])

    # Convert the sequence format to the same as scale format
    sequence = _convert_residue_name_format(sequence, sequence_format, scale.residue_name_format)

    # Number of amino acid residues
    n_residues = len(sequence)

    # Convert the offset to radians, flip the sign, and compute angles between residues
    offset = -np.deg2rad(offset)
    angles = np.arange(0, n_residues * offset, offset)

    # Every residue has a 2D hydrophobic vector (-y points toward the hydrophobic medium)
    vector = np.zeros((n_residues, 2))
    vector[:, 0] = scale[sequence] * np.cos(angles)
    vector[:, 1] = scale[sequence] * np.sin(angles)

    # Return the hydrophobic moment
    # return distance(vector, method='euclidean')
    return np.sqrt(np.sum(np.square(vector)))

hydrophobic_moment = compute_hydrophobic_moment


# RMSD
def rmsd(coord1, coord2, align=True):
    """
    Compute the RMSD between two sets of coordinates

    Parameters
    ----------
    coord1 : ArrayLike
    coord2 : ArrayLike

    Returns
    -------

    """

    # Sanity
    if not coord1.shape == coord2.shape:
        raise AttributeError('coordinates must be same shape')

    # Return RMSD
    return np.linalg.norm(coord1 - coord2)/np.sqrt(coord1.shape[0])


if __name__ == '__main__':
    print(np.sum(hydrophobic_moment('GAIIGLMVGGVV')))

    # sequence = ['GLY', 'ALA', 'ILE', 'ILE', 'GLY', 'LEU', 'MET', 'VAL', 'GLY', 'GLY', 'VAL', 'VAL']
    sequence = ['GLY', 'SER', 'ASN', 'LYS', 'GLY', 'ALA', 'ILE', 'ILE', 'GLY', 'LEU', 'MET']
    scale = _load_hydrophobicity_scale('wimley-white')
    moment = [0., 0.]
    angle = 0.
    for s in sequence:
        moment[0] = moment[0] + scale[s] * np.cos(angle)
        moment[1] = moment[1] + scale[s] * np.sin(angle)
        angle = angle - np.radians(100.)
    print(moment)
    print(np.sqrt(np.sum(np.square(moment))))
