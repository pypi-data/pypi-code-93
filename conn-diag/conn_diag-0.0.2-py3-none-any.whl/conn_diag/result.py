from netrange import dump_ips
from conn_diag.conn_diag.constants import DEFAULT_DELIMITER
from conn_diag.conn_diag.connectivity import Connectivity
from conn_diag.conn_diag.connectivity import ConnectivityCollection
from conn_diag.conn_diag.utilities import print_pretty_table


class SSHResult:
    def __init__(self, unreachable, unauthorized, failed, host, stdout, stderr, failed_msg=None):
        self.host = host
        self.failed = failed
        self.failed_msg = failed_msg
        self.unreachable = unreachable
        self.unauthorized = unauthorized
        self.stdout_lines = [line.strip() for line in stdout.readlines() if stdout] if stdout else None
        self.stderr_lines = [line.strip() for line in stderr.readlines() if stderr] if stderr else None

    @property
    def connected(self):
        return self.unreachable is False and self.unauthorized is False and self.failed is False

    def stderr_msg(self):
        if not self.stdout_lines:
            return None
        return self.stderr_lines[0]

    def connectivity_list(self):
        _list = list()
        for line in self.stdout_lines:
            splitted_line = line.split(sep=DEFAULT_DELIMITER, maxsplit=3)
            status = splitted_line[0]
            destination = splitted_line[1]
            port = splitted_line[2]
            details = repr(splitted_line[3])
            _list.append(Connectivity(status=status, source=self.host, destination=destination, port=port, details=details))
        return _list


class SSHResultCollection:
    def __init__(self, data: [SSHResult]):
        self._data: [SSHResult] = data

    def __iter__(self):
        for result in self._data:
            yield result

    def connectivity_collection(self) -> ConnectivityCollection:
        connectivity_list = []
        for ssh_result in self.connected_data():
            connectivity_list.extend(ssh_result.connectivity_list())
        return ConnectivityCollection(data=connectivity_list)

    # boolean

    def all_connected(self) -> bool:
        return all(ssh_result.connected for ssh_result in self._data)

    def partially_connected(self) -> bool:
        return any(ssh_result.connected for ssh_result in self._data)

    def has_unreachable_data(self) -> bool:
        return any([ssh_result.unreachable for ssh_result in self._data])

    def has_unauthorized_data(self) -> bool:
        return any([ssh_result.unauthorized for ssh_result in self._data])

    def has_failed_data(self) -> bool:
        return any([ssh_result.failed for ssh_result in self._data])

    def has_connected_data(self) -> bool:
        return any([ssh_result.connected for ssh_result in self._data])

    # Filter data

    def unreachable_data(self) -> [SSHResult]:
        return [ssh_result for ssh_result in self._data if ssh_result.unreachable]

    def unauthorized_data(self) -> [SSHResult]:
        return [ssh_result for ssh_result in self._data if ssh_result.unauthorized]

    def failed_data(self) -> [SSHResult]:
        return [ssh_result for ssh_result in self._data if ssh_result.failed]

    def connected_data(self) -> [SSHResult]:
        return [ssh_result for ssh_result in self._data if ssh_result.connected]

    def dumps_log(self, with_connectivity=False):
        lines = []

        for ssh_result in self.connected_data():
            lines.append('ssh result: {} {}'.format('connected', ssh_result.host))

        for ssh_result in self.unreachable_data():
            lines.append('ssh result: {} {}'.format('unreachable', ssh_result.host))

        for ssh_result in self.unauthorized_data():
            lines.append('ssh result: {} {}'.format('unauthorized', ssh_result.host))

        for ssh_result in self.failed_data():
            lines.append('ssh result: {} {} {}'.format('failed', ssh_result.host, ssh_result.failed_msg or ssh_result.stderr_msg()))

        if with_connectivity is True:
            lines.append('\n' + self.connectivity_collection().dumps_log())

        return '\n'.join(lines)

    def print_table(self, _range=False, short=False):
        data_list = []

        if self.has_unreachable_data():
            unreachable_hosts = [ssh_result.host for ssh_result in self.unreachable_data()]
            for host in dump_ips(*unreachable_hosts, _range=_range, short=short):
                data_list.append({
                    'SOURCE': host,
                    'DESTINATION': 'N/A',
                    'PORT': 'N/A',
                    'STATUS': 'unreachable',
                })

        if self.has_unauthorized_data():
            unauthorized_hosts = [ssh_result.host for ssh_result in self.unauthorized_data()]
            for host in dump_ips(*unauthorized_hosts, _range=_range, short=short):
                data_list.append({
                    'SOURCE': host,
                    'DESTINATION': 'N/A',
                    'PORT': 'N/A',
                    'STATUS': 'unauthorized',
                })

        if self.has_failed_data():
            group = dict()
            for data in self.failed_data():
                group.setdefault(data.failed_msg, []).append(data.host)

            for failed_msg, hosts in group.items():
                for host in dump_ips(*hosts, _range=_range, short=short):
                    data_list.append({
                        'SOURCE': host,
                        'DESTINATION': 'N/A',
                        'PORT': 'N/A',
                        'STATUS': 'failed: {}'.format(failed_msg),
                    })

        data_list += self.connectivity_collection().dump_table(_range=_range, short=short)
        print_pretty_table(data_list=data_list, delimiter='  ')
