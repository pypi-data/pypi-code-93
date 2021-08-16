
import os
import subprocess
import pandas
from concurrent.futures import ThreadPoolExecutor


def inflate_arguments_to_commands(script, argument_configurations):

    commands = []

    for args in argument_configurations:
        cmd = ['python3', script, *args]
        commands.append(cmd)

    return commands


def run_shell_command(cmd):
    returncode = subprocess.Popen(cmd).wait()

    if returncode != 0:
        raise Exception(f'Command \'{cmd}\' failed!')


def run(script, argument_configurations, threads=1):

    assert isinstance(script, str)
    assert os.path.isfile(script), f'Could not find file {script}.'

    assert isinstance(argument_configurations, (list, tuple))
    for args in argument_configurations:

        assert isinstance(args, (list, tuple))
        for arg in args:

            assert isinstance(arg, str)

    commands = inflate_arguments_to_commands(script, argument_configurations)

    with ThreadPoolExecutor(max_workers=threads) as executor:
        future = executor.map(run_shell_command, commands)
    
        for result in future:
            result

    if not os.path.isdir('args_to_db_cache'):
        return

    table = pandas.read_pickle('data.pkl') if os.path.isfile('data.pkl') else None

    for filename in os.listdir('args_to_db_cache'):

        row = pandas.read_pickle(f'args_to_db_cache/{filename}')

        if table is None:
            table = row
        else:
            table = table.append(row, verify_integrity=True)
        
    table.to_pickle('data.pkl')
    table.to_csv('data.csv')