""" This module contain the RobotWorld base abstract class. """
from abc import ABC, abstractmethod

class RobotWorld(ABC):
  """ 
  This is an abstract class defining our toy robot's world.
  
  It can be modified in the future, for instance, to define 
  a three dimensional space, or a two dimensional surface in 
  space.
  """
  @abstractmethod
  def is_within_boundaries(self):
    """ 
    Abstract method.

    Checks is given coordinates are within boundaries. """
    pass

  @abstractmethod
  def next_position(self):
    """ 
    Abstract method.

    Returns the next position, depending on boundaries and 
    other constraints. 
    """
    pass
