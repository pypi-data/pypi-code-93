import logging
log = logging.getLogger("📡dotrelay")
log.addHandler(logging.NullHandler()) # ignore log messages by defualt

import os
import sys

MAX_DEPTH = 10
RELAY_FILENAME = '.relay'

def init(path, max_depth=MAX_DEPTH):
  radio = Radio(path, max_depth)
  radio.__enter__()
  return radio

# use context manager
class Radio():
  def __init__(self, origin_path, max_depth=MAX_DEPTH):
    self.origin_path = os.path.abspath(origin_path)
    self.max_depth = max_depth
    self.resolved_path = None
  
  def __enter__(self):
    '''scan ancestor directories up to a certain depth for the first relay file and add that directory to the module import context'''

    curr_path = self.origin_path

    for depth in range(1, self.max_depth+1):
      curr_path = os.path.dirname(curr_path) # go up to parent path
      relay_file_path = os.path.join(curr_path, RELAY_FILENAME)
      if os.path.exists(relay_file_path):
        log.info(f'depth of {depth} reached - .relay file found in {curr_path} - adding to module import context...')
        self.resolved_path = curr_path
        if self.resolved_path not in sys.path:
          sys.path.append(self.resolved_path)
        break
      else:
        log.info(f'depth of {depth} reached - .relay file not found in {curr_path} - checking next parent...')

    if not self.resolved_path:    
      log.warning(f'max depth of {depth} reached - .relay file not found in any ancestor paths - no changes were made to module import context.')
    
    return self

  def __exit__(self, type, value, traceback):
    '''remove relayed directory from the module import context'''

    if self.resolved_path:
      log.debug(f'finished relaying {self.resolved_path} to {self.origin_path} - removing from module import context...')
      sys.path.remove(self.resolved_path)