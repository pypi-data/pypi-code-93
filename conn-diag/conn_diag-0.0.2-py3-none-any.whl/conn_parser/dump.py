from conn_diag.conn_parser.core import range_connections
from conn_diag.conn_parser.core import unrange_connections
from conn_diag.conn_parser.utilities import validate_connections


def dump_connections(connections, _range=False, unrange=False, short=False, cidr=False):
    connections = validate_connections(connections=connections)
    if _range:
        connections = range_connections(connections=connections, short=short, cidr=cidr)
    elif unrange:
        connections = unrange_connections(connections=connections, cidr=cidr)
    return connections
