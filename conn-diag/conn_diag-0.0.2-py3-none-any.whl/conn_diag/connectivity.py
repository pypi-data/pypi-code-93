from conn_diag.conn_parser.models import Connection
from conn_diag.conn_parser.dump import dump_connections
from conn_diag.conn_diag.utilities import print_success
from conn_diag.conn_diag.utilities import print_pretty_table


class Connectivity:
    __slots__ = ['status', 'source', 'destination', 'port', 'details']

    def __init__(self, status, source, destination, port, details):
        self.status = status
        self.source = source
        self.destination = destination
        self.port = port
        self.details = details

    def is_connected(self):
        return self.status == 'connected'

    def is_timed_out(self):
        return self.status == 'timeout'

    def is_refused(self):
        return self.status == 'refused'

    # def is_other(self):
    #     return self.status == 'other'

    def connection(self):
        return Connection(source=self.source, destination=self.destination, port=self.port)


class ConnectivityCollection:

    def __init__(self, data: [Connectivity]):
        self._data: [Connectivity] = data

    def all_connected(self) -> bool:
        return all(connectivity.is_connected() for connectivity in self._data)

    def all_connected_or_refused(self) -> bool:
        return all(connectivity.is_connected() or connectivity.is_refused() for connectivity in self._data)

    def has_connected(self) -> bool:
        return any(connectivity.is_connected() for connectivity in self._data)

    def has_timeout(self) -> bool:
        return any(connectivity.is_timed_out() for connectivity in self._data)

    def has_refused(self) -> bool:
        return any(connectivity.is_refused() for connectivity in self._data)

    # def has_other(self) -> bool:
    #     return any(connectivity.is_other() for connectivity in self._data)

    # Filter data

    def connected_data(self) -> [Connectivity]:
        return [connectivity for connectivity in self._data if connectivity.is_connected()]

    def refused_data(self) -> [Connectivity]:
        return [connectivity for connectivity in self._data if connectivity.is_refused()]

    def timed_out_data(self) -> [Connectivity]:
        return [connectivity for connectivity in self._data if connectivity.is_timed_out()]

    # def other_data(self) -> [Connectivity]:
    #     return [connectivity for connectivity in self._data if connectivity.is_other()]

    def group_connections_by_status(self):
        group = dict()
        for connectivity in self._data:
            group.setdefault(connectivity.status, []).append(connectivity.connection())
        return group

    # dump string

    def dumps_log(self):
        lines = list()
        group = dict()

        for connectivity in self._data:
            group.setdefault(connectivity.status, []).append(connectivity)

        for _, connectivity_list in group.items():
            for connectivity in connectivity_list:
                connection = connectivity.connection()
                msg = '{} {} -> {}:{} {}'.format(connectivity.status, connection.source, connection.destination, connection.port, connectivity.details)
                lines.append(msg)

        return '\n'.join(lines)

    def dumps_repr(self, _range=False):
        lines = list()
        group = dict()

        for connectivity in self._data:
            group.setdefault(connectivity.status, []).append(connectivity.connection())

        for status, connections in group.items():
            connections = dump_connections(connections=connections, unrange=not _range, _range=_range, short=_range)
            for connection in connections:
                msg = '{} -> {}:{} ({})'.format(connection.source, connection.destination, connection.port, status)
                lines.append(msg)
        return '\n'.join(lines)

    def __repr__(self):
        return self.dumps_repr()

    def dump_table(self, _range=False, short=False):
        lines = list()
        for status, connections in self.group_connections_by_status().items():
            for connection in dump_connections(connections=connections, unrange=not _range, _range=_range, short=short):
                lines.append({
                    'SOURCE': connection.source,
                    'DESTINATION': connection.destination,
                    'PORT': connection.port,
                    'STATUS': status,
                })

        return lines
