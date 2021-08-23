import os
import yaml

# Terminal Colours
# https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-terminal-in-python
class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

class NoPasswordError(Exception):
  pass

def get_journal_key():
  """
  :return the symmetric key stored in ~/.config/seckerwiki/credentials
  """
  path = os.path.expanduser("~/.config/seckerwiki/credentials")

  if not os.path.exists(path):
    raise FileNotFoundError(f"Couldn't find credentials file at {path}")
  
  with open(os.path.abspath(path), 'r') as f:
    auth = yaml.safe_load(f)

    if not 'password' in auth or auth['password'] is None or auth['password'] == "":
      raise NoPasswordError(f"Password isn't defined in credentials file! ({path})")
    return auth['password']

def file_contains_markers(path, start, end):
  """
  :return true if both :start and :end are in the file 
  """

  with open(path, 'r') as f_in:
    contents = f_in.read()
    return start in contents and end in contents

def replace_between_markers(file, start, end, content):
  # TODO check if content is the same - if it is, skip
  with open(file, 'r') as f_in:
    contents = f_in.readlines()

  start_line = contents.index(start)+1
  end_line = contents.index(end)

  del contents[start_line:end_line]

  contents.insert(start_line, content)
  
  with open(file, 'w') as f_out:
    f_out.writelines(contents)

  