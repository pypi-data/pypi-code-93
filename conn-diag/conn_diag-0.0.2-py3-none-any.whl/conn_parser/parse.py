from netrange import dumps_ips
from netrange import dumps_ports
from netrange import exceptions as netrange_e

from conn_diag.conn_parser.models import Connection
from conn_diag.conn_parser.exceptions import ParseError
from conn_diag.conn_parser.constants import DEFAULT_DELIMITER
from conn_diag.conn_parser.constants import DEFAULT_LINE_SEPARATOR
from conn_diag.conn_parser.utilities import validate_file


def parse_connections_from_file(file, delimiter=DEFAULT_DELIMITER, line_separator=DEFAULT_LINE_SEPARATOR):
    connections = []
    file = validate_file(file=file)
    content = open(file=file).read()
    for line in content.split(line_separator):
        if delimiter in line:
            try:
                if line.count(delimiter) == 1:
                    splitted_line = line.split(delimiter)
                    source = '127.0.0.1'
                    destination = dumps_ips(splitted_line[0], line_sep=',')
                    port = dumps_ports(splitted_line[1], line_sep=',')
                    connections.append(Connection(source=source, destination=destination, port=port))
                elif line.count(delimiter) == 2:
                    splitted_line = line.split(delimiter)
                    source = dumps_ips(splitted_line[0], line_sep=',')
                    destination = dumps_ips(splitted_line[1], line_sep=',')
                    port = dumps_ports(splitted_line[2], line_sep=',')
                    connections.append(Connection(source=source, destination=destination, port=port))
            except netrange_e.NetrangeParserError as e:
                raise ParseError(str(e))
    if not connections:
        raise ParseError('No connection was found.')
    return connections


def parse_connections_from_str(_str: str, delimiter=DEFAULT_DELIMITER, line_separator=DEFAULT_LINE_SEPARATOR):
    if not _str:
        raise ParseError('string is empty.')

    connections = []
    for line in _str.split(line_separator):
        if delimiter in line:
            try:
                if line.count(delimiter) == 1:
                    splitted_line = line.split(delimiter)
                    source = '127.0.0.1'
                    destination = dumps_ips(splitted_line[0], line_sep=',')
                    port = dumps_ports(splitted_line[1], line_sep=',')
                    connections.append(Connection(source=source, destination=destination, port=port))
                elif line.count(delimiter) == 2:
                    splitted_line = line.split(delimiter)
                    source = dumps_ips(splitted_line[0], line_sep=',')
                    destination = dumps_ips(splitted_line[1], line_sep=',')
                    port = dumps_ports(splitted_line[2], line_sep=',')
                    connections.append(Connection(source=source, destination=destination, port=port))
                else:
                    raise ParseError(f'Found {_str.count(delimiter)} delimiters \'{delimiter}\' was found in {_str}.')
            except netrange_e.NetrangeParserError as e:
                raise ParseError(str(e))
        else:
            raise ParseError(f'The delimiter \'{delimiter}\' was not found in {_str}.')
    return connections
