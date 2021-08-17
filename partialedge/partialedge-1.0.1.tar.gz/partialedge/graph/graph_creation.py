import networkx as nx
import random
import itertools
import scipy.special
from partialedge.structure import data_structure as ds
from partialedge.core import tree_decomp as td
from partialedge.exception.ped_exception import PartialEdgeDrawingException
from pygeos.creation import linestrings
from pygeos.predicates import crosses

RETRIES_COMBINATIONS = 10000000000
RETRIES_TREE_WIDTH = 10


def create_random_with_tree_width(treewidth, n_max, m_max, symmetric, layout="spring"):
    for _ in range(RETRIES_COMBINATIONS):
        n = random.randint(2, n_max)
        complete_graph_limit = int(scipy.special.binom(n, 2))
        m = random.randint(1, min(complete_graph_limit, m_max))
        for _ in range(RETRIES_TREE_WIDTH):
            graph = create_random_graph(n, m, layout)
            intersection_graph = create_intersection_graph(graph.edges, symmetric)
            tw = td.determine_treewidth(intersection_graph)
            if tw == treewidth:
                return graph

    raise PartialEdgeDrawingException("random graph with treewidth {0} generation took too long, max n/m ratio of {1}/{2} not appropriate".format(treewidth, n_max, m_max))


def create_random_with_tree_intersection(n, m):
    """
    Tries to create a random graph with an tree as intersection graph by randomly adding edges if they do not violate the condition
    :param n: number of nodes
    :param m: number of edges
    :return: graph, where intersection graph forms a tree
    """
    nodes = []
    edge_list = []

    attempt = 0
    while len(edge_list) < m:
        if attempt >= 10:
            raise PartialEdgeDrawingException("random graph with intersection tree generation took too long, m value too high")

        nodes = [ds.Node(i) for i in range(n)]
        for i in range(len(nodes)):
            nodes[i].coords = (random.uniform(-1, 1), random.uniform(-1, 1))
        edge_list = []
        potential_edges = list(itertools.combinations(range(n), 2))

        while len(edge_list) < m and potential_edges:
            edge = random.choice(potential_edges)
            pair = [nodes[edge[0]], nodes[edge[1]]]
            edge_test = edge_list + [pair]
            intersection_edges = get_intersection_edges(edge_test)
            intersection_graph = nx.Graph()
            intersection_graph.add_node(0)
            intersection_graph.add_edges_from(intersection_edges)
            if nx.is_forest(intersection_graph):
                edge_list.append(pair)
            potential_edges.remove(edge)

        attempt += 1

    edges = [ds.Edge(node_pair) for node_pair in edge_list]
    graph = ds.Graph(nodes, edges)
    return graph


def create_random_graph(n, m, layout):
    """
    Uses networkx algorithm to create a random graph
    :param n: number of nodes
    :param m: number of edges
    :param layout: string describing a networkx layout
    :return: random graph
    """
    nx_graph = nx.gnm_random_graph(n, m)
    pos = set_layout(nx_graph, layout)
    nodes = [ds.Node(node) for node in nx_graph.nodes]
    for i in range(len(nodes)):
        nodes[i].coords = tuple(pos[i])

    nx_edges = [e for e in nx_graph.edges]
    edges = [ds.Edge((nodes[nx_edge[0]], nodes[nx_edge[1]]), color="black") for nx_edge in nx_edges]

    graph = ds.Graph(nodes, edges)
    return graph


def set_layout(nx_graph, layout):
    if layout == "random":
        rand_pos = nx.random_layout(nx_graph)
        pos = nx.rescale_layout(rand_pos, (-1, 1))
    elif layout == "spring":
        pos = nx.spring_layout(nx_graph)
    elif layout == "circle":
        pos = nx.circular_layout(nx_graph)
    elif layout == "kamada":
        pos = nx.kamada_kawai_layout(nx_graph)
    elif layout == "shell":
        pos = nx.shell_layout(nx_graph)
    elif layout == "spectral":
        pos = nx.shell_layout(nx_graph)
    else:
        raise PartialEdgeDrawingException("layout " + layout + " not supported")

    return pos


def create_intersection_graph(source_edges, symmetric):
    """
    Uses pygeos to detect crossings and form an intersection graph accordingly
    :param source_edges: edges of source graph
    :param symmetric: determines if content is prepared for SPED or PED
    :return: intersection graph of source
    """
    node_pairs = [edge.nodes for edge in source_edges]
    edge_indexes = get_intersection_edges(node_pairs)

    nodes = [ds.IntersectionNode(i, source_edges[i], symmetric=symmetric) for i in range(len(source_edges))]
    edges = [ds.Edge([nodes[i], nodes[j]]) for (i, j) in edge_indexes]
    intersection_graph = ds.Graph(nodes, edges)
    return intersection_graph


def get_intersection_edges(node_pairs):
    sh_segments = [linestrings([node_pair[0].coords, node_pair[1].coords]) for node_pair in node_pairs]
    edges = []
    for i in range(len(sh_segments)):
        for j in range(i+1, len(sh_segments)):
            if crosses(sh_segments[i], sh_segments[j]):
                edges.append((i, j))
    return edges


def create_content_nodes(intersection_graph, symmetric=False):
    """
    Creates content nodes out of an intersection graph, which can be used for quick access to crossing data
    :param intersection_graph: source for content node creation
    :param symmetric: determines if content is prepared for SPED or PED
    :return: list of content nodes
    """
    content_nodes = [ds.ContentNode(node, symmetric=symmetric) for node in intersection_graph.nodes]
    for edge in intersection_graph.edges:
        intersection_out = edge.nodes[0].intersect(edge.nodes[1])
        content_nodes[edge.nodes[0].index].intersections[edge.nodes[1].index] = intersection_out

        intersection_in = edge.nodes[1].intersect(edge.nodes[0])
        content_nodes[edge.nodes[1].index].intersections[edge.nodes[0].index] = intersection_in
    return content_nodes


def load_graph_from_dicts(node_set, edge_set):
    nodes = []
    for node_dict in node_set:
        node = ds.Node(node_dict["index"])
        node.coords = tuple(node_dict["coordinates"])
        nodes.append(node)
    nodes = sorted(nodes, key=lambda x: x.index)

    edges = []
    for edge_dict in edge_set:
        edge = ds.Edge([nodes[index] for index in edge_dict["incident_nodes"]])
        edges.append(edge)

    graph = ds.Graph(nodes, edges)
    return graph


def load_graph_from_graph_dict(graph_dict):
    try:
        return load_graph_from_dicts(graph_dict["nodes"], graph_dict["edges"])
    except Exception:
        raise PartialEdgeDrawingException("Could not load graph from input")


def load_graph_from_result_dict(result_dict):
    try:
        return load_graph_from_dicts(result_dict["graph"]["node_data"]["nodes"], result_dict["graph"]["edge_data"]["edges"])
    except Exception:
        raise PartialEdgeDrawingException("Could not load graph from input")



