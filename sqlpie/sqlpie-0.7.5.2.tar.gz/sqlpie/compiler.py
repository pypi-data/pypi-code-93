from jinja2 import Environment

class Compiler:

  def __init__(self, query_path, payload = {}):
    self.file = open(query_path, 'r')
    self.raw_template = self.file.read()
    self.file.close()
    self.payload = payload
    self.jinja = Environment()
    self.query_template = self.jinja.from_string(self.raw_template)
    self.query_string = self.query_template.render(self.payload)