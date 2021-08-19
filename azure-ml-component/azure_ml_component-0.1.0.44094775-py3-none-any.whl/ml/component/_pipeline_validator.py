# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A class used for validate pipeline of azure.ml.component.PipelineComponent, and validate dsl.Pipeline recursion."""
from azure.ml.component._util._exceptions import PipelineValidationError


class _ModuleNode(object):
    """Used to save graph module nodes info for cycle tracking."""

    def __init__(self, node_id, input_ports, output_ports):
        self.node_id = node_id
        self._input_ports = input_ports
        self._output_ports = output_ports
        self.outputs = []


class _NodeStatus(object):
    """When checking for cycles in the graph, keep track of which nodes have been visited."""

    # Initial state (not visited yet)
    NOT_VISITED = 0
    # Final state (completed visit of node, putted it neighbors into stack)
    VISITED = 1


class PipelineValidator(object):
    """
    Graph/module validation and visualization.

    For now we are able to detect error when step nodes are missing necessary parameters, and detect if there exists
    module cycles in a pipeline. If we are confident that users are using jupyter notebook, this method will display
    the visualization of the pipeline, in which the errors will be displayed.
    """
    @staticmethod
    def validate_empty_pipeline(pipeline_steps, process_error):
        """
        Validate if a pipeline is empty.

        :param pipeline_steps: pipeline steps, got from VisualizationContext.step_nodes
        :rtype pipeline_steps: List[_Component]
        :param process_error: function to handle invalid situation
        :type process_error: Callable
        """
        if len(pipeline_steps) == 0:
            error = PipelineValidationError(
                message="No node was found in pipeline.", error_type=PipelineValidationError.EMPTY_PIPELINE)
            process_error(error)

    @staticmethod
    def validate_pipeline_steps(pipeline_steps, process_error):
        """
        Graph/module validation and visualization.

        :param pipeline_steps: pipeline steps, got from VisualizationContext.step_nodes
        :rtype pipeline_steps: List[_Component]
        :param process_error: function to handle invalid situation
        :type process_error: Callable
        :return: List of errors
        :rtype: list
        """
        for s in pipeline_steps:
            if len(s.validation_info) > 0:
                process_error(s.validation_info)

    @staticmethod
    def validate_module_cycle(pipeline_steps, process_error):
        """Detect if there is a cycle in pipeline."""
        CycleValidator.validate_cycles(pipeline_steps, process_error)

    @staticmethod
    def validate_pipeline_cycle(definition_builder_stack):
        """
        Return cycled pipeline.

        :param definition_builder_stack: pipeline component definition stack
        :rtype definition_builder_stack: _PipelineComponentDefinitionBuilderStack
        :return: cycled_pipeline_nodes: cycled pipelines
        :rtype: list
        """
        pipeline_stack = [pipeline for pipeline in reversed(definition_builder_stack.items)]
        if not pipeline_stack:
            return []
        cycled_pipeline = [pipeline_stack[0]]
        for pipeline in pipeline_stack[1:]:
            if pipeline.id != cycled_pipeline[0].id:
                cycled_pipeline.append(pipeline)
            else:
                break

        # adjust cycled-pipelines' order according to their calling sequence
        cycled_pipeline_index = [
            definition_builder_stack.items.index(pipeline) for pipeline in cycled_pipeline]
        sorted_index_pipelines = sorted(zip(cycled_pipeline_index, cycled_pipeline))
        # Sorted pipeline number equals stack size indicate there is no loop.
        if len(sorted_index_pipelines) == definition_builder_stack.size():
            return []
        sorted_cycled_pipeline = [pipeline for _, pipeline in sorted_index_pipelines]
        cycled_pipeline_nodes = [item.name for item in sorted_cycled_pipeline]

        return cycled_pipeline_nodes


class CycleValidator:
    """This class is used for checking module-cycles in pipeline"""

    @staticmethod
    def validate_cycles(pipeline_steps, process_error):
        """
        Check for cycle in the graph.

        :param pipeline_steps: got from VisualizationContext.step_nodes
        :type pipeline_steps: List[_Component]
        :param process_error: function to handle invalid situation
        :type process_error: Callable
        :return: cycle_detected: detected cycle, empty if no cycle is detected
        :rtype: list
        """
        # Construct graph
        graph_nodes = CycleValidator._construct_graph(pipeline_steps)
        # Detect all cycles
        cycle_detected = CycleValidator._detect_cycles(graph_nodes)
        # Handle exception
        if cycle_detected:
            cycles_nodes = []
            for node in cycle_detected:
                step = next(item for item in pipeline_steps if item.id == node.node_id)
                # use component name in error message when available
                step_id = step.component_name if step.component_name else step.id
                cycles_nodes.append("{0}({1})".format(step.name, step_id))
            error = PipelineValidationError(message="Module cycle detected, including nodes: {}".format(cycles_nodes),
                                            error_type=PipelineValidationError.MODULE_CYCLE)
            process_error(error)

        return cycle_detected

    @staticmethod
    def _construct_graph(pipeline_steps):
        """
        Construct pipeline graph, which will be used for cycle detection.

        :param pipeline_steps: got from VisualizationContext.step_nodes
        :rtype: List[_Component]
        :return: graph_nodes: module nodes in cycle, including name, id, inputs, outputs info
        :rtype: list
        """
        graph_nodes = []
        for node in pipeline_steps:
            input_ports = [node.inputs[port].node_id for port in node.inputs.keys()]
            output_ports = [node.outputs[port].node_id for port in node.outputs.keys()]
            module_node = _ModuleNode(node_id=node.id, input_ports=input_ports, output_ports=output_ports)
            graph_nodes.append(module_node)

        for graph_node in graph_nodes:
            for output_port in graph_node._output_ports:
                graph_node.outputs += [node for node in graph_nodes if output_port in node._input_ports]

        return graph_nodes

    @staticmethod
    def _detect_cycles(graph_nodes):
        """
        Detect cycles in pipeline. Iterate nodes in graph, do a dfs for each node, return cycle once cycle is detected.

        Prove:
        1. algorithm is not infinite: iterate over finite number graph nodes, for each iteration, only push not_visited
           node into stack, stack pops, one iteration will stop when stack became empty.
        2. if return cycle_detected is not empty, nodes inside are cycle nodes. when the algo encountered starting node
           again, a cycle must be detected. Besides, we use this_cyc with hierarchical level to maintain a path from
           starting node to current node, therefore, returned nodes in cycle_detected is the cycle vertexes.
        3. if there exit a cycle in the graph, this algo can detect it. Because this algo will do a dfs for each node,
           it will start search from one vertex node in that cycle for sure, by then, that cycle will be detected.

        :param graph_nodes: module nodes in pipeline
        :rtype graph_nodes: list
        :return cycle_detected: cycle detected, empty if no cycle is detected
        :rtype cycle_detected: list
        """
        cycle_detected = []

        for node in graph_nodes:
            node_status = {}
            for module_node in graph_nodes:
                node_status[module_node.node_id] = _NodeStatus.NOT_VISITED
            if CycleValidator._get_cycled_nodes(node, node_status, cycle_detected):
                cycle_detected.insert(0, node)
                return cycle_detected

        return cycle_detected

    @staticmethod
    def _get_cycled_nodes(node: _ModuleNode, node_status, cycle_detected):
        """
        Do a depth first search from root module node. If we encountered root node during dfs, return detected cycle.

        Example: graph 1->2->3; 1->4->5->1
        start node: 1
        stack: [(4, 0), (2, 0)]         this_cyc: [(2, 0)]
        stack: [(4, 0), (3, 1)]         this_cyc: [(2, 0), (3, 1)]
        stack: [(4, 0)]                 this_cyc = []
        After stack pop, current_node = 2, layer = 0, thus, POP this_cyc until its node's layer is lower than 'layer'.
                                        this_cyc: [(4, 0)]
        stack: [(5, 1)]                 this_cyc: [(4, 0), (5, 1)]
        After stack pop, current_node = 5, its output is 1, encounter START node, return.

        :param node: root node
        :rtype node: _ModuleNode
        :param node_status: nodes status
        :rtype node_status: dict
        :param cycle_detected: detected cycle
        :rtype cycle_detected: list
        :return cycle_detected: detected cycle
        :rtype cycle_detected: list
        """
        # stack stores all nodes currently wait for search in depth-first searching branch.
        stack = []
        # this_cyc: store current depth-first searching branch, from starting node to current node.
        this_cyc = []
        # layer_count is the hierarchical level(depth) from starting node, which is used for maintain a path from
        # starting node to current node.
        layer_count = 0

        # node element in stack is a tuple (node number, hierarchical level from starting node).
        if node.outputs:
            for neighbor in node.outputs:
                stack.append((neighbor, layer_count))

        while stack:
            current_node, current_layer = stack.pop()
            # retrieve this_cyc's nodes back to current_node's lower layer, by popping nodes out in this_cyc until
            # this_cyc[-1].layer is one layer lower than current_node's layer, which is current_layer.
            if this_cyc:
                _, layer_now = this_cyc[-1]
                while layer_now >= current_layer and this_cyc:
                    _, layer_now = this_cyc.pop()

            # add current node into this_cyc as its last element to ensure the elements in this_cyc are nodes in
            # current searching branch (from starting node to current node) in sequential order.
            this_cyc.append((current_node, current_layer))

            if current_node.outputs:
                # visit current node's outputs, which is next layer/depth, layer_count plus 1
                layer_count = current_layer + 1
                for neighbor in current_node.outputs:
                    # if encountered the starting node, cycle is detected
                    if neighbor.node_id == node.node_id:
                        for n, _ in this_cyc:
                            cycle_detected.append(n)
                        return cycle_detected
                    # if not-visited, push it to stack
                    if node_status[neighbor.node_id] == _NodeStatus.NOT_VISITED:
                        stack.append((neighbor, layer_count))
            # after pushed current node's all outputs to stack, mark current node's status as visited
            node_status[current_node.node_id] = _NodeStatus.VISITED

        return cycle_detected
