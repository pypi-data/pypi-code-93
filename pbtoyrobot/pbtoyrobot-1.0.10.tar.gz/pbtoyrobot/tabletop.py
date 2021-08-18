""" This module contain the TableTop class. """
from .robotworld import RobotWorld

class TableTop(RobotWorld):
  """ This class defines a rectangular table top. """
  def __init__(self, width, length):
    self.__width = width
    self.__length = length
  
  # PROPERTIES
  #
  @property
  def width(self):
    """ Width property. """
    return self.__width

  @width.setter
  def width(self, value):
    """ Sets the width property to a given value. """
    if value <= 0:
      raise ValueError("Width cannot be negative or zero.")
    self.__width = value

  @property
  def length(self):
    """ Length property. """ 
    return self.__length

  @length.setter
  def length(self, value):
    """ Sets the length property to a given value. """
    if value <= 0:
      raise ValueError("Length cannot be negative or zero.")
    self.__length = value

  # METHODS
  #
  def is_within_boundaries(self, x, y):
    """ 
    Checks if the given coordinates are within boundaries. 
    
    Parameters:
      x (int): x coordinate.
      y (int): y coordinate.

    Returns:
      True if the given coordinates are within boundaries.
    """
    return (0 <= x <= self.width and 0 <= y <= self.length)

  def next_position(self, x, y, direction_angle, step = 1):
    """ 
    Returns the next position depending on the current direction and coordinates. 
    
    Movements are multiples of step.
    """
    if direction_angle == 0:
      new_x = x + step
    elif direction_angle == 180:
      new_x = x - step
    else:
      new_x = x
    
    if direction_angle == 90:
      new_y = y + step
    elif direction_angle == 270:
      new_y = y - step
    else:
      new_y = y

    if not self.is_within_boundaries(new_x, new_y):
      return (x, y)
    else:
      return (new_x, new_y)
