
import os
import subprocess
import pandas
from concurrent.futures import ThreadPoolExecutor


# def inflate_arguments_to_commands(script, argument_configurations):

#     commands = []

#     for args in argument_configurations:
#         cmd = ['python3', script, *args]
#         commands.append(cmd)

#     return commands


def run_shell_command(cmd):
    returncode = subprocess.Popen(cmd).wait()

    if returncode != 0:
        raise Exception(f'Command \'{cmd}\' failed!')


def run(commands, threads=1, data_file='data.pkl', cache_dir='args_to_db_cache'):

    assert isinstance(commands, (list, tuple))
    for args in commands:
        assert isinstance(args, (list, tuple))
        for arg in args:
            assert isinstance(arg, str)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(run_shell_command, commands)

        for result in future:
            result

    if not os.path.isdir(cache_dir):
        return

    table = pandas.read_pickle(data_file) if os.path.isfile(data_file) else None

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
    table.to_csv(f'{data_file}.csv') #TODO