

def parse(arg_file, description=None):
    """
    :param description: string
    :param arg_file: string
    :returns: dict

    Example YAML file for arguments:
    ---
    string:
      help: Example string parameter.
      type: str
      default: 'default string'
    bool_false:
      help: Example boolean with a default of false.
      default: False
      action: 'store_true'
    bool_true:
      help: Example boolean with a default of true
      default: True
      action: 'store_false'
    list:
      help: List of n number of unnamed arguments.
      default: ''
      nargs: '*'

    Example usage:
    python3.8 ./script.py --string "this is a test string" --bool_false --bool_true --list a b c
    returns
    {'string': 'this is a test string', 'bool_false': True, 'bool_true': False, 'list': ['a', 'b', 'c']}
    """
    import argparse
    from pydoc import locate
    import yaml
    with open(arg_file, 'r') as y:
        data = yaml.load(y, Loader=yaml.FullLoader)
        parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        for argument, parameters in data.items():
            if 'type' in parameters.keys():
                parameters['type'] = locate(parameters['type'])
            parser.add_argument('--' + argument, **parameters)
        return vars(parser.parse_args())

