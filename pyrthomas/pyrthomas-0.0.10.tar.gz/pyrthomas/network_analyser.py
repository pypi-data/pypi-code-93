import itertools
from typing import Tuple, Dict, List

from networkx import DiGraph, simple_cycles
from networkx.classes.reportviews import EdgeView, NodeView

from pyrthomas import utils


class NetworkAnalyser:

    @staticmethod
    def set_predecessor_combinations(network: DiGraph):
        for node in network.nodes:
            predecessors = frozenset(DiGraph.predecessors(network, node))
            combinations = frozenset(utils.all_subsets(predecessors))
            nx.set_node_attributes(network, {node: combinations}, 'predecessor_combinations')

    @staticmethod
    def get_state_space(graph: DiGraph) -> List[Dict[str, int]]:
        max_thresholds = [NetworkAnalyser.get_max_threshold(graph, node) for node in graph.nodes]
        state_space = tuple(itertools.product(*max_thresholds))
        return [dict(zip(graph.nodes, state)) for state in state_space]

    @staticmethod
    def get_max_threshold(graph: DiGraph, node: NodeView) -> Tuple[int]:
        edges = graph.edges(node, data=True)
        max_weighted_edge = max(edges, key=lambda x: utils.get_weight(x, absolute=True))
        max_threshold = utils.get_weight(max_weighted_edge, True)
        return tuple(range(max_threshold + 1))

    @staticmethod
    def get_state_graph(network: DiGraph, parameters: Dict[str, List[Tuple[List[str], int]]]) -> DiGraph:
        """
        Args:
            network: Interaction graph in networkx format
            parameters: Parameters for state graph representing the current state of the entities

        Returns:
            Returns state graph in teh networkx format
        """
        state_space = NetworkAnalyser.get_state_space(network)
        state_graph = DiGraph()
        state_space_nodes = [utils.create_node_from_dict(state) for state in state_space]
        state_graph.add_nodes_from(state_space_nodes)

        resources = NetworkAnalyser.calculate_resources(network, state_space)

        k_states = NetworkAnalyser.calculate_k(resources, parameters)

        next_states = NetworkAnalyser.calculate_next_states(k_states)

        edges = NetworkAnalyser.generate_edges(next_states)
        state_graph.add_edges_from(edges)
        state_graph.graph['parameters'] = parameters
        return state_graph

    @staticmethod
    def generate_edges(next_states):
        edges = list()
        for key, states in next_states.items():
            previous_value = dict(key)
            source = utils.create_node_from_dict(previous_value)
            for state in states:
                target = utils.create_node_from_dict(state)
                edges.append((source, target))
        return edges

    @staticmethod
    def calculate_next_states(k_states):
        for state_key, state in k_states.items():
            previous_entities = dict(state_key)
            new_val = list()
            temp_previous = previous_entities.copy()
            for entity_key, previous_entity in previous_entities.items():
                next_value = k_states[state_key][entity_key]

                if next_value > previous_entity:
                    previous_entities[entity_key] = previous_entity + 1
                elif next_value < previous_entity:
                    previous_entities[entity_key] = previous_entity - 1

                if not (previous_entities in new_val) and not previous_entities == temp_previous:
                    new_val.append(previous_entities.copy())
                    previous_entities[entity_key] = temp_previous[entity_key]
            k_states[state_key] = new_val
        return k_states

    @staticmethod
    def calculate_k(resources, parameters):
        for resource_key, entities in resources.items():
            for entity_key, entity in entities.items():
                matched_interaction = filter(lambda x: sorted(x[0]) == sorted(entity),
                                             parameters[entity_key])
                first_interaction = next(matched_interaction)
                entities[entity_key] = first_interaction[1]
        return resources

    @staticmethod
    def get_cycles(network: DiGraph):
        return simple_cycles(network)

    @staticmethod
    def get_deadlock_states(network: DiGraph):
        out_degree_iter = network.out_degree(network.nodes)
        return [node for node, out_degree in out_degree_iter if out_degree == 0]

    @staticmethod
    def calculate_resources(network: DiGraph, state_space: List[Dict[str, int]]):
        resources = dict()
        for state in state_space:
            node = dict()
            for key in state:
                entity_resources = list()
                in_edges = network.in_edges(key, data=True)
                for edge in in_edges:
                    is_resource = NetworkAnalyser.is_resource_of_state(state, edge)
                    if is_resource:
                        entity_resources.append(edge[0])
                entity_resources.sort()
                node[key] = entity_resources
            state_key = tuple(state.items())
            resources[state_key] = node
        return resources

    @staticmethod
    def get_required_parameters(network: DiGraph):
        nodes = network.nodes
        parameters = dict()
        for node in nodes:
            predecessors = frozenset(DiGraph.predecessors(network, node))
            required_interactions = [(interaction, None) for interaction in
                                     utils.all_subsets(predecessors)]
            parameters[node] = required_interactions

        return parameters

    @staticmethod
    def is_resource_of_state(state: dict, edge: EdgeView):
        weight = utils.get_weight(edge)
        is_positive = weight >= 0
        value = state[edge[0]]
        return (is_positive and value >= abs(weight)) or (not is_positive and value < abs(weight))

    @staticmethod
    def get_possible_parameters(network: DiGraph):
        combinations = dict()
        for node in network.nodes:
            combinations[node] = list()
            max_threshold = utils.get_max_weighted_edge_threashold(network, node)
            predecessors = frozenset(DiGraph.predecessors(network, node))
            required_interactions = list(utils.all_subsets(predecessors))
            for arrangement in itertools.product(range(0, max_threshold + 1), repeat=len(required_interactions)):
                arranged_combination = list(zip(required_interactions, arrangement))
                combinations[node].append(arranged_combination)
        return [dict(zip(combinations, v)) for v in itertools.product(*combinations.values())]

    @staticmethod
    def get_possible_state_graphs(network: DiGraph):
        all_params = NetworkAnalyser.get_possible_parameters(network)
        for param in all_params:
            yield NetworkAnalyser.get_state_graph(network, param)
