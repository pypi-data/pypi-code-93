import os
import json

LIGRAL_PATH = 'ligral.exe'
JSON_STORE_PATH = os.path.join(os.path.dirname(__file__), 'nodejsons')
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nodes.py')


def gen_jsons():
    os.system(f'{LIGRAL_PATH}  doc --json --output {JSON_STORE_PATH}')


def create_default_instance(type: str):
    if type == 'signal':
        return 0
    elif type == 'string':
        return 'string'
    else:
        raise NotImplementedError(f'type {repr(type)} is not implemented')


def parse_jsons(path: str):
    with open(path, 'rb') as f:
        node = json.load(f)
    class_name = node['type']
    info = {}
    print(node)
    for d in node['parameters']:
        if d['required']:
            info[d['name']] = create_default_instance(d['type'])
    input_ports = node['in-ports']
    output_ports = node['out-ports']
    code = f"""
class {class_name}(BaseLigralGenerator):
    def __init__(self):
        super().__init__()
        self.input_args_labels = {repr(input_ports)}
        self.output_ports_labels = {repr(output_ports)}
        self.parameters = {repr(node['parameters'])}
        self.info = {repr(info)}
    """
    # print(code)
    return code


def gen_code():
    files = os.listdir(JSON_STORE_PATH)
    code = \
        """\"\"\"
This file is generated by Ligral Class Generator.
DO NOT EDIT or your modification will be overwritten!
\"\"\"

from .simulation import BaseLigralGenerator
            """
    for file_name in files:
        json_file_abso_path = os.path.join(JSON_STORE_PATH, file_name)
        code += parse_jsons(json_file_abso_path)
    with open(OUTPUT_PATH, 'w') as f:
        f.write(code)


if __name__ == '__main__':
    # gen_jsons()
    gen_code()
