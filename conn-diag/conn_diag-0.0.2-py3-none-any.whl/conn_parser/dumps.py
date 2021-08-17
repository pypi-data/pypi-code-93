from conn_diag.conn_parser.constants import DEFAULT_DELIMITER
from conn_diag.conn_parser.constants import DEFAULT_LINE_SEPARATOR
from conn_diag.conn_parser.core import repr_connections
from conn_diag.conn_parser.core import range_connections
from conn_diag.conn_parser.core import unrange_connections
from conn_diag.conn_parser.utilities import validate_connections


def dumps_connections(connections, _range=False, unrange=False, short=False, cidr=False, delimiter=DEFAULT_DELIMITER, line_separator=DEFAULT_LINE_SEPARATOR):
    valid_connections = validate_connections(connections)
    if _range:
        connections = range_connections(connections=valid_connections, short=short, cidr=cidr)
    elif unrange:
        connections = unrange_connections(connections=valid_connections, cidr=cidr)
    return repr_connections(connections=connections, delimiter=delimiter, line_separator=line_separator)
