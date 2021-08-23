import os
import pathlib
import click
from .utils import one_to_one_map, imports, example
from gstorm.helpers.gql_schema_helpers import load_schema_from_file
from ValiotWorker.Logging import log, LogLevel
from gstorm.helpers.os_helpers import query_yes_no
from gstorm.helpers.str_handling import scream_case

def _build_classes(schema, dir_to_save, mpath):

    for class_name, attributes in schema.items():
        path_and_file = os.path.join(dir_to_save, class_name + ".py")
        log(LogLevel.WARNING, f'Building class file for {class_name} model')
        # Extract class attributes for enumeration
        cls_attrs_buffer = ''
        with open(path_and_file, 'w') as file:
            # * Clases GraphQLType
            if attributes['kind'] == 'TYPE':
                cls_attrs = [
                    scream_case(field['name']) 
                    for field in attributes['fields']
                    if field['type']['kind'] == 'SCALAR'
                ]
                cls_attrs = ['ID'] + sorted(cls_attrs) +  ['INSERTED_AT', 'UPDATED_AT']
                # build ClassNameAttrs class (Enum):
                cls_attrs_buffer = f'\nclass {class_name}Attrs(Enum):\n'
                for attr in cls_attrs:
                    cls_attrs_buffer += f"\t{attr} = '{attr}'\n"
                file.write( imports )
                buffer_written = f"\nmpath = '{mpath}'\n\n@attr.s\nclass {class_name}(GraphQLType):\n"
                for field in attributes['fields']:
                    name = field['name']
                    kind = field['type']['kind']
                    temp = field['type']['name']
                    has_one = field['has_one']
                    unique = field['unique']
                    if any([unique, has_one]):
                        metadata = ", metadata={{{0}{1}{2}}}"\
                        .format("'unique':True" if unique else '', \
                            ',' if all([has_one, unique]) else '', \
                            "'has_one':True" if has_one else '')
                    else: metadata = ''
                    type_name, default = (temp,"None") if temp not in one_to_one_map else one_to_one_map[temp]
                            
                    if kind == "OBJECT":
                        buffer_written += \
                            f"    {name}: '{type_name}' = attr.ib(default={default}, repr=gql_repr, converter=convert_to(mpath,'{type_name}') {metadata})\n"
                    elif kind == "LIST":
                        buffer_written += \
                            f"    {name}: List[GraphQLType] = attr.ib(factory=list, repr=gql_list_repr, converter=list_convert_to(mpath,'{type_name}'), metadata={{'type':list}})\n"
                    elif kind == "ENUM":
                        file.write(f"from .{type_name} import {type_name}\n")
                        buffer_written += \
                            f"    {name}: {type_name} = attr.ib(default='{schema[type_name]['enumValues'][0]}', converter=convert_to(mpath,'{type_name}'){metadata})\n"
                    else:
                        buffer_written += \
                            f"    {name}: {type_name} = attr.ib(default={default}{metadata})\n"

            # * Clases Enum
            elif attributes['kind'] == 'ENUM':
                file.write("from enum import Enum")
                buffer_written = f"\n\nclass {class_name}(Enum):\n"     
                for enum in attributes['enumValues']:
                    buffer_written += f"    {enum} = '{enum}'\n"
            if (cls_attrs_buffer):
                file.write( cls_attrs_buffer )
            file.write(buffer_written)

    # Creacion del archivo __init__.py
    path_and_file = os.path.join(dir_to_save, "__init__.py")
    with open(path_and_file, 'w') as file:
        file.write('\n# Models and Attribute enums\n')
        for class_name, attributes in schema.items():
            if attributes['kind'] != 'TYPE':
                continue
            file.write(f"from .{class_name} import {class_name}, {class_name}Attrs\n")
        file.write('\n# Enumerations\n')
        for class_name, attributes in schema.items():
            if attributes['kind'] != 'ENUM':
                continue
            file.write(f"from .{class_name} import {class_name}\n")

@click.command()
@click.option('--src', default=None, help='Graphql schema file to analyze')
@click.option('--output', default=None, help='output directory for the GQL model files')
def build_classes(src: str, output: str):
    # from "tests/models" or "tests/models/" to "tests.models"
    mpath = output.rstrip('/').replace('/', '.')
    output = os.path.join(os.getcwd(), output)
    out_path_exists = os.path.isdir(output)
    if not out_path_exists:
        log(LogLevel.WARNING, 'Output directory not found, this command will create a directory with files in:')
        log(LogLevel.WARNING, f'{output}')
        answer = query_yes_no("Do you want to proceed?", "no", LogLevel.WARNING)
        if not answer:
            log(LogLevel.INFO, 'Exiting without building any class.')
            return
        pathlib.Path(output).mkdir(parents=True, exist_ok=True)
    schema = load_schema_from_file(src)
    _build_classes(schema, output, mpath)
    log(LogLevel.SUCCESS, 'Done')
