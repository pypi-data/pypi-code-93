import netrange
from conn_diag.conn_parser.models import Connection
from conn_diag.conn_parser.constants import DEFAULT_DELIMITER
from conn_diag.conn_parser.constants import DEFAULT_LINE_SEPARATOR


def unrange_connections(connections, cidr=False):
    conn_tree = generate_conn_tree(connections, cidr=cidr)
    for port, value in conn_tree.items():
        for destination, sources in value.items():
            for source in sources:
                yield Connection(source=source, destination=destination, port=port)


def range_connections(connections, short=False, cidr=False):
    # step 1
    # { 'port': ['src|dst',], ... }
    tmp_conn_tree = dict()
    for port, dst_dict in generate_conn_tree(connections).items():
        tmp_src_dict = dict()
        for destination, sources in dst_dict.items():
            shorter_ranged_sources = netrange.dumps_ips(*sources, _range=True, line_sep=',', short=short, cidr=cidr)
            tmp_src_dict.setdefault(shorter_ranged_sources, []).append(destination)

        src_dst_keys = list()
        for src, dsts in tmp_src_dict.items():
            shorter_ranged_dsts = netrange.dumps_ips(*dsts, _range=True, line_sep=',', short=short, cidr=cidr)
            src_dst_key = src + DEFAULT_DELIMITER + shorter_ranged_dsts
            src_dst_keys.append(src_dst_key)

        tmp_conn_tree[port] = src_dst_keys

    # step 2
    # { 'src|dst||src|dst': [port,], ... }
    tmp_keys_dict = dict()
    for port, value in tmp_conn_tree.items():
        tmp_keys_dict.setdefault(DEFAULT_LINE_SEPARATOR.join(value), []).append(port)

    # step 3
    # { 'src|dst': [ports], ... }
    tmp_key_dict = dict()
    for keys, ports in tmp_keys_dict.items():
        for src_dst in keys.split(DEFAULT_LINE_SEPARATOR):
            tmp_key_dict.setdefault(src_dst, []).extend(ports)

    # step 4
    # ['scr|dst|port', ...]
    conn_lines = list()
    for key, ports in tmp_key_dict.items():
        ranged_ports = netrange.dumps_ports(*ports, _range=True, line_sep=',')
        for conn in key.split(DEFAULT_LINE_SEPARATOR):
            conn_lines.append(conn + DEFAULT_DELIMITER + ranged_ports)

    for line in conn_lines:
        split = line.split(DEFAULT_DELIMITER)
        yield Connection(source=split[0], destination=split[1], port=split[2])


def generate_conn_tree(connections, cidr=False):
    connections_tree = dict()
    for connection in connections:
        sources = netrange.dump_ips(connection.source, unrange=True, cidr=cidr)
        destinations = netrange.dump_ips(connection.destination, unrange=True, cidr=cidr)
        ports = netrange.dump_ports(connection.port, unrange=True)

        # port: destination: [source,]
        for port in ports:
            for destination in destinations:
                for source in sources:
                    connections_tree.setdefault(port, dict()).setdefault(destination, list()).append(source)

    return connections_tree


def repr_connections(connections, delimiter, line_separator):
    lines = []
    sorted_connections = sorted(connections, key=lambda i: (i.source, i.destination, i.port))
    for connection in sorted_connections:
        line = connection.source + delimiter + connection.destination + delimiter + connection.port
        lines.append(line)

    if line_separator == r'\n':
        return '\n'.join(lines)

    return line_separator.join(lines)
