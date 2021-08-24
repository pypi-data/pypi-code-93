"""
A module containing functions to plot STAD networks and sweeps

Functions
---------
network : 
    Uses networkx and matplotlib to plot a node-link diagram of
    the network.
sweeps : 
    Uses matplotlib to show the correlations and objectives found
    during a sweep over the normalized distance distribution.
    Useful to inspect whether STAD found a good network representation.
"""

from .network import network
from .sweep import sweep
from .traces import traces