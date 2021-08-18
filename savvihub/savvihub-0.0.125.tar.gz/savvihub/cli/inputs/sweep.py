import ast
import os
from enum import Enum
from typing import List, Optional

import yaml

from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Context
from savvihub.cli.utils import (
    inquire_float,
    inquire_int,
    inquire_list,
    inquire_text,
    validate_enum,
    validate_float,
    validate_int,
    validate_text,
)


class SweepAlgorithmEnum(str, Enum):
    grid = "grid"
    random = "random"
    bayesian = "bayesian"


class SweepObjectiveTypeEnum(str, Enum):
    maximize = "maximize"
    minimize = "minimize"


class SweepSearchSpaceParameterTypeEnum(str, Enum):
    int = "int"
    float = "float"
    double = "double"
    categorical = "categorical"


def sweep_config_file_callback(ctx: Context, filepath: str) -> Optional[str]:
    if not filepath:
        return

    if not os.path.isfile(filepath):
        raise ExitException(f'File does not exist: {filepath}')

    try:
        yaml.safe_load(filepath)
    except yaml.YAMLError:
        raise ExitException(f'Invalid YAML: {filepath}')

    with open(filepath, 'r') as stream:
        configs = yaml.load(stream, Loader=yaml.FullLoader)

    ctx.spec['experiment'] = configs['spec']['experiment']
    ctx.spec['sweep'] = configs['spec']['sweep']
    return


def algorithm_callback(ctx: Context, algorithm: str) -> str:
    valid_algorithms = [a.value for a in SweepAlgorithmEnum]

    if algorithm:
        ctx.store['algorithm'] = algorithm.lower()
        validate_enum(
            ctx.store['algorithm'],
            SweepAlgorithmEnum, 
            f'Invalid sweep algorithm: {algorithm}. (choose from {", ".join(valid_algorithms)})'
        )
        return ctx.store['algorithm']

    ctx.store['algorithm'] = inquire_list(
        "Please select an algorithm",
        [(x.capitalize(), x) for x in valid_algorithms],
    )
    return ctx.store['algorithm']


def objective_type_callback(ctx: Context, objective_type: str) -> str:
    valid_objective_types = [t.value for t in SweepObjectiveTypeEnum]

    if objective_type:
        ctx.store['objective_type'] = objective_type.lower()
        validate_enum(
            ctx.store['objective_type'],
            SweepObjectiveTypeEnum, 
            f'Invalid objective type: {objective_type}. (choose from {", ".join(valid_objective_types)})'
        )
        return ctx.store['objective_type']

    ctx.store['objective_type'] = inquire_list(
        "Please choose an objective type",
        [(x.capitalize(), x) for x in valid_objective_types],
    )
    return ctx.store['objective_type']


def objective_goal_callback(ctx: Context, objective_goal: float) -> float:
    ctx.store['objective_goal'] = objective_goal

    if ctx.store['objective_goal'] is None:
        ctx.store['objective_goal'] = inquire_float("Objective goal (between 0 and 1)")

    validate_float(
        ctx.store['objective_goal'],
        f'Invalid objective goal: {objective_goal}. Please enter a decimal between 0 and 1.',
        gte=0, lte=1,
    )
    return ctx.store['objective_goal']


def objective_metric_callback(ctx: Context, objective_metric: str) -> str:
    ctx.store['objective_metric'] = objective_metric
    if not ctx.store['objective_metric']:
        ctx.store['objective_metric'] = inquire_text("Objective metric")

    validate_text(ctx.store['objective_metric'], "Objective metric cannot be blank.")
    return ctx.store['objective_metric']


def _parse_parameter(unparsed_parameter, valid_parameter_types):
    parameter = ast.literal_eval(unparsed_parameter)

    # Parameter name
    parameter["name"] = parameter.get("name")
    validate_text(parameter["name"], "Parameter name cannot be blank.")
    
    # Parameter type
    parameter["type"] = parameter.get("type")
    validate_enum(
        parameter["type"],
        SweepSearchSpaceParameterTypeEnum, 
        f'Invalid parameter type {parameter["type"]}. (choose from {", ".join(valid_parameter_types)}) '
    )

    # Parameter values
    parameter_range = parameter.get("range", {})
    parameter["range"]["list"] = parameter_range.get("list")
    parameter["range"]["min"] = parameter_range.get("min")
    parameter["range"]["max"] = parameter_range.get("max")

    # Parameter values: list
    if parameter["range"]["list"] or parameter["type"] == SweepSearchSpaceParameterTypeEnum.categorical:
        if not isinstance(parameter["range"]["list"], list) or len(parameter["range"]["list"]) == 0:
            raise ExitException("Invalid parameter range values.")

        if parameter["type"] == SweepSearchSpaceParameterTypeEnum.int:
            for v in parameter["range"]["list"]:
                validate_int(v, "Invalid parameter range values.")
        elif parameter["type"] in [SweepSearchSpaceParameterTypeEnum.float, SweepSearchSpaceParameterTypeEnum.double]:
            for v in parameter["range"]["list"]:
                validate_float(v, "Invalid parameter range values.")

    # Parameter values: min/max
    elif parameter["range"]["min"] and parameter["range"]["max"]:
        validate_int(parameter["range"]["min"], "Invalid parameter range values.")
        validate_int(parameter["range"]["max"], "Invalid parameter range values.", gt=parameter["range"]["min"])

    else:
        raise ExitException("Invalid parameter range type (must be min/max or list).")
    
    return parameter


def search_space_parameters_callback(ctx: Context, unparsed_parameters: List[str]) -> Optional[List[str]]:
    search_space_parameters = []
    valid_parameter_types = [t.value for t in SweepSearchSpaceParameterTypeEnum]

    # Via options
    if unparsed_parameters:
        for unparsed_parameter in unparsed_parameters:
            parameter = _parse_parameter(unparsed_parameter, valid_parameter_types)
            search_space_parameters.append(parameter)

        ctx.store["search_space"] = search_space_parameters
        return

    # Via inquirer
    while True:
        parameter = {}
        parameter["range"] = {}

        count = len(search_space_parameters) + 1
        message_prefix = f'Search space parameter #{count}'

        # Parameter name
        parameter["name"] = inquire_text(f'{message_prefix} - name')
        validate_text(parameter["name"], "Parameter name cannot be blank.")

        # Parameter type
        parameter["type"] = inquire_list(f'{message_prefix} - type', valid_parameter_types)

        # Parameter range type (min_max / list)
        if parameter["type"] == SweepSearchSpaceParameterTypeEnum.categorical:
            range_type = "list"
        else:
            range_types = [("[1] Min, max", "min_max") , ("[2] List", "list")]
            range_type = inquire_list(f'{message_prefix} - range type', range_types)
        
        # Parameter values
        if range_type == "min_max":
            parameter["range"]["min"] = inquire_int(f'{message_prefix} - minimum')
            parameter["range"]["max"] = inquire_int(f'{message_prefix} - maximum')

            validate_int(parameter["range"]["max"], "Invalid parameter range values.", gt=parameter["range"]["min"])

            if ctx.store['algorithm'] == SweepAlgorithmEnum.grid and \
                    parameter["type"] != SweepSearchSpaceParameterTypeEnum.categorical:
                parameter["step"] = inquire_int(f'{message_prefix} - step')
        else:
            examples = "[64, 128, 256]"
            if parameter["type"] == SweepSearchSpaceParameterTypeEnum.categorical:
                examples = '["sgd", "adam"]'

            range_list_string = inquire_text(f'{message_prefix} - list (ex. {examples})')
            parameter["range"]["list"] = ast.literal_eval(range_list_string)

            if not isinstance(parameter["range"]["list"], list) or len(parameter["range"]["list"]) == 0:
                raise ExitException("Invalid parameter range values.")

            if parameter["type"] == SweepSearchSpaceParameterTypeEnum.int:
                for v in parameter["range"]["list"]:
                    validate_int(v, "Invalid parameter range values.")
            elif parameter["type"] in [SweepSearchSpaceParameterTypeEnum.float, SweepSearchSpaceParameterTypeEnum.double]:
                for v in parameter["range"]["list"]:
                    validate_float(v, "Invalid parameter range values.")

        # Add parameter to list
        search_space_parameters.append(parameter)
        
        # Add another or finish
        if inquire_list("Choose", [
            ("[1] Add another parameter", False),
            ("[2] Finish adding parameters", True),
        ]):
            ctx.store["search_space"] = search_space_parameters
            return


def max_experiment_count_callback(ctx: Context, max_experiment_count: int) -> int:
    ctx.store['max_experiment_count'] = max_experiment_count
    if ctx.store['max_experiment_count'] is None:
        ctx.store['max_experiment_count'] = inquire_int("Maximum number of experiments")

    validate_int(
        ctx.store['max_experiment_count'], 
        f'Invalid max experiment count: {ctx.store["max_experiment_count"]}. Must be greater than 0.',
        gt=0,
    )
    return ctx.store['max_experiment_count']


def parallel_experiment_count_callback(ctx: Context, parallel_experiment_count: int) -> int:
    assert ctx.store['max_experiment_count']

    ctx.store['parallel_experiment_count'] = parallel_experiment_count
    if ctx.store['parallel_experiment_count'] is None:
        ctx.store['parallel_experiment_count'] = inquire_int("Number of experiments to be run in parallel", default=1)

    validate_int(
        ctx.store["parallel_experiment_count"],
        (
            f'Invalid parallel experiment count: {ctx.store["parallel_experiment_count"]}. '
            f'Must be greater than 0, at most {ctx.store["max_experiment_count"]} (max experiment count).'
        ),
        gt=0, lte=ctx.store['max_experiment_count'],
    )
    return ctx.store['parallel_experiment_count']


def max_failed_experiment_count_callback(ctx: Context, max_failed_experiment_count: int) -> int:
    assert ctx.store['max_experiment_count']

    ctx.store['max_failed_experiment_count'] = max_failed_experiment_count
    if ctx.store['max_failed_experiment_count'] is None:
        ctx.store['max_failed_experiment_count'] = inquire_int(
            "Maximum number of experiments to allow to fail",
            default=ctx.store['max_experiment_count']
        )

    validate_int(
        ctx.store["parallel_experiment_count"],
        (
            f'Invalid max failed experiment count: {ctx.store["max_failed_experiment_count"]}. '
            f'Must be greater than 0, at most {ctx.store["max_experiment_count"]} (max experiment count).'
        ),
        gt=0, lte=ctx.store['max_experiment_count'],
    )
    return ctx.store['max_failed_experiment_count']
