# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains classes for creating and managing reusable computational units of an Azure Machine Learning pipeline.

A component is self-contained set of code that performs one step in the ML workflow (pipeline), such as data
preprocessing, model training, model scoring and so on. A component is analogous to a function, in that it has a name,
parameters, expects certain input and returns some value.

Component is designed to be reused in different jobs and can be evolved to adapt to different specific computation
logics in different usage cases. Anonymous Component can be used to improve an algorithm in a fast iteration mode,
and once the goal is achieved, the algorithm can be published as a registered Component which enables reuse.
"""
import copy
import functools
import importlib
import inspect
import json
import logging
import os
from enum import Enum
from pathlib import Path
import tempfile
import time
import types
from typing import Any, List, Callable, Mapping, Optional
import uuid

from azure.ml.component._api._api import _dto_2_definition, _definition_to_dto
from azure.ml.component.dsl.types import _Group, _GroupAttrDict
from azureml.core import Workspace, Experiment, ScriptRunConfig
from azureml.core.run import Run
from azureml.core.runconfig import RunConfiguration
from azureml.data.abstract_dataset import AbstractDataset
from azureml.data.abstract_datastore import AbstractDatastore
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.data.data_reference import DataReference
from azureml.exceptions._azureml_exception import UserErrorException

from ._core._component_definition import CommandComponentDefinition, ComponentType
from ._dataset import _GlobalDataset
from ._debug._constants import DATA_REF_PREFIX
from ._dynamic import KwParameter, create_kw_method_from_parameters
from ._component_func import get_dynamic_input_parameter, to_component_func_from_definition
from ._execution._component_run_helper import ComponentRunHelper, RunMode
from ._execution._component_snapshot import _prepare_component_snapshot
from ._execution._tracker import RunHistoryTracker
from ._execution._component_run_helper import EXECUTION_LOGFILE
from ._component_validator import ComponentValidator, Diagnostic
from ._module_dto import ModuleDto
from ._pipeline_parameters import PipelineParameter, LinkedParametersMixedIn
from ._parameter_assignment import _ParameterAssignment
from .run_settings import _RunSettingsInterfaceGenerator, _has_specified_runsettings, \
    _get_compute_type, _update_run_config
from ._util._attr_dict import _AttrDict
from ._util._cache import DatastoreCache
from ._util._exceptions import ComponentValidationError, CannotSetAttributeError
from ._util._loggerfactory import _LoggerFactory, _PUBLIC_API, track, timer
from ._util._telemetry import TelemetryMixin, WorkspaceTelemetryMixin
from ._util._utils import _get_parameter_static_value, _sanitize_python_variable_name, _get_short_path_name, \
    trans_to_valid_file_name, _ensure_dataset_saved_in_workspace, is_valid_component_name
from ._restclients.designer.models import DatasetRegistration, DatasetOutputOptions

_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class Input(TelemetryMixin, LinkedParametersMixedIn):
    """Define one input of a Component."""

    _AVAILABLE_MODE = ['mount', 'download', 'direct']
    _ALLOWED_TYPES = (
        AbstractDataset, _GlobalDataset, DataReference, DatasetConsumptionConfig,  # Data in remote
        str, Path,  # Data in local
        PipelineParameter,  # Reference from pipeline parameter
        _ParameterAssignment,  # Reference from parameter assignment
        type(None),  # Not set
    )
    _built_datasets = {}  # This cache is used for sharing built dataset across different inputs.

    def __init__(self, dset, name: str, mode=None, owner=None):
        """Initialize an input of a component.

        :param dset: The input data. Valid types include Dataset, PipelineParameter and Output of another component.
            Note that the PipelineParameter and the Component of Output associated should be reachable in the scope
            of current pipeline.
        :type dset: Union[azureml.core.Dataset,
                          azure.ml.component.component.Output,
                          azure.ml.component._flattened_pipeline_parameters]
        :param name: The name of the input.
        :type name: str
        :param mode: The mode of the input.
        :type mode: str
        :param owner: The owner component of the input.
        :type owner: azure.ml.component.Component
        """
        super().__init__()
        self._name = name
        self._dset = self._resolve_dset(dset, name)
        self._owner = owner
        self._mode = mode
        self._path_on_compute = None
        # if a input is annotated, store it's annotation for validation
        self._annotation = None
        # Attention: If any field added here, please make sure the field copied correctly in
        # the `update_component_extra_settings()` func in pipeline.py during pipeline creation

    def _resolve_dset(self, dset, name):
        from .pipeline import Pipeline
        if isinstance(dset, Component) or isinstance(dset, Pipeline):
            # For the case use a component/pipeline as the input, we use its only one output as the real input.
            # Here we set dset = dset.outputs, then the following logic will get the output object.
            dset = dset.outputs

        if isinstance(dset, _OutputsAttrDict):
            # For the case that use the outputs of another component as the input,
            # we use the only one output as the real input, if multiple outputs are provided, an exception is raised.
            output_len = len(dset)
            if output_len != 1:
                raise UserErrorException('%r output(s) found of specified outputs when setting input %r,'
                                         ' exactly 1 output required.' % (output_len, name))
            dset = list(dset.values())[0]

        # We validate the type here to avoid bugs when constructing graph.
        # TODO: If we could move component.validate before constructing graph, we could do this when calling validate
        if not isinstance(dset, self._ALLOWED_TYPES) and not isinstance(dset, (Input, Output)):
            raise UserErrorException(
                "Invalid type %r for input %r, only one of the following is accepted:\n"
                "Dataset, output of another component, local file path(for local run only)." % (type(dset), name)
            )
        return dset

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="input_configure")
    def configure(self, mode=None, path_on_compute=None):
        """
        Use this method to configure the input.

        :param mode: The mode that will be used for this input. For File Dataset, available options are 'mount',
                     'download' and 'direct', for Tabular Dataset, available options is 'direct'.
                     See https://aka.ms/dataset-mount-vs-download for more details.
        :type mode: str
        :param path_on_compute: Specify the input path to write the data on the compute,
                                should be adapted to the OS of the compute.
                                E.g., "/tmp/path" in linux compute, "C:/tmp/path" in windows compute.
                                Both absolute path and relative path are supported.
                                If the path doesn't exists, new folder will be created for writing data.
                                If it is not specified, a temp folder will be used.
        :type path_on_compute: str
        """
        self._configure(mode, path_on_compute)

    def _configure(self, mode=None, path_on_compute=None):
        # @track on public will increase call stack depth,
        # and log unnecessary telemetry which not triggered by user, which we should avoid.
        if mode is not None:
            if mode not in self._AVAILABLE_MODE:
                raise UserErrorException("Invalid mode: '{}', only 'mount', 'download' or 'direct' is allowed."
                                         .format(mode))
            self._mode = mode

            if self._owner is not None:
                self._owner._specify_input_mode = True

        if path_on_compute is not None:
            self._path_on_compute = path_on_compute

    @property
    def name(self):
        """Return the name of the input.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def mode(self):
        """Return the mode that will be used for this input.

        :return: The mode.
        :rtype: str
        """
        return self._mode

    def _get_internal_data_source(self):
        """Get the dset iterativly until the dset is not an Input."""
        dset = self._dset
        while isinstance(dset, Input):
            dset = dset._dset
        return dset

    def _get_telemetry_values(self):
        return self._owner._get_telemetry_values() if self._owner else {}

    @classmethod
    def _build_dataset(cls, dset: AbstractDataset, mode=None):
        """Build the dataset as a DatasetConsumptionConfig for component submission."""
        hash_key = '%s_%s' % (id(dset), mode)
        if hash_key in cls._built_datasets:
            return cls._built_datasets[hash_key]

        # For the dataset which is unregistered, we use the name 'dataset' for the built named input.
        # Note that to avoid name conflict, we will use xx_mount and xx_download for such cases.
        name = _sanitize_python_variable_name(dset.name) if dset.name else 'dataset'
        if mode == 'mount':
            result = dset.as_named_input(name + '_mount').as_mount()
        elif mode == 'download':
            result = dset.as_named_input(name + '_download').as_download()
        elif mode == 'direct' or mode is None:
            result = dset.as_named_input(name)
        else:
            raise ValueError("Got invalid mode %r for dataset %r." % (mode, dset.name))
        cls._built_datasets[hash_key] = result
        return result


class Output(TelemetryMixin):
    """Define one output of a Component."""

    _AVAILABLE_MODE = ['mount', 'upload']

    def __init__(
        self, name: str, datastore=None, output_mode=None, port_name=None,
        owner=None,
    ):
        """Initialize an output of a component.

        :param name: The name of the output.
        :type name: str
        :param datastore: The datastore that will be used for the output.
        :type datastore: azureml.core.datastore.Datastore
        :param output_mode: Specifies whether to use "upload" or "mount" to access the data.
        :type output_mode: str
        :param port_name: The name to be shown of the output.
        :type port_name: str
        :param owner: The owner component of the output.
        :type owner: azure.ml.component.Component
        """
        super().__init__()
        self._datastore = datastore
        self._name = name
        self._output_mode = output_mode
        self._last_build = None
        self._port_name = port_name if port_name else name
        self._owner = owner
        self._dataset_registration = None
        self._path_on_compute = None
        self._dataset_output_options = None
        self._datastore_name = None
        # Attention: If any field added here, please make sure the field copied correctly in
        # the `update_component_extra_settings()` func in pipeline.py during pipeline creation

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="output_configure")
    def configure(self, datastore=None, output_mode=None, path_on_compute=None, path_on_datastore=None):
        """
        Use this method to configure the output.

        :param datastore: The datastore that will be used for the output.
        :type datastore: azureml.core.datastore.Datastore or str
        :param output_mode: Specify whether to use "upload" or "mount" to access the data.
                            Note that 'mount' only works in a linux compute, windows compute only supports 'upload'.
                            If 'upload' is specified, the output data will be uploaded to the datastore
                            after the component process ends;
                            If 'mount' is specified, all the updates of the output folder will be synced to the
                            datastore when the component process is writting the output folder.
        :type output_mode: str
        :param path_on_compute: Specify the output path to write the data on the compute,
                                should be adapted to the OS of the compute.
                                E.g., "/tmp/path" in linux compute, "C:/tmp/path" in windows compute.
                                Both absolute path and relative path are supported.
                                If the path doesn't exists, new folder will be created for writing data.
                                If it is not specified, a temp folder will be used.
        :type path_on_compute: str
        :param path_on_datastore: Specify the location in datastore to write the data. If it is not specified, the
                                  default path will be "azureml/{run-id}/outputs/{output-name}".
        :type path_on_datastore: str
        """
        self._configure(datastore, output_mode, path_on_compute, path_on_datastore)

    def _configure(self, datastore=None, output_mode=None, path_on_compute=None, path_on_datastore=None):
        # @track on public will increase call stack depth,
        # and log unnecessary telemetry which not triggered by user, which we should avoid.
        if datastore is not None:
            if isinstance(datastore, str):
                if self._owner is None:
                    raise UserErrorException(
                        'Cannot configure the output with datastore name' +
                        ' when there is no owner.')
                elif not hasattr(self._owner, 'workspace') or self._owner.workspace is None:
                    raise UserErrorException(
                        'Cannot configure the output with datastore name' +
                        ' when the owner has no workspace.')
                self._datastore_name = datastore
                # directly set _datastore as None here, only validate the existence in validation phase
                self._datastore = None
            elif isinstance(datastore, AbstractDatastore):
                self._datastore = datastore
                self._datastore_name = datastore.name
            else:
                raise UserErrorException(
                    'Invalid datastore type: {}. '.format(type(datastore).__name__) +
                    'Use azureml.core.Datastore or datastore\'s name.')

            if self._owner is not None:
                self._owner._specify_output_datastore = True

        if output_mode is not None:
            if output_mode not in self._AVAILABLE_MODE:
                raise UserErrorException("Invalid mode: %r, only 'mount' or 'upload' is allowed." % output_mode)

            self._output_mode = output_mode
            if self._owner is not None:
                self._owner._specify_output_mode = True

        if path_on_compute is not None:
            self._path_on_compute = path_on_compute

        if path_on_datastore is not None:
            self._dataset_output_options = DatasetOutputOptions(path_on_datastore=path_on_datastore)

    @property
    def datastore(self):
        """Return the datastore of this output.

        .. remarks::

            The returned datastore might be None if the datastore was created
            after you configured the output with the datastore name.
            If that happends, try to retrive the property after a few seconds.

        :return: The datastore.
        :rtype: azureml.core.datastore.Datastore
        """
        if self._datastore is None and self._datastore_name is not None:
            self._datastore = DatastoreCache.get_item(self._owner.workspace, self._datastore_name)
        return self._datastore

    @property
    def output_mode(self):
        """Return the output mode that will be used for the output.

        :return: The output mode.
        :rtype: str
        """
        return self._output_mode

    @property
    def port_name(self):
        """Return the output port name displayed to the user.

        :return: The displayed output port name.
        :rtype: str
        """
        return self._port_name

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="OutputBuilder_register_as")
    def register_as(self, name, create_new_version: bool = True):
        """Register the output dataset to the workspace.

        .. remarks::

            Registration can only be applied to output but not input, this means if you only pass the object returned
            by this method to the inputs parameter of a pipline step, nothing will be registered. You must pass the
            object to the outputs parameter of a pipeline step for the registration to happen.

        :param name: The name of the registered dataset once the intermediate data is produced.
        :type name: str
        :param create_new_version: Whether to create a new version of the dataset if the data source changes. Defaults
            to True. By default, all intermediate output will output to a new location when a pipeline runs, so
            it is highly recommended to keep this flag set to True.
        :type create_new_version: bool
        :return: The output itself.
        :rtype: azure.ml.component.component.Output
        """
        self._dataset_registration = DatasetRegistration(name=name, create_new_version=create_new_version)
        return self

    def _get_telemetry_values(self):
        return self._owner._get_telemetry_values() if self._owner else {}


class _InputsAttrDict(_AttrDict):
    """Use this class for inputs to enable inputs.some_input = some_dataset."""

    def __init__(self, dct):
        super().__init__(dct)

    def __getitem__(self, item) -> Input:
        return super().__getitem__(item)

    def __getattr__(self, item) -> Input:
        return super().__getattr__(item)

    def __setitem__(self, key, value):
        original_input = self.__getitem__(key)  # Note that an exception will be raised if the keyword is invalid.
        if value == original_input:
            return
        if isinstance(original_input, Input):
            # Call resolve dset to enable type check
            # Set binding of pipeline input/parameter
            original_input._dset = original_input._resolve_dset(value, original_input.name)
        elif isinstance(original_input, PipelineParameter):
            # Set binding of pipeline parameter
            original_input.default_value = value
        else:
            # Set literal value, dataset, or parameter group
            self.update({key: value})

    def __setattr__(self, key, value):
        self.__setitem__(key, value)


class _OutputsAttrDict(_AttrDict):
    """Use this class for outputs to make sure outputs.some_output = xx will raise exception."""

    def __init__(self, dct):
        for v in dct.values():
            if not isinstance(v, Output):
                raise ValueError("OutputsAttrDict must be mappings from key to Outputs.")
        super().__init__(dct)

    def __getitem__(self, item) -> Output:
        return super().__getitem__(item)

    def __getattr__(self, item) -> Output:
        return super().__getattr__(item)

    def __setitem__(self, key, value):
        raise CannotSetAttributeError('outputs')

    def __setattr__(self, key, value):
        raise CannotSetAttributeError('outputs')


class _ComponentLoadSource(object):
    UNKNOWN = 'unknown'
    REGISTERED = 'registered'
    FROM_YAML = 'from_yaml'
    FROM_FUNC = 'from_func'
    FROM_NOTEBOOK = 'from_notebook'


class Component(WorkspaceTelemetryMixin):
    r"""
    An operational unit that can be used to produce a pipeline.

    A pipeline consists of a series of :class:`azure.ml.component.Component` nodes.

    .. remarks::

        Note that you should not use the constructor yourself. Use :meth:`azure.ml.component.Component.load`
        and related methods to acquire the needed :class:`azure.ml.component.Component`.

        The main functionality of the Component class resides at where we call "component function".
        A "component function" is essentially a function that you can call in Python code, which has parameters
        and returns the value that mimics the component definition in Azure Machine Learning.

        The following example shows how to create a pipeline using :class:`azure.ml.component.Component` class:

        .. code-block:: python

            # Suppose we have a workspace as 'ws'
            input1 = Dataset.get_by_name(ws, name='dset1')
            input2 = Dataset.get_by_name(ws, name='dset2')

            # Loading built-in component "Join Data" and "remove_duplicate_rows_func" as component functions
            join_data_component_func = Component.load(ws, name='azureml://Join Data')
            remove_duplicate_rows_func = Component.load(ws, name='azureml://Remove Duplicate Rows')

            # Use `azure.ml.component.dsl.Pipeline` to create a pipeline with two component nodes
            @dsl.pipeline(name='Sample pipeline',
                          description='Sample pipeline with two nodes',
                          default_compute_target='aml-compute')
            def sample_pipeline():
                # join_data_component_func is a dynamic-generated function, which has the signature of
                # the actual inputs & parameters of the "Join Data" component.
                join_data = join_data_component_func(
                    dataset1=input1,
                    dataset2=input2,
                    comma_separated_case_sensitive_names_of_join_key_columns_for_l=
                        "{\"KeepInputDataOrder\":true,\"ColumnNames\":[\"MovieId\"]}",
                    comma_separated_case_sensitive_names_of_join_key_columns_for_r=
                        "{\"KeepInputDataOrder\":true,\"ColumnNames\":[\"Movie ID\"]}",
                    match_case="True",
                    join_type="Inner Join",
                    keep_right_key_columns_in_joined_table="True"
                )
                # join_data is now a `azure.ml.component.Component` instance.

                # Note that function parameters are optional, you can just use remove_duplicate_rows_func()
                # and set the parameters afterwards using `set_inputs` method.
                remove_duplicate_rows = remove_duplicate_rows_func()

                remove_duplicate_rows.set_inputs(
                    # Note that we can directly use outputs of previous components.
                    dataset=join_data.outputs.result_dataset,
                    key_column_selection_filter_expression=
                        "{\"KeepInputDataOrder\":true,\"ColumnNames\":[\"Movie Name\", \"UserId\"]}",
                    retain_first_duplicate_row = "True"
                )

            pipeline = sample_pipeline()

            # Submit the run
            pipeline.submit(experiment_name="SamplePipeline", ws)

        Note that we prefer to use Dataset over DataReference in component SDK. The following example demonstrates
        how to register a dataset from data in Designer global datasets store:

        .. code-block:: python

            try:
                dset = Dataset.get_by_name(ws, 'Automobile_price_data_(Raw)')
            except Exception:
                global_datastore = Datastore(ws, name="azureml_globaldatasets")
                dset = Dataset.File.from_files(global_datastore.path('GenericCSV/Automobile_price_data_(Raw)'))
                dset.register(workspace=ws,
                            name='Automobile_price_data_(Raw)',
                            create_new_version=True)
                dset = Dataset.get_by_name(ws, 'Automobile_price_data_(Raw)')
            blob_input_data = dset
            component = some_component_func(input=blob_input_data)


    For more information about components, see:

    * `What's an azure ml component <https://github.com/Azure/DesignerPrivatePreviewFeatures>`_

    * `Define a component using component specs <https://aka.ms/azureml-component-specs>`_
    """

    def __init__(self, definition: CommandComponentDefinition, _init_params: Mapping[str, str],
                 _is_direct_child=True):
        """Initialize a component with a component definition.

        :param definition: The CommandComponentDefinition object which describe the interface of the component.
        :type definition: azure.ml.component._core._component_definition.CommandComponentDefinition
        :param _init_params: (Internal use only.) The init params will be used to initialize inputs and parameters.
        :type _init_params: dict
        :param _is_direct_child: If there is a pipeline component definition
            is_direct_child means whether the component is current definition's direct child.
        :type _is_direct_child: bool
        """
        WorkspaceTelemetryMixin.__init__(self, definition.workspace)
        self._workspace = definition.workspace
        self._definition = definition
        self._name_to_argument_name_mapping = {
            **{p.name: arg for arg, p in definition.inputs.items()},
            **{p.name: arg for arg, p in definition.parameters.items()},
            **{p.name: arg for arg, p in definition.outputs.items()},
        }

        # Generate an id for every component instance
        self._instance_id = str(uuid.uuid4())

        # Telemetry
        self._specify_input_mode = False
        self._specify_output_mode = False
        self._specify_output_datastore = False

        self._init_public_interface(_init_params)

        self._name = definition.name
        self._runsettings, self._k8srunsettings = _RunSettingsInterfaceGenerator.build(self, self._workspace)

        self._env = None
        # parent will be set in pipeline if is pipeline node
        self._parent = None

        self._init_dynamic_method()
        self._is_direct_child = _is_direct_child
        self._regenerate_output = None
        self._comment = None

        if _is_direct_child:
            # Add current component to global parent pipeline if there is one
            from ._pipeline_component_definition_builder import _add_component_to_current_definition_builder
            _add_component_to_current_definition_builder(self)

    @property
    def _specify_runsettings(self):
        return _has_specified_runsettings(self._runsettings)

    @property
    def _specify_k8srunsettings(self):
        return _has_specified_runsettings(self._k8srunsettings)

    #  region Private Methods

    def _init_public_interface(self, init_params):
        init_params = {} if init_params is None else init_params
        for k, v in init_params.items():
            if isinstance(v, Enum):
                # Extract enum value
                init_params[k] = v.value
            elif isinstance(v, _GroupAttrDict) and v == self._definition.parameters[k].default:
                # Create new if group parameter is from definition default
                init_params[k] = copy.deepcopy(v)
        # Record for pipeline component definition
        self._init_params = init_params
        # Extra settings record the inputs and parameters using set_inputs function after component created.
        self._extra_input_settings = {}
        # Record for pipeline component definition

        # Keep order of inputs as definition
        input_builder_map = {
            name: Input(init_params[name], name=name, owner=self)
            for name, _input in self._definition.inputs.items()
            if name in init_params.keys()
        }
        # Keep order of parameters as definition
        self._inputs = _InputsAttrDict({**input_builder_map, **{
            name: init_params[name] for name, _input in self._definition.parameters.items()
            if name in init_params.keys()
        }})

        output_builder_map = {
            name: Output(name, port_name=output.name, owner=self)
            for name, output in self._definition.outputs.items()
        }
        self._outputs = _OutputsAttrDict(output_builder_map)

        self._pythonic_name_to_parameter_map = {name: name for name in self._definition.parameters}

        self._pythonic_name_to_input_map = {
            name: input.name
            for name, input in self._definition.inputs.items()
        }
        self._pythonic_name_to_output_map = {
            name: output.name
            for name, output in self._definition.outputs.items()
        }

        # TODO: Remove the following properties once the validation logic is refined
        # This case occurs when the component is initialized with a local yaml without registering to a workspace.
        if not self._definition._module_dto:
            return
        self._init_structured_interface()

    def _init_structured_interface(self):
        """Init structured interface for component."""
        interface = self._definition._module_dto.module_entity.structured_interface
        self._interface_inputs = interface.inputs
        self._interface_parameters = interface.parameters
        self._interface_outputs = interface.outputs

    def _init_dynamic_method(self):
        """Update methods set_inputs according to the component input/param definitions."""
        # Here we set all default values as None to avoid overwriting the values by default values.
        transformed_parameters = [
            KwParameter(name=name, annotation=str(param.type), default=None, _type=str(param.type))
            for name, param in self._definition.parameters.items()]
        self.set_inputs = create_kw_method_from_parameters(
            self.set_inputs, get_dynamic_input_parameter(self._definition) + transformed_parameters,
        )

    def _build_params(self) -> Mapping[str, Any]:
        """Build a map from param name -> param value."""
        params = {}
        for name, param in self._definition.parameters.items():
            if self.inputs.get(name) is None:
                continue
            provided_value = self.inputs[name]
            # Flatten group parameter
            if isinstance(provided_value, _GroupAttrDict):
                params.update(provided_value._flatten(group_parameter_name=name))
            else:
                params[param.name] = provided_value
        return params

    def _resolve_compute_for_telemetry(self, default_compute):
        """
        Resolve compute to tuple.

        :param default_compute: pipeline compute specified.
        :type default_compute: tuple(name, type)
        :return: (resolve compute, use_component_compute)
        :rtype: tuple(tuple(name, type), bool)
        """
        if not isinstance(default_compute, tuple):
            raise TypeError("default_compute must be a tuple")

        # scope component does not have compute target. special handle here
        if self._definition.type == ComponentType.ScopeComponent:
            return (None, True)

        runsettings = self._runsettings
        target = runsettings._get_target()

        # it will return None when no target is set
        if target is None or target == 'local':
            return default_compute, False

        if isinstance(target, tuple):
            return target, True
        target = _get_parameter_static_value(target)

        if isinstance(target, str):
            default_compute_name, _ = default_compute
            if target == default_compute_name:
                return default_compute, True

            # try to resolve
            from ._restclients.service_caller_factory import _DesignerServiceCallerFactory
            service_caller = _DesignerServiceCallerFactory.get_instance(self._workspace)
            target_in_workspace = service_caller.get_compute_by_name(target)
            if target_in_workspace is None:
                print('target={}, not found in workspace, assume this is an AmlCompute'.format(target))
                return (target, "AmlCompute"), True
            else:
                return (target_in_workspace.name, target_in_workspace.compute_type), True
        else:
            return target, True

    def _get_telemetry_values(self, compute_target=None, additional_value=None):
        """
        Get telemetry value out of a Component.

        The telemetry values include the following entries:

        * load_source: The source type which the component node is loaded.
        * specify_input_mode: Whether the input mode is being by users.
        * specify_output_mode: Whether the output mode is being by users.
        * specify_output_datastore: Whether the output datastore is specified by users.
        * specify_runsettings: Whether the runsettings is specified by users.
        * specify_k8srunsettings: Whether the k8srunsettings is specified by users.
        * pipeline_id: the pipeline_id if the component node belongs to some pipeline.
        * specify_node_level_compute: Whether the node level compute is specified by users.
        * compute_type: The compute type that the component uses.

        :param compute_target: The compute target.
        :return: telemetry values.
        :rtype: dict
        """
        telemetry_values = super()._get_telemetry_values()
        if self._module_dto:
            telemetry_values.update(self._module_dto._get_telemetry_values())
        telemetry_values['load_source'] = self._definition._load_source
        telemetry_values['specify_input_mode'] = self._specify_input_mode
        telemetry_values['specify_output_mode'] = self._specify_output_mode
        telemetry_values['specify_output_datastore'] = self._specify_output_datastore
        telemetry_values['specify_runsettings'] = self._specify_runsettings
        telemetry_values['specify_k8srunsettings'] = self._specify_k8srunsettings
        telemetry_values['specify_comment'] = self._comment is not None

        node_compute_target, specify_node_level_compute = self._resolve_compute_for_telemetry(compute_target) \
            if compute_target is not None else (None, False)

        if self._parent is not None:
            telemetry_values['pipeline_id'] = self._parent._id
        if node_compute_target is not None:
            telemetry_values['specify_node_level_compute'] = specify_node_level_compute
            telemetry_values['compute_type'] = node_compute_target[1]

        telemetry_values.update(additional_value or {})
        return telemetry_values

    def _get_instance_id(self):
        return self._instance_id

    def _get_run_setting(self, name, expected_type, default_value=None):
        """Get run setting with name, returns default_value if didn't find or type did not match expected_type."""
        try:
            val = getattr(self._runsettings, name)
            if not isinstance(val, expected_type):
                raise ValueError("{} should be returned.".format(expected_type))
            else:
                return val
        except (AttributeError, ValueError):
            return default_value

    def _get_default_parameters(self):
        """Get exposed parameters' key-value pairs."""
        params = {}
        for name, param in self._definition.parameters.items():
            value = param.default
            # Flatten group parameter
            if isinstance(value, _GroupAttrDict):
                params.update(value._flatten(group_parameter_name=name))
            else:
                params[param.name] = value

        return params

    @property
    def _compute(self):
        """
        Get resolved compute target of the component considering inheritance (Disable subgraph).

        :return: ComputeName, ComputeType, use_root_pipeline_default_compute(use_graph_default_compute)
        :rtype: str, str, boolean
        """
        return self._resolve_compute()

    def _resolve_compute(self, enable_subpipeline_registration=False):
        """
        Get resolved compute target of the component considering inheritance.

        :return: ComputeName, ComputeType, use_root_pipeline_default_compute(use_graph_default_compute)
        :rtype: str, str, boolean
        """
        compute_name = None
        compute_type = None
        use_root_pipeline_default_compute = False
        pipeline = self

        if not self._is_pipeline:
            # Get runsettings target if is not pipeline.
            # Some component type do not has target, e.g. scope component
            compute_name = self.runsettings.target if hasattr(self.runsettings, 'target') else None
            if isinstance(compute_name, tuple):
                compute_name, compute_type = self.runsettings.target
            # Extract value from pipeline parameter/assignment/Input
            if enable_subpipeline_registration:
                if isinstance(compute_name, PipelineParameter) or isinstance(compute_name, _ParameterAssignment):
                    # return compute_name, compute_type, use_root_pipeline_default_compute
                    return None, None, False

            compute_name = _get_parameter_static_value(compute_name)

            if compute_name is not None:
                if compute_type is None:
                    compute_type = _get_compute_type(self.workspace, compute_name)
                return compute_name, compute_type, use_root_pipeline_default_compute
            else:
                pipeline = self._parent

        use_root_pipeline_default_compute = True
        if pipeline is None:
            return compute_name, compute_type, use_root_pipeline_default_compute

        def _get_compute(pipeline):

            pipeline_compute = pipeline._get_default_compute_target()
            # If pipeline _parent is None, it is root pipeline, use_graph_default_compute shall be True
            if pipeline_compute[0] is not None:
                compute_type = pipeline_compute[1] if pipeline_compute[1] is not None \
                    else _get_compute_type(self.workspace, pipeline_compute[0])
                return pipeline_compute[0], compute_type, pipeline._parent is None

            # Component is sub_pipeline
            if pipeline._parent is not None:
                return _get_compute(pipeline._parent)

            # If pipeline _parent is None, it is root pipeline, use_graph_default_compute shall be True
            return None, None, pipeline._parent is None

        return _get_compute(pipeline)

    def _resolve_default_datastore(self):
        """
        Resolve default datastore on component considering inheritance.

        :return: the default datastore.
        :rtype: azureml.core.Datastore
        """
        pipeline = self if self._is_pipeline else self._parent
        if pipeline is None:
            return None

        def _get_default_datastore(pipeline):
            if pipeline.default_datastore is not None:
                return pipeline.default_datastore

            # Component is sub_pipeline
            if pipeline._parent is not None:
                return _get_default_datastore(pipeline._parent)

            # If pipeline _parent is None, it is root pipeline, return the workspace default_datastore
            return _get_workspace_default_datastore(pipeline.workspace)
        return _get_default_datastore(pipeline)

    def _resolve_inputs_for_runconfig(self):
        """Resolve inputs to data_references, datasets, and input mapping for runconfig."""
        data_references, datasets, inputs = {}, {}, {}
        for name, input in self._input_ports.items():
            if input._dset is None:
                # For this case, we set it as None to indicate this is an optional input without value.
                inputs[name] = None
            elif isinstance(input._dset, (str, Path)):
                # We simply put the path in the input if the path is provided
                inputs[name] = str(input._dset)

            elif isinstance(input._dset, DataReference):
                reference = input._dset
                # Change the mode according to the input mode, only 'mount' and 'download' are valid.
                if input.mode == 'download':
                    reference = reference.as_download()
                else:
                    reference = reference.as_mount()
                data_references[name] = reference.to_config()
                inputs[name] = "{}{}".format(DATA_REF_PREFIX, name)

            elif isinstance(input._dset, (AbstractDataset, DatasetConsumptionConfig)):
                # If it is a dataset, convert it to DatasetConsumptionConfig first
                # If input.mode is not set, here we use 'mount' as default, since most components only handle mount
                # TODO: Maybe we need to use the default input mode of the component.
                consumption_config = input._dset if isinstance(input._dset, DatasetConsumptionConfig) else \
                    input._build_dataset(input._dset, input.mode or 'mount')

                # Make sure this has been registered in the workspace
                _ensure_dataset_saved_in_workspace(consumption_config.dataset, self._workspace)
                datasets[name] = consumption_config
                inputs[name] = consumption_config.arg_val
            else:
                msg = "The input %r has unsupported type %r, only DataReference and Dataset are supported." % (
                    input.name, type(input._dset),
                )
                raise UserErrorException(msg)
        return data_references, datasets, inputs

    def _resolve_outputs_for_runconfig(self, run_id):
        """Resolve outputs to data_references and output mapping for runconfig."""
        default_datastore = self._workspace.get_default_datastore() if self._workspace else None
        data_references, outputs = {}, {}
        for name, output in self.outputs.items():
            # This path will be showed on portal's outputs if datastore is workspaceblobstore
            # Note that in default {run-id} and {output-name} are valid templates in pipeline,
            # we need have a replacement for a runconfig run.
            path = "azureml/{run-id}/outputs/{output-name}"
            if output._dataset_output_options:
                path = output._dataset_output_options.path_on_datastore
            path = path.format(**{'run-id': run_id, 'output-name': name})

            datastore = output.datastore if output.datastore else default_datastore
            if datastore is None:
                raise ValueError("Resolving outputs without datastore is not allowed for component %r." % self.name)
            reference = datastore.path(path)

            # Change the mode according to the output mode, only 'mount' and 'upload' are valid.
            if output.output_mode == 'mount':
                reference = reference.as_mount()
            elif output.output_mode == 'upload':
                reference = reference.as_upload()
            # Change the path on compute of the output
            if output._path_on_compute:
                reference.path_on_compute = output._path_on_compute
            data_references[name] = reference.to_config()
            outputs[name] = "{}{}".format(DATA_REF_PREFIX, name)
        return data_references, outputs

    def _populate_runconfig(self, run_id, use_local_compute=False):
        """Populate runconfig from component."""
        raw_conf = json.loads(self._module_dto.module_entity.runconfig)
        run_config = RunConfiguration._get_runconfig_using_dict(raw_conf)
        run_config._target, compute_type = ('local', None)
        if not use_local_compute and self._runsettings.target is not None:
            compute_type = _get_compute_type(self._workspace, self._runsettings.target)
            run_config._target, compute_type = (self._runsettings.target, compute_type)

        if self.type == ComponentType.DistributedComponent.value:  # MPI related run config update
            node_count = getattr(self._runsettings, 'node_count', 1)
            process_count_per_node = getattr(self._runsettings, 'process_count_per_node', 1)
            if use_local_compute:  # When running in local, these values are 1
                node_count, process_count_per_node = 1, 1
            run_config.mpi.node_count, run_config.mpi.process_count_per_node = node_count, process_count_per_node
            run_config.node_count = node_count

        # Update k8s runsettings related config
        _update_run_config(self, run_config, compute_type)

        # Resolve inputs/outputs for runconfig.
        data_references, datasets, inputs = self._resolve_inputs_for_runconfig()
        run_config.data_references.update(data_references)
        data_references, outputs = self._resolve_outputs_for_runconfig(run_id=run_id)
        run_config.data_references.update(data_references)

        from azure.ml.component._execution._command_execution_builder import ComponentRunCommand
        inputs_with_parameters = {**inputs, **self._parameter_params}
        # Use resolved inputs/outputs/parameters to get the command to run
        command = ComponentRunCommand.generate_component_command(self._definition, inputs_with_parameters, outputs)

        # If the returned command is a string, it is an AnyCommand
        if isinstance(command, str):
            run_config.command = command
        # Otherwise, it is a python command with list arguments, we should remove the first two "python xx.py"
        else:
            run_config.arguments = command[2:]
            # This logic is for submitting to remote run so the datasets in the arguments could be correctly handled.
            replacements = {dataset.arg_val: dataset for dataset in datasets.values()}
            for i in range(len(run_config.arguments)):
                arg = run_config.arguments[i]
                if isinstance(arg, str) and arg in replacements:
                    run_config.arguments[i] = replacements[arg]

        return run_config

    def _replace(self, new_component: 'Component'):
        """Replace component in pipeline. Use it cautiously."""
        self._workspace = new_component.workspace
        self._definition = new_component._definition

    def _replace_inputs(self, *args, **kwargs) -> 'Component':
        """Replace the inputs of component."""
        self._inputs = _InputsAttrDict({
            k: Input(v, k, owner=self) if k in self._definition.inputs else v for k, v in kwargs.items()})
        return self

    def _update_parameter_assignments_with_pipeline_parameter(self, pipeline_parameter, print_warning=True):
        """Try resolve a string with @@ as _ParameterAssignment."""
        def update_obj(obj):
            if isinstance(obj, str):
                obj = _ParameterAssignment.resolve(obj, pipeline_parameter, print_warning)
            elif isinstance(obj, _ParameterAssignment):
                # Str parameter assignment's value_dict need update.
                obj.update(**pipeline_parameter)
            elif isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = update_obj(v)
            elif type(obj) in [tuple, list]:
                obj = type(obj)([update_obj(i) for i in obj])
            return obj

        # 1. Update current component parameters.
        for _k, _v in self._parameter_params.items():
            from_extra_input = _k in self._extra_input_settings and _v == self._extra_input_settings[_k]
            self._inputs[_k] = update_obj(_v)
            # Update if input value is from extra input settings
            if from_extra_input:
                self._extra_input_settings[_k] = self._inputs[_k]
        # 2. Update comment object.
        self._comment = update_obj(self._comment)
        if self._is_pipeline or self._runsettings is None:
            return
        # 3. Update component runsettings.
        runsettings_values = self._runsettings._store._user_provided_values
        for p_id, value in runsettings_values.items():
            runsettings_values[p_id] = update_obj(runsettings_values[p_id])

    def _is_replace_target(self, target: 'Component'):
        """
        Provide for replace a component in pipeline.

        Check if current node(component) is the target one we want

        :return: Result of comparision between two components
        :rtype: bool
        """
        if target.name != self.name:
            return False
        if target._identifier != self._identifier:
            return False
        return True

    def _get_environment(self):
        """Get environment of component by deserializing runconfig or definition."""
        if self._env is None:
            # When component is initialized by ComponentDefinition, using _definition to get environment.
            self._env = self._definition.environment._to_aml_sdk_env()
            # If component using curated environment, definition environment name and version not be None.
            # If not using curated environment, environment not set name and version, only contains
            # python and docker info.
            is_environment_registered = self._env.name is not None
            # Need to register environment before build it.
            if not is_environment_registered:
                # When register environment, it need to set environment name and will generate conda env name by hash
                # env info, except name. Since environments with same env info and diff name, have same conda env name.
                # Because component name may containe strange character, using component identifier as env name to
                # avoid registering failure.
                # When component is not registered, identifier will be None.
                self._env.name = self._identifier if self._identifier else self._id
                self._env = self._env.register(self.workspace)
        return self._env

    @staticmethod
    def _from_func_imp(
            workspace: Workspace,
            func: types.FunctionType,
            force_reload=True,
            load_source=_ComponentLoadSource.UNKNOWN
    ) -> Callable[..., 'Component']:
        def _reload_func(f: types.FunctionType):
            """Reload the function to make sure the latest code is used to generate yaml."""
            module = importlib.import_module(f.__module__)
            # if f.__name__ == '__main__', reload will throw an exception
            if f.__module__ != '__main__':
                from azure.ml.component.dsl._utils import _force_reload_module
                _force_reload_module(module)
            return getattr(module, f.__name__)

        if force_reload:
            func = _reload_func(func)
        # Import here to avoid circular import.
        from azure.ml.component.dsl._component import ComponentExecutor
        from azure.ml.component.dsl._module_spec import SPEC_EXT
        from azure.ml.component.dsl._utils import _temporarily_remove_file
        # If a ComponentExecutor instance is passed, we directly use it,
        # otherwise we construct a ComponentExecutor with the function
        executor = func if isinstance(func, ComponentExecutor) else ComponentExecutor(func)
        # Use a temp spec file to register.
        temp_spec_file = Path(inspect.getfile(func)).absolute().with_suffix(SPEC_EXT)
        temp_conda_file = temp_spec_file.parent / 'conda.yaml'
        conda_exists = Path(temp_conda_file).is_file()
        # the conda may be the notebook gen conda, cannot temporarily remove if exists
        with _temporarily_remove_file(temp_spec_file):
            try:
                temp_spec_file = executor.to_spec_yaml(folder=temp_spec_file.parent,
                                                       spec_file=temp_spec_file.name)
                return Component._from_module_spec(workspace=workspace, yaml_file=str(temp_spec_file),
                                                   load_source=load_source)
            finally:
                if not conda_exists and Path(temp_conda_file).is_file():
                    Path(temp_conda_file).unlink()

    @staticmethod
    def _from_module_spec(
            workspace: Optional[Workspace],
            yaml_file: str,
            load_source: str = None,
            register=True,
    ) -> Callable[..., 'Component']:
        if not register:
            definition = CommandComponentDefinition.load(yaml_file=yaml_file)
            definition._workspace = workspace
            definition._load_source = load_source
            definition._module_dto = _definition_to_dto(definition)
            return Component._component_func_from_definition(definition)

        if workspace is None:
            raise UserErrorException("Workspace cannot be None if register=True.")

        definition = CommandComponentDefinition.register(
            workspace, spec_file=yaml_file, package_zip=None,
            anonymous_registration=True,
            set_as_default=False, amlignore_file=None, version=None,
        )
        definition._load_source = load_source

        return Component._component_func_from_definition(definition)

    @staticmethod
    def _component_func(
            workspace: Workspace,
            module_dto: ModuleDto,
            load_source: str = _ComponentLoadSource.UNKNOWN
    ) -> Callable[..., 'Component']:
        """
        Get component func from ModuleDto.

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param module_dto: ModuleDto instance
        :type module_dto: azure.ml.component._module_dto
        :param load_source: The source which the component is loaded.
        :type load_source: str
        :return: a function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        def create_component_func(**kwargs) -> 'Component':
            return Component(definition, _init_params=kwargs)

        definition = _dto_2_definition(module_dto, workspace)
        # TODO: Set the source when initialize the definition.
        definition._load_source = load_source
        return to_component_func_from_definition(definition=definition,
                                                 component_creation_func=create_component_func)

    @staticmethod
    def _component_func_from_definition(
            definition: CommandComponentDefinition,
    ):
        @timer(activity_name='create_component_func')
        def create_component_func(**kwargs) -> 'Component':
            return Component(definition, _init_params=kwargs)

        return to_component_func_from_definition(definition=definition,
                                                 component_creation_func=create_component_func)

    # endregion

    # region Local run

    def _get_argument_name_by_name(self, name):
        """Return the argument name of an input/output according its name."""
        return self._name_to_argument_name_mapping.get(name)

    def _input_is_optional(self, argument_name):
        return self._definition.inputs[argument_name].optional

    def _get_input_name_by_argument_name(self, argument_name):
        return self._definition.inputs[argument_name].name

    def _output_is_file(self, argument_name):
        """Return True if the output is expected to be a file instead of a directory.

        This is only used in Component.run, will be refined in the future.
        """
        return self._definition.outputs[argument_name].type == 'AnyFile'

    def _validate_parameters(self, parameters):
        """
        Validate parameters' key and return the valid k-v pairs.

        Parameters with key which appear in neither parameters nor inputs are invalid and will be ignored.

        :param parameters: the pipeline parameters
        :type parameters: dict
        :return: valid parameters
        :rtype: dict
        """
        if parameters is None:
            return
        result = {}
        # Print warning if there is unrecognized parameter key.
        for _k, _v in parameters.items():
            if _k not in self.inputs and _k not in self._outputs:
                # _dynamic.py will raise exception before reach here.
                logging.warning('Parameter \'{}={}\' was unrecognized by pipeline {} and will be ignored.'.format(
                    _k, _v, self.name
                ))
            if _v is None:
                # Parameters with default None will be added for method intelligence.
                continue
            result[_k] = _v
        return result

    def _parse_graph_path(self):
        """
        Split graph path into pipeline path and component name.

        :return: pipeline_path, component_name
        :rtype: str, str
        """
        if self._parent:
            pipeline_path = self._parent._graph_path
            component_name = _sanitize_python_variable_name(
                self._parent._node_id_variable_name_dict.get(self._instance_id, self.name))
        else:
            pipeline_path = None
            component_name = self._graph_path
        return pipeline_path, component_name

    def _get_component_name(self):
        """
        Get the name for the component. The name is unique accros the components belong to the same pipeline.

        :return: component_name
        :rtype: str
        """
        return self._parse_graph_path()[1]

    # endregion

    # region Public Methods

    @property
    def comment(self):
        """
        Get the comment of the Component.

        :return: The comment.
        :rtype: str
        """
        # self._comment could be either basic type or _ParameterAssignment
        value = self._comment.value if isinstance(self._comment, _ParameterAssignment) else self._comment
        return value if value is None else str(value)

    @comment.setter
    def comment(self, comment):
        """Set the comment of the Component."""
        if isinstance(comment, Input):
            comment = comment._get_internal_data_source()
        if isinstance(comment, PipelineParameter):
            # Convert PipelineParameter to string to treat it as Parameter Assignment.
            comment = str(comment)

        self._comment = comment

    @property
    def name(self):
        """
        Get the name of the Component.

        :return: The name.
        :rtype: str
        """
        return self._definition.name

    @property
    def display_name(self):
        """
        Get the display name of the Component.

        :return: The display name.
        :rtype: str
        """
        return self._definition.display_name

    @property
    def type(self):
        """
        Get the type of the Component.

        :return: The type.
        :rtype: str
        """
        return self._definition.type.value

    @property
    def inputs(self) -> _AttrDict[str, Input]:
        """Get the inputs of the Component.

        :return: The dict in which the keys are input names, the values are input instances initialized by datasets.
        :rtype: dict[str, Input]
        """
        # Note here we return component inputs and parameters
        # which is different from component definition
        return self._inputs

    @property
    def outputs(self) -> _AttrDict[str, Output]:
        """Get the outputs of the Component.

        :return: The dict in which the keys are the output names, the values are the output instances.
        :rtype: dict[str, Output]
        """
        return self._outputs

    @property
    def runsettings(self):
        """
        Get run settings of the Component.

        :return: The run settings.
        :rtype: azure.ml.component.RunSettings
        """
        return self._runsettings

    @property
    def k8srunsettings(self):
        """
        Get compute run settings of the Component.

        :return: The compute run settings
        :rtype: _K8sRunSettings
        """
        return self._k8srunsettings

    @property
    def workspace(self):
        """
        Get the workspace of the Component.

        :return: The workspace.
        :rtype: azureml.core.Workspace
        """
        return self._definition.workspace

    @property
    def regenerate_output(self):
        """
        Get or set the flag indicating whether the component should be run again.

        Set to True to force a new run (disallows component/datasource reuse).

        :return: the regenerate_output value.
        :rtype: bool
        """
        return self._regenerate_output

    @regenerate_output.setter
    def regenerate_output(self, regenerate_output):
        self._regenerate_output = regenerate_output

    @property
    def _module_dto(self):
        # TODO: Remove all reference to this
        return self._definition._module_dto

    @property
    def _graph_path(self):
        """
        Return the component's graph path when defined in pipeline.

        The graph_path can show the path from top pipeline to current node.
        e.g.
        @dsl.pipeline()
        def sub_pipeline():
            node = component_func()
        @dsl.pipeline()
        def parent_pipeline():
            sub = sub_pipeline()

        Then the node._graph_path would be 'parent_pipeline.sub.node'.
        """
        if self._parent is None:
            return _sanitize_python_variable_name(self.name)
        trace = []
        node = self
        while node._parent is not None:
            parent = node._parent
            trace.append(_sanitize_python_variable_name(
                parent._node_id_variable_name_dict.get(node._id, node.name)))
            node = parent
        # Append root pipeline function name
        trace.append(_sanitize_python_variable_name(node.name))

        return '.'.join(reversed(trace))

    @property
    def _identifier(self):
        """Return the identifier of the component.

        :return: The identifier.
        :rtype: str
        """
        return self._definition.identifier

    @property
    def _is_pipeline(self):
        """Return the component is a pipeline or not.

        :return: The result.
        :rtype: bool
        """
        return False

    @property
    def _is_registered(self):
        """Return the pipeline component has been registered or not.

        :return: The result.
        :rtype: bool
        """
        if self._definition and self._definition.identifier:
            return True
        else:
            return False

    @property
    def version(self):
        """Return the version of the component.

        :return: The version.
        :rtype: str
        """
        return self._definition.version

    @property
    def created_by(self):
        """Return the name who created the corresponding component in the workspace.

        :return: The name who created the component.
        :rtype: str
        """
        return self._definition.creation_context.created_by

    @property
    def created_date(self):
        """Return the created date of the corresponding component in the workspace.

        :return: The created date with the ISO format.
        :rtype: str
        """
        return self._definition.creation_context.created_date

    @property
    def _id(self):
        """Return the instance id of component.

        :return: The unique instance id.
        :rtype: str
        """
        return self._instance_id

    @property
    def _input_ports(self):
        """Return the input ports of component.

        :return: The input ports.
        :rtype: dict
        """
        return {k: v for k, v in self._inputs.items() if k in self._definition.inputs}

    @property
    def _parameter_params(self):
        """Return the parameters of component.

        :return: The parameters.
        :rtype: dict
        """
        return {k: v for k, v in self._inputs.items() if k in self._definition.parameters}

    def set_inputs(self, *args, **kwargs) -> 'Component':
        """Update the inputs and parameters of the component.

        :return: The component itself.
        :rtype: azure.ml.component.Component
        """
        # Note that the argument list must be "*args, **kwargs" to make sure
        # vscode intelligence works when the signature is updated.
        # https://github.com/microsoft/vscode-python/blob/master/src/client/datascience/interactive-common/intellisense/intellisenseProvider.ts#L79
        kwargs = self._validate_parameters(kwargs)
        for k, v in kwargs.items():
            if isinstance(v, Enum):
                v = v.value
            kwargs[k] = _Group._customer_class_value_to_attr_dict(v)
        self._inputs.update(
            {k: Input(v, k, owner=self) for k, v in kwargs.items()
             if v is not None and k in self._definition.inputs})
        self._inputs.update(
            {k: v for k, v in kwargs.items()
             if v is not None and k in self._definition.parameters})
        if self._is_direct_child:
            self._extra_input_settings.update(kwargs)
            # Use current build's parameter to resolve assignments if exist.
            from ._pipeline_component_definition_builder import _try_resolve_assignments_and_update_parameters
            _try_resolve_assignments_and_update_parameters(self)
        return self

    def _validate(
            self, raise_error=False, pipeline_parameters=None, is_local=False,
            default_datastore=None, default_compute=None
    ) -> List:
        """
        Validate that all the inputs and parameters are in fact valid.

        :param raise_error: Whether to raise exceptions on error
        :type raise_error: bool
        :param pipeline_parameters: The pipeline parameters provided.
        :type pipeline_parameters: dict
        :param is_local: Whether the validation is for local run in the host, false if it is for remote run in AzureML.
                         If is_local=True, TabularDataset is not support, component will support local path as input
                         and skip runsettings validation.
        :type is_local: bool
        :param default_datastore: The default datastore of component.
        :type default_datastore: azureml.core.Datastore
        :param default_compute: The default compute of pipeline in which the component is located.
        :type default_compute: tuple(str, str)

        :return: The errors found during validation.
        :rtype: builtin.list
        """
        return self._validate_component(
            raise_error=raise_error, pipeline_parameters=pipeline_parameters, is_local=is_local,
            default_datastore=default_datastore, default_compute=default_compute
        )

    def _process_error(self, e: Exception, error_type, variable_name, variable_type, raise_error=False, errors=None):
        """
        Process component validation error.

        :param e: Inner error exception
        :param error_type: Error type
        :param variable_name: Variable name
        :param variable_type: Variable type
        :param raise_error: If raise the error
        :param errors: all collected errors
        """
        ve = ComponentValidationError(str(e), e, error_type)
        if raise_error:
            raise ve
        else:
            errors.append(Diagnostic.create_diagnostic_by_component(self, ve.message, ve.error_type,
                                                                    variable_name, variable_type))

    def _validate_component(
            self, raise_error=False, pipeline_parameters=None, is_local=False,
            default_datastore=None, default_compute=None, for_definition_validate=False, definition_validator=None,
            inputs=None, parameters=None, skip_datastore_compute_validation=False
    ) -> List:
        """
        Validate Pipeline/Component as a component.

        :param raise_error: Whether to raise exceptions on error
        :type raise_error: bool
        :param pipeline_parameters: The pipeline parameters provided.
        :type pipeline_parameters: dict
        :param is_local: Whether the validation is for local run in the host, false if it is for remote run in AzureML.
                         If is_local=True, TabularDataset is not support, component will support local path as input
                         and skip runsettings validation.
        :type is_local: bool
        :param default_datastore: The default datastore of component.
        :type default_datastore: azureml.core.Datastore
        :param default_compute: The default compute of pipeline in which the component is located.
        :type default_compute: tuple(str, str)
        :param for_definition_validate: if the validate is for pipeline definition validate.
        :type for_definition_validate: bool
        :param definition_validator: definition validator
        :type definition_validator: azure.ml.component._component_validator.DefinitionValidator
        :param inputs: inputs to validate, will use component's input if None
        :type inputs: dict
        :param parameters: parameters to validate, will use component's parameter if None
        :type parameters: dict
        :param skip_datastore_compute_validation: Datastore/compute might be incorrect when validating definition but
                            overwrite to correct one before submission. So we skip this check when validating
                            definition and validate it before submission.
        :type skip_datastore_compute_validation: bool

        :return: The errors found during validation.
        :rtype: builtin.list
        """
        # Validate inputs
        errors = []

        if for_definition_validate and definition_validator:
            # use pipeline definition func to process error if defined
            process_error = definition_validator.process_error
        else:
            process_error = functools.partial(self._process_error, raise_error=raise_error, errors=errors)

        if inputs is None:
            inputs = self._input_ports
        if parameters is None:
            parameters = self._parameter_params
        if for_definition_validate:
            # skip datastore/compute validation for definition because it can be updated
            # after the pipeline definition built
            skip_datastore_compute_validation = True

        def update_provided_inputs(provided_inputs, pipeline_parameters):
            if pipeline_parameters is None:
                return provided_inputs
            _provided_inputs = {}
            for k, v in provided_inputs.items():
                _input = v._get_internal_data_source()
                if not isinstance(_input, PipelineParameter) or _input.name not in pipeline_parameters.keys():
                    _provided_inputs[k] = v
                else:
                    _provided_inputs[k] = (Input(PipelineParameter(
                        name=_input.name, default_value=pipeline_parameters[_input.name]),
                        name=v.name, mode=v.mode, owner=v._owner))
            return _provided_inputs

        def update_provided_parameters(provided_parameters, pipeline_parameters):
            _params = {}
            for k, v in provided_parameters.items():
                _input = v._get_internal_data_source() if isinstance(v, Input) else v
                if isinstance(v, _GroupAttrDict):
                    # Add flattened group parameters
                    _params.update({
                        _k: pipeline_parameters.get(_k, _v) if isinstance(_v, PipelineParameter) else _v
                        for _k, _v in v._flatten(group_parameter_name=k).items()})
                elif not isinstance(_input, PipelineParameter) or \
                        pipeline_parameters is None or \
                        _input.name not in pipeline_parameters.keys():
                    _params[k] = _input
                else:
                    _params[k] = pipeline_parameters[_input.name]
            return _params

        def replace_inputs_with_original_object(provided_inputs: dict, pipeline_parameters: dict):
            # Replace Input/PipelineParameter in provided_inputs with objects in pipeline_parameters.
            # We are doing this because we have multiple objects for same pipeline parameter
            _provided_inputs = {}
            for k, v in provided_inputs.items():
                function_param = v._dset
                if isinstance(function_param, (
                        Input, PipelineParameter)) and function_param.name in pipeline_parameters.keys():
                    # for sub pipeline validation, extract 1 layer of input to get original pipeline parameter object
                    _provided_inputs[k] = pipeline_parameters[function_param.name]
                else:
                    _provided_inputs[k] = v
            return _provided_inputs

        def replace_params_with_original_object(provided_parameters: dict, pipeline_parameters: dict):
            # Replace PipelineParameter in provided_parameters with objects in pipeline_parameters.
            # We are doing this because we have multiple objects for same pipeline parameter
            _params = {}
            from .dsl.types import _GroupAttrDict
            for k, v in provided_parameters.items():
                if isinstance(v, _GroupAttrDict):
                    # Add flattened group parameters
                    _params.update({
                        _k: pipeline_parameters.get(_k, _v) if isinstance(_v, PipelineParameter) else _v
                        for _k, _v in v._flatten(group_parameter_name=k).items()})
                else:
                    _params[k] = definition_validator.get_original_object_for_parameter(v)
            return _params

        # Because inputs and params are obtained from _module_dto, it not support unregistered component.
        if self._definition._module_dto:
            if not for_definition_validate:
                provided_inputs = update_provided_inputs(inputs, pipeline_parameters)
            else:
                # for pipeline definition validate, won't update provided inputs, just replace Input/PipelineParameter
                # in self._input_ports with original object.
                provided_inputs = replace_inputs_with_original_object(inputs, pipeline_parameters)
            ComponentValidator.validate_component_inputs(workspace=self.workspace,
                                                         provided_inputs=provided_inputs,
                                                         interface_inputs=self._interface_inputs,
                                                         param_python_name_dict=self._module_dto
                                                         .module_python_interface.inputs_name_mapping,
                                                         process_error=process_error,
                                                         definition_validator=definition_validator,
                                                         is_local=is_local,
                                                         for_definition_validate=for_definition_validate,
                                                         pipeline_parameters=pipeline_parameters)

            if not for_definition_validate:
                provided_parameters = update_provided_parameters(parameters, pipeline_parameters)
            else:
                # for pipeline definition validate, won't update provided params, just replace PipelineParameter
                # in self._parameter_params with original object.
                provided_parameters = replace_params_with_original_object(parameters, pipeline_parameters)
                # mark pipeline parameter used for validation
                definition_validator.mark_pipeline_parameter_used(provided_parameters)
            # Skip search space params, since we cannot change its type to `dict`
            # This will not change the real value
            # TODO: Only apply this logic for SweepComponent
            if getattr(self._definition.runsettings, "linked_parameters", None) is not None:
                for p_name in provided_parameters:
                    if p_name in self._definition.runsettings.linked_parameters:
                        provided_parameters[p_name] = None
            ComponentValidator.validate_component_parameters(provided_parameters=provided_parameters,
                                                             interface_parameters=self._interface_parameters,
                                                             param_python_name_dict=self._module_dto
                                                             .module_python_interface.parameters_name_mapping,
                                                             process_error=process_error,
                                                             definition_validator=definition_validator,
                                                             for_definition_validate=for_definition_validate)

        if not is_local:
            # For pipeline component, there's no run settings
            if getattr(self, "_runsettings", None):
                self._runsettings.validate(
                    raise_error=raise_error,
                    process_error=process_error,
                    for_definition_validate=for_definition_validate,
                    definition_validator=definition_validator,
                )
                if self._k8srunsettings is not None:
                    self._k8srunsettings.validate(
                        raise_error=raise_error,
                        process_error=process_error,
                        for_definition_validate=for_definition_validate,
                        definition_validator=definition_validator,
                    )

            if not skip_datastore_compute_validation:
                ComponentValidator._validate_datastore(
                    component_type=self.type,
                    output_interfaces=self._module_dto.module_entity.structured_interface.outputs,
                    output_ports=self.outputs,
                    process_error=process_error,
                    default_datastore=default_datastore,
                )

                # Only validate component has compute or not.
                # Compute value in runsettings will be validate in runsettings validation.
                ComponentValidator._validate_compute_on_component(self, default_compute, self.workspace, process_error)
        else:
            ComponentValidator._validate_local_run_component_type(self, process_error)

        return errors

    def run(self, experiment_name=None, working_dir=None, mode=RunMode.Docker.value,
            track_run_history=True, show_output=True, skip_validation=False, raise_on_error=True, **kwargs):
        """
        Run component in local environment. For more information about Component.run, see https://aka.ms/component-run.

        .. remarks::

            Note that after execution of this method, scripts, output dirs, and log files will be created in
            working dir. Below is an usage example.

            .. code-block:: python

                # Suppose we have a workspace as 'ws'
                # First, load a component, and set parameters of component
                ejoin = Component.load(ws, name='microsoft.com.bing.ejoin')
                component = ejoin(leftcolumns='m:name;age', rightcolumns='income',
                    leftkeys='m:name', rightkeys='m:name', jointype='HashInner')
                # Second, set prepared input path and output path to run component in local. If not set working_dir,
                # will create it in temp dir. In this example, left_input and right_input are input port of ejoin.
                # And after running, output data and log will write in working_dir
                component.set_inputs(left_input=your_prepare_data_path)
                component.set_inputs(right_input=your_prepare_data_path)

                # Run component with docker-based environment
                result = component.run(working_dir=dataset_output_path, mode='docker')

                # Run component with conda-based environment
                result = component.run(working_dir=dataset_output_path, mode='conda')

                # Run component with user-managed environment
                result = component.run(working_dir=dataset_output_path, mode='host')

        :param experiment_name: The experiment_name will show in portal. If not set, will use component name.
        :type experiment_name: str
        :param working_dir: The output path for component output info
        :type working_dir: str
        :param mode: Three modes are supported to run component.
                     docker: Start a container with the component's image and run component in it.
                     conda: Build a conda environment in the host with the component's conda definition and
                     run component in it.
                     host: Directly run component in host environment.
        :type mode: str
        :param track_run_history: If track_run_history=True, will create azureml.core.Run and upload component output
                                  and log file to portal.
                                  If track_run_history=False, will not create azureml.core.Run to upload outputs
                                  and log file.
        :type track_run_history: bool
        :param show_output: Indicates whether to show the component run status on sys.stdout.
        :type show_output: bool
        :param skip_validation: Indicates whether to skip the validation of the component.
        :type skip_validation: bool
        :param raise_on_error: Indicates whether to raise an error when the Run is in a failed state
        :type raise_on_error: bool

        :return: The run status, such as, Completed and Failed.
        :rtype: str
        """
        from .pipeline import Pipeline
        if isinstance(self, Pipeline) or self._definition.type == ComponentType.PipelineComponent:
            return self._run(experiment_name=experiment_name, working_dir=working_dir, mode=mode,
                             track_run_history=track_run_history, show_output=show_output,
                             skip_validation=skip_validation, raise_on_error=raise_on_error, **kwargs)
        else:
            return self._run(experiment_name=experiment_name, working_dir=working_dir, mode=mode,
                             track_run_history=track_run_history, show_output=show_output,
                             skip_validation=skip_validation, raise_on_error=raise_on_error)

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name='Component_run')
    def _run(self, experiment_name=None, working_dir=None, mode=RunMode.Docker.value,
             track_run_history=True, show_output=True, skip_validation=False, raise_on_error=True):
        """
        Run component in local environment.

        :param experiment_name: The experiment_name will show in portal. If not set, will use component name.
        :type experiment_name: str
        :param working_dir: The output path for component output info
        :type working_dir: str
        :param mode: Three modes are supported to run component.
                     docker: Start a container with the component's image and run component in it.
                     conda: Build a conda environment in the host with the component's conda definition and
                            run component in it.
                     host: Directly run component in host environment.
        :type mode: str
        :param track_run_history: If track_run_history=True, will create azureml.Run and upload component output
                                  and log file to portal.
                                  If track_run_history=False, will not create azureml.Run to upload outputs
                                  and log file.
        :type track_run_history: bool
        :param show_output: Indicates whether to show the component run status on sys.stdout.
        :type show_output: bool
        :param skip_validation: Indicates whether to skip the validation of the component.
        :type skip_validation: bool
        :param raise_on_error: Indicates whether to raise an error when the Run is in a failed state
        :type raise_on_error: bool

        :return: The run status, such as, Completed and Failed.
        :rtype: RunStatus
        """
        if not skip_validation:
            self._validate(raise_error=True, is_local=True)
        if not self.type or self.type not in {
            ComponentType.CommandComponent.value, ComponentType.DistributedComponent.value,
            ComponentType.ParallelComponent.value,
        }:
            raise UserErrorException(
                'Unsupported component type {}, " \
                "only Command/MPI/Parallel Component is supported now.'.format(self.type))
        if not working_dir:
            working_dir = os.path.join(tempfile.gettempdir(), trans_to_valid_file_name(self.name))
        short_working_dir = _get_short_path_name(working_dir, is_dir=True, create_dir=True)
        print('working dir is {}'.format(working_dir))

        # prepare input dataset
        ComponentRunHelper.download_datasets(
            [dataset._dset for dataset in self._input_ports.values()], self.workspace, short_working_dir)
        # prepare component image
        run_mode = RunMode.get_run_mode_by_str(mode)
        if run_mode.is_build_env_mode():
            ComponentRunHelper.prepare_component_env(self, short_working_dir, run_mode == RunMode.Docker)

        experiment_name = experiment_name if experiment_name else _sanitize_python_variable_name(self.display_name)
        tracker = RunHistoryTracker.with_definition(
            experiment_name=experiment_name.replace(' ', '_'),
            track_run_history=track_run_history,
            component=self,
            working_dir=None,
            path=EXECUTION_LOGFILE)
        component_run_helper = ComponentRunHelper(
            self, short_working_dir, mode=run_mode, tracker=tracker, show_output=show_output)
        return component_run_helper.component_run(raise_on_error)

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_submit")
    def _submit(self, experiment_name=None, source_dir=None, tags=None, skip_validation=False) -> Run:
        """Submit component to remote compute target.

        .. remarks::

            Submit is an asynchronous call to the Azure Machine Learning platform to execute a trial on
            remote hardware.  Depending on the configuration, submit will automatically prepare
            your execution environments, execute your code, and capture your source code and results
            into the experiment's run history.
            An example of how to submit an experiment from your local machine is as follows:

            .. code-block:: python

                # Suppose we have a workspace as 'ws'
                # First, load a component, and set parameters of component
                train_component_func = Component.load(ws, name='microsoft.com/aml/samples://Train')
                train_data = Dataset.get_by_name(ws, 'training_data')
                train = train_component_func(training_data=train_data, max_epochs=5, learning_rate=0.01)
                # Second, set compute target for component then add compute running settings.
                # After running finish, the output data will be in outputs/$output_file
                train.runsettings.configure(target="k80-16-c")
                train.runsettings.resource_configuration.configure(gpu_count=1, is_preemptible=True)
                run = train.submit(experiment_name="component-submit-test")
                print(run.get_portal_url())
                run.wait_for_completion()

        :param experiment_name: The experiment name
        :type experiment_name: str
        :param source_dir: The source dir is where the machine learning scripts locate
        :type source_dir: str
        :param tags: Tags to be added to the submitted run, e.g., {"tag": "value"}
        :type tags: dict
        :param skip_validation: Indicates whether to skip the validation of the component.
        :type skip_validation: bool

        :return: The submitted run.
        :rtype: azureml.core.Run
        """
        if not skip_validation:
            self._validate(raise_error=True)

        if self._definition.type != CommandComponentDefinition.TYPE:
            raise NotImplementedError(
                "Currently only CommandComponent support Submit, got %r." % self._definition.type.value
            )
        # TODO: Support any command component submit.
        if self._definition.is_command:
            raise NotImplementedError(
                "Currently only python CommandComponent support Submit, got %r." % self._definition.command
            )

        if self._runsettings.target is None:
            raise UserErrorException("Submit require a remote compute configured.")
        if experiment_name is None:
            experiment_name = _sanitize_python_variable_name(self.display_name)
        if source_dir is None:
            source_dir = os.path.join(tempfile.gettempdir(), self._identifier)
            print("[Warning] script_dir is None, create tempdir: {}".format(source_dir))
        experiment = Experiment(self._workspace, experiment_name)
        run_id = experiment_name + "_" + \
            str(int(time.time())) + "_" + str(uuid.uuid4())[:8]
        run_config = self._populate_runconfig(run_id)

        script = run_config.script
        if not os.path.isfile("{}/{}".format(source_dir, script)):
            print("[Warning] Can't find {} from {}, will download from remote".format(script, source_dir))
            _prepare_component_snapshot(self, source_dir)

        src = ScriptRunConfig(
            source_directory=source_dir, script=script,
            run_config=run_config,
        )
        run = experiment.submit(config=src, tags=tags, run_id=run_id)
        print('Link to Azure Machine Learning Portal:', run.get_portal_url())
        return run

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def batch_load(workspace: Workspace, selectors: List[str] = None, ids: List[str] = None) -> \
            List[Callable[..., 'Component']]:
        """
        Batch load components by identifier list.

        If there is an exception with any component, the batch load will fail. Partial success is not allowed.

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param selectors: A list of str formatted as name:version or name@label
        :type selectors: builtin.list[str]
        :param ids: The component version ids
        :type ids: builtin.list[str]

        :return: A tuple of component functions
        :rtype: tuple(function)
        """
        definitions = CommandComponentDefinition.batch_get(workspace, ids, selectors)
        telemetry_values = WorkspaceTelemetryMixin._get_telemetry_value_from_workspace(workspace)
        telemetry_values.update({
            'count': len(definitions),
        })
        _LoggerFactory.add_track_dimensions(_get_logger(), telemetry_values)
        for definition in definitions:
            definition._load_source = _ComponentLoadSource.REGISTERED

        component_funcs = [Component._component_func_from_definition(definition)
                           for definition in definitions]
        if len(definitions) == 1:
            component_funcs = component_funcs[0]
        return component_funcs

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def load(workspace: Workspace, name: str = None,
             version: str = None, selector: str = None, id: str = None) -> Callable[..., 'Component']:
        """
        Get component function from workspace.

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param name: The name of component
        :type name: str
        :param version: The version
        :type version: str
        :param selector: A string formatted as name:version or name@label, when loading component,
            you can choose one between selector and name, version.
        :type selector: str
        :param id: The component version id of an existing component
        :type id: str

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        if id is not None:
            definition = CommandComponentDefinition.get_by_id(workspace, id)
        elif name is not None or selector is not None:
            if selector is not None:
                from ._restclients.service_caller import _resolve_parameter_from_selector
                name, version = _resolve_parameter_from_selector(selector)
            definition = CommandComponentDefinition.get(workspace, name, version)
        else:
            raise UserErrorException('Load component failed: One of the name/id/selector must not be empty.')

        definition._load_source = _ComponentLoadSource.REGISTERED

        return Component._component_func_from_definition(definition)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_from_notebook")
    def _from_notebook(workspace: Workspace, notebook_file: str, source_dir=None) -> Callable[..., 'Component']:
        """Register an anonymous component from a jupyter notebook file and return the registered component func.

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param notebook_file: The jupyter notebook file run in component.
        :type notebook_file: str
        :param source_dir: The source directory of the component.
        :type source_dir: str

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        from azure.ml.component.dsl._component_from_notebook import gen_component_by_notebook
        if source_dir is None:
            source_dir = Path(notebook_file).parent
            notebook_file = Path(notebook_file).name
        if not notebook_file.endswith('.ipynb'):
            raise UserErrorException("'%s' is not a jupyter notebook file" % notebook_file)
        temp_target_file = '_' + Path(notebook_file).with_suffix('.py').name
        temp_target_path = Path(source_dir) / Path(temp_target_file)
        conda_file = temp_target_path.parent / 'conda.yaml'

        from azure.ml.component.dsl._utils import _temporarily_remove_file, _change_working_dir
        with _temporarily_remove_file(temp_target_path), _temporarily_remove_file(conda_file):
            generator = gen_component_by_notebook(
                notebook_file,
                working_dir=source_dir,
                target_file=temp_target_file,
                force=True)

            with _change_working_dir(source_dir):
                from runpy import run_path
                notebook_component = run_path(temp_target_file)
                notebook_func = notebook_component[generator.func_name]
                return Component._from_func_imp(workspace=workspace, func=notebook_func,
                                                force_reload=False, load_source=_ComponentLoadSource.FROM_NOTEBOOK)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_from_func")
    def _from_func(workspace: Workspace, func: types.FunctionType, force_reload=True) -> Callable[..., 'Component']:
        """Register an anonymous component from a wrapped python function and return the registered component func.

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param func: A wrapped function to be loaded or a ComponentExecutor instance.
        :type func: types.FunctionType
        :param force_reload: Whether reload the function to make sure the code is the latest.
        :type force_reload: bool

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        return Component._from_func_imp(workspace=workspace, func=func,
                                        force_reload=force_reload, load_source=_ComponentLoadSource.FROM_FUNC)

    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_export_yaml")
    def _export_yaml(self, directory=None):
        """
        Export component to yaml files.

        This is an experimental function, will be changed anytime.

        :param directory: The target directory path. Default current working directory
            path will be used if not provided.
        :type directory: str
        :return: The directory path
        :rtype: str
        """
        pass

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API)
    def from_yaml(workspace: Workspace, yaml_file: str) -> Callable[..., 'Component']:
        """
        Register an anonymous component from yaml file to workspace and return the registered component func.

        Assumes source code is in the same directory with yaml file. Then return the registered component func.

        For example:

        .. code-block:: python

            # Suppose we have a workspace as 'ws'
            # Register and get an anonymous component from yaml file
            component = from_yaml(workspace, "custom_component/component_spec.yaml")
            # Register and get an anonymous component from Github url
            component = from_yaml(
                workspace,
                https://github.com/wangchao1230/hello-aml-modules/blob/wanhan/add_component_sample/sample_components_do_not_delete/build_artifact_demo_0.0.1/component_spec.yaml")

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param yaml_file: The component spec file. The spec file could be located in local or Github.
        :type yaml_file: str

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        return Component._from_module_spec(workspace=workspace, yaml_file=yaml_file,
                                           load_source=_ComponentLoadSource.FROM_YAML)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_register")
    def _register(workspace: Workspace, yaml_file: str, amlignore_file: str = None,
                  set_as_default: bool = False, version: str = None) -> \
            Callable[..., 'Component']:
        """
        Register an component from yaml file to workspace.

        Assumes source code is in the same directory with yaml file. Then return the registered component func.

        For example:

        .. code-block:: python

            # Suppose we have a workspace as 'ws'
            # Register and get an anonymous component from yaml file
            component = from_yaml(workspace, "custom_component/component_spec.yaml")
            # Register and get an anonymous component from Github url
            component = from_yaml(
                workspace,
                https://github.com/wangchao1230/hello-aml-modules/blob/wanhan/add_component_sample/sample_components_do_not_delete/build_artifact_demo_0.0.1/component_spec.yaml")

        :param workspace: The workspace object this component will belong to.
        :type workspace: azureml.core.Workspace
        :param yaml_file: The component spec file. The spec file could be located in local or Github.
        :type yaml_file: str
        :param amlignore_file: The .amlignore or .gitignore file path used to exclude files/directories in the snapshot
        :type amlignore_file: str
        :param set_as_default: By default false, default version of the component will not be updated
            when registering a new version of component. Specify this flag to set the new version as the component's
            default version.
        :type set_as_default: bool
        :param version: If specified, registered component will use specified value as version
            instead of the version in the yaml.
        :type version: str

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        if version is not None:
            if not isinstance(version, str):
                raise UserErrorException('Only string type of supported for param version.')
            elif version == "":
                # Hint user when accidentally set empty string to set_version
                raise UserErrorException('Param version does not allow empty value.')
        definition = CommandComponentDefinition.register(
            workspace, spec_file=yaml_file,
            package_zip=None,
            anonymous_registration=False,
            set_as_default=set_as_default,
            amlignore_file=amlignore_file,
            version=version
        )
        definition._load_source = _ComponentLoadSource.FROM_YAML

        return Component._component_func_from_definition(definition)

    @staticmethod
    @track(_get_logger, activity_type=_PUBLIC_API, activity_name="Component_create")
    def create(function: Callable, version: str = None, set_as_default: bool = False):
        """
        Create a dsl.pipeline decorated function into workspace as a PipelineComponent.

        Then return the created component func.

        For example:

        .. code-block:: python

            from azure.ml.component import dsl, Component

            @dsl.pipeline(version='0.0.1')
            def sample_pipeline():
                pass

            # workspace parameter can be omitted as can be inferred from components contained in pipeline
            named_component_func = Component.create(sample_pipeline)

        .. note::

            The name of dsl pipeline here must be between 1 to 255 characters, start with letters or numbers.
            Valid characters are letters, numbers, ".", "-" and "_".

        :param function: dsl decorated function.
        :type function: function
        :param version: If specified version, will override the version specified in dsl.pipeline function.
        Version must be specified by user here or in dsl.pipeline.
        :type version: str
        :param set_as_default: By default false, default version of the component will not be updated
        when registering a new version of component. Specify this flag to set the new version as the
        component's default version.
        :type set_as_default: bool

        :return: A function that can be called with parameters to get a :class:`azure.ml.component.Component`
        :rtype: function
        """
        # Check function
        from . import dsl
        if not dsl._utils.is_dsl_func(function):
            raise UserErrorException("The value of parameter 'function' is not a dsl decorated function.")
        # Process parameters
        parameters = dsl.types._get_param_with_standard_annotation(function, is_func=True)
        default_args = {k: v._default for k, v in parameters.items()}
        pipeline = function(**default_args)
        version = version if version is not None else pipeline.version
        # Check 'version'
        if version is None:
            raise UserErrorException(
                "'version' is required, please specify 'version' by Component.create(version='your_version')"
                " or dsl.pipeline(version='your_version').")
        elif not isinstance(version, str):
            raise UserErrorException("'version' must be a string value.")
        # Check 'name'
        if not is_valid_component_name(pipeline._definition.name):
            raise UserErrorException(
                f"Component name {pipeline._definition.name!r} is invalid. "
                "Name must be between 1 to 255 characters, "
                "start with letters or numbers. Valid characters are letters, numbers, '.', '-' and '_'.")
        component_dto = pipeline._create(version=version, set_as_default_version=set_as_default)
        repr_dict = _get_repr_dict_of_component_dto(component_dto)
        repr_dict.update({
            "workspace": pipeline.workspace.name,
            "subscriptionId": pipeline.workspace.subscription_id,
            "resourceGroup": pipeline.workspace.resource_group,
        })
        print("Created Component:", repr_dict)
        return Component._component_func(pipeline.workspace, component_dto, _ComponentLoadSource.REGISTERED)
    # endregion


def _get_repr_dict_of_component_dto(component_dto):
    return {
        "name": component_dto.module_name,
        "version": component_dto.module_version,
        "defaultVersion": component_dto.default_version,
        "type": component_dto.job_type,
    }


def _get_workspace_default_datastore(workspace):
    """
    Get the default datastore in the workspace.

    :return: the default datastore.
    :rtype: azureml.core.Datastore
    """
    if workspace is None:
        return None
    from ._restclients.service_caller_factory import _DesignerServiceCallerFactory
    service_caller = _DesignerServiceCallerFactory.get_instance(workspace)
    return service_caller.get_default_datastore()
