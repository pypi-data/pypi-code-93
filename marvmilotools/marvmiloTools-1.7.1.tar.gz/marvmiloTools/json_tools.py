import json

from . import dictionary_tools

#load a json file to dict or object
def load(filename, object = True):
    with open(filename, "r") as rd:
        loaded = json.loads(rd.read())
    if object:
        return dictionary_tools.toObj(loaded)
    else:
        return loaded

#save json file from dictionary to file
def save(dictionary, filename):
    with open(filename, "w") as wd:
        if type(dictionary) == dictionary_tools.DictObject:
            wd.write(json.dumps(dictionary.toDict(), indent = 4))
        else:
            wd.write(json.dumps(dictionary, indent = 4))

#write a variable to json
def write(value, json_file, path):
    json_content = load(json_file, object=False)
    current_content = json_content
    for path_val in path:
        if not path_val == path[-1]:
            try:
                current_content = current_content[path_val]
            except:
                raise KeyError("invalid path list")
        else:
            if isinstance(path_val, int):
                current_content.insert(path_val, value)
            else:
                current_content[path_val] = value
    save(json_content, json_file)