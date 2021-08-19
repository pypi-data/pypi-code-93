import networkx as nx
from networkx import MultiDiGraph

from pyrthomas.cytoscape import read_sif, write_sif


class NetworkService:
    network: nx.DiGraph

    def __init__(self) -> None:
        self.network = nx.DiGraph()

    def add_node(self, node):
        self.network.add_node(node.id, min=node.min, max=node.max)

    def add_edge(self, edge):
        self.network.add_edge(edge.source, edge.target, weight=edge.weight)

    def get_nodes(self):
        return list(self.network.nodes)

    def clear(self):
        self.network.clear()

    def get_edges(self):
        return list(self.network.edges)

    def import_graphml(self, file):
        self.network = nx.read_graphml(file)

    def import_dot(self, file):
        dot = nx.drawing.nx_pydot.read_dot(file)
        is_multi_graph = isinstance(dot, MultiDiGraph)
        for source, target, attr in dot.edges(data=True):
            converted_weight = int(attr.get("weight", "0").replace('"', ""))
            if is_multi_graph:
                dot[source][target][0]["weight"] = converted_weight
            dot[source][target][0]["weight"] = converted_weight
        self.network = dot

    def import_sif(self, file):
        self.network = read_sif(file)

    def export_graphml(self, file):
        nx.write_graphml(self.network, file, prettyprint=True)

    def export_dot(self, file):
        nx.drawing.nx_pydot.write_dot(self.network, file)

    def export_sif(self, file):
        write_sif(self.network, file)
