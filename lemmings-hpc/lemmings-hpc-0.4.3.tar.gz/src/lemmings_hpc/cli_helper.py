"""Module helper for the CLI of lemmings"""
import os
import random
import string
import glob
from pathlib import Path
from pkg_resources import resource_filename
from lemmings_hpc.chain.path_tool import PathTools

# We have to avoid offensive names, here in french
FORBIDDEN_NAMES = [
    "", "PUTE", "PEDE", "BITE", "CACA", "ZIZI", "CUCU", "PIPI", "CONE",
    "CULE", "PENE", "SODO", "SUCE", "SUCA", "KUKU", "CUNI"]

def custom_name():
    """
    Random Name generator --> Cons + Vowels + Cons + Vowels + 2*Int
    """
    vowels = list("AEIOU")
    consonants = list(set(string.ascii_uppercase) - set(vowels))
    name = ""
    while name in FORBIDDEN_NAMES:
        name = ""
        name += random.choice(consonants)
        name += random.choice(vowels)
        name += random.choice(consonants)
        name += random.choice(vowels)

    name += str(random.randrange(1, 10))
    name += str(random.randrange(1, 10))
    return name


def get_workflow_py(workflow):
    """
    *Get the path of the {workflow}.py file.*

    :param workflow: workflow name
    :type workflow: str
    """
    path_tool = PathTools()
    env_var = dict(os.environ)
    catch = False

    if Path("./" + workflow + ".py").is_file():
        wf_py_path = path_tool.abspath(workflow + ".py")
        catch = True
    if catch is False and "LEMMINGS_WORKFLOWS" in env_var:
        wf_py_path = env_var["LEMMINGS_WORKFLOWS"]
        if Path(wf_py_path).is_file():
            catch = True
        else:
            raise EnvironmentError("\n ENVIRONMENT VAR :\nunable to open file at " + wf_py_path)
    if catch is False:
        wf_py_path = Path(resource_filename('lemmings_hpc', "")) / "chain" / "workflows" /  str(workflow + ".py") #pylint: disable=line-too-long
        if Path(wf_py_path).is_file():
            catch = True
        else:
            raise EnvironmentError("\nFOLDER LEMMING : unable to open file at " + str(wf_py_path))

    if wf_py_path is not None:
        return wf_py_path

    raise EnvironmentError("Your workflow doesn't exist in :\n"
                           + "  - current directory\n"
                           + "  - Environment variable ('LEMMING_WORKFLOWS')\n"
                           + "  - Folder workflows of lemmings\n")


def get_workflow_yml(workflow, user_yaml = False):
    """
    *Get the path of the {workflow}.yml file.*

    :param workflow: workflow name
    :type workflow: str
    """
    path_tool = PathTools()
    if user_yaml:
        if Path(workflow + ".yml").is_file():
            wf_yml_path = path_tool.abspath(workflow + ".yml")
        else:
            raise FileNotFoundError("Oops!  Couldn't find the %s.yml file relative to your current directory. Please generate it." % workflow)
    else:
        if Path("./" + workflow + ".yml").is_file():
            wf_yml_path = path_tool.abspath(workflow + ".yml")
        else:
            raise FileNotFoundError("Oops!  Couldn't find the %s.yml file in your current directory. Please generate it." % workflow)

    return wf_yml_path


def check_cpu_input(cpu_limit):
    """
    *Ask a confirmation of the cpu_limit to the user*

    :param cpu_limit: the cpu limit found in the {workflow}.yml file
    :type cpu_limit: float
    """
    cpu_confirm = input("Your CPU limit is " + str(cpu_limit) + " [hours]."
                        + " Confirm it typing the same value: ")

    if int(cpu_confirm) != int(cpu_limit):
        raise ValueError("Confirmation failed: " + str(cpu_confirm) + " != " + str(cpu_limit))


def find_all_wf():
    """
    *Find all available workflows.*
    They can be in the current directory,
    workflows folder of lemmings or in a environment variable.
    """
    path_workflows = {"current": {},
                      "env_var": {},
                      "lemmings": {}}

    files_wf = []
    env_var = dict(os.environ)

    #find in the workflows folder of lemmings
    path_folder_wf = Path(resource_filename('lemmings_hpc', "")) / "chain" / "workflows"
    for file in glob.glob(str(path_folder_wf) + "/*.py"):
        if "__init__" not in file:
            files_wf.append(file.split("/")[-1])
            path_workflows["lemmings"][files_wf[-1].split('.py')[0]] = file

    #find in current directory 
    for file in glob.glob("*.py"):
        if file in files_wf: # -> requires to be def
            path_workflows["current"][file.split('/')[-1].split('.py')[0]] = file

    #find in environment variable
    if "LEMMINGS_WORKFLOWS" in env_var:
        for var in env_var["LEMMINGS_"]:
            if var.split('/')[-1] in files_wf:
                path_workflows["env_var"][var.split('/')[-1].split('.py')[0]] = var

    return path_workflows
