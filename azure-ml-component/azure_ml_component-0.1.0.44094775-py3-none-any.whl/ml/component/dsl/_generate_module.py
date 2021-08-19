# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from fnmatch import fnmatch

from azure.ml.component._api._api import ComponentAPI
from azure.ml.component._util._loggerfactory import _LoggerFactory, _PUBLIC_API, track

from azureml.core import Workspace
from azureml.exceptions import UserErrorException

from ._component_generator import ModuleFileGenerator
from ._utils import _import_component_with_working_dir, _sanitize_python_variable_name


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


@track(_get_logger, activity_type=_PUBLIC_API, activity_name="dsl_generate_module")
def _generate_module(components, module_name, force_regenerate=False):
    """For a set of components, generate a python module which contains component consumption functions and import it
    for use.

    :param components: glob string which specify a set of components. Example values:
        # components from workspace
        azureml://{subscription_id}/{resource_group}/{workspace_name}
        azureml://{subscription_id}/{resource_group}/{workspace_name}/components/microsoft_samples_*
        # components from local yaml
        file:components/**/module_spec.yaml
     # components from feeds
     # TBD: after the component sharing design finalized. See: https://aka.ms/azuremlsharing​.
        azureml:OfficeMLFeeds
    :param module_name: name of the generated python module.
        We generate the file relative to the folder that triggers the dsl.generate_module call.
    :type module_name: str
    :param force_regenerate: whether to force regenerate the python module file.
        If True, will always generate and re-import the newly generated file.
        If False, will reuse previous generated file. If the existing file is invalid, raise import error.
    :type force_regenerate: bool
    """
    dir_path = os.getcwd()
    full_path = os.path.join(dir_path, f'{module_name}.py')
    components = [components] if type(components) == str else components
    # Generate module file
    if force_regenerate or not os.path.exists(full_path):
        # Get matched components in ws
        workspace, components = _resolve_workspace_and_components(components)
        api_caller = ComponentAPI(workspace, _logger)
        ws_patten = f'azureml://{workspace.subscription_id}/{workspace.resource_group}/{workspace.name}/components'
        ws_components_definition = _get_components_in_ws(api_caller, ws_patten, components)
        ModuleFileGenerator(definitions=ws_components_definition, workspace=workspace,
                            components_from_call=components, module_name_from_call=module_name)\
            .to_component_entry_file(target=full_path)
        print(f'Successfully generate module {module_name!r} at {full_path}.')
    # Import module
    module = _import_component_with_working_dir(module_name, dir_path, force_regenerate)
    print(f'Dynamically import module {module_name!r} at {full_path}.')
    return module


def _get_components_in_ws(api_caller, ws_patten, components):
    result = api_caller.list(basic_info_only=False)
    return [definition for definition in result for component in components if fnmatch('%s/%s' % (
        ws_patten, _sanitize_python_variable_name(definition.name)), component)]


WORKSPACE_PREFIX = 'azureml://'
LOCAL_PREFIX = 'file:'


def _resolve_workspace_and_components(components):
    subscription_id = None
    resource_group = None
    workspace_name = None
    standard_components = []
    invalid_format_msg =  \
        "Invalid components identifier: %s, expected formats are " \
        "'azureml://{subscription_id}/{resource_group}/{workspace_name}' and " \
        "azureml://{subscription_id}/{resource_group}/{workspace_name}/components/{component_name_glob_patten}"
    for component in components:
        # TODO: support local prefix
        if not component.startswith(WORKSPACE_PREFIX):
            raise UserErrorException(invalid_format_msg % component)
        meta_str = component[len(WORKSPACE_PREFIX):]
        parts = [part for part in meta_str.split(sep='/') if part]
        # azureml://{subscription_id}/{resource_group}/{workspace_name}
        if len(parts) == 3:
            parts += ['components', '*']
        # azureml://{subscription_id}/{resource_group}/{workspace_name}/components/{patten}
        if len(parts) != 5 or parts[3] != 'components':
            raise UserErrorException(invalid_format_msg % component)
        sub, rg, ws_name = parts[:3]
        if subscription_id is None:
            subscription_id, resource_group, workspace_name = sub, rg, ws_name
        elif sub != subscription_id or rg != resource_group or ws_name != workspace_name:
            raise UserErrorException(f'Not all components from same workspace. Components: {components}')
        standard_components.append('azureml://%s' % '/'.join(parts))
    return Workspace.get(subscription_id=subscription_id,
                         resource_group=resource_group,
                         name=workspace_name), standard_components
