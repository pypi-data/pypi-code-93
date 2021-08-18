from enum import Enum

class PrintOutput:
  def __init__(self):
    pass

  @staticmethod
  def write_output(output: str, output_file=None):
    if output_file:
      try:
        with open(output_file, "a") as o:
          return o.write(output)
      except:
        return print(f"Error writing to output file {output_file}")
    else:
      return print(output)