class FileLoader:
  """Base class for all loaders, specifying their functionality."""
  def __init__(self, path):
    self.path = path
  
  def load(self):
    pass

class FileSaver:
  """Base class for all loaders, specifying their functionality."""
  def __init__(self, path):
    self.path = path
  
  def save(self, array):
    pass
  
  @staticmethod
  def query_dims(arrayshape):
    pass
