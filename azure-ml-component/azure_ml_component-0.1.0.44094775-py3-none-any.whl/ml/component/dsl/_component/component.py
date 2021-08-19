# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A wrapper to analyze function annotations, generate component specs, and run component in command line."""
import copy
import types
import inspect
import argparse
import re
import sys
import functools
import contextlib
import multiprocessing
import importlib
from multiprocessing.pool import ThreadPool
from collections import OrderedDict
from enum import EnumMeta
from pathlib import Path
from io import StringIO

from azure.ml.component.dsl._utils import logger, _import_component_with_working_dir, \
    _infer_func_relative_path_with_source
from azure.ml.component.dsl._module_spec import ParallelRunModuleSpec, SPEC_EXT
from azure.ml.component._core._component_definition import ComponentType, CommandComponentDefinition
from azure.ml.component._core._environment import Environment
from ._annotations import _InputFileList, DSLCommandLineGenerator, OutputFile
from azure.ml.component.dsl.types import Enum, Input, Output, _Param, String, _get_annotation_cls_by_type
from ._exceptions import RequiredParamParsingError, TooManyDSLComponentsError, DSLComponentDefiningError
from ..._aml_core_dependencies import _get_tagged_image

OPENMPI_CPU_IMAGE = _get_tagged_image("mcr.microsoft.com/azureml/openmpi3.1.2-ubuntu16.04")


def _component(
    name=None, version='0.0.1', display_name=None, description=None, is_deterministic=None,
    tags=None, os=None,
    base_image=None, conda_dependencies=None,
    custom_image=None,
):
    """Return a decorator which is used to declare a component with @dsl._component.

    A component is a reusable unit in an Azure Machine Learning workspace.
    With the decorator @dsl._component, a function could be registered as a component in the workspace.
    Then the component could be used to construct an Azure Machine Learning pipeline.
    The parameters of the decorator are the properties of the component spec,
    see https://aka.ms/azureml-component-specs.

    .. remarks::

        The following example shows how to use @dsl._component to declare a simple component.

        .. code-block:: python

            @dsl._component
            def your_component_function(output: OutputPath(), input: InputPath(), param='str_param'):
                pass

        The following example shows how to declare a component with detailed meta data.

        .. code-block:: python

            @dsl._component(name=name, version=version, namespace=namespace, job_type=job_type,
                            description=description)
            def your_component_function(output: OutputPath(), input: InputPath(), param='str_param'):
                pass

        An executable component should be in an entry file and could handle command line arguments.
        The following code is a full example of entry.py which could be registered.

        .. code-block:: python

            import sys
            from azure.ml.component import dsl
            from azure.ml.component.dsl._component import ComponentExecutor

            @dsl._component
            def your_component_function(output: OutputPath(), input: InputPath(), param='str_param'):
                pass

            if __name__ == '__main__':
                ComponentExecutor(your_component_function).execute(sys.argv)

        With the entry.py file, we could build a component specification yaml file.
        For more details of the component spec, see https://aka.ms/azureml-component-specs
        With the yaml file, we could register the component to workspace using az ml cli.
        See https://docs.microsoft.com/en-us/cli/azure/ext/azure-cli-ml/ml?view=azure-cli-latest.
        The command lines are as follows.
        az ml component build --target entry.py
        az ml component register --spec-file entry.spec.yaml


    :param name: The name of the component. If None is set, camel cased function name is used.
    :type name: str
    :param description: The description of the component. If None is set, the doc string is used.
    :type description: str
    :param version: Version of the component.
    :type version: str
    :param display_name: Display name of the component.
    :type display_name: str
    :param is_deterministic: Specify whether the component will always generate the same result. The default value is
                             None, the component will be reused by default behavior, the same for True value. If
                             False, this component will never be reused.
    :type is_deterministic: bool
    :param tags: Tags of the component.
    :type tags: builtin.list
    :param os: OS type of the component.
    :type os: str
    :param base_image: Base image of the component.
    :type base_image: str
    :param conda_dependencies: Dependencies of the component.
    :type conda_dependencies: str
    :param custom_image: User provided docker image, if it is not None, the component will directly run with the image,
                         user should take care of preparing all the required dependent packages in the image.
                         in this case, both base_image and conda_dependencies should be None.
    :type custom_image: str
    :return: An injected function which could be passed to ComponentExecutor
    """
    if os and os.lower() not in {'windows', 'linux'}:
        raise DSLComponentDefiningError("Keyword 'os' only support two values: 'windows', 'linux'.")

    if name and not CommandComponentDefinition.is_valid_name(name):
        msg = "Name is not valid, it could only contains a-z, A-Z, 0-9 and '.-_', got '%s'." % name
        raise DSLComponentDefiningError(msg)

    spec_args = {k: v for k, v in locals().items() if v is not None}
    wrap_callable = False
    if callable(name):
        wrap_callable = True
        spec_args = {}

    def wrapper(func):
        nonlocal spec_args
        spec_args = _refine_spec_args(spec_args)

        spec_args['name'] = spec_args.get('name', func.__name__)
        spec_args['display_name'] = spec_args.get('display_name', spec_args['name'])
        spec_args['description'] = spec_args.get('description', func.__doc__)
        entry, source_dir = _infer_func_relative_path_with_source(func)
        spec_args['command'] = ['python', entry]
        spec_args['code'] = Path(source_dir).as_posix()
        # Initialize a ComponentExecutor to make sure it works and use it to update the component function.
        executor = ComponentExecutor(func, copy.copy(spec_args))
        executor._update_func(func)

        func._is_dsl_func = True

        return func

    return wrapper(name) if wrap_callable else wrapper


def _refine_spec_args(spec_args: dict) -> dict:
    spec_args = copy.copy(spec_args)
    tags = spec_args.get('tags', {})

    # Convert the type to support old style list tags.
    if isinstance(tags, list):
        tags = {tag: None for tag in tags}

    if not isinstance(tags, dict):
        raise DSLComponentDefiningError("Keyword 'tags' must be a dict.")

    # Indicate the component is generated by dsl.component
    if 'codegenBy' not in tags:
        tags['codegenBy'] = 'dsl.component'
    spec_args['tags'] = tags

    os = spec_args.pop('os') if 'os' in spec_args else None
    base_image = spec_args.pop('base_image') if 'base_image' in spec_args else None
    custom_image = spec_args.pop('custom_image') if 'custom_image' in spec_args else None
    docker = {'image': base_image or custom_image} if base_image or custom_image else None
    conda_dependencies = spec_args.pop('conda_dependencies') if 'conda_dependencies' in spec_args else None
    conda = None
    if not custom_image:  # Only when custom image is specified, we need conda to build image.
        if conda_dependencies is None:
            conda = {'conda_dependencies_file': None}  # This indicates that we need to dump a default conda.
        else:
            conda = {'conda_dependencies_file': conda_dependencies} if isinstance(conda_dependencies, str) else \
                {'conda_dependencies': conda_dependencies}
    spec_args['environment'] = Environment(os=os, docker=docker, conda=conda)
    return spec_args


class ComponentExecutor:
    """An executor to analyze the spec args of a function and convert it to a runnable component in AzureML."""

    INJECTED_FIELD = '_spec_args'  # The injected field is used to get the component spec args of the function.

    def __init__(self, func: types.FunctionType, spec_args=None):
        """Initialize a ComponentExecutor with a function to enable calling the function with command line args.

        :param func: A function wrapped by dsl.component.
        :type func: types.FunctionType
        """
        if not isinstance(func, types.FunctionType):
            raise TypeError("Only function type is allowed to initialize ComponentExecutor.")
        if spec_args is None:
            spec_args = getattr(func, self.INJECTED_FIELD, None)
            if spec_args is None:
                raise TypeError("You must wrap the function with @dsl._component() before using it.")
        self._raw_spec_args = copy.copy(spec_args)
        self._name = spec_args['name']
        self._type = spec_args.get('type', ComponentType.CommandComponent.value)
        executor_cls = self._get_executor_by_type(self.type)
        self._executor = executor_cls(func, spec_args=spec_args)
        self._func = func

    @property
    def name(self):
        """Return the name of the component."""
        return self._name

    @property
    def type(self):
        """Return the job type of the component."""
        return self._type

    @property
    def spec(self):
        """Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        return self._executor.spec

    @property
    def spec_dict(self):
        """Return the component spec data as a python dict."""
        return self._executor.spec._to_dict()

    def to_spec_yaml(self, folder=None, spec_file=None):
        """Generate spec dict object, and dump it as a yaml spec file."""
        pyfile = Path(inspect.getfile(self._func))
        if folder is None:
            # If the folder is not provided, we generate the spec file in the same folder of the function file.
            folder = pyfile.parent
        if spec_file is None:
            # If the spec file name is not provided, get the name from the file name.
            spec_file = pyfile.with_suffix(SPEC_EXT).name
        self.spec._save_to_code_folder(Path(folder), spec_file)
        return Path(folder) / spec_file

    def get_interface(self):
        """Return the interface of this component.

        :return: A dictionary including the definition of inputs/outputs/params.
        """
        return self._executor.get_interface()

    def execute(self, argv):
        """Execute the component with command line arguments."""
        return self._executor.execute(argv)

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor equals to calling the underlying function directly."""
        return self._func(*args, **kwargs)

    @classmethod
    def collect_component_from_file(cls, py_file, working_dir=None, force_reload=False):
        """Collect single dsl component in a file and return the executors of the components."""
        py_file = Path(py_file).absolute()
        if py_file.suffix != '.py':
            raise ValueError("%s is not a valid py file." % py_file)
        if working_dir is None:
            working_dir = py_file.parent
        working_dir = Path(working_dir).absolute()

        component_path = py_file.relative_to(working_dir).as_posix().split('.')[0].replace('/', '.')

        return cls.collect_component_from_py_module(component_path, working_dir=working_dir, force_reload=force_reload)

    @classmethod
    def collect_component_from_py_module(cls, py_module, working_dir, force_reload=False):
        """Collect single dsl component in a py module and return the executors of the components."""
        components = [component for component in cls.collect_components_from_py_module(py_module,
                                                                                       working_dir,
                                                                                       force_reload)]

        def defined_in_current_file(component):
            entry_file = inspect.getfile(component._func)
            component_path = py_module.replace('.', '/') + '.py'
            return Path(entry_file).resolve().absolute() == (Path(working_dir) / component_path).resolve().absolute()

        components = [component for component in components if defined_in_current_file(component)]
        if len(components) == 0:
            return None
        component = components[0]
        entry_file = inspect.getfile(component._func)
        if len(components) > 1:
            raise TooManyDSLComponentsError(len(components), entry_file)
        component.check_entry_valid(entry_file)
        return component

    @classmethod
    def collect_components_from_py_module(cls, py_module, working_dir=None, force_reload=False):
        """Collect all components in a python module and return the executors of the components."""
        if isinstance(py_module, str):
            try:
                py_module = _import_component_with_working_dir(py_module, working_dir, force_reload)
            except Exception as e:
                raise ImportError("""Error occurs when import component '%s': %s.\n
                Please make sure all requirements inside conda.yaml has been installed.""" % (py_module, e)) from e
        for _, obj in inspect.getmembers(py_module):
            if cls.look_like_component(obj):
                component = cls(obj)
                component.check_py_module_valid(py_module)
                yield component

    @classmethod
    def look_like_component(cls, f):
        """Return True if f looks like a component."""
        if not isinstance(f, types.FunctionType):
            return False
        if not hasattr(f, cls.INJECTED_FIELD):
            return False
        return True

    @classmethod
    def _get_executor_by_type(cls, type):
        """Get the real executor class according to the type, currently we only support CommandComponent."""
        if type != ComponentType.CommandComponent.value:
            raise DSLComponentDefiningError("Currently only CommandComponent is supported, got '%s'." % type)
        return _CommandComponentExecutor

    def check_entry_valid(self, entry_file):
        """Check whether the entry file is valid to make sure it could be run in AzureML."""
        return self._executor.check_entry_valid(entry_file)

    def check_py_module_valid(self, py_module):
        """Check whether the entry py module is valid to make sure it could be run in AzureML."""
        return self._executor.check_py_module_valid(py_module)

    def _update_func(self, func: types.FunctionType):
        # Set the injected field so the function could be used to initializing with `ComponentExecutor(func)`
        setattr(func, self.INJECTED_FIELD, self._raw_spec_args)
        if hasattr(self._executor, '_update_func'):
            self._executor._update_func(func)


class _CommandComponentExecutor:
    SPEC_CLASS = CommandComponentDefinition  # This class is used to initialize a definition instance.
    SPECIAL_FUNC_CHECKERS = {
        'Coroutine': inspect.iscoroutinefunction,
        'Generator': inspect.isgeneratorfunction,
    }
    # This is only available on Py3.6+
    if sys.version_info.major == 3 and sys.version_info.minor > 5:
        SPECIAL_FUNC_CHECKERS['Async generator'] = inspect.isasyncgenfunction

    VALID_SPECIAL_FUNCS = set()

    def __init__(self, func: types.FunctionType, spec_args=None):
        """Initialize a ComponentExecutor with a function."""
        if spec_args is None:
            spec_args = getattr(func, ComponentExecutor.INJECTED_FIELD)
        self._spec_args = copy.deepcopy(spec_args)
        self._assert_valid_func(func)
        self._func = func
        self._arg_mapping = self._analyze_annotations(func)
        self._parallel_inputs = None
        if 'parallel_inputs' in spec_args:
            self._parallel_inputs = _InputFileList(self._spec_args.pop('parallel_inputs'))

    @property
    def type(self):
        return self._spec_args.get('type', ComponentType.CommandComponent.value)

    @property
    def spec(self):
        """
        Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        io_properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        command, args = self._spec_args['command'], io_properties.pop('args')
        spec_args = copy.copy(self._spec_args)
        spec_args['command'] = self.get_command_str_by_command_args(command, args)
        return self.SPEC_CLASS._from_dict({**spec_args, **io_properties})

    @classmethod
    def get_command_str_by_command_args(cls, command, args):
        return ' '.join(command + args)

    def get_interface(self):
        """Return the interface of this component.

        :return: A dictionary including the definition of inputs/outputs/params.
        """
        properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        properties.pop('args')
        return properties

    def execute(self, argv):
        """Execute the component with command line arguments."""
        args = self._parse(argv)
        run = self._func(**args)
        if self._parallel_inputs is not None:
            run(self._parallel_inputs.load_from_argv(argv))

    def __call__(self, *args, **kwargs):
        """Directly calling a component executor equals to calling the underlying function directly."""
        return self._func(*args, **kwargs)

    @classmethod
    def is_valid_type(cls, type):
        return type in {None, ComponentType.CommandComponent.value}

    def _assert_valid_func(self, func):
        """Check whether the function is valid, if it is not valid, raise."""
        for k, checker in self.SPECIAL_FUNC_CHECKERS.items():
            if k not in self.VALID_SPECIAL_FUNCS:
                if checker(func):
                    raise NotImplementedError("%s function is not supported for %s now." % (k, self.type))

    def check_entry_valid(self, entry_file):
        """Check whether the entry file call .execute(sys.argv) to make sure it could be run in AzureML."""
        # Now we simply use string search, will be refined in the future.
        main_code = """if __name__ == '__main__':\n    %sExecutor(%s).execute(sys.argv)""" % (
            'Component', self._func.__name__)
        module_main_code = """if __name__ == '__main__':\n    %sExecutor(%s).execute(sys.argv)""" % (
            'Module', self._func.__name__)
        with open(entry_file) as fin:
            content = fin.read()
            if main_code not in content and module_main_code not in content:
                msg = "The following code doesn't exist in the entry file, it may not run correctly.\n%s" % main_code
                logger.warning(msg)

    def check_py_module_valid(self, py_module):
        pass

    @classmethod
    def _parse_with_mapping(cls, argv, arg_mapping):
        """Use the parameters info in arg_mapping to parse commandline params.

        :param argv: Command line arguments like ['--param-name', 'param-value']
        :param arg_mapping: A dict contains the mapping from param key 'param_name' to _ComponentBaseParam
        :return: params: The parsed params used for calling the user function.
        """
        parser = argparse.ArgumentParser()
        for param in arg_mapping.values():
            DSLCommandLineGenerator(param).add_to_arg_parser(parser)
        args, _ = parser.parse_known_args(argv)

        # Convert the string values to real params of the function.
        params = {}
        for name, param in arg_mapping.items():
            val = getattr(args, param.name)
            generator = DSLCommandLineGenerator(param)
            if val is None:
                if isinstance(param, Output) or not param.optional:
                    raise RequiredParamParsingError(name=param.name, arg_string=generator.arg_string)
                continue
            # If it is a parameter, we help the user to parse the parameter,
            # if it is an input port, we use load to get the param value of the port,
            # otherwise we just pass the raw value as the param value.
            param_value = val
            if isinstance(param, _Param):
                param_value = param._parse_and_validate(val)
            elif isinstance(param, Input):
                param_value = val
            params[name] = param_value
            # For OutputPath, we will create a folder for it.
            if isinstance(param, Output) and not isinstance(param, OutputFile) and not Path(val).exists():
                Path(val).mkdir(parents=True, exist_ok=True)
        return params

    def _parse(self, argv):
        return self._parse_with_mapping(argv, self._arg_mapping)

    @classmethod
    def _generate_spec_outputs(cls, arg_mapping) -> dict:
        """Generate output ports of a component, from the return annotation and the arg annotations.

        The outputs including the return values and the special PathOutputPort in args.
        """
        return {val.name: val for val in arg_mapping.values() if isinstance(val, Output)}

    @classmethod
    def _generate_spec_inputs(cls, arg_mapping, parallel_inputs: _InputFileList = None) -> dict:
        """Generate input ports of the component according to the analyzed argument mapping."""
        input_ports = {val.name: val for val in arg_mapping.values() if isinstance(val, Input)}
        parallel_input_ports = {val.name: val for val in parallel_inputs.inputs} if parallel_inputs else {}
        return {**input_ports, **parallel_input_ports}

    @classmethod
    def _generate_spec_params(cls, arg_mapping) -> dict:
        """Generate parameters of the component according to the analyzed argument mapping."""
        return {val.name: val for val in arg_mapping.values() if isinstance(val, _Param)}

    @classmethod
    def _generate_spec_io_properties(cls, arg_mapping, parallel_inputs=None):
        """Generate the required properties for a component spec according to the annotation of a function."""
        inputs = cls._generate_spec_inputs(arg_mapping, parallel_inputs)
        outputs = cls._generate_spec_outputs(arg_mapping)
        params = cls._generate_spec_params(arg_mapping)
        args = []
        for val in list(inputs.values()) + list(outputs.values()) + list(params.values()):
            args.append(DSLCommandLineGenerator(val).arg_group_str())
        return {'inputs': inputs, 'outputs': outputs, 'parameters': params, 'args': args}

    @classmethod
    def _analyze_annotations(cls, func):
        """Analyze the annotation of the function to get the parameter mapping dict and the output port list.

        :param func:
        :return: (param_mapping, output_list)
            param_mapping: The mapping from function param names to input ports/component parameters;
            output_list: The output port list analyzed from return annotations.
        """
        mapping = OrderedDict()
        sig = inspect.signature(func)
        for param_name, param_attr in sig.parameters.items():
            annotation = cls._generate_parameter_annotation(param_attr)
            if annotation.name is None:
                annotation._name = param_name
            annotation.arg_name = param_name
            mapping[param_name] = annotation

        return mapping

    @classmethod
    def _generate_parameter_annotation(cls, param_attr):
        """Generate an input port/parameter according to a param annotation of the function."""
        annotation = param_attr.annotation

        # If the user forgot to initialize an instance, help him to initalize.
        if isinstance(annotation, type) and issubclass(annotation, (_Param, Input, Output)):
            annotation = annotation()

        # If the param doesn't have annotation, we get the annotation from the default value.
        # If the default value is None or no default value, it is treated as str.
        if annotation is param_attr.empty:
            default = param_attr.default
            annotation = str if default is None or default is param_attr.empty else type(param_attr.default)

        # An enum type will be converted to EnumParameter
        if isinstance(annotation, EnumMeta):
            annotation = Enum(enum=annotation)

        # If the annotation is not one of _ComponentParam/ComponentInputPort/ComponentPort,
        # we use DATA_TYPE_MAPPING to get the corresponding class according to the type of annotation.
        if not isinstance(annotation, (_Param, Input, Output)):
            param_cls = _get_annotation_cls_by_type(annotation)
            if param_cls is None:
                # If the type is still unrecognized, we treat is as string.
                param_cls = String
            annotation = param_cls()
        annotation = copy.copy(annotation)

        # If the default value of a parameter is set, set the port/param optional,
        # and set the default value of a parameter.
        # Note that output port cannot be optional.
        if not isinstance(param_attr, Output) and param_attr.default is not param_attr.empty:
            # Only parameter support default value in yaml.
            if isinstance(annotation, _Param):
                annotation._update_default(param_attr.default)
            # Change optional as True if user given a default to param
            # Because here we use optional as python optional concept
            annotation._optional = True

        return annotation

    def _update_func(self, func):
        pass


class _ParallelComponentExecutor(_CommandComponentExecutor):
    """This executor handle parallel component specific operations to enable parallel component."""

    SPEC_CLASS = ParallelRunModuleSpec
    JOB_TYPE = 'parallel'
    FIELDS = {'init', 'run', 'shutdown'}
    CONFLICT_ERROR_TPL = "It is not allowed to declare {}() once a parallel component is defined."
    VALID_SPECIAL_FUNCS = {'Generator'}

    def __init__(self, func: callable, spec_args=None):
        """Initialize a ParallelComponentExecutor with a provided function."""
        super().__init__(func, spec_args)
        if not self._parallel_inputs:
            raise ValueError(
                "Parallel component should have at lease one parallel input, got 0.",
            )
        self._output_keys = [key for key, val in self._arg_mapping.items() if isinstance(val, Output)]
        if len(self._output_keys) == 0:
            raise ValueError(
                "Parallel component should have at least one OutputPath, got %d." % len(self._output_keys)
            )
        self._args = {}
        self._spec_args.update({
            'input_data': [port.name for port in self._parallel_inputs.inputs],
            # We use the first output as the parallel output data.
            # This is only a workaround according to current parallel run design, picking any output port is OK.
            'output_data': self._arg_mapping[self._output_keys[0]].name,
        })
        command = self._spec_args.pop('command')
        self._spec_args['entry'] = command[-1]
        self._spec_args.pop('job_type')
        self._run_func = None
        self._generator = None

    def execute(self, argv, batch_size=4):
        """Execute the component using parallel run style. This is used for local debugging."""
        self.init_argv(argv)

        files = self._parallel_inputs.load_from_argv(argv)
        # Use multiprocessing to run batches.
        count = len(files)
        batches = (count + batch_size - 1) // batch_size
        nprocess = min(max(batches, 1), multiprocessing.cpu_count())
        logger.info("Run %d batches to process %d files." % (batches, count))
        batch_files = [files[i * batch_size: (i + 1) * batch_size] for i in range(batches)]
        with ThreadPool(nprocess) as pool:
            batch_results = pool.map(self.run, batch_files)
        results = []
        for result in batch_results:
            results += result
        shutdown_result = self.shutdown()
        return shutdown_result if shutdown_result is not None else results

    @staticmethod
    def _remove_ambiguous_option_in_argv(argv: list, parse_method):
        """Remove ambiguous options in argv for an argparser method.

        This is a workaround to solve the issue that parallel run will add some other command options
        which will cause the problem 'ambiguous option'.
        """
        pattern = re.compile(r"error: ambiguous option: (\S+) could match")
        while True:
            stderr = StringIO()
            with contextlib.redirect_stderr(stderr):
                try:
                    parse_method(argv)
                except SystemExit:
                    stderr_value = stderr.getvalue()
                    match = pattern.search(stderr_value)
                    if not match:
                        # If we cannot found such pattern, which means other problems is raised, we directly raise.
                        sys.stdout.write(stderr_value)
                        raise
                    # Remove the option_str and the value of it.
                    option_str = match.group(1)
                    logger.debug("Ambiguous option '%s' is found in argv, remove it." % option_str)
                    idx = argv.index(option_str)
                    argv = argv[:idx] + argv[idx + 2:]
                else:
                    # If no exception is raised, return the ready args.
                    return argv

    def init(self):
        """Init params except for the InputFiles with the sys args when initializing parallel component.

        This method will only be called once in one process.
        """
        return self.init_argv(sys.argv)

    def init_argv(self, argv=None):
        """Init params except for the InputFiles with argv."""
        if argv is None:
            argv = sys.argv
        logger.info("Initializing parallel component, argv = %s" % argv)
        mapping = copy.copy(self._arg_mapping)
        argv = self._remove_ambiguous_option_in_argv(
            argv, functools.partial(self._parse_with_mapping, arg_mapping=mapping),
        )
        args = self._parse_with_mapping(argv, mapping)
        logger.info("Parallel component initialized, args = %s" % args)
        ret = self._func(**args)
        # If the init function is a generator, the first yielded result is the run function.
        if isinstance(ret, types.GeneratorType):
            self._generator = ret
            ret = next(ret)

        # Make sure the return result is a callable.
        if callable(ret):
            self._run_func = ret
        else:
            raise TypeError("Return/Yield result of the function must be a callable, got '%s'." % (type(ret)))

        sig = inspect.signature(self._run_func)
        if len(sig.parameters) != 1:
            raise ValueError(
                "The method {}() returned by {}() has incorrect signature {}."
                " It should have exact one parameter.".format(ret.__name__, self._func.__name__, sig)
            )
        return self._run_func

    def run(self, files):
        results = self._run_func(files)
        if results is not None:
            return files
        return results

    def shutdown(self):
        if self._generator:
            # If the function is using yield, call next to run the codes after yield.
            while True:
                try:
                    next(self._generator)
                except StopIteration as e:
                    return e.value

    def check_entry_valid(self, entry_file):
        pass

    def check_py_module_valid(self, py_module):
        # For parallel component, the init/run/shutdown in py_module should be
        # _ParallelComponentExecutor.init/run/shutdown
        for attr in self.FIELDS:
            func = getattr(py_module, attr)
            if not self.is_valid_init_run_shutdown(func, attr):
                raise AttributeError(self.CONFLICT_ERROR_TPL.format(attr))

    def _update_func(self, func: types.FunctionType):
        # For a parallel component, we should update init/run/shutdown for the script.
        # See "Write your inference script" in the following link.
        # https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-parallel-run-step
        py_module = importlib.import_module(func.__module__)
        for attr in self.FIELDS:
            func = getattr(py_module, attr, None)
            # We don't allow other init/run/shutdown in the script.
            if func is not None and not self.is_valid_init_run_shutdown(func, attr):
                raise AttributeError(self.CONFLICT_ERROR_TPL.format(attr))
            setattr(py_module, attr, getattr(self, attr))

    @classmethod
    def is_valid_init_run_shutdown(cls, func, attr):
        return isinstance(func, types.MethodType) and func.__func__ == getattr(_ParallelComponentExecutor, attr)

    @classmethod
    def _generate_spec_io_properties(cls, arg_mapping, parallel_inputs=None):
        """Generate the required properties for a component spec according to the annotation of a function.

        For parallel component, we need to remove InputFiles and --output in args.
        """
        properties = super()._generate_spec_io_properties(arg_mapping, parallel_inputs)
        args_to_remove = []
        for k, v in arg_mapping.items():
            # InputFiles and the output named --output need to be removed in the arguments.
            # For InputFiles: the control script will handle it and pass the files to run();
            # For the output, the control script will add an arg item --output so we should not define it again.
            if v.to_cli_option_str() == '--output':
                args_to_remove.append(v)
        if parallel_inputs:
            args_to_remove += [port for port in parallel_inputs.inputs]
        args = properties['args']
        for arg in args_to_remove:
            args.remove(arg.arg_group_str())
        return properties

    @property
    def spec(self):
        """
        Return the module spec instance of the component.

        Initialized by the function annotations and the meta data.
        """
        io_properties = self._generate_spec_io_properties(self._arg_mapping, self._parallel_inputs)
        return self.SPEC_CLASS._from_dict({**self._spec_args, **io_properties})

    @classmethod
    def is_valid_type(cls, job_type):
        return job_type == cls.JOB_TYPE
