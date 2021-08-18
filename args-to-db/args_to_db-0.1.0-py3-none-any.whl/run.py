import subprocess
from concurrent.futures import ThreadPoolExecutor
from os import listdir
from os.path import isfile, isdir
from shutil import rmtree
import pandas


def run_shell_command(cmd):
    returncode = subprocess.Popen(cmd).wait()

    if returncode != 0:
        raise Exception(f'Command \'{cmd}\' failed!')


def _run_commands(commands, threads):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(run_shell_command, commands)

        for _ in future:
            pass


def _read_data_file(data_file):
    return pandas.read_pickle(data_file) if isfile(data_file) else None


def _combine_output_data(data_file, cache_dir):
    table = _read_data_file(data_file)

    for filename in listdir(cache_dir):

        row = pandas.read_pickle(f'{cache_dir}/{filename}')

        if table is None:
            table = row
        else:
            if row.iloc[0].name in table.index:
                table = table.update(row)
            else:
                table = table.append(row, verify_integrity=True)

    return table


def run(commands, threads=1, data_file='data.pkl', write_data=True,
        remove_cache_dir=True):
    cache_dir = 'args_to_db_cache'
    assert isinstance(threads, int)
    assert isinstance(data_file, str)
    assert isinstance(write_data, bool)
    assert isinstance(cache_dir, str)
    assert isinstance(remove_cache_dir, bool)
    assert isinstance(commands, (list, tuple))
    for args in commands:
        assert isinstance(args, (list, tuple))
        for arg in args:
            assert isinstance(arg, str)

    _run_commands(commands, threads)

    if not isdir(cache_dir):
        return None

    table = _combine_output_data(data_file, cache_dir)

    if remove_cache_dir:
        rmtree(cache_dir)

    if write_data:
        table.to_pickle(data_file)
        table.to_csv(f'{data_file}.csv')

    return table
