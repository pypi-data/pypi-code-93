import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import Component as _Component_2b0ad27f, Project as _Project_57d89203


class Task(metaclass=jsii.JSIIMeta, jsii_type="projen.tasks.Task"):
    '''(experimental) A task that can be performed on the project.

    Modeled as a series of shell
    commands and subtasks.

    :stability: experimental
    '''

    def __init__(
        self,
        name: builtins.str,
        *,
        exec: typing.Optional[builtins.str] = None,
        condition: typing.Optional[builtins.str] = None,
        cwd: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        required_env: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param name: -
        :param exec: (experimental) Shell command to execute as the first command of the task. Default: - add steps using ``task.exec(command)`` or ``task.spawn(subtask)``
        :param condition: (experimental) A shell command which determines if the this task should be executed. If the program exits with a zero exit code, steps will be executed. A non-zero code means that task will be skipped.
        :param cwd: (experimental) The working directory for all steps in this task (unless overridden by the step). Default: - process.cwd()
        :param description: (experimental) The description of this build command. Default: - the task name
        :param env: (experimental) Defines environment variables for the execution of this task. Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``. Default: {}
        :param required_env: (experimental) A set of environment variables that must be defined in order to execute this task. Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        props = TaskOptions(
            exec=exec,
            condition=condition,
            cwd=cwd,
            description=description,
            env=env,
            required_env=required_env,
        )

        jsii.create(Task, self, [name, props])

    @jsii.member(jsii_name="builtin")
    def builtin(self, name: builtins.str) -> None:
        '''(experimental) Execute a builtin task.

        Builtin tasks are programs bundled as part of projen itself and used as
        helpers for various components.

        In the future we should support built-in tasks from external modules.

        :param name: The name of the builtin task to execute (e.g. ``release/resolve-version``).

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "builtin", [name]))

    @jsii.member(jsii_name="env")
    def env(self, name: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds an environment variable to this task.

        :param name: The name of the variable.
        :param value: The value. If the value is surrounded by ``$()``, we will evaluate it within a subshell and use the result as the value of the environment variable.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "env", [name, value]))

    @jsii.member(jsii_name="exec")
    def exec(
        self,
        command: builtins.str,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Executes a shell command.

        :param command: Shell command.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "exec", [command, options]))

    @jsii.member(jsii_name="prepend")
    def prepend(
        self,
        shell: builtins.str,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(deprecated) Adds a command at the beginning of the task.

        :param shell: The command to add.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :deprecated: use ``prependExec()``

        :stability: deprecated
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "prepend", [shell, options]))

    @jsii.member(jsii_name="prependExec")
    def prepend_exec(
        self,
        shell: builtins.str,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a command at the beginning of the task.

        :param shell: The command to add.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "prependExec", [shell, options]))

    @jsii.member(jsii_name="prependSay")
    def prepend_say(
        self,
        message: builtins.str,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Says something at the beginning of the task.

        :param message: Your message.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "prependSay", [message, options]))

    @jsii.member(jsii_name="prependSpawn")
    def prepend_spawn(
        self,
        subtask: "Task",
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Adds a spawn instruction at the beginning of the task.

        :param subtask: The subtask to execute.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "prependSpawn", [subtask, options]))

    @jsii.member(jsii_name="reset")
    def reset(
        self,
        command: typing.Optional[builtins.str] = None,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Reset the task so it no longer has any commands.

        :param command: the first command to add to the task after it was cleared.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "reset", [command, options]))

    @jsii.member(jsii_name="say")
    def say(
        self,
        message: builtins.str,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Say something.

        :param message: Your message.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "say", [message, options]))

    @jsii.member(jsii_name="spawn")
    def spawn(
        self,
        subtask: "Task",
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Spawns a sub-task.

        :param subtask: The subtask to execute.
        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        options = TaskStepOptions(cwd=cwd, name=name)

        return typing.cast(None, jsii.invoke(self, "spawn", [subtask, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) Task name.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="steps")
    def steps(self) -> typing.List["TaskStep"]:
        '''(experimental) Returns an immutable copy of all the step specifications of the task.

        :stability: experimental
        '''
        return typing.cast(typing.List["TaskStep"], jsii.get(self, "steps"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="condition")
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A command to execute which determines if the task should be skipped.

        If it
        returns a zero exit code, the task will not be executed.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "condition"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the task.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))


@jsii.data_type(
    jsii_type="projen.tasks.TaskCommonOptions",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "cwd": "cwd",
        "description": "description",
        "env": "env",
        "required_env": "requiredEnv",
    },
)
class TaskCommonOptions:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        cwd: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        required_env: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param condition: (experimental) A shell command which determines if the this task should be executed. If the program exits with a zero exit code, steps will be executed. A non-zero code means that task will be skipped.
        :param cwd: (experimental) The working directory for all steps in this task (unless overridden by the step). Default: - process.cwd()
        :param description: (experimental) The description of this build command. Default: - the task name
        :param env: (experimental) Defines environment variables for the execution of this task. Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``. Default: {}
        :param required_env: (experimental) A set of environment variables that must be defined in order to execute this task. Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if cwd is not None:
            self._values["cwd"] = cwd
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if required_env is not None:
            self._values["required_env"] = required_env

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command which determines if the this task should be executed.

        If
        the program exits with a zero exit code, steps will be executed. A non-zero
        code means that task will be skipped.

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cwd(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory for all steps in this task (unless overridden by the step).

        :default: - process.cwd()

        :stability: experimental
        '''
        result = self._values.get("cwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of this build command.

        :default: - the task name

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Defines environment variables for the execution of this task.

        Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def required_env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A set of environment variables that must be defined in order to execute this task.

        Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        result = self._values.get("required_env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskCommonOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.tasks.TaskOptions",
    jsii_struct_bases=[TaskCommonOptions],
    name_mapping={
        "condition": "condition",
        "cwd": "cwd",
        "description": "description",
        "env": "env",
        "required_env": "requiredEnv",
        "exec": "exec",
    },
)
class TaskOptions(TaskCommonOptions):
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        cwd: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        required_env: typing.Optional[typing.Sequence[builtins.str]] = None,
        exec: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param condition: (experimental) A shell command which determines if the this task should be executed. If the program exits with a zero exit code, steps will be executed. A non-zero code means that task will be skipped.
        :param cwd: (experimental) The working directory for all steps in this task (unless overridden by the step). Default: - process.cwd()
        :param description: (experimental) The description of this build command. Default: - the task name
        :param env: (experimental) Defines environment variables for the execution of this task. Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``. Default: {}
        :param required_env: (experimental) A set of environment variables that must be defined in order to execute this task. Task execution will fail if one of these is not defined.
        :param exec: (experimental) Shell command to execute as the first command of the task. Default: - add steps using ``task.exec(command)`` or ``task.spawn(subtask)``

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if cwd is not None:
            self._values["cwd"] = cwd
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if required_env is not None:
            self._values["required_env"] = required_env
        if exec is not None:
            self._values["exec"] = exec

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command which determines if the this task should be executed.

        If
        the program exits with a zero exit code, steps will be executed. A non-zero
        code means that task will be skipped.

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cwd(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory for all steps in this task (unless overridden by the step).

        :default: - process.cwd()

        :stability: experimental
        '''
        result = self._values.get("cwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of this build command.

        :default: - the task name

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Defines environment variables for the execution of this task.

        Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def required_env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A set of environment variables that must be defined in order to execute this task.

        Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        result = self._values.get("required_env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exec(self) -> typing.Optional[builtins.str]:
        '''(experimental) Shell command to execute as the first command of the task.

        :default: - add steps using ``task.exec(command)`` or ``task.spawn(subtask)``

        :stability: experimental
        '''
        result = self._values.get("exec")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class TaskRuntime(metaclass=jsii.JSIIMeta, jsii_type="projen.tasks.TaskRuntime"):
    '''(experimental) The runtime component of the tasks engine.

    :stability: experimental
    '''

    def __init__(self, workdir: builtins.str) -> None:
        '''
        :param workdir: -

        :stability: experimental
        '''
        jsii.create(TaskRuntime, self, [workdir])

    @jsii.member(jsii_name="runTask")
    def run_task(
        self,
        name: builtins.str,
        parents: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''(experimental) Runs the task.

        :param name: The task name.
        :param parents: -

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "runTask", [name, parents]))

    @jsii.member(jsii_name="tryFindTask")
    def try_find_task(self, name: builtins.str) -> typing.Optional["TaskSpec"]:
        '''(experimental) Find a task by name, or ``undefined`` if not found.

        :param name: -

        :stability: experimental
        '''
        return typing.cast(typing.Optional["TaskSpec"], jsii.invoke(self, "tryFindTask", [name]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> "TasksManifest":
        '''(experimental) The contents of tasks.json.

        :stability: experimental
        '''
        return typing.cast("TasksManifest", jsii.get(self, "manifest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tasks")
    def tasks(self) -> typing.List["TaskSpec"]:
        '''(experimental) The tasks in this project.

        :stability: experimental
        '''
        return typing.cast(typing.List["TaskSpec"], jsii.get(self, "tasks"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workdir")
    def workdir(self) -> builtins.str:
        '''(experimental) The root directory of the project and the cwd for executing tasks.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "workdir"))


@jsii.data_type(
    jsii_type="projen.tasks.TaskSpec",
    jsii_struct_bases=[TaskCommonOptions],
    name_mapping={
        "condition": "condition",
        "cwd": "cwd",
        "description": "description",
        "env": "env",
        "required_env": "requiredEnv",
        "name": "name",
        "steps": "steps",
    },
)
class TaskSpec(TaskCommonOptions):
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        cwd: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        required_env: typing.Optional[typing.Sequence[builtins.str]] = None,
        name: builtins.str,
        steps: typing.Optional[typing.Sequence["TaskStep"]] = None,
    ) -> None:
        '''(experimental) Specification of a single task.

        :param condition: (experimental) A shell command which determines if the this task should be executed. If the program exits with a zero exit code, steps will be executed. A non-zero code means that task will be skipped.
        :param cwd: (experimental) The working directory for all steps in this task (unless overridden by the step). Default: - process.cwd()
        :param description: (experimental) The description of this build command. Default: - the task name
        :param env: (experimental) Defines environment variables for the execution of this task. Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``. Default: {}
        :param required_env: (experimental) A set of environment variables that must be defined in order to execute this task. Task execution will fail if one of these is not defined.
        :param name: (experimental) Task name.
        :param steps: (experimental) Task steps.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if condition is not None:
            self._values["condition"] = condition
        if cwd is not None:
            self._values["cwd"] = cwd
        if description is not None:
            self._values["description"] = description
        if env is not None:
            self._values["env"] = env
        if required_env is not None:
            self._values["required_env"] = required_env
        if steps is not None:
            self._values["steps"] = steps

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''(experimental) A shell command which determines if the this task should be executed.

        If
        the program exits with a zero exit code, steps will be executed. A non-zero
        code means that task will be skipped.

        :stability: experimental
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cwd(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory for all steps in this task (unless overridden by the step).

        :default: - process.cwd()

        :stability: experimental
        '''
        result = self._values.get("cwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of this build command.

        :default: - the task name

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Defines environment variables for the execution of this task.

        Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``.

        :default: {}

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def required_env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''(experimental) A set of environment variables that must be defined in order to execute this task.

        Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        result = self._values.get("required_env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) Task name.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def steps(self) -> typing.Optional[typing.List["TaskStep"]]:
        '''(experimental) Task steps.

        :stability: experimental
        '''
        result = self._values.get("steps")
        return typing.cast(typing.Optional[typing.List["TaskStep"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.tasks.TaskStepOptions",
    jsii_struct_bases=[],
    name_mapping={"cwd": "cwd", "name": "name"},
)
class TaskStepOptions:
    def __init__(
        self,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for task steps.

        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cwd is not None:
            self._values["cwd"] = cwd
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def cwd(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory for this step.

        :default: - determined by the task

        :stability: experimental
        '''
        result = self._values.get("cwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Step name.

        :default: - no name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskStepOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Tasks(
    _Component_2b0ad27f,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.tasks.Tasks",
):
    '''(experimental) Defines project tasks.

    Tasks extend the projen CLI by adding subcommands to it. Task definitions are
    synthesized into ``.projen/tasks.json``.

    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        jsii.create(Tasks, self, [project])

    @jsii.member(jsii_name="addEnvironment")
    def add_environment(self, name: builtins.str, value: builtins.str) -> None:
        '''(experimental) Adds global environment.

        :param name: Environment variable name.
        :param value: Value.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addEnvironment", [name, value]))

    @jsii.member(jsii_name="addTask")
    def add_task(
        self,
        name: builtins.str,
        *,
        exec: typing.Optional[builtins.str] = None,
        condition: typing.Optional[builtins.str] = None,
        cwd: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        required_env: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> Task:
        '''(experimental) Adds a task to a project.

        :param name: The name of the task.
        :param exec: (experimental) Shell command to execute as the first command of the task. Default: - add steps using ``task.exec(command)`` or ``task.spawn(subtask)``
        :param condition: (experimental) A shell command which determines if the this task should be executed. If the program exits with a zero exit code, steps will be executed. A non-zero code means that task will be skipped.
        :param cwd: (experimental) The working directory for all steps in this task (unless overridden by the step). Default: - process.cwd()
        :param description: (experimental) The description of this build command. Default: - the task name
        :param env: (experimental) Defines environment variables for the execution of this task. Values in this map will be evaluated in a shell, so you can do stuff like ``$(echo "foo")``. Default: {}
        :param required_env: (experimental) A set of environment variables that must be defined in order to execute this task. Task execution will fail if one of these is not defined.

        :stability: experimental
        '''
        options = TaskOptions(
            exec=exec,
            condition=condition,
            cwd=cwd,
            description=description,
            env=env,
            required_env=required_env,
        )

        return typing.cast(Task, jsii.invoke(self, "addTask", [name, options]))

    @jsii.member(jsii_name="removeTask")
    def remove_task(self, name: builtins.str) -> typing.Optional[Task]:
        '''(experimental) Removes a task from a project.

        :param name: The name of the task to remove.

        :return: The ``Task`` that was removed, otherwise ``undefined``.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Task], jsii.invoke(self, "removeTask", [name]))

    @jsii.member(jsii_name="tryFind")
    def try_find(self, name: builtins.str) -> typing.Optional[Task]:
        '''(experimental) Finds a task by name.

        Returns ``undefined`` if the task cannot be found.

        :param name: The name of the task.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[Task], jsii.invoke(self, "tryFind", [name]))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="MANIFEST_FILE")
    def MANIFEST_FILE(cls) -> builtins.str:
        '''(experimental) The project-relative path of the tasks manifest file.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "MANIFEST_FILE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="all")
    def all(self) -> typing.List[Task]:
        '''(experimental) All tasks.

        :stability: experimental
        '''
        return typing.cast(typing.List[Task], jsii.get(self, "all"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.Mapping[builtins.str, builtins.str]:
        '''(experimental) Returns a copy of the currently global environment for this project.

        :stability: experimental
        '''
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "env"))


@jsii.data_type(
    jsii_type="projen.tasks.TasksManifest",
    jsii_struct_bases=[],
    name_mapping={"env": "env", "tasks": "tasks"},
)
class TasksManifest:
    def __init__(
        self,
        *,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tasks: typing.Optional[typing.Mapping[builtins.str, TaskSpec]] = None,
    ) -> None:
        '''(experimental) Schema for ``tasks.json``.

        :param env: (experimental) Environment for all tasks.
        :param tasks: (experimental) All tasks available for this project.

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if env is not None:
            self._values["env"] = env
        if tasks is not None:
            self._values["tasks"] = tasks

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment for all tasks.

        :stability: experimental
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tasks(self) -> typing.Optional[typing.Mapping[builtins.str, TaskSpec]]:
        '''(experimental) All tasks available for this project.

        :stability: experimental
        '''
        result = self._values.get("tasks")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, TaskSpec]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TasksManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="projen.tasks.TaskStep",
    jsii_struct_bases=[TaskStepOptions],
    name_mapping={
        "cwd": "cwd",
        "name": "name",
        "builtin": "builtin",
        "exec": "exec",
        "say": "say",
        "spawn": "spawn",
    },
)
class TaskStep(TaskStepOptions):
    def __init__(
        self,
        *,
        cwd: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        builtin: typing.Optional[builtins.str] = None,
        exec: typing.Optional[builtins.str] = None,
        say: typing.Optional[builtins.str] = None,
        spawn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A single step within a task.

        The step could either be  the execution of a
        shell command or execution of a sub-task, by name.

        :param cwd: (experimental) The working directory for this step. Default: - determined by the task
        :param name: (experimental) Step name. Default: - no name
        :param builtin: (experimental) The name of a built-in task to execute. Built-in tasks are node.js programs baked into the projen module and as component runtime helpers. The name is a path relative to the projen lib/ directory (without the .task.js extension). For example, if your built in builtin task is under ``src/release/resolve-version.task.ts``, then this would be ``release/resolve-version``. Default: - do not execute a builtin task
        :param exec: (experimental) Shell command to execute. Default: - don't execute a shell command
        :param say: (experimental) Print a message. Default: - don't say anything
        :param spawn: (experimental) Subtask to execute. Default: - don't spawn a subtask

        :stability: experimental
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if cwd is not None:
            self._values["cwd"] = cwd
        if name is not None:
            self._values["name"] = name
        if builtin is not None:
            self._values["builtin"] = builtin
        if exec is not None:
            self._values["exec"] = exec
        if say is not None:
            self._values["say"] = say
        if spawn is not None:
            self._values["spawn"] = spawn

    @builtins.property
    def cwd(self) -> typing.Optional[builtins.str]:
        '''(experimental) The working directory for this step.

        :default: - determined by the task

        :stability: experimental
        '''
        result = self._values.get("cwd")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''(experimental) Step name.

        :default: - no name

        :stability: experimental
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def builtin(self) -> typing.Optional[builtins.str]:
        '''(experimental) The name of a built-in task to execute.

        Built-in tasks are node.js programs baked into the projen module and as
        component runtime helpers.

        The name is a path relative to the projen lib/ directory (without the .task.js extension).
        For example, if your built in builtin task is under ``src/release/resolve-version.task.ts``,
        then this would be ``release/resolve-version``.

        :default: - do not execute a builtin task

        :stability: experimental
        '''
        result = self._values.get("builtin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def exec(self) -> typing.Optional[builtins.str]:
        '''(experimental) Shell command to execute.

        :default: - don't execute a shell command

        :stability: experimental
        '''
        result = self._values.get("exec")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def say(self) -> typing.Optional[builtins.str]:
        '''(experimental) Print a message.

        :default: - don't say anything

        :stability: experimental
        '''
        result = self._values.get("say")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spawn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Subtask to execute.

        :default: - don't spawn a subtask

        :stability: experimental
        '''
        result = self._values.get("spawn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TaskStep(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Task",
    "TaskCommonOptions",
    "TaskOptions",
    "TaskRuntime",
    "TaskSpec",
    "TaskStep",
    "TaskStepOptions",
    "Tasks",
    "TasksManifest",
]

publication.publish()
