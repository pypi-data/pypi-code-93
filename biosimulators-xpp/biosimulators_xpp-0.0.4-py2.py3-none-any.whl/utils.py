""" Utility methods

:Author: Jonathan Karr <karr@mssm.edu>
:Date: 2021-08-06
:Copyright: 2021, Center for Reproducible Biomedical Modeling
:License: MIT
"""

from .data_model import KISAO_ALGORITHM_MAP
from biosimulators_utils.report.data_model import VariableResults
from biosimulators_utils.sedml.data_model import ModelAttributeChange, UniformTimeCourseSimulation, Symbol, Variable  # noqa: F401
from biosimulators_utils.simulator.utils import get_algorithm_substitution_policy
from biosimulators_utils.warnings import warn, BioSimulatorsWarning
from kisao.data_model import AlgorithmSubstitutionPolicy, ALGORITHM_SUBSTITUTION_POLICY_LEVELS
from kisao.utils import get_preferred_substitute_algorithm_by_ids
import collections  # noqa: F401
import os
import pandas
import subprocess
import tempfile

__all__ = [
    'get_simulation_method_kisao_map',
    'validate_variables',
    'apply_model_changes',
    'set_up_simulation',
    'write_xpp_parameter_file',
    'write_xpp_initial_conditions_file',
    'write_method_to_xpp_simulation_file',
    'exec_xpp_simulation',
    'get_results_of_sed_variables',
]


def get_simulation_method_kisao_map():
    """ Invert the map from KiSAO ids to simulation methods

    Returns:
        :obj:`dict`: inverted map
    """
    simulation_method_kisao_map = {}
    for alg_props in KISAO_ALGORITHM_MAP.values():
        simulation_method_kisao_map[alg_props['id']] = {
            'kisao_id': alg_props['kisao_id'],
            'parameters': {
            },
        }
        for param_props in alg_props['parameters'].values():
            if param_props['enabled']:
                simulation_method_kisao_map[alg_props['id']]['parameters'][param_props['id']] = param_props['kisao_id']
    return simulation_method_kisao_map


def validate_variables(xpp_model, sed_variables):
    """ Validate the SED variables for a XPP model

    Args:
        xpp_model (:obj:`dict`): XPP model
        sed_variables (:obj:`list` of :obj:`Variable`): SED variables
    """
    invalid_symbols = []
    invalid_targets = []
    for sed_variable in sed_variables:
        if sed_variable.symbol:
            if sed_variable.symbol != Symbol.time.value:
                invalid_symbols.append(sed_variable.symbol)

        else:
            if sed_variable.target.upper() not in xpp_model['initial_conditions']:
                invalid_targets.append(sed_variable.target)

    if invalid_symbols:
        msg = 'The following symbols are not supported:\n  {}\n\nThe following symbols are supported:\n  {}'.format(
            '\n  - '.join(sorted(invalid_symbols)),
            '  - ' + Symbol.time.value,
        )
        raise NotImplementedError(msg)

    if invalid_targets:
        msg = 'The following targets are not supported:\n  {}\n\nThe following targets are supported:\n  {}'.format(
            '\n  - '.join(sorted(invalid_targets)),
            '\n  - '.join(sorted(xpp_model['initial_conditions'].keys())),
        )
        raise ValueError(msg)


def apply_model_changes(xpp_model, sed_changes):
    """ Validate the SED variables for a XPP model

    Args:
        xpp_model (:obj:`dict`): XPP model
        sed_changes (:obj:`list` of :obj:`ModelAttributeChange`): SED model attribute changes
    """
    invalid_targets = []
    for change in sed_changes:
        type, sep, target = change.target.partition('.')

        if type == 'parameters':
            block = xpp_model['parameters']
            target = target.lower()

        elif type == 'initialConditions':
            block = xpp_model['initial_conditions']
            target = target.upper()

        else:
            invalid_targets.append(change.target)
            continue

        if target in block:
            block[target] = change.new_value
        else:
            invalid_targets.append(change.target)

    if invalid_targets:
        msg = 'Model changes with the following targets could not be executed:\n  {}\n\nThe following targets are supported:\n  {}'.format(
            '\n  - '.join(sorted(invalid_targets)),
            '\n  - '.join(sorted(
                ['parameters.{}'.format(param) for param in xpp_model['parameters'].keys()] +
                ['initialConditions.{}'.format(var) for var in xpp_model['initial_conditions'].keys()]
            ))
        )
        raise ValueError(msg)


def set_up_simulation(sed_sim, xpp_sim):
    """ Apply SED simulation settings to the configuration of a XPP simulation

    Args:
        sed_sim (:obj:`UniformTimeCourseSimulation`): SED simulation
        xpp_sim (:obj:`dict`): XPP simulation

    Returns:
        :obj:`str`: KiSAO id of the algorithm to execute
    """
    xpp_sim['t0'] = str(sed_sim.initial_time)
    xpp_sim['total'] = str(sed_sim.output_end_time - sed_sim.initial_time)
    xpp_sim['dt'] = str((sed_sim.output_end_time - sed_sim.output_start_time) / sed_sim.number_of_points)
    xpp_sim['njmp'] = str(1)

    substitution_policy = get_algorithm_substitution_policy()
    exec_kisao_id = get_preferred_substitute_algorithm_by_ids(
        sed_sim.algorithm.kisao_id, KISAO_ALGORITHM_MAP.keys(),
        substitution_policy=substitution_policy)

    alg_props = KISAO_ALGORITHM_MAP[exec_kisao_id]
    xpp_sim['meth'] = alg_props['id']

    for temp_alg_props in KISAO_ALGORITHM_MAP.values():
        for param_props in temp_alg_props['parameters'].values():
            if param_props['enabled']:
                xpp_sim.pop(param_props['id'], None)

    if exec_kisao_id == sed_sim.algorithm.kisao_id:
        for change in sed_sim.algorithm.changes:
            param_props = alg_props['parameters'].get(change.kisao_id, None)
            if param_props and param_props['enabled']:
                xpp_sim[param_props['id']] = change.new_value
            else:
                msg = 'Algorithm `{}` ({}) does not support parameter `{}`. The algorithm supports the following parameters:\n  {}'.format(
                    exec_kisao_id, alg_props['id'], change.kisao_id,
                    sorted('\n  - '.join(
                        '{}: {}'.format(param_props['kisao_id'], param_props['id'])
                        for param_props in alg_props['parameters'].values()
                        if param_props['enabled']
                    )),
                )
                if (
                    ALGORITHM_SUBSTITUTION_POLICY_LEVELS[substitution_policy]
                    > ALGORITHM_SUBSTITUTION_POLICY_LEVELS[AlgorithmSubstitutionPolicy.NONE]
                ):
                    warn(msg, BioSimulatorsWarning)
                else:
                    raise NotImplementedError(msg)

    return exec_kisao_id


def write_xpp_parameter_file(parameters, filename):
    """ Write a set of parameters to a XPP parameter (``.par``) file

    Args:
        parameters (:obj:`dict`): dictionary that maps the id of each parameter to its value
        filename (:obj:`str`): path to save the parameters
    """
    with open(filename, 'w') as file:
        file.write('{} Number params\n'.format(len(parameters)))
        for key, val in parameters.items():
            file.write('{} {}\n'.format(val, key))


def write_xpp_initial_conditions_file(initial_conditions, filename):
    """ Write a set of initial conditions to a XPP initial conditions (``.ic``) file

    Args:
        initial_conditions (:obj:`collections.OrderedDict`): dictionary that maps the id of each parameter to its value
        filename (:obj:`str`): path to save the initial conditions
    """
    with open(filename, 'w') as file:
        for val in initial_conditions.values():
            file.write('{}\n'.format(val))


def write_method_to_xpp_simulation_file(simulation_method, in_filename, out_filename):
    """ Overwrite the simulation method settings in an XPP simulation file

    Args:
        simulation_method (:obj:`dict`): dictionary of simulation method settings
        in_filename (:obj:`str`): base XPP simulation file
        out_filename (:obj:`str`): path to save modified XPP simulation file
    """
    lines = []
    with open(in_filename, 'r') as file:
        for line in file:
            if line.startswith('@'):
                continue
            if line.startswith('d') and not ('=' in line and (' ' not in line or line.find('=') < line.find(' '))):
                # check for "done" line; note just the singular character ``d`` defines the "done" line
                break
            lines.append(line)

    for key, val in simulation_method.items():
        lines.append('@ {}={}\n'.format(key, val))

    with open(out_filename, 'w') as file:
        for line in lines:
            file.write(line)


def exec_xpp_simulation(sim_filename, simulation,
                        overwrite_parameters=True,
                        overwrite_initial_conditions=True,
                        overwrite_method=True):
    """ Execute an XPP simulation, optionally overwriting its default parameters and initial conditions

    Args:
        sim_filename (:obj:`str`): path to the XPP file
        simulation (:obj:`dict`): simulation parameters, initial conditions, and method to override defaults
        overwrite_parameters (:obj:`bool`, optional): whether to overwrite the default parameters
        overwrite_initial_conditions (:obj:`bool`, optional): whether to overwrite the default initial conditions
        overwrite_method (:obj:`bool`, optional): whether to overwrite the default simulation method and its settings

    Returns:
        :obj:`pandas.DataFrame`: simulation results
    """
    # set up XPP command
    fid, out_filename = tempfile.mkstemp(suffix='.dat')
    os.close(fid)
    cmd = ["xppaut", sim_filename, '-silent', '-outfile', out_filename]

    # write parameters and initial conditions to files
    if overwrite_parameters:
        fid, parameters_filename = tempfile.mkstemp(suffix='.par')
        os.close(fid)
        write_xpp_parameter_file(simulation['parameters'], parameters_filename)
        cmd.append('-parfile')
        cmd.append(parameters_filename)

    if overwrite_initial_conditions:
        fid, initial_conditions_filename = tempfile.mkstemp(suffix='.ic')
        os.close(fid)
        write_xpp_initial_conditions_file(simulation['initial_conditions'], initial_conditions_filename)
        cmd.append('-icfile')
        cmd.append(initial_conditions_filename)

    if overwrite_method:
        fid, temp_sim_filename = tempfile.mkstemp(suffix='.ode')
        os.close(fid)
        write_method_to_xpp_simulation_file(simulation['simulation_method'], sim_filename, temp_sim_filename)
        cmd[1] = temp_sim_filename

    # execute simulation
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    # read results
    if result.returncode == 0:
        results = pandas.read_csv(out_filename,
                                  sep=' ',
                                  header=None,
                                  usecols=list(range(len(simulation['initial_conditions']) + 1)),
                                  names=[Symbol.time.value] + list(simulation['initial_conditions'].keys()))

    # cleanup temporary files
    if out_filename:
        os.remove(out_filename)

    if overwrite_parameters:
        os.remove(parameters_filename)

    if overwrite_initial_conditions:
        os.remove(initial_conditions_filename)

    if overwrite_method:
        os.remove(temp_sim_filename)

    # raise exception if XPP failed
    if result.returncode != 0:
        raise RuntimeError('XPP failed: {}'.format(result.stdout.decode("utf-8")))

    # return results
    return results


def get_results_of_sed_variables(sed_simulation, xpp_results, sed_variables):
    """ Get the results of a list of SED variables

    Args:
        sed_simulation (:obj:`UniformTimeCourseSimulation`): SED simulation
        xpp_results (:obj:`pandas.DataFrame`): raw results generated by XPP
        sed_variables (:obj:`list` of :obj:`Variable`): SED variables

    Returns:
        :obj:`VariableResults`: results
    """
    variable_results = VariableResults()
    for sed_variable in sed_variables:
        if sed_variable.symbol:
            col = sed_variable.symbol

        else:
            col = sed_variable.target.upper()

        variable_results[sed_variable.id] = xpp_results.loc[:, col][-(sed_simulation.number_of_points + 1):].to_numpy()

    return variable_results
