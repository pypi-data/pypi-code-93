"""
CLI for Lemmings
"""

import os
import click

@click.group()
def cli():
    """
    *Creation of the group that contains all cli commands.*
    """
    pass


@cli.command('run')
@click.argument('workflow', type=str, nargs=1)
@click.option("--status", "-s", type=str, default="start",
              help="Your job status, Expert users only")
@click.option('--yaml', required=False, type=str, default = None,
              help = "Path to .yml file associated with workflow")
@click.option("--parallel", '-p', is_flag=True,
              help="Parallel mode activation, Expert users only")
@click.option("--noverif", is_flag=True)
@click.option("--restart", is_flag=True,
              help="If activated, the last chain will be continued.")
def lemmings_cli(workflow, status, yaml, noverif, restart, parallel):
    """
    This is the command to launch your workflow with Lemmings.
    ' lemmings run {workflow_name} '
    """
    import sys
    import importlib.util
    from lemmings_hpc.cli_helper import (
        get_workflow_py,
        get_workflow_yml,
        custom_name,
        check_cpu_input,
    )

    from lemmings_hpc.chain.database import Database
    from lemmings_hpc.chain.machine import Machine
    from lemmings_hpc.chain.chain import Lemmings
    from lemmings_hpc.chain.lemmingjob_base import LemmingsStop
    from lemmings_hpc.chain.chain import _handle_exception

    #pylint: disable=too-many-function-args

    #get path of the WorkFlow desired
    if workflow.lower().endswith(('.yml', '.py')):
        raise ValueError("A workflow name can't contain an extension like '.yml', "
                         + "please enter a valid workflow name. ")
#                         + "You can use the 'lemmings info workflows' "
#                        + "command to see available workflows")

    try:
        wf_py_path = get_workflow_py(workflow)
    except EnvironmentError as error:
        print("EnivironmentError", error)
        return

    try:
        if yaml is not None:
            wf_yml_path = get_workflow_yml(yaml.split('.yml')[0], user_yaml = True)
        else:
            wf_yml_path = get_workflow_yml(workflow)
    except FileNotFoundError as error:
        print("FileNotFoundError: \n", error)
        return

    database = Database()
    

    # if we are at a restart we wish to continue the exisiting chain
    # therefore we will overwrite the status to something else
    # a new loop must also be initiated
    if restart:
        status = "restart"
        database.initialise_new_loop()
        database.update_current_loop('restart',
                                           True)

    if status == "start":
        chain_name = custom_name()
    else:
        chain_name = database.latest_chain_name.split("_")[-1]
        # database.initialise_new_loop()



    try:
        machine = Machine(path_yml=wf_yml_path,
                          chain_name=chain_name)
    # except FileNotFoundError as file_error:
    #     print("\nThe initialisation of Lemmings went wrong:\n", file_error)
    except EnvironmentError as excep:
        print("\nThe initialisation of Lemmings went wrong:\n")
        print("   -->  " + str(excep) + '\n')
        return
        #sys.exit() # look into replacing this with return!
    except KeyError as excep:
        print("\nThe initialisation of Lemmings went wrong:\n", excep)
        return
        #sys.exit()

    # put status back to start so lemmings know what to do in the chain
    if restart:
        status = "start"

    if status == "start":
        try:
            if not restart:
                database.initialise_new_chain(machine.job_name)
                print("Starting chain named " + machine.job_name)
            else:
                print("Continue chain named " + machine.job_name)
            if not noverif:
                check_cpu_input(machine.user.cpu_limit)
        except ValueError as excep:
            print("\nThe initialisation of Lemmings went wrong:\n", excep)
            return
        except AttributeError as excep:
            print("\nThe initialisation of Lemmings went wrong:\n AttributeError: keyword cpu_limit not defined in .yml file\n")
            return



    loop_count = database.count

    if wf_py_path is not None:
        spec = importlib.util.spec_from_file_location("module.name",
                                                      wf_py_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        lemming_job = module.LemmingJob(workflow,
                                        machine,
                                        loop_count,
                                        status=status,
                                        cpu_limit=machine.user.cpu_limit)


    lemmings = Lemmings(lemming_job)

    if parallel:
        try:
            lemmings.create_replicate_workflows()
        except LemmingsStop as stop:
            _handle_exception(lemmings.lemmings_job,lemmings.database,
                            stop, lemmings_stop= True)
            print(stop)
            sys.exit()


    lemmings.run()

@cli.command('kill')
def lemmings_kill():
    """Kill the current job and pjob of lemmings"""
    import os
    import yaml
    from lemmings_hpc.chain.database import Database
    import subprocess as sbp

    database = Database()
    # chain_name = database.latest_chain_name

    env_var = dict(os.environ)
    try:
        machine_path = env_var["LEMMINGS_MACHINE"]
    except KeyError:
        print("No LEMMINGS_MACHINE environment variable specified")
        return

    with open(machine_path) as fin:
        machine_dict = yaml.load(fin, Loader=yaml.SafeLoader)

    try:
        job_id = database.get_loop_val('job_id', 0) #latest loop
        pjob_id = database.get_loop_val('pjob_id', 0)
    except KeyError:
        print("No job and / or post job to kill in current database loop")
        return

    print("Killing the current job and post-job...")

    try:
        #print(type(machine_dict['commands']['cancel']))
        machine_dict['commands']['cancel']
    except KeyError:
        print("No 'cancel' command specified in the machine file")
        return

    sbp.run([machine_dict['commands']['cancel'],
             job_id],
            stdout=sbp.PIPE)
    print("   job  "+ str(job_id) + " was killed")
    sbp.run([machine_dict['commands']['cancel'],
             pjob_id],
            stdout=sbp.PIPE)
    print("   pjob "+ str(pjob_id) + " was killed")




@cli.command('safestop')
def lemmings_safestop():
    """
    Lemmings finish properly the current loop and stop.
    """
    from lemmings_hpc.chain.database import Database
    
    database = Database()
    database.update_loop('safe_stop', True, 0) #latest


@cli.command('endlog')
# @click.option("--job", "-j", type=str, default=None,
#               help="The job name you want to show")
def lemmings_endlog():
    """
    Show the lemmings log of the actual/most_recent job upon finishing.
    """
    import os
    from lemmings_hpc.chain.database import Database
    db = Database()
    # database = db._database
    chain_name = db.latest_chain_name
    if chain_name is None:
        print("No lemmings database found. Check your current directory...")
    else:
        with open(os.path.join(chain_name, chain_name + ".log"), 'r') as fin:
            print(fin.read())

@cli.command('status')
# @click.option("--timeformat", "-tf", required=False , type=click.Choice(['s','ms']), default= 'ms',
#               help="Simulation time format")
@click.option("--database", "-db", required=False , type=str, default = None,
              help="Path to database  YAML file to read")
@click.option("--progress", '-p', is_flag=True,
              help="If activated, the latest progress will also be shown.")
# @click.option("--job", "-j", type=str, default=None,
#               help="The job name you want to show")
def lemmings_status(database, progress):
    """
    Show the status during runtime
    """
    from lemmings_hpc.chain.database import Database

    try:
        if database is not None:
            if os.path.isdir(database): # try find database.yml in directory
                database = os.path.join(database, 'database.yml')
            if not os.path.isfile(database):
                raise FileNotFoundError(database + " does not exist")
        else:
            if not os.path.isfile("database.yml"):
                raise FileNotFoundError("database.yml does not exist")
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return

    if database is not None:
        db = Database(database)
    else:
        ## this init will generate a database.yml file,
        ## so if not present we should check before
        db = Database()

    try:
        _ = [print(string) for string in db.get_current_status(with_progress = progress)]
    except ValueError as excep:
        print("ValueError:", excep)
        return
    except TypeError as excep:
        print("Database currently not accessible, try again shortly")
        print("Make sure it is not corrupted")
        return # might be that database chain not found instead!!!
    except KeyError as excep:
        print("Database currently not accessible, try again shortly")
        return


# @cli.command('get_tuto_files')
# def lemmings_get_tuto():
#     """
#     Recover tuto lemmings/barbatruc files
#     """
#     import os
#     import shutil
#     from pathlib import Path
#     from pkg_resources import resource_filename
#     tuto_path = Path(resource_filename('lemmings', "")) / "example" / "barbatruc"
#     shutil.copytree(tuto_path, os.getcwd() + '/tuto_lemmings')

@cli.command('clean')
@click.option("--database", "-db", required=False , type=str, default = None,
              help="Path to database  YAML file to read")

def lemmings_clean(database):
    """
    Clean lemmings run files in current folder
    """
    import os
    import sys
    import shutil
    from lemmings_hpc.chain.database import Database

    # need to add option to have other database.yml name to look at
    # cfr. lemmings status of FEATURE/parallel branch

    lst_remove = ["__pycache__", "batch_job", "batch_pjob", "database.yml"]

    def remove(my_path):
        """
        Clean removal of file/folders based on the database.yml file info
        """
        if os.path.exists(my_path):
            if os.path.isfile(my_path):
                print("> Remove file: %s" % my_path)
                os.remove(my_path)
                return

            if os.path.isdir(my_path):
                print("> Remove folder: %s" % my_path)
                shutil.rmtree(my_path)
                return

    try:
        if database is not None:
            if not os.path.isfile(database):
                raise FileNotFoundError(database + " does not exist")
            lst_remove = [string.replace('database.yml',database) for string in lst_remove]
        else:
            if not os.path.isfile("database.yml"):
                raise FileNotFoundError("database.yml does not exist")
    except FileNotFoundError as excep:
        print("Error: ", excep)
        return

    if database is not None:
        db = Database(database)
    else:
        ## this init will generate a database.yml file,
        ## so if not present we should check before
        db = Database()

    try:
        db.latest_chain_name
    except UnboundLocalError as excep:
        print("'lemmings clean' aborted")
        return
    except TypeError as excep:
        print("'lemmings clean' aborted")
        return 2

    # Todo: add later option to remove only latest chain name
    try:
        chain_names = db.get_chain_names()
    except TypeError as excep:
        print("ValueError:", excep)
        print("Your file database.yml is corrupted, I can't automatically clean this folder\n")
        sys.exit()

    lst_remove.extend(chain_names)

    # currently only remove WF_xxx folders associated with latest chain
    try:
        par_dict, = db.get_current_loop_val('parallel_runs')
        lst_remove.extend(list(par_dict))
    except KeyError:
        pass

    for path in lst_remove:
        remove(path)


#Main function called by setup.py
main = click.CommandCollection(sources=[cli], help="This is the help of lemmings")
