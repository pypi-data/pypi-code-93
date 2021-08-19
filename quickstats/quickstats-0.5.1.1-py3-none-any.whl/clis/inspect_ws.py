import click

import fnmatch
from quickstats.components import ExtendedModel
    
@click.group(name='inspect_ws')
def inspect_ws():
    '''
        Tool for inspecting workspace attributes
    '''
    pass

def get_ws_attributes(attrib_name, input_file, ws_name, mc_name, output_file=None, patterns=None):
    attrib_func_map = {
        'pois': ExtendedModel.get_poi_names,
        'datasets': ExtendedModel.get_dataset_names,
        'nuisance_parameters': ExtendedModel.get_nuisance_parameter_names
    }
    attrib_func = attrib_func_map.get(attrib_name, None)
    if attrib_func is None:
        raise ValueError('invalid workspace attribute {}'.format(attrib_name))
    attributes = attrib_func(input_file, ws_name, mc_name)
    if output_file is None:
        print(attributes)
    else:
        with open(output_file, 'w') as output:
            output.write('\n'.join(attributes) + '\n')
    if patterns is not None:
        patterns = patterns.split(',')
        matched = sorted(list(set([attr for pattern in patterns for attr in attributes if fnmatch.fnmatch(attr, pattern)])))
        escaped = sorted(list(set(attributes) - set(matched)))
        print("INFO: Attributes that match the given pattern(s):")
        print(matched)
        print("INFO: Attributes that escaped the given pattern(s):")
        print(escaped)

@inspect_ws.command(name='nuisance_parameters')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-o', '--output_file', default=None, help='Export output to text file')
@click.option('-p', '--patterns', default=None, help='Match nuisance parameters with given patterns (separated by commas).')
def get_ws_nuisance_parameters(input_file, ws_name, mc_name, output_file=None, patterns=None):
    get_ws_attributes('nuisance_parameters', input_file, ws_name, mc_name, output_file, patterns)
    
@inspect_ws.command(name='datasets')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-o', '--output_file', default=None, help='Export output to text file')
@click.option('-p', '--patterns', default=None, help='Match datasets with given patterns (separated by commas).')
def get_ws_datasets(input_file, ws_name, mc_name, output_file=None, patterns=None):
    get_ws_attributes('datasets', input_file, ws_name, mc_name, output_file, patterns)
    
@inspect_ws.command(name='pois')
@click.option('-i', '--input_file', required=True, help='Path to the input workspace file')
@click.option('-w', '--workspace', 'ws_name', default=None, help='Name of workspace. Auto-detect by default.')
@click.option('-m', '--model_config', 'mc_name', default=None, help='Name of model config. Auto-detect by default.')
@click.option('-o', '--output_file', default=None, help='Export output to text file')
@click.option('-p', '--patterns', default=None, help='Match POIs with given patterns (separated by commas).')
def get_ws_pois(input_file, ws_name, mc_name, output_file=None, patterns=None):
    get_ws_attributes('pois', input_file, ws_name, mc_name, output_file, patterns)    