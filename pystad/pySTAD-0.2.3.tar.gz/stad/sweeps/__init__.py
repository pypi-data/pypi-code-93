"""
A module for configuring how STAD optimizes the network.

All classes extend the internal SweepBase and keep track of the values found
during the sweep.

Classes
-------
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
"""

from .OptimizerFunction import OptimizerFunction
from .SweepDistanceLinear import SweepDistanceLinear
from .SweepDistanceLogarithmic import SweepDistanceLogarithmic
from .SweepEdgesLinear import SweepEdgesLinear
from .SweepEdgesLogarithmic import SweepEdgesLogarithmic
from .ThresholdDistance import ThresholdDistance
from .ThresholdEdges import ThresholdEdges
