""" This module contain the Robot class. """
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from .tabletop import TableTop
from .input_output import PrintOutput

class Robot:
  """ This class defines our robot """
  def __init__(self, output_file=None):
    self.__directions = {
      "0": "EAST", 
      "90": "NORTH", 
      "180": "WEST", 
      "270": "SOUTH"
    }
    self.__directions_inv = {v : k for k, v in self.__directions.items()}
    self.__world = TableTop(5, 5)
    self.__output_file = output_file

  # METHODS
  #
  def load_state(self, file):
    # Read state to load inital position
    #
    path = Path(file)
    if path.exists():
      try:
        with open(file) as f:
          self.__state = yaml.load(f, Loader = SafeLoader)
          self.__state_file = file
      except:
        return PrintOutput.write_output(output="State file missing", output_file=self.__output_file)
    else:
      try:
        import importlib.resources as pkg_resources
      except ImportError:
        # Try backported to PY<37 `importlib_resources`.
        import importlib_resources as pkg_resources
      try:
        with pkg_resources.open_text(__package__, path.name) as f:
          self.__state = yaml.load(f, Loader = SafeLoader)
          self.__state_file = file
      except:
        return PrintOutput.write_output(output="State file missing", output_file=self.__output_file)
    
    self.__x = self.__state["X"]
    self.__y = self.__state["Y"]
    self.__facing = self.__state["F"]
    self.__place_command_executed = self.__state["PlaceCommandExecuted"]
    self.__angle = int(self.__directions_inv[self.__facing])

  def __get_cardinal_directions(self):
    return list(self.__directions.values())

  def __get_angles(self):
    return list(self.__directions.keys())

  def __get_cardinal_direction(self, angle):
    return self.__directions[str(angle)]

  def __is_first_command_executed(self):
    return self.__place_command_executed

  def __set_first_command_executed(self):
    self.__place_command_executed = True

  def __save_state(self, X, Y, F):
    state = {
      "X": X,
      "Y": Y,
      "F": F,
      "PlaceCommandExecuted": self.__is_first_command_executed()
    }
    full_path = Path(self.__state_file)
    if full_path.exists():
      try:
        with open(full_path, "w") as f:
          yaml.dump(state, f, sort_keys=False, default_flow_style=False)
      except:
        return PrintOutput.write_output(output="State file missing", output_file=self.__output_file)
    else:
      try:
        import importlib.resources as pkg_resources
      except ImportError:
        # Try backported to PY<37 `importlib_resources`.
        import importlib_resources as pkg_resources
      try:
        with pkg_resources.path(__package__, full_path.name) as path:
          with open(path, "w") as f:
            yaml.dump(state, f, sort_keys=False, default_flow_style=False)
      except:
        return PrintOutput.write_output(output="State file missing", output_file=self.__output_file)

  def move(self, args):
    """ Moves the robot by step units in the current direction. Default step value is 1. """
    retcode_ok = True
    if not self.__is_first_command_executed():
      # Error
      PrintOutput.write_output(output="The first command must be a PLACE X,Y,F", output_file=self.__output_file)
      retcode_ok = False
    else:
      angle = int(self.__directions_inv[self.__facing])
      (new_x, new_y) = self.__world.next_position(self.__x, self.__y, angle)

      if new_x != self.__x or new_y != self.__y:
        self.__x = new_x
        self.__y = new_y
    return retcode_ok

  def place(self, args):
    """ 
    Places the robot at the given coordinates, with the given direction.
    
    Parameters:
      args (list): list of arguments. This list should include coordinates and direction.
    """
    #
    # Parse arguments
    arg_len = len(args)
    new_coordinates = []
    retcode_ok = True
    if arg_len != 3:
      # Error
      PrintOutput.write_output(output="Wrong command arguments", output_file=self.__output_file)
      retcode_ok = False
    else:
      for i in range(2):
        try:
          new_coordinates.append(int(args[i]))
        except:
          # Error
          PrintOutput.write_output(output="The first two arguments must be integers", output_file=self.__output_file)
          retcode_ok = False
      if not args[2].upper() in self.__get_cardinal_directions():
        # Error
        PrintOutput.write_output(output="Valid directions are NORTH, SOUTH, EAST and WEST", output_file=self.__output_file)
        retcode_ok = False
      
      if self.__world.is_within_boundaries(new_coordinates[0], new_coordinates[1]):
        self.__x = new_coordinates[0]
        self.__y = new_coordinates[1]
        self.__set_first_command_executed()
        self.__facing = args[2].upper()
        self.__angle = int(self.__directions_inv[self.__facing])
    return retcode_ok

  def rotate_left(self, args):
    """ Rotates the robot to the left. """
    retcode_ok = True
    if not self.__is_first_command_executed():
      # Error
      PrintOutput.write_output(output="The first command must be a PLACE X,Y,F", output_file=self.__output_file)
      retcode_ok = False
    self.__angle = (self.__angle + 90) % 360
    self.__facing = self.__get_cardinal_direction(self.__angle)
    return retcode_ok

  def rotate_right(self, args):
    """ Rotates the robot to the right. """
    retcode_ok = True
    if not self.__is_first_command_executed():
      # Error
      PrintOutput.write_output(output="The first command must be a PLACE X,Y,F", output_file=self.__output_file)
      retcode_ok = False
    self.__angle = (self.__angle - 90) % 360
    self.__facing = self.__get_cardinal_direction(self.__angle)
    return retcode_ok

  def report(self, args):
    """ Print the current coordinates and direction of the robot. """
    retcode_ok = True
    if not self.__is_first_command_executed():
      # Error
      PrintOutput.write_output(output="The first command must be a PLACE X,Y,F", output_file=self.__output_file)
      retcode_ok = False
    PrintOutput.write_output(output=f"{self.__x},{self.__y},{self.__facing}", output_file=self.__output_file)
    return retcode_ok

  # ATTRIBUTES
  #
  commands_desc = [
    {"name": "MOVE", "has_parameters": False, "method" : move},
    {"name": "PLACE", "has_parameters": True, "method" : place},
    {"name": "LEFT", "has_parameters": False, "method" : rotate_left},
    {"name": "RIGHT", "has_parameters": False, "method" : rotate_right},
    {"name": "REPORT", "has_parameters": False, "method" : report}
  ]

  def execute(self, commands, output_file=None):
    self.__output_file = output_file
    """ Executes all CLI commands """
    for command in commands:
      command_name = command[0].upper()
      command_args = command[1]
      for dict in self.commands_desc:
        for k, v, *_ in dict.items():
          if command_name == v:
            retcode_ok = dict["method"](self, command_args)
            if not retcode_ok:
              return
    # Finally save current state
    self.__save_state(X = self.__x, Y = self.__y, F = self.__facing)
