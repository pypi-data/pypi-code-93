import logging
import networkx as nx
from enum import Enum

from partialedge.exception.ped_exception import PartialEdgeDrawingException
from partialedge.structure.data_structure import FULL_LENGTH_STUB

DEFAULT_LOGGER_NAME = "ped"
VERBOSITY_LEVEL_STUB = logging.INFO - 4
VERBOSITY_LEVEL_INK = logging.INFO - 5
VERBOSITY_LEVEL_CUT = logging.INFO - 6

logging.basicConfig(format="%(message)s\n", level=logging.INFO)


class IntersectionRange(Enum):
    SHORT = 0
    LONG = 1


class TreeNode:
    """
    Data-structure for the intersection-tree based algorithm
    """

    def __init__(self, intersection_node, logger=logging.getLogger(DEFAULT_LOGGER_NAME)):
        self.intersection_node = intersection_node
        self.logger = logger

        self.children = []

        self.parent_intersection = None

        self.intersection_collection = {IntersectionRange.SHORT: dict(), IntersectionRange.LONG: dict()}
        self.best_ink = {IntersectionRange.SHORT: None, IntersectionRange.LONG: None}
        self.best_factor = {IntersectionRange.SHORT: None, IntersectionRange.LONG: None}

    def calculate_intersections(self, parent_node=None):
        """
        calculates, processes, and stores stub length values as keys in a dictionary
        referencing their respective intersection nodes
        :param parent_node: used for determining parent node intersection
        """
        if parent_node is not None:
            self.parent_intersection = min(
                self.intersection_node.intersect(parent_node.intersection_node)
            )
        else:
            self.parent_intersection = FULL_LENGTH_STUB

        for child in self.children:
            cut = min(self.intersection_node.intersect(child.intersection_node))
            if cut <= self.parent_intersection:
                self.intersection_collection[IntersectionRange.SHORT][cut] = child
            else:
                self.intersection_collection[IntersectionRange.LONG][cut] = child
            child.calculate_intersections(self)

        self.logger.log(VERBOSITY_LEVEL_CUT, "Edge {} determining range of children\nshort range: [{}]\nlong range: [{}]".format(
            self.intersection_node,
            ", ".join([str(tree_node.intersection_node) for tree_node in self.intersection_collection[IntersectionRange.SHORT].values()]),
            ", ".join([str(tree_node.intersection_node) for tree_node in self.intersection_collection[IntersectionRange.LONG].values()])
        ))

    def get_best_ink(self, range=IntersectionRange.LONG):
        if self.best_ink[range] is None:
            self.calculate_maximum_for_range(range)
        return self.best_ink[range]

    def calculate_maximum_for_range(self, range):
        """
        calculate short(node) or long(node) as defined by the paper
        :param range: determines if short or long is calculated
        """
        best_ink = 0
        best_factor = None
        stub_list = \
            list(self.intersection_collection[IntersectionRange.SHORT].keys()) + \
            [self.parent_intersection]
        if range == IntersectionRange.LONG:
            stub_list += \
                list(self.intersection_collection[IntersectionRange.LONG].keys()) + \
                [FULL_LENGTH_STUB]

        for stub_factor in stub_list:
            total = self.test_ink_for_stub_factor(stub_factor)
            if total > best_ink:
                best_factor = stub_factor
                best_ink = total

        self.logger.log(VERBOSITY_LEVEL_STUB, "Edge {} best stub value for range {}: {:.5f}".format(self.intersection_node, range.name, best_factor))
        self.logger.log(VERBOSITY_LEVEL_INK, "Edge {} best ink  value for range {}: {:.3f}\n".format(self.intersection_node, range.name, best_ink))
        self.best_factor[range] = best_factor
        self.best_ink[range] = best_ink

    def test_ink_for_stub_factor(self, stub_factor):
        """
        calculate W_i(node) as defined by the paper
        :param stub_factor: needed to get l_i(node)
        :return: sum of ink in partial tree limited by stub_factor
        """
        sum = 2 * stub_factor * self.intersection_node.edge.get_length()
        for stub, node in list(self.intersection_collection[IntersectionRange.SHORT].items()) +\
                          list(self.intersection_collection[IntersectionRange.LONG].items()):
            if stub < stub_factor:
                sum += node.get_best_ink(IntersectionRange.SHORT)
            else:
                sum += node.get_best_ink(IntersectionRange.LONG)
        return sum

    def collect_result_ink(self, result_dict, range=IntersectionRange.LONG):
        """
        iterates over tree and stores the best stub factors in a dictionary
        :param result_dict: dictionary where result will be stored
        :param range: maximum range limited by parent best factor
        """
        factor = self.best_factor[range]
        result_dict[self.intersection_node.index] = (self.intersection_node, [factor, factor])
        for intersection, node in \
                list(self.intersection_collection[IntersectionRange.SHORT].items()) + \
                list(self.intersection_collection[IntersectionRange.LONG].items()):
            child_range = IntersectionRange.SHORT if intersection < factor \
                else IntersectionRange.LONG
            node.collect_result_ink(result_dict, child_range)


def form_forest(graph, logger=logging.getLogger(DEFAULT_LOGGER_NAME)):
    """
    separates forest into trees and creates a tree structure of custom tree nodes
    assigns plot coordinates to the underlying custom nodes as a side effect
    :param graph: custom graph class containing list of custom nodes and list of custom edges
    :return: list of root custom tree nodes
    """
    nx_graph = nx.Graph()
    nodes = [node.index for node in graph.nodes]
    edges = [(edge.nodes[0].index, edge.nodes[1].index) for edge in graph.edges]
    nx_graph.add_nodes_from(nodes)
    nx_graph.add_edges_from(edges)

    if not nx.is_forest(nx_graph):
        raise PartialEdgeDrawingException("Graph does not form a forest")

    components = list(nx.connected_components(nx_graph))
    roots = []
    for component in components:
        root = next(iter(component))
        roots.append(root)

    def _subtree_pos(G, root, width=1., vert_gap=0.2, vert_loc=0.0, xcenter=0.5, pos=None, parent=None):
        node = graph.nodes[root]
        node.coords = (xcenter, vert_loc)
        tree_node = TreeNode(node, logger)

        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)

        if len(children) != 0:
            dx = width / len(children)
            nextx = xcenter - width / 2 - dx / 2
            for child in children:
                nextx += dx
                tree_node.children.append(_subtree_pos(G, child, width=dx, vert_gap=vert_gap, vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, parent=root))
        return tree_node

    result = [_subtree_pos(nx_graph, roots[i], width=(1.0/len(roots)), xcenter=(1.0/(len(roots)+1)*(i+1))) for i in range(len(roots))]
    return result