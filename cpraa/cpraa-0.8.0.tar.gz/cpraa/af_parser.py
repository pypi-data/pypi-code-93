import os

import DPGM


def parse_interval(string, obj):
    """Parse a value or an interval and add it to either the node or edge passed as obj.
    '0.2:0.8' -> add interval (0.2, 0.8)
    '0.5' -> add value 0.5
    'ABC' -> print warning, add nothing"""

    split = string.split(':')

    p1 = float(split[0])
    if len(split) == 1:
        obj.add_value(p1)
    elif len(split) == 2:
        p2 = float(split[1])
        obj.add_interval((p1, p2))
    else:
        print("Warning: Ill-formed probability '" + string + "'")


def parse_tgf(path: str):
    """
    Parse a file in (extended) trivial graph format. Returns a directed probabilistic graphical model (DPGM) object.
    """
    with open(path, "r") as file:
        tgf_file = file.read()

    base = os.path.basename(path)  # 'AFs\simple_odd_cycle.tgf' -> 'simple_odd_cycle.tgf'
    (name, extension) = os.path.splitext(base)  # name: 'simple_odd_cycle', extension: '.tgf'
    dpgm = DPGM.DPGM(name, path)

    # remove blank lines and line comments (starting with ';')
    lines = tgf_file.split('\n')
    node_declarations = []
    edge_declarations = dict()  # from edge_type to list of edge declarations
    start_edges = False
    current_edge_type = None
    for line in lines:
        split = line.split(";")
        if split[0].startswith("#"):
            start_edges = True
            current_edge_type = split[0].strip('#').strip()
            edge_declarations[current_edge_type] = []
            continue
        if split[0].strip() != "":
            if start_edges:
                edge_declarations[current_edge_type].append(split[0])
            else:
                node_declarations.append(split[0])

    # parse nodes and edges
    for d in node_declarations:
        # format: <node_id> [<node_name>] [<node_prob>|<node_prob_min>:<node_prob_max>]
        tokens = [token for token in d.split(' ') if token.strip()]
        node_id = tokens[0]
        node = DPGM.Node(node_id)

        if len(tokens) > 1:
            next_token = tokens[1]
            if next_token[0].isalpha():  # <node_name> is given
                node.name = next_token
                if len(tokens) > 2:
                    next_token = tokens[2]
                else:
                    next_token = None
            if next_token:
                parse_interval(next_token, node)
        dpgm.add_node(node)

    for edge_type in edge_declarations.keys():
        for d in edge_declarations[edge_type]:
            tokens = [token for token in d.split(' ') if token.strip()]
            node_from_id = tokens[0]
            node_from = dpgm.get_node(node_from_id)
            node_to_id = tokens[1]
            node_to = dpgm.get_node(node_to_id)
            if edge_type is not "":
                edge = DPGM.Edge(node_from, node_to, edge_type=edge_type)
            else:
                edge = DPGM.Edge(node_from, node_to)
            if len(tokens) > 2:
                next_token = tokens[2]
                if next_token[0].isalpha():
                    edge.label = next_token
                    if len(tokens) > 3:
                        next_token = tokens[3]
                    else:
                        next_token = None
                if next_token:
                    parse_interval(next_token, edge)
            dpgm.add_edge(edge)

    return dpgm
