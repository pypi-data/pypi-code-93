# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import hashlib
import inspect
import json
import logging
import uuid
import concurrent.futures
from enum import Enum
from pathlib import Path

from azureml.core.compute import AmlCompute, ComputeInstance, RemoteCompute, HDInsightCompute
from azureml.data.abstract_dataset import AbstractDataset
from azureml.data.data_reference import DataReference
from azureml.data.dataset_consumption_config import DatasetConsumptionConfig
from azureml.exceptions import UserErrorException

from azure.ml.component.dsl.types import _GroupAttrDict
from azure.ml.component._restclients.designer.models import LegacyDataPath
from azure.ml.component._core._component_definition import ComponentType, PipelineComponentDefinition
from azure.ml.component._util._utils import _get_dataset_def_from_dataset

from .component import Component, Input, Output, _get_workspace_default_datastore
from ._dataset import _GlobalDataset
from ._module_dto import _python_type_to_type_code
from ._parameter_assignment import _ParameterAssignment
from ._pipeline_parameters import PipelineParameter
from ._util._loggerfactory import timer
from ._util._utils import _ensure_dataset_saved_in_workspace, _get_parameter_static_value

from ._restclients.designer.models import GraphDraftEntity, GraphModuleNode, GraphDatasetNode, GraphReferenceNode, \
    GraphEdge, ParameterAssignment, PortInfo, DataSetDefinition, EntityInterface, Parameter, DataPathParameter, \
    OutputSetting, InputSetting, GraphModuleNodeRunSetting, ComputeSetting, \
    RunSettingUIWidgetTypeEnum, ComputeType, MlcComputeInfo, RunSettingParameterAssignment, \
    MinMaxParameterRule, EnumParameterRule, NodePortInterface, NodeInputPort, NodeOutputPort, \
    DatastoreSetting


DATAFRAMEDIRECTORY = 'DataFrameDirectory'


class _GraphEntityBuilderContext(object):
    def __init__(self, compute_target=None, pipeline_parameters=None, pipeline_regenerate_outputs=None,
                 module_nodes=None, workspace=None, default_datastore=None, outputs=None,
                 pipeline_nodes=None, pipeline_component_definition=None):
        """
        Init the context needed for graph builder.

        :param compute_target: The compute target.
        :type compute_target: tuple(name, type)
        :param pipeline_parameters: The values of pipeline parameters.
        :type pipeline_parameters: dict
        :param pipeline_regenerate_outputs: the `regenerate_output` value of all module node
        :type pipeline_regenerate_outputs: bool
        :param module_nodes: The list of components expanded from the current pipeline
        :type module_nodes: list[Component]
        :param workspace: The workspace of the current pipeline.
        :type workspace: Workspace
        :param default_datastore: The default datastore.
        :type default_datastore: str
        :param outputs: pipeline outputs
        :type outputs: _AttrDict
        :param pipeline_nodes: The top level pipeline nodes in the current pipeline.
        :type pipeline_nodes: list[Pipeline, Component]
        :param pipeline_component_definition: The definition of the current pipeline.
        :type pipeline_component_definition: PipelineComponentDefinition
        """
        self.compute_target = compute_target
        # Copy pipeline parameters here because after build graph, dataset parameters will be removed.
        self.pipeline_parameters = {} if pipeline_parameters is None else {**pipeline_parameters}
        self.pipeline_regenerate_outputs = pipeline_regenerate_outputs

        self.module_nodes = module_nodes
        self.workspace = workspace
        # Correct top pipeline's default datastore here.
        if default_datastore is None:
            default_datastore = _get_workspace_default_datastore(workspace)
        self.default_datastore = default_datastore
        self.outputs = outputs
        self.pipeline_nodes = pipeline_nodes
        self._pipeline_component_definition = pipeline_component_definition
        self._flattened_parameters_group = self._get_flattened_parameters_group()

    def _get_flattened_parameters_group(self):
        """Get flattened parameters name and groups matched dict."""
        flattened_parameters_group = {}
        for k, v in self.pipeline_parameters.items():
            if isinstance(v, _GroupAttrDict):
                flattened_parameters_group.update({group_k: [k] for group_k in v._flatten(group_parameter_name=k)})
            else:
                flattened_parameters_group[k] = []
        return flattened_parameters_group


class _GraphEntityBuilder(object):
    """The builder that constructs SMT graph-related entities from `azure.ml.component.Component`."""
    DATASOURCE_PORT_NAME = 'data'
    DATASOURCE_TYPES = (
        AbstractDataset, DatasetConsumptionConfig, _GlobalDataset, DataReference,
        PipelineParameter,  # Special data source
        str, Path,  # For local run
    )

    def __init__(self, context: _GraphEntityBuilderContext):
        """
        Init the graph entity builder.

        :param context: The graph entity builder context.
        :type context: _GraphEntityBuilderContext
        """
        self._context = context
        self._nodes = {}
        self._input_nodes = {}
        self._data_path_parameter_input = {}
        self._dataset_parameter_keys = set()
        # This is a mapping from the instance ids of modules(components) in the pipeline
        # to the graph node ids in the built graph.
        # We use this mapping to get the graph node according to the module instance in the pipeline
        # when constructing subpipeline, visualization graph, etc..
        self._module_node_to_graph_node_mapping = {}
        self.data_path_assignments = {}
        self._reversed_outputs = {}

    @property
    def module_node_to_graph_node_mapping(self):
        return self._module_node_to_graph_node_mapping

    def _get_node_by_component(self, component: Component):
        return self._nodes.get(self.module_node_to_graph_node_mapping.get(component._get_instance_id()))

    def _get_mapped_sub_graph_output_port(self, component: Component, port_name: str):
        pipelines = [m for m in self._modules if m._is_pipeline]
        for p in pipelines:
            for k, v in p.outputs.items():
                if v._owner == component and v.port_name == port_name:
                    return PortInfo(node_id=self._get_node_by_component(p).id, port_name=k)

    @timer()
    def build_graph_entity(self, for_registration: bool = False, enable_subpipeline_registration: bool = False,
                           anonymous_creation=True):
        """
        Build graph entity that can be used to create pipeline draft, pipeline run and pipeline component.

        Notice that context.pipeline_parameters will be modified after build,
            dataset parameters will be removed.

        :param for_registration: Whether the graph builder is for pipeline component registration.
        In this case, we need to generate specific graph entity interfaces.
        :type for_registration: bool
        :param enable_subpipeline_registration: Whether do sub pipeline registration
        when building the graph draft entity. Currently, we will still need to check the environment variable
        'ENABLE_SUBPIPELINE_REGISTER' to decide if the graph builder will did the registration
        :type enable_subpipeline_registration: bool
        :param anonymous_creation: is anonymous register or not
        :type anonymous_creation: bool
        :return Tuple of (graph entity, module node run settings)
        :rtype tuple
        """
        graph_entity = GraphDraftEntity()
        if self._context.outputs is not None:
            self._reversed_outputs = {val: name for name, val in self._context.outputs.items()}

        # if subpipeline registration is enabled, we need to do three things here:
        # 1. overwrite the module nodes, since we do not want the sub pipeline node be expanded
        # 2. register subpipeline if it is not registered
        thread_pool, create_component_futures = concurrent.futures.ThreadPoolExecutor(), []
        if enable_subpipeline_registration:
            self._modules = self._context.pipeline_nodes
            for node in self._modules:
                if node._is_pipeline and not node._is_registered:
                    # Pure node means the empty component with only default params on function as input
                    pure_node = node._definition.create_pure_component_for_registration()
                    # Parallel registering pipeline component.
                    # Because the operations, checking register_task and submitting register task, are not atomic,
                    # it may happen that the registration request of the same definition is sent at the same time.
                    if node._definition._register_task:
                        create_component_futures.append(node._definition._register_task)
                    else:
                        # Note: Here we use pure node to show the link between pipeline parameter and node.
                        register_task = thread_pool.submit(pure_node._anonymous_create)
                        create_component_futures.append(register_task)
                        node._definition._register_task = register_task
        else:
            self._modules = self._context.module_nodes

        concurrent.futures.wait(create_component_futures, return_when=concurrent.futures.ALL_COMPLETED)
        # Raise exception in the thread pool.
        [future.result() for future in create_component_futures]

        # Prepare the entity
        graph_entity.dataset_nodes = []
        graph_entity.module_nodes = []
        graph_entity.sub_graph_nodes = []
        graph_entity.edges = []
        graph_entity.entity_interface = EntityInterface(parameters=[], data_path_parameters=[],
                                                        data_path_parameter_list=[])

        if self._context.compute_target is not None:
            default_compute_name, default_compute_type = self._context.compute_target
            graph_entity.default_compute = ComputeSetting(name=default_compute_name,
                                                          compute_type=ComputeType.mlc,
                                                          mlc_compute_info=MlcComputeInfo(
                                                              mlc_compute_type=default_compute_type))
        if self._context.default_datastore is not None:
            graph_entity.default_datastore = DatastoreSetting(data_store_name=self._context.default_datastore.name)

        module_node_run_settings = []

        # Note that we need to generate all module nodes before constructing edges.
        for module in self._modules:
            if isinstance(module._definition, PipelineComponentDefinition):
                module_node = self._build_graph_ref_node(module,
                                                         self._context.pipeline_regenerate_outputs,
                                                         for_registration)
                graph_entity.sub_graph_nodes.append(module_node)
            else:
                module_node = self._build_graph_module_node(module,
                                                            self._context.pipeline_regenerate_outputs,
                                                            for_registration)
                graph_entity.module_nodes.append(module_node)
            self._nodes[module_node.id] = module_node

        # Start generating edges and other settings
        for module in self._modules:
            module_node = self._get_node_by_component(module)
            # Note that for old components(especially for built-in components),
            # input_name could be different from argument name, we need to use input_name as the key
            inputs_map = {
                module._get_input_name_by_argument_name(k): i
                for k, i in module._input_ports.items() if i._dset is not None
            }
            for input_name, i in inputs_map.items():
                input_dataset = i._get_internal_data_source()
                # when the input is assigned with non None value, i._dset will be Input, otherwise PipelineParameter
                if (isinstance(i._dset, Input) or isinstance(i._dset, PipelineParameter)) and \
                        enable_subpipeline_registration and for_registration:
                    edge = self._produce_edge_graph_port_to_module_node(
                        i._dset.name, input_name, module_node)
                elif isinstance(input_dataset, self.DATASOURCE_TYPES):
                    dataset_node = self._get_or_create_dataset_node(graph_entity, i, for_registration)
                    edge = self._produce_edge_dataset_node_to_module_node(
                        input_name, dataset_node, module_node)
                elif isinstance(input_dataset, Output):
                    edge = self._produce_edge_module_node_to_module_node(
                        input_name, input_dataset, module_node)
                else:
                    raise ValueError("Invalid input type: {0}".format(type(input_dataset)))
                if edge is not None:
                    graph_entity.edges.append(edge)

            # sub graph node has no runsettings
            if not module._is_pipeline:
                # Flatten group parameters to calculate runsettings
                pipeline_parameters = \
                    module._parent._definition._flatten_pipeline_parameters(self._context.pipeline_parameters)
                module_node_run_settings.append(
                    self._produce_module_runsettings(
                        graph_entity, module, module_node, pipeline_parameters, enable_subpipeline_registration))
            else:
                module_node.use_graph_default_compute = module.default_compute_target is None

            self._update_module_node_params(graph_entity, module_node, module)

        self._update_data_path_parameter_list(graph_entity)

        # disable this for now. Because backend will hit null ref when data path assignments is not valued
        # self._update_data_path_parameters(graph_entity)

        # Set this for further usage including creating subpipeline info, creating visualization graph and export.
        # This is a little hacky, but graph_entity is a swagger generated class which cannot be modified,
        # so currently we just keep this.
        setattr(graph_entity, 'module_node_to_graph_node_mapping', self.module_node_to_graph_node_mapping)

        # Remove empty data source node.
        # Remove instead of just not adding it because we need display empty node when visualize in notebook.
        remove_node_ids = self.resolve_empty_nodes(graph_entity)
        graph_entity.dataset_nodes = [node for node in graph_entity.dataset_nodes
                                      if node.id not in remove_node_ids]
        graph_entity.edges = [edge for edge in graph_entity.edges
                              if edge.source_output_port.node_id not in remove_node_ids]

        # Re-generate entity interface for pipeline component registration graph
        if for_registration:
            self.update_graph_entity_interface(graph_entity, anonymous_creation=anonymous_creation)
        else:
            # Keep graph data path parameter order as original pipeline parameter order.
            # Just easy for customer to read if there are many parameters.
            graph_entity.entity_interface.data_path_parameter_list = \
                self.sort_parameter_order(graph_entity.entity_interface.data_path_parameter_list)
            graph_entity.entity_interface.parameters = \
                self.sort_parameter_order(graph_entity.entity_interface.parameters)

        return graph_entity, module_node_run_settings

    def build_graph_json(self, for_registration: bool = False):
        """Build graph and convert the object to json string recursively."""
        def serialize_object_to_dict(obj):
            if type(obj) in [str, int, float, bool] or obj is None:
                return obj

            if isinstance(obj, dict):
                for k, v in obj.items():
                    obj[k] = serialize_object_to_dict(v)
            elif type(obj) in [tuple, list]:
                obj = [serialize_object_to_dict(i) for i in obj]
            else:
                obj = serialize_object_to_dict(obj.__dict__)
            return obj

        graph, module_node_run_settings = self.build_graph_entity(for_registration=for_registration)
        compute_name = None if graph.default_compute is None else graph.default_compute.name
        datastore_name = None if graph.default_datastore is None else graph.default_datastore.data_store_name
        graph_dict = {'module_nodes': [serialize_object_to_dict(i) for i in graph.module_nodes],
                      'sub_graph_nodes': [serialize_object_to_dict(i) for i in graph.sub_graph_nodes],
                      'dataset_nodes': [serialize_object_to_dict(i) for i in graph.dataset_nodes],
                      'edges': [serialize_object_to_dict(i) for i in graph.edges],
                      'entity_interface': serialize_object_to_dict(graph.entity_interface),
                      'default_compute': compute_name,
                      'default_datastore': datastore_name,
                      'module_node_run_settings': serialize_object_to_dict(module_node_run_settings)}

        return json.dumps(graph_dict, indent=4, sort_keys=True)

    def sort_parameter_order(self, parameters_list):
        parameters = {_p.name: _p for _p in parameters_list}
        results = {_k: parameters[_k] for _k in self._context.pipeline_parameters.keys() if _k in parameters}
        results.update({_p.name: _p for _p in parameters_list if _p.name not in results})
        return list(results.values())

    def resolve_empty_nodes(self, graph_entity):
        remove_node_ids = []
        data_path_param_names = set(i.name for i in graph_entity.entity_interface.data_path_parameter_list
                                    if i.default_value is not None)
        for node in graph_entity.dataset_nodes:
            dataset_def = node.data_set_definition
            if dataset_def is None or (
                    dataset_def.value is None and dataset_def.parameter_name not in data_path_param_names):
                remove_node_ids.append(str(node.id))
        return set(remove_node_ids)

    def _produce_module_runsettings(
            self, graph_entity: GraphDraftEntity, module: Component, module_node: GraphModuleNode,
            pipeline_parameters, enable_subpipeline_registration):
        if module.runsettings is None:
            return None

        # do not remove this, or else module_node_run_setting does not make a difference
        module_node_run_setting = GraphModuleNodeRunSetting()
        module_node_run_setting.module_id = module._identifier
        module_node_run_setting.node_id = module_node.id
        module_node_run_setting.step_type = module._definition._module_dto.module_entity.step_type
        # Populate submission runsettings
        module_node_run_setting.run_settings, use_default_compute = \
            _populate_submission_runsettings(module, pipeline_parameters, enable_subpipeline_registration)
        # module_node.use_graph_default_compute doesn't take effect,
        # only runsettings.target.use_graph_default_compute takes effect
        module_node.use_graph_default_compute = use_default_compute
        # Add required pipeline parameter, add them to graph.
        _GraphEntityBuilder._append_component_runsetting_pipeline_parameter_to_interface(
            graph_entity, module_node_run_setting.run_settings, pipeline_parameters)
        return module_node_run_setting

    def _produce_edge_dataset_node_to_module_node(self, input_name, dataset_node, module_node):
        source = PortInfo(node_id=dataset_node.id, port_name=self.DATASOURCE_PORT_NAME)
        dest = PortInfo(node_id=module_node.id, port_name=input_name)
        return GraphEdge(source_output_port=source, destination_input_port=dest)

    def _produce_edge_module_node_to_module_node(self, input_name, output: Output, dest_module_node):
        # Note that we call topology sort before this so we could make sure the source module node has been added.
        source_module_node = self._get_node_by_component(output._owner)
        # if source_module_node is None, it means the output._owner is inside a pipeline component
        # in this case, we should make the source output port as the corresponding pipeline component's output port
        if source_module_node is None:
            source = self._get_mapped_sub_graph_output_port(output._owner, output._port_name)
        else:
            source = PortInfo(node_id=source_module_node.id, port_name=output.port_name)
        dest = PortInfo(node_id=dest_module_node.id, port_name=input_name)
        return GraphEdge(source_output_port=source, destination_input_port=dest)

    def _produce_edge_graph_port_to_module_node(self, source_port_name, input_name, module_node):
        source = PortInfo(graph_port_name=source_port_name)
        dest = PortInfo(node_id=module_node.id, port_name=input_name)
        return GraphEdge(source_output_port=source, destination_input_port=dest)

    def _get_or_create_dataset_node(self, graph_entity: GraphDraftEntity, input: Input, for_registration: bool):
        # Need to be refined, what if a dataset provide different modes?
        input_hash = input._get_internal_data_source()
        if input_hash not in self._input_nodes:
            dataset_node = self._build_graph_datasource_node(input, for_registration)
            graph_entity.dataset_nodes.append(dataset_node)
            self._nodes[dataset_node.id] = dataset_node
            self._input_nodes[input_hash] = dataset_node
        return self._input_nodes[input_hash]

    def _build_graph_module_node(self, module: Component,
                                 pipeline_regenerate_outputs: bool, for_registration: bool) -> GraphModuleNode:
        node_name = module._get_component_name()
        node_id = self._generate_node_id(node_name) \
            if for_registration else self._generate_node_id()

        regenerate_output = pipeline_regenerate_outputs \
            if pipeline_regenerate_outputs is not None else module.regenerate_output

        module_node = GraphModuleNode(id=node_id, module_id=module._identifier, name=node_name,
                                      regenerate_output=regenerate_output, comment=module.comment)
        module_node.module_parameters = []
        module_node.module_metadata_parameters = []
        self.module_node_to_graph_node_mapping[module._get_instance_id()] = node_id
        return module_node

    def _build_graph_ref_node(self, module: Component,
                              pipeline_regenerate_outputs: bool, for_registration: bool) -> GraphReferenceNode:
        node_name = module._get_component_name()
        node_id = self._generate_node_id(node_name) \
            if for_registration else self._generate_node_id()

        regenerate_output = pipeline_regenerate_outputs \
            if pipeline_regenerate_outputs is not None else module.regenerate_output

        module_node = GraphReferenceNode(id=node_id, module_id=module._identifier, name=node_name,
                                         regenerate_output=regenerate_output, comment=module.comment)
        module_node.module_parameters = []
        module_node.module_metadata_parameters = []
        self.module_node_to_graph_node_mapping[module._get_instance_id()] = node_id
        return module_node

    @staticmethod
    def _append_pipeline_parameter_to_interface(graph_entity, pipeline_parameters, parameter_name):
        """
        Add necessary pipeline parameter to resolve parameter reference.

        :param graph_entity: the graph entity.
        :type graph_entity: GraphDraftEntity
        :param pipeline_parameters: the pipeline parameters dict.
        :type pipeline_parameters: dict
        :param parameter_name: the parameter name.
        :type parameter_name: str
        """
        if pipeline_parameters is None or graph_entity is None or parameter_name not in pipeline_parameters:
            return
        exist = next((x for x in graph_entity.entity_interface.parameters
                      if x.name == parameter_name), None) is not None
        if not exist:
            value = pipeline_parameters[parameter_name]
            graph_entity.entity_interface.parameters.append(Parameter(
                name=parameter_name, default_value=value,
                is_optional=False, type=_python_type_to_type_code(type(value))))

    @staticmethod
    def _append_pipeline_parameter_in_assignment_to_interface(graph_entity, pipeline_parameters, assignment):
        """Append assignment used parameter to entity interface."""
        if pipeline_parameters is None or not isinstance(assignment, _ParameterAssignment) or graph_entity is None:
            return
        # Add necessary pipeline parameter to resolve parameter reference
        for name in assignment.expand_all_parameter_name_set():
            # If name is sub pipeline parameter, it will not appear in pipeline parameter
            if name in pipeline_parameters:
                _GraphEntityBuilder._append_pipeline_parameter_to_interface(
                    graph_entity, pipeline_parameters, name)

    @staticmethod
    def _append_component_runsetting_pipeline_parameter_to_interface(
            graph_entity, module_node_runsettings, pipeline_parameters):
        """Append pipeline parameter used in component runsettings to interface."""

        def append_by_type(obj):
            if obj.value_type == _GraphEntityBuilder.GRAPH_PARAMETER_NAME:
                _GraphEntityBuilder._append_pipeline_parameter_to_interface(
                    graph_entity, pipeline_parameters, obj.value)
            elif obj.value_type == _GraphEntityBuilder.CONCATENATE:
                for part in obj.assignments_to_concatenate:
                    append_by_type(part)

        for runsetting in module_node_runsettings:
            if runsetting.value_type == _GraphEntityBuilder.LITERAL:
                continue
            append_by_type(runsetting)

    def _update_module_node_params(
        self, graph_entity: GraphDraftEntity, module_node: GraphModuleNode, module: Component
    ):
        """Add module node parameters and update it with context.pipeline_parameters."""
        pipeline_parameters = module._parent._definition._flatten_pipeline_parameters(
            self._context.pipeline_parameters)

        node_parameters = module._get_default_parameters()
        node_pipeline_parameters = {}
        node_str_assignment_parameters = {}

        user_provided_params = module._build_params()
        for param_name, param_value in user_provided_params.items():
            # TODO: Use an enum for value_type
            if isinstance(param_value, Input):
                param_value = param_value._get_internal_data_source()
            if isinstance(param_value, PipelineParameter):
                # Notice that pipeline_param_name != param_name here
                # pipeline_param_name is the real value's pipeline parameter name
                # param_name is the parameter definition name on component
                pipeline_param_name = param_value._full_name
                if pipeline_param_name in pipeline_parameters:
                    node_pipeline_parameters[param_name] = pipeline_param_name
                    # Add necessary pipeline parameter to resolve parameter reference
                    _GraphEntityBuilder._append_pipeline_parameter_to_interface(
                        graph_entity, pipeline_parameters, pipeline_param_name)
                    if param_name in node_parameters:
                        del node_parameters[param_name]
                else:
                    # Some call from visualize may reach here,
                    # because they pass the pipeline parameter without default params.
                    node_parameters[param_name] = param_value.default_value
            elif isinstance(param_value, _ParameterAssignment):
                node_str_assignment_parameters[param_name] = param_value
                _GraphEntityBuilder._append_pipeline_parameter_in_assignment_to_interface(
                    graph_entity, pipeline_parameters, param_value)
                if param_name in node_parameters:
                    del node_parameters[param_name]
            else:
                node_parameters[param_name] = param_value

        # Put PipelineParameter as data_path_parameter for updating datapath list
        module_node.module_input_settings = []
        for input in module._input_ports.values():
            input_setting = InputSetting(
                name=module._get_input_name_by_argument_name(input.name),
                data_store_mode=input.mode,
                path_on_compute=input._path_on_compute
            )
            module_node.module_input_settings.append(input_setting)

            input_data_source = input._get_internal_data_source()
            if not isinstance(input_data_source, PipelineParameter) or \
                    input_data_source.name in self._data_path_parameter_input:
                continue
            self._data_path_parameter_input[input_data_source.name] = input_data_source

        self._batch_append_module_node_parameter(module_node, node_parameters)
        self._batch_append_module_node_pipeline_parameters(module_node, node_pipeline_parameters)
        # Update formatter parts using new pipeline_parameters dict.
        self._batch_append_module_node_assignment_parameters(
            module_node, node_str_assignment_parameters, pipeline_parameters)

        module_node.module_output_settings = []
        # Resolve the pipeline datastore first
        pipeline_datastore = module._resolve_default_datastore()
        pipeline_datastore_name = pipeline_datastore.name if pipeline_datastore is not None else None

        module_node.use_graph_default_datastore = True

        # If a component's port is exposed as a subgraph port, set use_graph_default_datastore = False
        if self._context.outputs and module.outputs:
            if set(module.outputs.keys()).intersection(set(self._context.outputs.keys())):
                module_node.use_graph_default_datastore = False

        for output_name, output in module.outputs.items():
            data_assignment_param_name = self._reversed_outputs.get(output, None)
            # for subgraph node, the output port name is not the same as the inner output's port name
            port_name = output_name if module._is_pipeline else output.port_name
            if output._datastore_name:
                module_node.use_graph_default_datastore = False
            output_setting = OutputSetting(
                name=port_name,
                data_store_name=output._datastore_name if output._datastore_name else pipeline_datastore_name,
                data_store_mode=output.output_mode,
                path_on_compute=output._path_on_compute,
                data_reference_name=port_name,
                dataset_registration=output._dataset_registration,
                dataset_output_options=output._dataset_output_options,
                parameter_name=data_assignment_param_name,
            )

            # if module's output is pipeline output, build as data path assignment and add edge for it
            if data_assignment_param_name is not None:
                if output._dataset_output_options is None:
                    relative_path = None
                else:
                    relative_path = output._dataset_output_options.path_on_datastore
                self.data_path_assignments[data_assignment_param_name] = LegacyDataPath(
                    data_store_name=output._datastore_name if output._datastore_name else pipeline_datastore_name,
                    relative_path=relative_path
                )
                # add edge for pipeline output
                source = PortInfo(node_id=module_node.id, port_name=port_name)
                dest = PortInfo(graph_port_name=data_assignment_param_name)
                graph_entity.edges.append(GraphEdge(source_output_port=source, destination_input_port=dest))
            module_node.module_output_settings.append(output_setting)

    def _update_data_path_parameter_list(self, graph_entity: GraphDraftEntity):
        """Update data path parameters with dataset parameters in context.pipeline_parameters."""
        def get_override_parameters_def(name, origin_val, pipeline_parameters):
            # Check if user choose to override with pipeline parameters
            if pipeline_parameters is not None and len(pipeline_parameters) > 0:
                for k, v in pipeline_parameters.items():
                    if k == name:
                        self._dataset_parameter_keys.add(k)
                        if isinstance(v, _GlobalDataset):
                            return _get_dataset_def_from_dataset(v)
                        elif isinstance(v, AbstractDataset):
                            _ensure_dataset_saved_in_workspace(v, self._context.workspace)
                            return _get_dataset_def_from_dataset(v)
                        else:
                            raise UserErrorException('Invalid parameter value for dataset parameter: {0}'.format(k))

            return origin_val

        pipeline_parameters = self._context.pipeline_parameters
        for name, pipeline_parameter in self._data_path_parameter_input.items():
            dset = pipeline_parameter.default_value
            dataset_def = None

            if isinstance(dset, DatasetConsumptionConfig):
                dset = dset.dataset

            if isinstance(dset, AbstractDataset):
                _ensure_dataset_saved_in_workspace(dset, self._context.workspace)
                dataset_def = _get_dataset_def_from_dataset(dset)

            if isinstance(dset, (_GlobalDataset, DataReference)):
                dataset_def = _get_dataset_def_from_dataset(dset)
            dataset_def = get_override_parameters_def(name, dataset_def, pipeline_parameters)
            if dataset_def is not None:
                exist = next((x for x in graph_entity.entity_interface.data_path_parameter_list
                              if x.name == name), None) is not None
                if not exist:
                    graph_entity.entity_interface.data_path_parameter_list.append(DataPathParameter(
                        name=name,
                        default_value=dataset_def.value,
                        is_optional=False,
                        data_type_id=DATAFRAMEDIRECTORY
                    ))

    def _update_data_path_parameters(self, graph_entity: GraphDraftEntity):
        entity_interface = graph_entity.entity_interface
        for output_name, output_def in self._context._pipeline_component_definition.outputs.items():
            entity_interface.data_path_parameters.append(DataPathParameter(
                name=output_name,
                # keep it as empty string, UX will handle this as no input on their side
                default_value=LegacyDataPath(data_store_name='', relative_path=''),
                is_optional=True,
                documentation=output_def.description,
                data_type_id=output_def.type
            ))

    def update_graph_entity_interface(self, graph_entity: GraphDraftEntity, anonymous_creation=True):
        """For pipeline component registration graph, we need to:
        - update entity_interface.parameters to definitions
        - move entity_interface.data_path_parameter_list to entity_interface.ports.inputs
        - add entity_interface.ports.outputs from output definition"""

        entity_interface = graph_entity.entity_interface
        # Update parameters
        entity_interface.parameters = []
        for param_name, param_def in self._context._pipeline_component_definition.flattened_parameters.items():
            from ._api._api import _DefinitionInterface
            group_names = self._context._flattened_parameters_group.get(param_name)
            param = Parameter(
                name=param_name,
                documentation=param_def.description,
                default_value=(None if param_def.default is inspect.Parameter.empty else param_def.default),
                is_optional=param_def.optional,
                type=_DefinitionInterface._convert_parameter_type_string_to_enum(param_def.type).value,
                group_names=group_names if group_names else None)
            if param_def.min or param_def.max:
                param.min_max_rules = [MinMaxParameterRule(min=param_def.min, max=param_def.max)]
            if param_def.enum:
                param.enum_rules = [EnumParameterRule(valid_values=param_def.enum)]
            entity_interface.parameters.append(param)

        entity_interface.ports = NodePortInterface(inputs=[], outputs=[])
        # Update inputs
        pipeline_definition = self._context._pipeline_component_definition
        for input_name, input_def in pipeline_definition.inputs.items():
            if input_def._default and not anonymous_creation:
                logging.warning(
                    f'Default value of pipeline component {pipeline_definition.name!r}'
                    f' port {input_name!r} is not supported and will be ignored.')
            entity_interface.ports.inputs.append(NodeInputPort(
                name=input_name,
                documentation=input_def.description,
                is_optional=input_def.optional,
                data_types_ids=[input_def.type]
            ))
            # Fix edge from dataset node (now is pipeline input port) to component node port
            data_node = next(
                (n for n in graph_entity.dataset_nodes if n.data_set_definition.parameter_name == input_name),
                None)
            if not data_node:
                continue
            edges = [e for e in graph_entity.edges if e.source_output_port.node_id == data_node.id]
            for edge in edges:
                edge.source_output_port = PortInfo(graph_port_name=input_name)
            # Delete dataset node
            graph_entity.dataset_nodes.remove(data_node)

        entity_interface.data_path_parameter_list = []
        entity_interface.data_path_parameters = []

        # Update outputs
        for output_name, output_def in self._context._pipeline_component_definition.outputs.items():
            entity_interface.ports.outputs.append(NodeOutputPort(
                name=output_name,
                documentation=output_def.description,
                data_type_id=output_def.type
            ))

    LITERAL = _ParameterAssignment.LITERAL
    GRAPH_PARAMETER_NAME = _ParameterAssignment.PIPELINE_PARAMETER
    CONCATENATE = _ParameterAssignment.CONCATENATE

    @staticmethod
    def _get_assignments_to_concatenate(obj: _ParameterAssignment, pipeline_parameters=None):
        """Convert the _ParameterAssignment to graph type ParameterAssignment."""
        if not isinstance(obj, _ParameterAssignment):
            return None
        obj = obj.flatten()
        assignments = []
        pipeline_parameters = {} if pipeline_parameters is None else pipeline_parameters
        for part in obj.assignments:
            # part will be LITERAL/PIPELINE PARAMETER
            # part.str in pipeline parameters indicate it is root pipeline parameter
            if part.type == _GraphEntityBuilder.LITERAL or part.str in pipeline_parameters:
                assignment = ParameterAssignment(value=part.str, value_type=part.type)
            else:
                # If part is PipelineParameter but not in pipeline_parameters, then it is
                # sub pipeline parameter, find value from values dict and resolve as LITERAL.
                real_value = obj.assignments_values_dict[part.str].default_value
                assignment = ParameterAssignment(value=real_value, value_type=_GraphEntityBuilder.LITERAL)
            assignments.append(assignment)
        return assignments

    @staticmethod
    def _resolve_parameter_value_and_type(
            parameter_value, pipeline_parameters=None):
        """Return the parameter value, value_type and assignment if there has one."""
        value = parameter_value
        value_type = _GraphEntityBuilder.LITERAL
        assignments = None
        pipeline_parameters = {} if pipeline_parameters is None else pipeline_parameters
        # Note that here the value is name if is pipeline parameter
        # so don't use _get_parameter_static_value here
        if isinstance(value, Input):
            value = value._get_internal_data_source()
        if isinstance(value, _ParameterAssignment):
            value_type = _GraphEntityBuilder.CONCATENATE
            # Get the resolved value if is _ParameterAssignment
            assignments = _GraphEntityBuilder._get_assignments_to_concatenate(value, pipeline_parameters)
            value = value.value
        elif isinstance(value, PipelineParameter):
            pipeline_param_name = value._full_name
            if pipeline_param_name in pipeline_parameters:
                value_type = _GraphEntityBuilder.GRAPH_PARAMETER_NAME
                # Link the pipeline parameter name if is pipeline parameter
                value = pipeline_param_name
            else:
                value = value.default_value
        return value, value_type, assignments

    @staticmethod
    def _resolve_runsetting_parameter_assignment(
            runsetting_def, runsetting_value, component,
            linked_parameter_name=None, pipeline_parameters=None, enable_subpipeline_registration=False):
        """Resolve the runsetting on component to RunsettingParameterAssignment."""
        is_compute_target = runsetting_def.is_compute_target
        resolved_value, value_type, assignments = \
            _GraphEntityBuilder._resolve_parameter_value_and_type(runsetting_value, pipeline_parameters)

        if is_compute_target:
            # Correct:
            # If compute is inherit from top pipeline then use_root_pipeline_default_compute is True.
            # If compute is inherit from sub pipeline then use_root_pipeline_default_compute is False.
            compute_name, compute_type, use_root_pipeline_default_compute = component._resolve_compute(
                enable_subpipeline_registration)
            if use_root_pipeline_default_compute:
                compute_name = None
                compute_type = None
            resolved_value = compute_name if value_type == _GraphEntityBuilder.LITERAL else resolved_value
            return RunSettingParameterAssignment(
                name=runsetting_def.name, value=resolved_value, value_type=value_type,
                use_graph_default_compute=use_root_pipeline_default_compute, mlc_compute_type=compute_type,
                assignments_to_concatenate=assignments, linked_parameter_name=linked_parameter_name)
        else:
            # If there are pipeline parameter or assignments, we just resolve the real value for validation
            # And it has no effect because we set the correct value_type.
            return RunSettingParameterAssignment(
                name=runsetting_def.name, value=resolved_value, value_type=value_type,
                assignments_to_concatenate=assignments, linked_parameter_name=linked_parameter_name)

    def _batch_append_module_node_pipeline_parameters(self, module_node: GraphModuleNode, params):
        for k, v in params.items():
            param_assignment = ParameterAssignment(name=k, value=v, value_type=self.GRAPH_PARAMETER_NAME)
            module_node.module_parameters.append(param_assignment)

    def _batch_append_module_node_parameter(self, module_node: GraphModuleNode, params):
        for k, v in params.items():
            param_assignment = ParameterAssignment(name=k, value=v, value_type=self.LITERAL)
            module_node.module_parameters.append(param_assignment)

    def _batch_append_module_node_assignment_parameters(
            self, module_node: GraphModuleNode, params: dict, pipeline_parameters: dict):
        """
        Resolve _ParameterAssignment as multiple parameter assignment.

        :param module_node: the module node on graph.
        :type module_node: GraphModuleNode
        :param params: key is param name and value is _StrParameterAssignment.
        :type params: dict[str, _ParameterAssignment]
        :param pipeline_parameters: use pipeline_parameters from user input to update concatenate value.
        :type pipeline_parameters: dict[str, Any]
        """
        for k, v in params.items():
            flattened_v = v.flatten()
            assignments_to_concatenate = \
                _GraphEntityBuilder._get_assignments_to_concatenate(flattened_v, pipeline_parameters)
            param_assignment = ParameterAssignment(
                name=k, value=flattened_v.get_value_with_pipeline_parameters(pipeline_parameters),
                value_type=self.CONCATENATE, assignments_to_concatenate=assignments_to_concatenate)
            module_node.module_parameters.append(param_assignment)

    def _append_module_meta_parameter(self, module_node: GraphModuleNode, param_name, param_value):
        param_assignment = ParameterAssignment(name=param_name, value=param_value, value_type=self.LITERAL)
        module_node.module_metadata_parameters.append(param_assignment)

    def _build_graph_datasource_node(self, input: Input, for_registration: bool) -> GraphDatasetNode:
        input = input._get_internal_data_source()  # Get the actual input
        if isinstance(input, DatasetConsumptionConfig):
            input = input.dataset  # Get the AbstractDataset instance

        if isinstance(input, (AbstractDataset, _GlobalDataset, DataReference)):
            if isinstance(input, AbstractDataset):  # Make sure this dataset is saved.
                _ensure_dataset_saved_in_workspace(input, self._context.workspace)

            dataset_def = _get_dataset_def_from_dataset(input)

        if isinstance(input, PipelineParameter):
            dataset_def = DataSetDefinition(data_type_short_name=DATAFRAMEDIRECTORY,
                                            parameter_name=input.name)

        if isinstance(input, str) or isinstance(input, Path):
            dataset_def = DataSetDefinition(data_type_short_name=DATAFRAMEDIRECTORY,
                                            value=str(input))

        if dataset_def is None:
            raise NotImplementedError("Unrecognized data source type: %r" % type(input))

        node_id = self._generate_node_id(str(dataset_def.as_dict())) \
            if for_registration else self._generate_node_id()

        return GraphDatasetNode(id=node_id, data_set_definition=dataset_def)

    @staticmethod
    def _extract_mlc_compute_type(target_type):
        if target_type == AmlCompute._compute_type or target_type == RemoteCompute._compute_type or \
                target_type == HDInsightCompute._compute_type or target_type == ComputeInstance._compute_type:
            if target_type == AmlCompute._compute_type:
                return 'AmlCompute'
            elif target_type == ComputeInstance._compute_type:
                return 'ComputeInstance'
            elif target_type == HDInsightCompute._compute_type:
                return 'Hdi'
        return None

    def _generate_node_id(self, identifier=None) -> str:
        """
        Generate a random 8-character node Id if identifier is None, else generate md5 of the identifier as node Id.

        :param: identifier: identifier used to generate node Id
        :type: identifier: str
        :return: node_id
        :rtype: str
        """
        if identifier is not None:
            s = bytes(identifier, 'utf8')
            return hashlib.md5(s).hexdigest()
        else:
            guid = str(uuid.uuid4())
            return guid[:8]


def _assert_graph_json_equal(graph_json1, graph_json2):
    """Compare graph json in same workspace."""
    def standardized_node(graph_json):
        """Standardized node id in graph json."""
        graph = json.loads(graph_json)
        # Map old node id to new
        node_id_dict = {}
        # Record the module id and instance count
        module_count = {}
        # 1. dataset_nodes - Format and update dataset node id as dataset_{number}
        for idx, node in enumerate(graph['dataset_nodes']):
            node_id = node['id']
            new_node_id = f'dataset_{idx}'
            node_id_dict[node_id] = new_node_id
            node['id'] = new_node_id
        # 2. module_nodes - Format and update module node id as {moduleid}_{number}
        # Format and update module node name as node id
        for node in graph['module_nodes']:
            node_id = node['id']
            module_id = node['module_id']
            if module_id not in module_count:
                module_count[module_id] = 0
            module_count[module_id] += 1
            new_node_id = f'{module_id}_{module_count[module_id]}'
            node_id_dict[node_id] = new_node_id
            node['id'] = new_node_id
            node['name'] = new_node_id
        # 3. edges - Update node id in edge
        for edge in graph['edges']:
            if edge['destination_input_port'].get('node_id', None) is not None:
                edge['destination_input_port']['node_id'] = node_id_dict[edge['destination_input_port']['node_id']]
            if edge['source_output_port'].get('node_id', None) is not None:
                edge['source_output_port']['node_id'] = node_id_dict[edge['source_output_port']['node_id']]
        # 4. module_node_runsettings - Update node id in module_node_runsettings
        for setting in graph['module_node_run_settings']:
            setting['node_id'] = node_id_dict[setting['node_id']]
            # 5. sort runsettings
            setting['run_settings'].sort(key=lambda item: item['name'])
            for run_setting in setting['run_settings']:
                if run_setting['compute_run_settings'] is not None:
                    run_setting['compute_run_settings'].sort(key=lambda item: item['name'])
        return json.dumps(graph)

    graph_json1 = standardized_node(graph_json1)
    graph_json2 = standardized_node(graph_json2)
    return graph_json1 == graph_json2


def _int_str_to_run_setting_ui_widget_type_enum(int_str_value):
    return list(RunSettingUIWidgetTypeEnum)[int(int_str_value)]


def _parse_choice_type_search_space_parameter(type, values):
    """Parse choice type search space paraameters.

    :param values: [[choice1, choice2, xxx]]
    :type values: list
    :return: dict_v
    :rtype: value with dictionary format
    """
    [options] = values
    if _is_sweep_conditional_hyperparameter(options):
        dict_v = {'type': type, 'values': options}
        for model in dict_v['values']:
            for k in model:
                if isinstance(model[k], list):
                    dict_k = _parse_hyperdrive_contract_for_sweep_search_space(k, model[k])
                    model[k] = dict_k
    else:
        # get values from enum
        options = [option.value if isinstance(option, Enum) else option for option in options]
        # change boolean to str
        options = [str(option) if isinstance(option, bool) else option for option in options]
        dict_v = {'type': type, 'values': options}
    return dict_v


def _parse_hyperdrive_contract_for_sweep_search_space(parameter, parameter_expression):
    """
    Parse Sweep search-space contract hyperparameter expression

    :param parameter: Input parameter.
    :type parameter: String
    :param parameter_expression: Hyperparameter expression, generated by azureml.train.hyperdrive uniform, quniform...
    :type parameter_expression: list
    :return: dict_v
    :rtype: value with dictionary format
    """
    [type, values] = parameter_expression

    if type == 'choice':
        dict_v = _parse_choice_type_search_space_parameter(type, values)
    elif type == 'randint':
        [upper] = values
        dict_v = {'type': type, 'upper': upper}
    elif type == 'uniform' or type == 'loguniform':
        [min_value, max_value] = values
        dict_v = {'type': type, 'min_value': min_value, 'max_value': max_value}
    elif type == 'quniform' or type == 'qloguniform':
        [min_value, max_value, q] = values
        dict_v = {'type': type, 'min_value': min_value, 'max_value': max_value, 'q': q}
    elif type == 'normal' or type == 'lognormal':
        [mu, sigma] = values
        dict_v = {'type': type, 'mu': mu, 'sigma': sigma}
    elif type == 'qnormal' or type == 'qlognormal':
        [mu, sigma, q] = values
        dict_v = {'type': type, 'mu': mu, 'sigma': sigma, 'q': q}
    else:
        raise UserErrorException("'{0}' is not an expected value of parameter '{1}'."
                                 .format(parameter_expression, parameter))
    return dict_v


def _populate_submission_runsettings(component, pipeline_parameters=None, enable_subpipeline_registration=False):
    pipeline_parameters = {} if pipeline_parameters is None else pipeline_parameters
    runsettings_values = component._runsettings._get_flat_values()
    runsettings_definition = component._definition.runsettings
    runsettings = []
    # Search space params
    if component.type == ComponentType.SweepComponent.value:
        search_space_params = _populate_sweep_search_space_runsettings(
            component, runsettings_definition, runsettings_values, pipeline_parameters)
        runsettings.extend(search_space_params)
    compute_target_param = None
    use_root_pipeline_default_compute = True

    # RunSettings params
    for name, p in runsettings_definition.params.items():
        value = runsettings_values.get(p.id)
        # Always add compute settings
        # Since module may use default compute, we don't have to detect this, MT will handle
        if p.is_compute_target:
            compute_value = value if value else p.default_value
            compute_target_param = _GraphEntityBuilder._resolve_runsetting_parameter_assignment(
                p, compute_value, component, pipeline_parameters=pipeline_parameters,
                enable_subpipeline_registration=enable_subpipeline_registration)
            use_root_pipeline_default_compute = compute_target_param.use_graph_default_compute
            runsettings.append(compute_target_param)
            continue
        if value is None:
            continue
        runsetting_param = _GraphEntityBuilder._resolve_runsetting_parameter_assignment(
            p, runsettings_values.get(p.id), component, pipeline_parameters=pipeline_parameters,
            enable_subpipeline_registration=enable_subpipeline_registration)
        runsettings.append(runsetting_param)

    # Compute runsettings
    if compute_target_param is not None and len(runsettings_definition.compute_params) > 0:
        compute_runsettings_values = component._k8srunsettings._get_flat_values()
        compute_settings = []
        for p in runsettings_definition.compute_params.values():
            value = compute_runsettings_values.get(p.id)
            if value is None:
                continue
            compute_param = _GraphEntityBuilder._resolve_runsetting_parameter_assignment(
                p, value, component, pipeline_parameters=pipeline_parameters,
                enable_subpipeline_registration=enable_subpipeline_registration)
            compute_settings.append(compute_param)
        compute_target_param.compute_run_settings = compute_settings
    return runsettings, use_root_pipeline_default_compute


def _populate_sweep_search_space_runsettings(
        component, runsettings_definition, runsettings_values, pipeline_parameters=None):
    algorithm = next(
        (p for p in runsettings_definition.params.values() if p.linked_parameters is not None), None)
    search_space_params = []
    if algorithm is None:
        return search_space_params

    # Get linked parameters
    linked_params = algorithm.linked_parameters.keys()
    # Get user inputs
    input_values = {k: v for k, v in component._parameter_params.items() if k in linked_params and v is not None}
    # get user provided inputs
    user_provided_linked_params = input_values.keys()
    algorithm_value = runsettings_values.get(algorithm.id, None)
    # For handling corner case: user doesn't set the value to the algorithm through runsettings but uses the default,
    # and sets search space params in the component's inputs. We need to get the default algorithm.
    # E.g. component = sweep_func(learning_rate=choice([0.2, 0.3]))
    if algorithm_value is None and any(input_values.values()):
        algorithm_value = algorithm.default_value

    def _parse_input_values_by_type(val):
        """Resolve and update input values by value type."""
        # Supported search-space input
        # 1. sweep_func(learning_rate=choice([0.02, 0.05]))
        # 2. sweep_func(learning_rate=0.05)
        # 3. class Rate(Enum):
        #       rate1 = 0.02
        #    sweep_func(learning_rate = Rate.rate1)
        if val is None:
            return {}
        elif isinstance(val, list):
            # This section is used for parsing input contract hyperparameter expressions from
            # azureml.train.hyperdrive Logic & assumption: for now, we don't support/have list type input,
            # therefore, we use isinstance(input, list) to predicate that the input is a
            # sweep-contract-hyperparameter-contract expression. Attention, if we support list-type parameters,
            # this logic must be changed.
            return _parse_hyperdrive_contract_for_sweep_search_space(
                parameter=p, parameter_expression=val)
        elif _is_supported_sweep_search_space_value(val):
            # convert single value to choice type
            logging.warning(
                "Single value passed to search space parameter '{}', converted it to choice type.".format(p))
            return _parse_hyperdrive_contract_for_sweep_search_space(
                parameter=p, parameter_expression=['choice', [[val]]])
        elif isinstance(val, dict):
            return val
        else:
            # if input_values[p] is not a dict, ignore for now, leave a todo here
            # TODO: validate the type and value of input_values[p] in component.validate
            logging.warning("Parameter '%s' type mismatch. Required 'dict', " % p +
                            "got '%s'. Will use default value." % type(val).__name__)
            return {}

    # Refine user inputs
    for p in user_provided_linked_params:
        input_values[p] = _parse_input_values_by_type(input_values[p])
    # Process type, use literal type value for validation
    algorithm_literal_value = _get_parameter_static_value(algorithm_value, pipeline_parameters)
    type_spec = next(
        (p.enabled_by[algorithm.name][algorithm_literal_value]
         for p in runsettings_definition.search_space_params.values() if p.argument_name == 'type' and
         algorithm.name in p.enabled_by and algorithm_literal_value in p.enabled_by[algorithm.name]), None)
    if type_spec is None:
        return search_space_params

    # Add type parameter and get params enabled by type for each linked parameter
    for linked_p_name in user_provided_linked_params:
        linked_p_value = input_values.get(linked_p_name)
        if linked_p_value is None:
            # TODO: rasie exception here?
            continue
        type_input_value = linked_p_value.get(type_spec.argument_name)
        type_literal_value = _get_parameter_static_value(type_input_value)
        if type_literal_value is None or type_literal_value not in type_spec.enum:
            # Try to validate the type value, if not valid, ignore it
            # TODO: put it in component.validation? and throw exception when invalid?
            continue
        # Add type value to submission runsettings
        runsetting_param = _GraphEntityBuilder._resolve_runsetting_parameter_assignment(
            type_spec, type_input_value, component, linked_p_name, pipeline_parameters)
        search_space_params.append(runsetting_param)
        # Append params enabled by type
        params_by_type = [
            p for p in runsettings_definition.search_space_params.values()
            if type_spec.name in p.enabled_by and type_literal_value in p.enabled_by[type_spec.name]]
        for p in params_by_type:
            search_space_param = _GraphEntityBuilder._resolve_runsetting_parameter_assignment(
                p.definition, linked_p_value.get(p.argument_name), component, linked_p_name, pipeline_parameters)
            search_space_params.append(search_space_param)
    return search_space_params


def _is_supported_sweep_search_space_value(value):
    if type(value) in [int, float, str] or isinstance(value, Enum):
        return True
    return False


def _is_sweep_conditional_hyperparameter(values):
    for model in values:
        if not isinstance(model, dict):
            # if values are not with dict type, they are not models
            return False
        for k in model:
            if isinstance(model[k], list):
                return True
    return False
