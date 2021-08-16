#!/usr/bin/env python

import os
import pkg_resources
import click
from pycortexintelligence.core import funcs_startproject


VERSION = pkg_resources.require("pycortexintelligence")[0].version


@click.group()
@click.version_option(version=VERSION, prog_name='pycortex')
def pycortex():
    pass


@click.command()
@click.option('--name', help='Start a project with this name! Like a "Project Name"')
@click.option('--sname', help='Define a Safe Name to project like a "project_name"')
def startproject(name, sname):
    """
    This script create a Cortex Default Integration Template
    """
    # Validate args
    # Getting project Name
    if name is None:
        print('Example: Project Name')
        name = click.prompt('Give a Project Name.', type=str)
    if sname is None:
        print('Example: project_name')
        sname = click.prompt('Give a Project Safe Name.', type=str)
        if ' ' in sname:
            raise ValueError('Safe name, cannot have spaces!')

    # Call the functions
    print('Initializing tool...')
    path_real = os.path.dirname(os.path.realpath(__file__))
    path_fake = path_real.replace('/bin', "")
    funcs_startproject.check_create_dirs()
    funcs_startproject.creck_create_files(project_name=name, safe_name=sname)
    print('> Files are created on "{}"'.format(path_fake))
    print('Creating a Default Project Template for {}'.format(name))


pycortex.add_command(startproject)

if __name__ == '__main__':
    pycortex()