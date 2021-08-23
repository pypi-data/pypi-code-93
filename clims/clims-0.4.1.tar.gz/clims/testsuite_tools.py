from clims.prepare_submission import write_submission_file
from clims.cli.configure import get_config_value
from ase.calculators.aims import Aims
from ase.io import read, write
from pathlib import Path
import itertools
import json


def generate_testsuite(calc_set):
    keys = []
    values = []

    for key, value in calc_set.items():
        if isinstance(value, list):
            length = len(value)
        else:
            length = 1
            value = [value]
        values.append(value)
        keys.append([key] * length)

    keys_product = itertools.product(*keys)
    values_product = itertools.product(*values)

    calcs = []
    for i in zip(keys_product, values_product):
        dict = {}
        for key, value in zip(*i):
            dict[key] = value
        calcs.append(dict)

    structure = read("geometry.in", format="aims")
    dir_list = []
    for i, c in enumerate(calcs):
        calc_dir = f"{i:03}"
        calc = Aims(**c)
        calc.directory = calc_dir
        calc.write_input(structure)
        with open(calc_dir + "/calculator.json", "w") as calc_file:
            json.dump(c, calc_file)
        submission_params = get_submission_params(c)
        write_submission_file(*submission_params, path=calc_dir)
        dir_list.append(calc_dir)
    write_submit_all(dir_list)

def write_submit_all(dir_list):
    dir_list_str = " ".join(dir_list)
    submit_command = get_config_value('submit_command')
    if "./" == submit_command:
        space = ''
    else:
        space = ' '
    print(dir_list_str)
    submit_all_str = '\n'.join((
        f'for i in  {dir_list_str}',
        'do',
        '    cd $i',
        f'    {submit_command}{space}submit.sh',
        '    cd ..',
        'done'
    ))
    with open('submit_all.sh','w') as submit_all:
        submit_all.write(submit_all_str)


def get_submission_params(c):
    if "outfilename" in c:
        output_name = c["outfilename"]
    else:
        output_name = get_config_value("output_name")

    if "aims_command" in c:
        command_split = c["aims_command"].split(" ")
        if len(command_split) == 2:
            mpi_command = command_split[0]
            aims_executable = command_split[1]
        elif len(command_split) == 1:
            mpi_command = ""
            aims_executable = command_split[0]
        else:
            print("Unexpected format for 'aims_command'.")
            print("Expected: <mpi_command> <aims_executable>")
            print("Or: <aims_executable>")
            return
    else:
        mpi_command = get_config_value("mpi_command")
        aims_executable = get_config_value("aims_executable")

    error_name = get_config_value("error_name")
    header = get_config_value("submission_header")

    return [header, mpi_command, aims_executable, output_name, error_name]


def get_directory_info():
    p = Path(".")
    dir_list = [x for x in p.iterdir() if x.is_dir()]

    calcs = {}
    for x in dir_list:
        calc_json = x / "calculator.json"
        if calc_json.exists():
            with open(calc_json, "r") as calc_file:
                c = json.load(calc_file)
            calcs[x.as_posix()] = c

    sorted_calcs = {
        k: v for k, v in sorted(calcs.items(), key=lambda item: int(item[0]))
    }

    for k, v in sorted_calcs.items():
        s = ""
        for ck, cv in v.items():
            s += f"{ck:8}: {str(cv):8}, "
        print(k, ":", s)
