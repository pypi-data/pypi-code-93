import os
from datetime import datetime

from conn_diag.conn_diag.constants import LOG_DIR
from conn_diag.conn_diag.constants import DEFAULT_DELIMITER
from conn_diag.conn_diag.constants import DEFAULT_CHECK_TIMEOUT
from conn_diag.conn_diag.constants import DEFAULT_LINE_SEPARATOR


def group_connections_by_source(connections):
    source_group = dict()
    for conn in connections:
        source_group.setdefault(conn.source, []).append(conn)

    return source_group


def generate_sockets(connections):
    _list = []
    for connection in connections:
        line = connection.destination + DEFAULT_DELIMITER + connection.port
        _list.append(line)
    return DEFAULT_LINE_SEPARATOR.join(_list)


# def get_private_key_path():
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     private_key_path = os.path.join(current_dir, 'src', 'conn_diag')
#     return private_key_path


def is_valid_file(parser, arg):
    if arg.isspace():
        parser.error('Path cannot be empty')
    if not os.path.exists(arg):
        parser.error('File doesn\'t exist')
    if os.stat(path=arg).st_size == 0:
        parser.error('File is empty')
    return arg


def build_bash_command(connections, check_timeout=DEFAULT_CHECK_TIMEOUT):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(current_dir, 'scripts', 'bash_script.sh')
    bash_script_lines = open(script_path).readlines()

    for index, line in enumerate(bash_script_lines):
        if line.startswith('TIMEOUT='):
            bash_script_lines[index] = f'TIMEOUT={check_timeout}'
        elif line.startswith('SOCKETS='):
            sockets_line = generate_sockets(connections=connections)
            bash_script_lines[index] = f'SOCKETS="{sockets_line}"'
        elif line.startswith('DELIMITER='):
            bash_script_lines[index] = f'DELIMITER=\'{DEFAULT_DELIMITER}\''
        elif line.startswith('LINE_SEPARATOR='):
            bash_script_lines[index] = f'LINE_SEPARATOR=\'{DEFAULT_LINE_SEPARATOR}\''

    return '\n'.join(bash_script_lines)


def print_verbose(msg, verbose):
    if verbose is True:
        print(msg)


def logging(title, content):
    date_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    if not os.path.exists(path=LOG_DIR):
        os.makedirs(name=LOG_DIR)

    filename = '{}_{}.log'.format(title, date_time)
    log_file = os.path.join(LOG_DIR, filename)

    with open(log_file, 'w') as f:
        f.write(content)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_success(msg):
    return (f"{bcolors.OKGREEN}{msg}{bcolors.ENDC}")


def print_error(msg):
    return (f"{bcolors.FAIL}{msg}{bcolors.ENDC}")


def print_warning(msg):
    return (f"{bcolors.WARNING}{msg}{bcolors.ENDC}")


def print_pretty_table(data_list, delimiter='\t'):
    lines = []
    # check if list has dictionaries with equal keys
    keys_list = [data_dict.keys() for data_dict in data_list]
    if not all(keys == keys_list[0] for keys in keys_list):
        print('list has dictionaries with different keys')
        return lines

    if not data_list:
        return lines

    # generate formatter with maximum with of each columns
    formatters = []
    for key in keys_list[0]:
        values = [str(key)] + [str(data_dict[key]) for data_dict in data_list]
        max_len = len(max(values, key=len))
        formatters.append('{!s:<' + str(max_len) + '}')
    row_format = delimiter.join(formatters)

    # print table
    lines.append(row_format.format(*keys_list[0]))
    for data_dict in data_list:
        lines.append(row_format.format(*data_dict.values()))

    print('\n'.join(lines))
