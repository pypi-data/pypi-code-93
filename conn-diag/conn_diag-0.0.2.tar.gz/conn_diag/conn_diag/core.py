from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from conn_diag.conn_diag.result import SSHResultCollection

from conn_diag.conn_diag.utilities import print_verbose
from conn_diag.conn_diag.utilities import build_bash_command
from conn_diag.conn_diag.utilities import group_connections_by_source

from conn_diag.conn_diag.connection_manager import ssh_connect
from conn_diag.conn_diag.connection_manager import local_connect

from conn_diag.conn_diag import exceptions

from conn_diag.conn_parser.dump import dump_connections


def dumps_cmd(connections, check_timeout):
    lines = []
    unranged_connections = dump_connections(connections=connections, unrange=True)
    connections_by_source = group_connections_by_source(connections=unranged_connections)
    for source, connections in connections_by_source.items():
        command = build_bash_command(connections=connections, check_timeout=check_timeout)
        header = f'>>> {source} <<<'
        lines.append(header)
        lines.append(command)
        lines.append('\n')
    return '\n'.join(lines)


def check_connectivity(connections, check_timeout, ssh_timeout, verbose, ssh_username, ssh_password=None, ssh_key=None, cidr=False, parallel=False):
    unranged_connections = dump_connections(connections=connections, unrange=True, cidr=True)
    connections_by_source = group_connections_by_source(connections=unranged_connections)

    if parallel:
        # build parallel_checker parameters
        args = [(host, connections, ssh_timeout, check_timeout, verbose, ssh_username, ssh_password, ssh_key) for host, connections in connections_by_source.items()]
        with ThreadPool(processes=cpu_count()) as pool:
            ssh_result_list = pool.starmap(func=run_checker, iterable=args)
        ssh_result_col = SSHResultCollection(data=ssh_result_list)
        return ssh_result_col

    ssh_results = []
    for host, connections in connections_by_source.items():
        ssh_result = run_checker(host=host, connections=connections, ssh_timeout=ssh_timeout, check_timeout=check_timeout, verbose=verbose, ssh_username=ssh_username, ssh_password=ssh_password, ssh_key=ssh_key)
        ssh_results.append(ssh_result)
    return SSHResultCollection(data=ssh_results)


def run_checker(host, connections, ssh_timeout, check_timeout, verbose, ssh_username, ssh_password=None, ssh_key=None):
    print_verbose('Connecting to {} ...'.format(host), verbose)
    command = build_bash_command(connections=connections, check_timeout=check_timeout)
    if host == '127.0.0.1':
        client_result = local_connect(command=command)
    else:
        client_result = ssh_connect(host=host, command=command, ssh_timeout=ssh_timeout, ssh_username=ssh_username, ssh_password=ssh_password, ssh_key=ssh_key)
    return client_result
