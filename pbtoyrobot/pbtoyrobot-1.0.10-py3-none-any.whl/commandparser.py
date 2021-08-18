from .input_output import PrintOutput

class CommandInfo:
  def __init__(self, exists: bool, has_parameters: bool, output_file=None):
    self.__exists = exists
    self.__has_parameters = has_parameters
    self.__output_file = output_file

  @property
  def exists(self):
    return self.__exists

  @exists.setter
  def exists(self, value: bool):
    self.__exists = value

  @property
  def has_parameters(self):
    return self.__has_parameters

  @has_parameters.setter
  def has_parameters(self, value: bool):
    self.__has_parameters = value

class Command:
  def __init__(self, command_desc, output_file=None):
    self.__command_desc = command_desc
    self.__output_file = output_file

  def get_command_info(self, command: str):
    command_exists = False
    has_parameters = False
    for dict in self.__command_desc:
      for k, v, *_ in dict.items():
        if v == command:
          command_exists = True
          has_parameters = dict["has_parameters"]
          break
    command_info = CommandInfo(command_exists, has_parameters)
    return command_info    

class CommandParser:
  def __init__(self, command_separator: str, argument_separator: str):
    self.__command_separator = command_separator
    self.__argument_separator = argument_separator
    self.__input_file = None
    self.__output_file = None

  def read(self, input, command: Command):
    input_file_command = "--input-file"
    output_file_command = "--output-file"
    self.__command_line = input
    
    input_list = input.split(self.__command_separator)
    if output_file_command in input_list:
      if len(input_list) < 2:
        return print("No output file specified")
      self.__output_file = input_list[input_list.index(output_file_command) + 1] 
    if input_file_command in input_list:
      if len(input_list) < 2:
        return print("No input file specified")
      self.__input_file = input_list[input_list.index(input_file_command) + 1]
      try:
        with open(self.__input_file, "r") as file:
          self.__command_line = file.read()
      except:
        PrintOutput.write_output(output="Error opening file", output_file=self.__output_file)
        return []
    return self.__parse(self.__command_line, command, self.__output_file)

  def __parse(self, input, command: Command, output_file):
    items = input.split(self.__command_separator)
    command_list = []
    i = 0
    while i < len(items):
      command_info = command.get_command_info(items[i])
      if command_info.exists:
        if command_info.has_parameters:
          command_list.append((items[i], items[i + 1].split(self.__argument_separator)))
          i += 2
        else:
          command_list.append((items[i], []))
          i += 1
      else:
        if not items[i]:
          PrintOutput.write_output(output="Parsing error: no command has been specified", 
                                  output_file=self.__output_file)
        else:  
          PrintOutput.write_output(output=f"Parsing error: the command {items[i]} is unknown and will be ignored", 
                                  output_file=self.__output_file)
        i += 1
    return (command_list, self.__output_file)
