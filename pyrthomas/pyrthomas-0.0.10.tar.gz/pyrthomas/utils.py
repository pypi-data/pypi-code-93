import itertools
from typing import FrozenSet, Dict

import networkx as nx
from networkx.classes.reportviews import EdgeView


def all_subsets(items: FrozenSet):
    return itertools.chain(
        *map(lambda x: itertools.combinations(items, x), range(0, len(items) + 1)))


def create_node_from_dict(item: Dict) -> str:
    return ','.join(map(str, item.values()))


def get_weight(edge: EdgeView, absolute=False) -> int:
    weight = edge[2]['weight']
    if type(weight) == str:
        weight = int(weight)
    return abs(weight) if absolute else weight


def get_max_weighted_edge_threashold(network: nx.DiGraph, node: str) -> int:
    edges_from_node = network.edges(node, data=True)
    max_weighted_edge = max(edges_from_node, key=lambda x: get_weight(x, True))
    return get_weight(max_weighted_edge, True)
