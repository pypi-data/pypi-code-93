from typing import Set, Tuple, Dict, List


DEFAULT_EDGE_TYPE = "attack"


class Node:
    """A node in a directed probabilistic graphical model"""
    __default_node_prefix = ""  # for nodes without a given name, the name is this prefix followed by the node's ID

    def __init__(self, node_id, name: str = ""):
        self.id = node_id
        self.dpgm = None
        if not name:
            self.name = self.__default_node_prefix + str(self.id)
        else:
            self.name = name

        self.all_parents: Set[Node] = set()
        self.parents: Dict[str, Set[Node]] = dict()  # parents by edge type
        self.parents_edges = dict()  # Dict[Node.id, Edge]

        self.all_children: Set[Node] = set()
        self.children:  Dict[str, Set[Node]] = dict()  # children by edge type
        self.children_edges = dict()  # Dict[Node.id, Edge]

        self.value = None  # float
        self.interval = None  # Tuple[float, float]

    def add_value(self, value: float):
        self.value = value

    def add_interval(self, interval: Tuple[float, float]):
        self.interval = interval

    def is_initial(self):
        return len(self.all_parents) == 0

    def get_parents(self, edge_type=DEFAULT_EDGE_TYPE):
        if edge_type in self.parents.keys():
            return self.parents[edge_type]
        else:
            return set()

    def get_children(self, edge_type=DEFAULT_EDGE_TYPE):
        if edge_type in self.children.keys():
            return self.children[edge_type]
        else:
            return set()

    def get_parent_edge(self, node_from):
        if node_from.id in self.parents_edges:
            return self.parents_edges[node_from.id]
        else:
            raise ValueError("Node '" + self.name + "' has no parent edge from node '" + node_from.name + "'.")

    def get_child_edge(self, node_to):
        if node_to.id in self.children_edges:
            return self.children_edges[node_to.id]
        else:
            raise ValueError("Node '" + self.name + "' has no child edge to node '" + node_to.name + "'.")

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return self.name
        # return "Node(" + self.id + ": " + self.name + ")"

    def __str__(self):
        return self.name


class Edge:
    """A directed edge in a directed probabilistic graphical model"""
    __default_label_prefix = "s"  # default label "s_A_B" for an edge from node A to node B

    def __init__(self, node_from, node_to, label="", edge_type=DEFAULT_EDGE_TYPE):
        self.node_from: Node = node_from
        self.node_to: Node = node_to
        self.label: str = label
        self.value = None
        self.interval = None
        self.type = edge_type  # e.g. "attack", "support"
        if self.label == "":
            self.label = self.__default_label_prefix + '_' + self.node_from.name + '_' + self.node_to.name

        self.node_from.all_children.add(self.node_to)
        if self.type not in self.node_from.children.keys():
            self.node_from.children[self.type] = set()
        self.node_from.children[self.type].add(self.node_to)
        self.node_from.children_edges[node_to.id] = self

        self.node_to.all_parents.add(self.node_from)
        if self.type not in self.node_to.parents.keys():
            self.node_to.parents[self.type] = set()
        self.node_to.parents[self.type].add(self.node_from)
        self.node_to.parents_edges[node_from.id] = self

    def add_value(self, value: float):
        self.value = value

    def add_interval(self, interval: Tuple[float, float]):
        self.interval = interval

    def __str__(self):
        return str(self.node_from) + "->" + str(self.node_to)


class DPGM:
    """A class representing a directed probabilistic graphical model"""
    def __init__(self, name: str = "", path: str = ""):
        self.name = name
        self.path = path
        self.nodes: Dict[str, Node] = dict()
        self.all_edges: Set[Edge] = set()
        self.edges: Dict[str, Set[Edge]] = dict()  # edges by type

    def add_node(self, node: Node):
        self.nodes[node.id] = node
        node.dpgm = self

    def add_edge(self, edge: Edge):
        self.all_edges.add(edge)
        if edge.type not in self.edges.keys():
            self.edges[edge.type] = set()
        self.edges[edge.type].add(edge)

    def get_node(self, node_id: str):
        return self.nodes[node_id]

    def get_nodes(self):
        return self.nodes.values()

    def get_node_by_name(self, name: str):
        for node in self.get_nodes():
            if node.name == name:
                return node
        raise ValueError("No node with name '" + name + "' found.")

    def get_initial_nodes(self):
        return set([node for node in self.nodes.values() if node.is_initial()])

    def get_edges(self):
        return self.all_edges

    def __str__(self):
        s = str(self.name)
        s += "\n" + str(len(self.nodes)) + " nodes: " + ', '.join([node.name for node in self.nodes.values()])
        s += "\n" + str(len(self.all_edges)) + " edges: " \
             + ', '.join([edge.node_from.name + '->' + edge.node_to.name for edge in self.all_edges])
        return s


def parents(nodes: List[Node], edge_type=DEFAULT_EDGE_TYPE) -> List[Node]:
    """
    Return the union of the nodes' parents w.r.t. to a an edge type
    :param nodes: A list of nodes
    :param edge_type: The type of the considered edges
    :return: The sorted list of the parents
    """
    parents_list = []
    for node in nodes:
        parents_list.extend([p for p in node.get_parents(edge_type) if p not in parents_list])
    parents_list.sort()
    return parents_list
