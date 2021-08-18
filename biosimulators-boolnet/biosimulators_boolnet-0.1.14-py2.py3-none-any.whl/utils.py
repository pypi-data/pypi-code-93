""" Utilities for working with BoolNet

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-01-08
:Copyright: 2020-2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .config import Config
from .data_model import KISAO_METHOD_ARGUMENTS_MAP
from biosimulators_utils.report.data_model import VariableResults
from biosimulators_utils.sedml.data_model import Variable, Symbol  # noqa: F401
from biosimulators_utils.utils.core import validate_str_value, parse_value
from rpy2.robjects.packages import importr, isinstalled, InstalledSTPackage  # noqa: F401
from rpy2.robjects.vectors import StrVector, ListVector  # noqa: F401
import biosimulators_utils.sedml.validation
import biosimulators_utils.xml.utils
import lxml
import numpy
import re

__all__ = [
    'install_boolnet',
    'get_boolnet',
    'validate_time_course',
    'validate_data_generator_variables',
    'get_variable_target_x_path_keys',
    'set_simulation_method_arg',
    'get_variable_results',
]


def install_boolnet():
    """ Install the BoolNet R package if its not already installed

    Raises:
        :obj:`RuntimeError`: if BoolNet could not be installed
    """
    version = Config().boolnet_version
    if isinstalled('BoolNet') and get_boolnet() != version:
        return

    # load R utilities module for installing packages
    utils = importr('utils')

    # select mirror for installing packages
    utils.chooseCRANmirror(ind=1)

    # install dev tools
    if not isinstalled('devtools'):
        utils.install_packages(StrVector(['devtools']))

    # load dev tools for installing specific versions of tools
    devtools = importr('devtools')

    # install BoolNet
    kw_args = {}
    if version:
        kw_args[version] = StrVector([version])
    devtools.install_version(StrVector(['BoolNet']), **kw_args)

    # check that BoolNet was installed
    if not isinstalled('BoolNet'):
        msg = 'BoolNet {}could not be installed'.format(version + ' ' if version else '')
        raise RuntimeError(msg)


def get_boolnet():
    """ Get the BoolNet R package

    Returns:
        :obj:`rpy2.robjects.packages.InstalledSTPackage`: BoolNet R package
    """
    return importr('BoolNet')


def validate_time_course(simulation):
    """ Validate that BoolNet can execute the desired time course

    Args:
        simulation (:obj:`UniformTimeCourseSimulation`): simulation

    Returns:
        nested of :obj:`list` of :obj:`str`: errors
    """
    errors = []

    if simulation.initial_time != 0:
        errors.append(['Initial time must be 0.'])

    if simulation.output_start_time != int(simulation.output_start_time):
        errors.append(['Output start time must be a non-negative integer.'])

    if simulation.output_end_time != int(simulation.output_end_time):
        errors.append(['Output end time must be a non-negative integer.'])

    if (simulation.output_end_time - simulation.output_start_time) != simulation.number_of_points:
        errors.append(['Number of points ({}) must be equal to the difference between the output end ({}) and start times ({}).'.format(
            simulation.number_of_points, simulation.output_end_time, simulation.output_start_time)])

    return errors


def validate_data_generator_variables(variables, algorithm_kisao_id):
    """ Validate that BoolNet can produce the desired variables of the desired data generators

    Args:
        variables (:obj:`list` of :obj:`Variable`): variables of data generators
        algorithm_kisao_id (:obj:`str`): KiSAO id of the algorithm

    Raises:
        :obj:`NotImplementedError`: a variable requires an unsupported symbol
        :obj:`ValueError`: a variable requires an unsupported type of target
    """
    alg_props = KISAO_METHOD_ARGUMENTS_MAP[algorithm_kisao_id]

    invalid_symbols = set()
    invalid_targets = set()
    for variable in variables:
        if variable.symbol:
            if variable.symbol != Symbol.time:
                invalid_symbols.add(variable.symbol)

        else:
            matches_target = False
            for var_target in alg_props['variable_targets']:
                if re.match(var_target['targets'], variable.target):
                    matches_target = True
                    break
            if not matches_target:
                invalid_targets.add(variable.target)

    if invalid_symbols:
        raise NotImplementedError("".join([
            "The following variable symbols are not supported:\n  - {}\n\n".format(
                '\n  - '.join(sorted(invalid_symbols)),
            ),
            "Symbols must be one of the following:\n  - {}".format(Symbol.time),
        ]))

    if invalid_targets:
        msg = ('The following variable targets are not supported:\n  - {}\n\n'
               'Targets must follow one of the the following patterns:\n  - {}').format(
            '\n  - '.join('`' + target + '`' for target in sorted(invalid_targets)),
            '\n  - '.join('{}: `{}`'.format(vt['variables'], vt['targets'])
                          for vt in sorted(alg_props['variable_targets'], key=lambda vt: vt['variables'])))
        raise ValueError(msg)


def get_variable_target_x_path_keys(variables, model_source):
    """ Get the BoolNet key for each XML XPath target of a SED-ML variable

    Args:
        variables (:obj:`list` of :obj:`Variable`): variables of data generators
        model_source (:obj:`str`): path to model

    Returns:
        :obj:`dict`: dictionary that maps each variable target to the BoolNet key
            of the corresponding qualitative species
    """
    namespaces = biosimulators_utils.xml.utils.get_namespaces_for_xml_doc(lxml.etree.parse(model_source))

    target_x_paths_ids = biosimulators_utils.sedml.validation.validate_variable_xpaths(
        variables,
        model_source,
        attr={
            'namespace': {
                'prefix': 'qual',
                'uri': namespaces['qual'],
            },
            'name': 'id',
        }
    )

    target_x_paths_names = biosimulators_utils.sedml.validation.validate_variable_xpaths(
        variables,
        model_source,
        attr={
            'namespace': {
                'prefix': 'qual',
                'uri': namespaces['qual'],
            },
            'name': 'name',
        }
    )

    target_x_paths_keys = {}
    variable_keys = []
    for variable in variables:
        if variable.target:
            species_id = target_x_paths_ids[variable.target]
            species_name = target_x_paths_names[variable.target]
            species_key = re.sub(r'[^a-zA-Z0-9]', '_', species_name or species_id, re.IGNORECASE)
            target_x_paths_keys[variable.target] = species_key
            variable_keys.append(species_key)

    if len(set(variable_keys)) < len(variable_keys):
        raise ValueError("Each species must generate a unique key (equal to `re.sub(r'^[a-zA-Z0-9]', '_', name or id, re.IGNORECASE)`)")

    return target_x_paths_keys


def set_simulation_method_arg(model, algorithm_kisao_id, parameter_change, simulation_method_args):
    """ Set the value of an argument of BoolNet's ``generateTimeSeries`` method based on
    a SED parameter object (represented by an instance of :obj:`AlgorithmParameterChange`).

    Args:
        model (:obj:`ListVector`): model
        algorithm_kisao_id (:obj:`str`): KiSAO id of the algorithm
        parameter_change (:obj:`AlgorithmParameterChange`): desired value of a parameter of the algorithm
        sim_method_args (:obj:`dict`): arguments for BoolNet's ``generateTimeSeries`` method
    """
    algorithm_props = KISAO_METHOD_ARGUMENTS_MAP[algorithm_kisao_id]

    parameter_kisao_id = parameter_change.kisao_id
    parameter_props = algorithm_props['parameters'].get(parameter_kisao_id, None)
    if parameter_props is None:
        raise NotImplementedError("".join([
            "Algorithm parameter with KiSAO id '{}' is not supported. ".format(parameter_kisao_id),
            "Parameter must have one of the following KiSAO ids:\n  - {}".format('\n  - '.join(
                '{}: {}'.format(parameter_kisao_id, parameter_props['name'])
                for parameter_kisao_id, parameter_props in algorithm_props['parameters'].items())),
        ]))

    value = parameter_change.new_value
    if not validate_str_value(value, parameter_props['type']):
        raise ValueError("'{}' is not a valid {} value for parameter {} ({}). {} {}.".format(
            value, parameter_props['type'].name, parameter_props['name'], parameter_kisao_id,
            parameter_props['name'], parameter_props['invalid_message']))

    parsed_value = parse_value(value, parameter_props['type'])

    transformed_value = parameter_props['transformer'](parsed_value, model)

    simulation_method_args[parameter_props['argument_name']] = transformed_value


def get_variable_results(simulation, variables, target_x_paths_keys, species_results):
    """ Get the predicted values of the desired variables

    Args:
        simulation (:obj:`UniformTimeCourseSimulation`): simulation
        variables (:obj:`list` of :obj:`Variable`): variables of data generators
        target_x_paths_keys (:obj:`dict`): dictionary that maps each variable target to the BoolNet key
            of the corresponding qualitative species
        species_results (:obj:`dict` of :obj:`str` to :obj:`numpy.ndarray`): dictionary that maps the
            id of each species to its predicted values

    Returns:
        :obj:`VariableResults`
    """
    variable_results = VariableResults()
    for variable in variables:
        if variable.symbol:
            variable_result = numpy.linspace(0, int(simulation.output_end_time), int(simulation.output_end_time) + 1)

        else:
            species_key = target_x_paths_keys[variable.target]
            variable_result = species_results[species_key]

        variable_results[variable.id] = variable_result

    return variable_results
