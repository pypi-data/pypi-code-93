import json
#import .fs_tools as fs_tools

def is_json(json_text):
  try:
    json_object = json.loads(json_text)
  except ValueError:
    return False
  return True    
  

def load_json(json_file):
  with open(json_file , encoding='utf-8') as json_fh:
    config = json.load(json_fh)
  return config    


def pretty_json(json_input) :
  if type(json_input).__name__ == "str" :
    return (json.dumps(json.loads(json_input), sort_keys=True, indent=2))
  
  if type(json_input).__name__ == "dict" :
    return (json.dumps(json_input, sort_keys=True, indent=2))
  
if __name__ == "__main__": 
  a  = '{"a":6}'
  print (pretty_json(a))
  a  = {"a":6}
  print (pretty_json(a))  
  pass