import collections
import os
import shlex
from typing import IO, List, Optional, Union

import yaml
from valohai_yaml.objs import Config, Mount, Step
from valohai_yaml.objs.environment_variable import EnvironmentVariable
from valohai_yaml.objs.input import Input
from valohai_yaml.objs.parameter import Parameter

from jupyhai.consts import JUPYTER_EXECUTION_STEP_NAME
from jupyhai.utils import get_current_image
from jupyhai.utils.notebooks import (
    get_type_name,
    parse_parameters_and_inputs)

yaml.SafeDumper.add_representer(  # type: ignore[no-untyped-call]
    collections.OrderedDict,
    lambda dumper, data: dumper.represent_mapping(
        'tag:yaml.org,2002:map', data.items()
    ),
)


def write_valohai_yaml(
    f: IO, notebook_relative_path: str, content: Union[str, dict], mounts: List[Mount]
) -> None:
    notebook_dir, notebook_name = os.path.split(notebook_relative_path)

    papermill_command = " ".join(
        [
            "papermill -k python3 -f /valohai/config/parameters.yaml",
            shlex.quote("/valohai/repository/{}".format(notebook_relative_path.replace(os.sep, "/"))),
            shlex.quote("/valohai/outputs/{}".format(notebook_name.replace(os.sep, "/"))),
        ]
    )

    command = [
        "bash /valohai/repository/prepare.sh",
        papermill_command,
    ]


    parameters, inputs = parse_parameters_and_inputs(content)

    jupyter_execution_step = Step(
        name=JUPYTER_EXECUTION_STEP_NAME,
        image=get_current_image(),
        command=command,
        parameters=[
            _create_parameter(attr, value)
            for (attr, value) in parameters.items()
        ],
        inputs=[
            Input(name=attr, default=value)
            for (attr, value) in inputs.items()
        ],
        environment_variables=[
            EnvironmentVariable(name="LC_ALL", default="C.UTF-8"),
            EnvironmentVariable(name="LANG", default="C.UTF-8"),
        ],
        mounts=mounts or [],
    )
    config = Config(steps=[jupyter_execution_step])
    yaml.safe_dump(config.serialize(), stream=f)


def _create_parameter(name: str, value: Optional[Union[str, int]]) -> Parameter:
    type_name = get_type_name(value)
    if type_name == "flag":
        return Parameter(
            name=name,
            type="flag",
            pass_true_as="-p %s True" % name,
            pass_false_as="-p %s False" % name,
            optional=True,
        )

    return Parameter(
        name=name,
        type=type_name,
        default=value,
        pass_as="-p %s {v}" % name,
        optional=True,
    )
