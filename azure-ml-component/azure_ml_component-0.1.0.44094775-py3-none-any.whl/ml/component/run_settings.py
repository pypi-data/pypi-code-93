# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines classes for run settings."""

import os
import copy
import logging
from inspect import Parameter
from typing import List, Sequence

from azureml._base_sdk_common.field_info import _FieldInfo
from azureml.core.runconfig import RunConfiguration
from azureml.exceptions._azureml_exception import UserErrorException
from ._core._component_definition import ComponentType
from ._core._run_settings_definition import RunSettingsDefinition, RunSettingParam, ParamStatus
from ._dynamic import KwParameter, create_kw_method_from_parameters
from ._pipeline_parameters import PipelineParameter
from ._restclients.service_caller_factory import _DesignerServiceCallerFactory
from ._run_settings_contracts import try_convert_obj_to_dict, try_convert_obj_to_value
from ._util._utils import _get_param_in_group_from_pipeline_parameters, _get_parameter_static_value
from ._util._exceptions import InvalidTargetSpecifiedError, ComponentValidationError, UnexpectedAttributeError
from ._util._loggerfactory import _LoggerFactory, _PUBLIC_API, track
from ._util._telemetry import WorkspaceTelemetryMixin

_logger = None
_deprecated_params_for_parallel_component = {
    'node_count', 'process_count_per_node', 'error_threshold', 'mini_batch_size', 'logging_level',
    'run_invocation_timeout', 'version', 'run_max_try', 'partition_keys'
}
_deprecated_params_for_distributed_component = {'node_count', 'process_count_per_node'}
_deprecated_params_for_hdinsight_component = {
    'queue', 'driver_memory', 'driver_cores', 'executor_memory', 'executor_cores', 'number_executors',
    'conf', 'name',
}
AZUREML_COMPONENT_POPULATE_DEFAULT_RUNSETTINGS = \
    os.environ.get('AZUREML_COMPONENT_POPULATE_DEFAULT_RUNSETTINGS', False)


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class _RunSettingsStore:
    """Dict store used by RunSettings."""

    def __init__(self):
        """Initialize store with an empty dictionary."""
        self._user_provided_values = {}

    def set_value(self, param_id, value):
        """Set parameter value by parameter id."""
        self._user_provided_values[param_id] = value

    def delete_value(self, param_id):
        """Delete the value by parameter id."""
        if param_id in self._user_provided_values:
            self._user_provided_values.pop(param_id)

    def get_value(self, param_id):
        """Get parameter value by parameter id."""
        return self._user_provided_values.get(param_id, None)

    @property
    def values(self):
        """Return the copy of parameter values dict."""
        return copy.copy(self._user_provided_values)

    @property
    def _is_specified(self):
        return len(self._user_provided_values) > 0


class _RunSettingsInterfaceParam:
    """Display wrapper for RunSettingParam."""

    def __init__(self, definition: RunSettingParam, interface, deprecated_hint=None, is_compute_param=False):
        """Initialize from RunSettingParam.

        :param definition: The definition of this parameter.
        :type definition: RunSettingParam
        :param interface: The interface path of this parameter. For example, interface of
        'target' is 'runsettings.target', interface of 'node_count' is 'runsettings.resource_layout.node_count'.
        This is for generating the hint message to customer.
        :type interface: str
        :param deprecated_hint: Hint message for deprecated parameter.
        :type deprecated_hint: str
        :param is_compute_param: Indicate this parameter is compute target parameter or not.
        :type is_compute_param: bool
        """
        self.definition = definition
        self.deprecated_hint = deprecated_hint
        if self.definition.is_compute_target:
            # Here we use a common name for compute target param
            # In backend contract, HDI uses 'compute_name', others use 'target'
            self.display_name = 'Target'
            self.display_argument_name = 'target'
        else:
            self.display_name = self.definition.name
            self.display_argument_name = self.definition.argument_name
        self.is_compute_param = is_compute_param
        self.interface = interface

    def __getattr__(self, name):
        """For properties not defined in this class, retrieve from RunSettingParam."""
        return getattr(self.definition, name)

    def _switch_definition_by_current_settings(self, settings: dict):
        """
        Switch to the right definition according to current settings for multi-definition parameter.

        :param settings: current runsettings in format of dict.
        :type settings: dict
        :return: parameter status in current settings.
        :rtype: ParamStatus
        """
        return self.definition._switch_definition_by_current_settings(settings)

    def __repr__(self):
        """Return str(self)."""
        return self.__str__()

    def __str__(self):
        """Return the description of a Output object."""
        return "{}".format(self.interface)


class _RunSettingsParamSection:
    """A section of parameters which will dynamically generate a configure function in runtime."""

    def __init__(self, display_name: str, description: str, sub_sections=[],
                 parameters: List[_RunSettingsInterfaceParam]=[]):
        """Initialize from a list of _RunSettingsInterfaceParam, display name and description.

        :param display_name: The argument name of this section.
        :type display_name: str
        :param description: The description of this section.
        :type description: str
        :param sub_sections: The sub sections of this section.
        :type sub_sections: List[_RunSettingsParamSection]
        :param parameters: The parameters of this section.
        :type parameters: List[_RunSettingsInterfaceParam]
        """
        self.display_name = display_name
        self.description = description
        self.sub_sections = sub_sections
        self.parameters = parameters


class _RunSettingsInterfaceGenerator:
    """Generator for RunSettings interfaces."""

    @classmethod
    def _get_runsettings_display_section_list(cls, component_type, definition: RunSettingsDefinition,
                                              component_name='component') -> List[_RunSettingsParamSection]:
        # runsettings
        _runsettings = _RunSettingsParamSection(
            display_name='_runsettings',
            description='Run setting configuration for component [{}]'.format(component_name),
            sub_sections=[],  # Fill later
            parameters=[],  # Fill later
        )
        params = definition.params.values()
        # For command, parallel, distributed, hdi components, generate deprecated params for keeping old interfaces
        # We use hard-code here, because new parameters are adding to these components, no need deprecate these,
        # like instance_type, instance_count
        deprecated_params = set()
        if component_type == ComponentType.DistributedComponent:
            deprecated_params = set(_deprecated_params_for_distributed_component)
        elif component_type == ComponentType.ParallelComponent:
            deprecated_params = set(_deprecated_params_for_parallel_component)
        elif component_type == ComponentType.HDInsightComponent:
            deprecated_params = set(_deprecated_params_for_hdinsight_component)

        runsettings_params = []
        # RunSettings sections {section name: section param list}
        runsettings_section_params = {}
        # Section names
        runsettings_sections = {}
        for p in params:
            if p.section_argument_name is None:
                # Parameters for component.runsettings.configure
                runsettings_params.append(_RunSettingsInterfaceParam(
                    p, interface='runsettings.{}'.format(p.argument_name)))
                continue
            # Section params
            section_name = p.section_argument_name
            if section_name not in runsettings_sections:
                runsettings_sections[section_name] = p.section_description
                runsettings_section_params[section_name] = []
            # Append to section params
            interface = 'runsettings.{}.{}'.format(section_name, p.argument_name)
            runsettings_section_params[section_name].append(_RunSettingsInterfaceParam(
                p, interface=interface))
            # Append to params if is deprecated param
            if p.argument_name in deprecated_params:
                old_param = _RunSettingsInterfaceParam(
                    p, interface='runsettings.{}'.format(p.argument_name),
                    deprecated_hint='deprecated, please use {}'.format(interface))
                runsettings_params.append(old_param)
        # Generate section and sub section display objects
        for section_name, section_description in sorted(runsettings_sections.items()):
            sub_section_names = section_name.split('.')
            parent = _runsettings
            for name in sub_section_names:
                section = next((s for s in parent.sub_sections if s.display_name == name), None)
                if section is None:
                    section = _RunSettingsParamSection(display_name=name, description=None, sub_sections=[])
                    parent.sub_sections.append(section)
                parent = section
            parent.description = section_description
            parent.parameters = runsettings_section_params.get(section_name, [])

        _runsettings.parameters = runsettings_params

        # Compute settings
        _compute_runsettings = None
        compute_params = [
            _RunSettingsInterfaceParam(
                p,
                interface='k8srunsettings.{}.{}'.format(p.section_argument_name, p.argument_name),
                is_compute_param=True) for p in definition.compute_params.values()]
        if len(compute_params) > 0:
            compute_settings_sections = {
                p.section_argument_name: p.section_description for p in compute_params}
            compute_settings_sub_sections = [
                _RunSettingsParamSection(
                    display_name=section_name,
                    description=section_description,
                    parameters=[p for p in compute_params if p.section_argument_name == section_name],
                ) for section_name, section_description in compute_settings_sections.items()
            ]
            _compute_runsettings = _RunSettingsParamSection(
                display_name='_k8srunsettings',
                description='The compute run settings for Component, only take effect when compute type is in {}.\n'
                            'Configuration sections: {}.'.format(definition.compute_types_with_settings,
                                                                 str([s for s in compute_settings_sections])),
                sub_sections=compute_settings_sub_sections,
            )

        return _runsettings, _compute_runsettings

    @classmethod
    def build(cls, component, workspace):
        """Return the runsettings interface for component in format of (runsettings, compute_runsettings)."""
        _runsettings, _compute_runsettings = None, None
        definition = component._definition
        if definition.runsettings is None:
            # For local-run components, no runsettings definition here
            return _runsettings, _compute_runsettings
        _runsettings_display, _compute_runsettings_display = cls._get_runsettings_display_section_list(
            definition.type,
            definition.runsettings, component_name=component.display_name)
        _runsettings_store = _RunSettingsStore()
        _compute_runsettings_store = _RunSettingsStore()
        _runsettings = RunSettings(_runsettings_display, _runsettings_store, workspace)
        if _compute_runsettings_display is not None:
            _compute_runsettings = RunSettings(_compute_runsettings_display, _compute_runsettings_store, workspace)
        return _runsettings, _compute_runsettings


class RunSettings(WorkspaceTelemetryMixin):
    """A RunSettings aggregates the run settings of a component."""

    # Set a flag here, so we could use it in __setattr__ to init private attrs in naive way.
    _initialized = False

    def __init__(self, display_section: _RunSettingsParamSection, store: _RunSettingsStore, workspace):
        """
        Initialize RunSettings.

        :param display_section: The display section.
        :type display_section: _RunSettingsParamSection
        :param store: The store which is used to hold the param values of RunSettings.
        :type store: _RunSettingsStore
        :param workspace: Current workspace.
        :type workspace: Workspace
        """
        self._store = store
        self._workspace = workspace
        self._params_mapping = {p.display_argument_name: p for p in display_section.parameters}
        self._sections_mapping = {}
        self._name = display_section.display_name
        self._generate_configure_func_and_properties(display_section)
        WorkspaceTelemetryMixin.__init__(self, workspace=workspace)
        self._initialized = True

    def _generate_configure_func_and_properties(self, display_section: _RunSettingsParamSection):
        # Generate configure function
        func_docstring_lines = []
        if display_section.description is not None:
            func_docstring_lines.append(display_section.description)
        if len(display_section.parameters) > 0:
            func_docstring_lines.append("\n")
        params, _doc_string = _format_params(display_section.parameters, display_section.sub_sections)
        func_docstring_lines.extend(_doc_string)
        func_docstring = '\n'.join(func_docstring_lines)
        self.configure = create_kw_method_from_parameters(
            self.configure,
            parameters=params,
            documentation=func_docstring,
        )
        # Generate parameter properties
        for param in display_section.parameters:
            setattr(self, param.display_argument_name, None)
        # Generate sub sections
        for sub_display_section in display_section.sub_sections:
            sub_section = RunSettings(sub_display_section, self._store, self._workspace)
            setattr(self, sub_display_section.display_name, sub_section)
            self._sections_mapping[sub_display_section.display_name] = sub_section
        self.__doc__ = func_docstring

    @track(_get_logger, activity_type=_PUBLIC_API)
    def configure(self, *args, **kwargs):
        """
        Configure the runsettings.

        Note that this method will be replaced by a dynamic generated one at runtime with parameters
        that corresponds to the runsettings of the component.
        """
        # Note that the argument list must be "*args, **kwargs" to make sure
        # vscode intelligence works when the signature is updated.
        # https://github.com/microsoft/vscode-python/blob/master/src/client/datascience/interactive-common/intellisense/intellisenseProvider.ts#L79
        # Filter None values since it's the default value
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        for k, v in kwargs.items():
            self._set_param_or_section(k, v)

    def validate(
            self, raise_error=False, process_error=None, for_definition_validate=False, definition_validator=None):
        """
        Validate RunSettings parameter values for current component.

        :param raise_error: Whether to raise exceptions on error.
        :type raise_error: bool
        :param process_error: The error process function to be used.
        :type process_error: function
        :param for_definition_validate: If the validate is for pipeline definition validate.
        :type for_definition_validate: bool
        :param definition_validator: definition validator
        :type definition_validator: azure.ml.component._component_validator.DefinitionValidator

        :return: The errors found during validation.
        :rtype: builtin.list
        """
        all_settings = self._get_flat_values()
        return self._validate(all_settings, raise_error, process_error, for_definition_validate, definition_validator)

    def _validate(
            self,
            all_settings,
            raise_error=False,
            process_error=None,
            for_definition_validate=False,
            definition_validator=None
    ):
        errors = []

        from ._component_validator import ComponentValidator, Diagnostic

        def process_runsetting_error(e: Exception, error_type, variable_name, variable_type):
            ve = ComponentValidationError(str(e), e, error_type)
            if raise_error:
                raise ve
            else:
                errors.append(Diagnostic.create_diagnostic(ve.message, ve.error_type, variable_name, variable_type))

        if process_error is None:
            process_error = process_runsetting_error
        # Validate top-level parameters
        for spec in self._params_mapping.values():
            ComponentValidator.validate_runsetting_parameter(
                all_settings, spec, process_error, for_definition_validate, definition_validator)
        # Validate sections
        for section in self._sections_mapping.values():
            section._validate(all_settings, raise_error, process_error, for_definition_validate, definition_validator)
        return errors

    def __setattr__(self, key, value):
        """Override base function to set parameter values to store, and do validation before set."""
        if not self._initialized or key == '_store':
            # bypass setattr in __init__ and in copy runsettings (_store)
            super().__setattr__(key, value)
        else:
            self._set_param_or_section(key, value)

    def _set_param_or_section(self, key, value):
        if key in self._params_mapping.keys():
            self._set_parameter(key, value)
        elif key in self._sections_mapping.keys():
            section = self._sections_mapping[key]
            section._set_section(value)
        else:
            all_available_keys = sorted(
                set(self._params_mapping.keys()).union(set(self._sections_mapping.keys())))
            raise UserErrorException(
                "'{}' is not an expected key, all available keys are: {}.".format(key, all_available_keys))

    def _set_parameter(self, key, value):
        spec = self._params_mapping[key]
        if spec.deprecated_hint is not None:
            logging.warning('{} is {}'.format(spec.interface, spec.deprecated_hint))
        value = try_convert_obj_to_value(spec.id, value, spec.parameter_type_in_py)
        # We use a store here, which is a component-level instance.
        # This is for support old interfaces and new interfaces work together.
        self._store.set_value(self._params_mapping[key].id, value)

    def __getattribute__(self, key):
        """Override base function to get parameter values from store."""
        if not key.startswith('_') and key in self._params_mapping:
            # For top-level parameters, we get the value from store.
            return self._store.get_value(self._params_mapping[key].id)
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            all_available_keys = sorted(
                set(self._params_mapping.keys()).union(set(self._sections_mapping.keys())))
            raise UnexpectedAttributeError(
                "'{}' is not an expected key, all available keys are: {}.".format(key, all_available_keys))

    def __repr__(self):
        """Customize for string representation."""
        return repr(self._get_values())

    def _get_values(self, ignore_none=False):
        # Here we skip deprecated parameters, generate the values with new interfaces.
        json_dict = {k: getattr(self, k) for k, v in self._params_mapping.items() if v.deprecated_hint is None}
        if ignore_none:
            json_dict = {k: v for k, v in json_dict.items() if v is not None}
        for section_name, section in self._sections_mapping.items():
            section_dict = section._get_values(ignore_none=ignore_none)
            if len(section_dict) > 0:
                json_dict[section_name] = section_dict
        return json_dict

    def _get_user_assigned_flat_values(self):
        return self._store.values

    def _get_flat_values(self):
        user_provided_values = self._get_user_assigned_flat_values()
        default_values = self._populate_default_values(user_provided_values)
        if AZUREML_COMPONENT_POPULATE_DEFAULT_RUNSETTINGS:
            return {**user_provided_values, **default_values}
        else:
            return user_provided_values

    def _copy_and_update(self, source_setting, pipeline_parameters):
        """
        Copy and update settings from source_setting to self with pipeline parameters.

        :param source_setting:
        :type source_setting: RunSettings
        :param pipeline_parameters: pipeline parameters
        :type pipeline_parameters: dict
        """
        def _update_pipeline_parameters_runsetting(obj):
            """Replace PipelineParameter in runsettings with parameter from input."""
            if pipeline_parameters is None:
                return obj
            from azure.ml.component.component import Input
            if isinstance(obj, PipelineParameter) or isinstance(obj, Input):
                obj = _get_param_in_group_from_pipeline_parameters(
                    obj.name, pipeline_parameters, obj._groups if isinstance(obj, PipelineParameter) else None)
                if obj is Parameter.empty:
                    raise Exception(f'Runsetting {param_id!r} not found in pipeline parameters!')
            elif isinstance(obj, dict):
                obj = {k: _update_pipeline_parameters_runsetting(v) for k, v in obj.items()}
            elif type(obj) in [list, tuple]:
                obj = type(obj)([_update_pipeline_parameters_runsetting(i) for i in obj])
            return obj

        if source_setting is None:
            return
        for param_id, param_value in source_setting._store._user_provided_values.items():
            self._store.set_value(param_id, _update_pipeline_parameters_runsetting(param_value))

    _TARGET_SELECTOR_NAME = 'target_selector'
    _TARGET_NAME = 'target'

    def _get_target(self):
        """
        Get the compute target of component.

        Return `target_selector` in format of ('target_selector', compute_type) if specified, otherwise
        return `target`.
        """
        # Check target_selector
        if hasattr(self, self._TARGET_SELECTOR_NAME):
            compute_type = _get_parameter_static_value(self.target_selector.compute_type)
            if compute_type is not None:
                return (self._TARGET_SELECTOR_NAME, compute_type)
        # Return target
        if not hasattr(self, self._TARGET_NAME):
            return None
        return _get_parameter_static_value(self.target)

    def _populate_default_values(self, user_provided_values, default_values=None):
        if default_values is None:
            default_values = {}
        # Get default values for parameters without enabled_by, disabled_by, and no user-provided values
        default_values.update({p.id: p.default_value for p in self._params_mapping.values()
                               if p.enabled_by is None and p.disabled_by is None and
                               p.id not in user_provided_values})
        for spec in self._params_mapping.values():
            param_id = spec.id
            if spec.deprecated_hint is not None or \
                    param_id in user_provided_values or param_id in default_values:
                # By pass deprecated, user-assigned and processed parameters
                continue

            # Use `user_provided_values` + `default_values` to calculate the status of parameter
            status = spec._switch_definition_by_current_settings({**user_provided_values, **default_values})
            # Only when status is active, and user-provided value is none
            if status == ParamStatus.Active:
                default_values[param_id] = spec.default_value

        # Iteratly populate sub sections
        for section in self._sections_mapping.values():
            section._populate_default_values(user_provided_values, default_values)
        return default_values

    def _clear_section_values(self):
        for v in self._params_mapping.values():
            self._store.delete_value(v.id)

    def _set_section_by_dict(self, obj):
        self._clear_section_values()
        for k, v in obj.items():
            self._set_param_or_section(k, v)

    def _set_section(self, obj):
        # Convert object to dict first, then set section by dict
        obj_dict = try_convert_obj_to_dict(self._name, obj)
        if obj_dict:
            self._set_section_by_dict(obj_dict)
        else:
            raise UserErrorException(
                "'{}' is an unsupported type for runsetting '{}'.".format(type(obj).__name__, self._name))


def _get_compute_type(ws, compute_name):
    if compute_name is None:
        return None
    service_caller = _DesignerServiceCallerFactory.get_instance(ws)
    compute = service_caller.get_compute_by_name(compute_name)
    if compute is None:
        raise InvalidTargetSpecifiedError(message="Cannot find compute '{}' in workspace.".format(compute_name))
    return compute.compute_type


def _has_specified_runsettings(runsettings: RunSettings) -> bool:
    return runsettings is not None and runsettings._store._is_specified


def _format_params(source_params: Sequence[_RunSettingsInterfaceParam],
                   section_params: Sequence[_RunSettingsParamSection]):
    target_params = []
    func_docstring_lines = []
    for param in source_params:
        # For the compute run settings,
        # the default value in spec is not match the value in description,
        # so we remove "default value" part in doc string for this case.
        param_line = ":param {}: {}".format(param.display_argument_name, param.description)
        if param.is_optional:
            param_line = "{} (optional{})".format(
                param_line, '' if param.is_compute_param else ', default value is {}'.format(param.default_value))
        if param.deprecated_hint is not None:
            param_line = "{} ({})".format(param_line, param.deprecated_hint)
        func_docstring_lines.append(param_line)

        func_docstring_lines.append(":type {}: {}".format(param.display_argument_name, param.parameter_type))
        target_params.append(KwParameter(
            param.display_argument_name,
            annotation=param.description,
            # Here we set all default values as None to avoid overwriting the values by default values.
            default=None,
            _type=param.parameter_type))
    for section in section_params:
        target_params.append(KwParameter(
            section.display_name,
            annotation=section.description,
            # Here we set all default values as None to avoid overwriting the values by default values.
            default=None,
            _type='object'))
    return target_params, func_docstring_lines


def _update_run_config(component, run_config: RunConfiguration, compute_type='Cmk8s'):
    """Use the settings in k8srunsettings to update RunConfiguration class."""
    if component._definition.runsettings is None:
        # For local-run components, no runsettings definition here
        return
    compute_params_spec = component._definition.runsettings.compute_params
    if compute_params_spec is None:
        return
    compute_field_map = {'Cmk8s': 'cmk8scompute', 'CmAks': 'cmakscompute'}
    if compute_type in compute_field_map:
        field_name = compute_field_map[compute_type]
        aks_config = {'configuration': dict()}
        k8srunsettings = component._k8srunsettings._get_flat_values()
        for param_id, param in compute_params_spec.items():
            value = k8srunsettings.get(param_id)
            if value is not None:
                aks_config['configuration'][param.argument_name] = value
        run_config._initialized = False
        setattr(run_config, field_name, aks_config)
        run_config._initialized = True
        RunConfiguration._field_to_info_dict[field_name] = _FieldInfo(dict,
                                                                      "{} specific details.".format(field_name))
        run_config.history.output_collection = True
