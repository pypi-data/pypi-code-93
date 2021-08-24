""" pySTAD - a python implementation of STAD.

STAD is a dimensionality reduction algorithm, that generates an abstract
representation of high-dimensional data by giving each data point a location
in a graph which preserves the distances in the original high-dimensional
space. The STAD graph is built upon a Minimum Spanning Tree (MST) to
which new edges are added until the correlation between the graph and the
original dataset is maximized. Additionally, STAD supports the inclusion
of filter functions to analyse data from new perspectives, emphasizing
traits in data which otherwise would remain hidden.

This package contains an implementation of STAD and provides interactive
visualization functionality.

Functions
---------
stad : 
  The main function for creating a STAD network: 
    `network, sweep = stad(distance_matrix, [lens = Lens, sweep = Sweep])`
  Where lens is an instance of the Lens class and sweep an instance of one
  of the Sweep classes.
__main__ : 
  The entrypoint used when calling STAD from the command-line. It combines
  stad.stad() and stad.export.to_json() to print a STAD network to stdout.
  See `stad -h` for more information. 

Classes
-------
Lens :
  A class that configures a 1-dimensional lens / filter.
OptimizerFunction :
  A class to configure an external optimization function to optimize the network.
SweepDistanceLinear :
  A class to configure a linear sweep using a distance threshold.
SweepDistanceLogarithmic :
  A class to configure a logarithmic sweep using a distance threshold.
SweepEdgesLinear :
  A class to configure a linear sweep using a threshold on the number of edges.
SweepEdgesLogarithmic :
  A class to configure a logarithmic sweep using a threshold on the number of edges.
ThresholdDistance :
  A class to apply a single distance threshold without sweeping other values.
ThresholdEdges :
  A class to apply a single edge threshold without sweeping other values.
Widget :
  A jupyter-lab widget.

Modules
-------
export :
  A module with functions to export the output of STAD to other formats.
lenses :
  A module with point-cloud functions that can be used as lens or filter.
masks :
  A module containing masking functions for condensed distance matrices.
objective :
  A module containing the functions used to evaluate the networks.
plot :
  A module to plot STAD networks and sweeps.
sparse :
  A module containing functions to work with sparse distances.

"""

from . import export, lenses, masks, objective, plot, sparse
from .lens import *
from .stad import stad
from .sweeps import *
from .widget import *
