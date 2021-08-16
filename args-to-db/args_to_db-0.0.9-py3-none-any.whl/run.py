
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import pandas


def valid_commands_structure(commands):
    if not isinstance(commands, (list, tuple)):
        return False

    for args in commands:
        if not isinstance(args, (list, tuple)):
            return False

        for arg in args:
            if not isinstance(arg, str):
                return False

    return True


def run_shell_command(cmd):
    returncode = subprocess.Popen(cmd).wait()

    if returncode != 0:
        raise Exception(f'Command \'{cmd}\' failed!')


def run_commands_in_parallel(commands, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(run_shell_command, commands)

        for _ in future:
            pass


def read_data_file(data_file):
    return pandas.read_pickle(data_file) if os.path.isfile(data_file) else None


def combine_output_data(data_file, cache_dir):
    table = read_data_file(data_file)

    for filename in os.listdir(cache_dir):

        row = pandas.read_pickle(f'{cache_dir}/{filename}')

        if table is None:
            table = row
        else:
            if row.iloc[0].name in table.index:
                table = table.update(row)
            else:
                table = table.append(row, verify_integrity=True)

    table.to_pickle(data_file)
    table.to_csv(f'{data_file}.csv')  # TODO


def run(commands, threads=1, data_file='data.pkl',
        cache_dir='args_to_db_cache'):

    assert valid_commands_structure(commands)

    run_commands_in_parallel(commands, threads)

    exists_output_data = os.path.isdir(cache_dir)
    if not exists_output_data:
        return

    combine_output_data(data_file, cache_dir)
