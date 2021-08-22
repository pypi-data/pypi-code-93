#!/usr/bin/env python3

###
# This module implements a Comand Line Interface.
###


import click

from .project import *


# --------- #
# -- CLI -- #
# --------- #

###
# prototype::
#     project = ; // See Python typing...
#               the folder project that will be used to communicate during 
#               the analysis.
#     src     = ; // See Python typing...
#               the **relative** path of the source dir (regarding the project
#               folder).
#     target  = ; // See Python typing...
#               the **relative** path of the final product dir (regarding the
#               project folder).
#     ignore  = ( '' ) ; // See Python typing...
#               the rules for ignoring files in addition to what ¨git does.
#               You can use this argument even if you don't work with 
#     usegit  = ( False ) ; // See Python typing...
#               ``True`` asks to use ¨git contrary to ``False``.
#     readme  = ( '' ) ; // See Python typing...
#               ``''`` is if you don't need to import an external 
#               path::``README`` file, otherwise give a **relative** path.
#
# This function is to update a project from a terminal.
###
@click.command()
@click.argument('project')
@click.option('--src',
              default = 'src',
              help    = 'Relative path of the source folder of the project. '
                        'The default value is "src".')
@click.option('--target',
              default = '',
              help    = 'Relative path of the targer folder of the project. '
                        'The default value "", an empty string, indicates '
                        'to use the name, in lower case, of the project.')
@click.option('--ignore',
              default = '',
              help    = 'Path to a file with the rules for ignoring '
                        'files in addition to what git does. '
                        'The default value "", an empty string, indicates '
                        'to not use any rule.')
@click.option('--usegit',
              is_flag = True,
              help    = 'This flag is to use git.')
@click.option('--readme',
              default = '',
              help    = 'Relative path of an external README file. '
                        'The default value "", an empty string, indicates '
                        'to not use any external README file.')
@click.option('--notsafe',
              is_flag = True,
              help    = 'This flag allows to remove a none empty target folder.')
def update(
    project: str,
    src    : str,
    target : str,
    ignore : str,
    usegit : bool,
    readme : str,
    notsafe: bool,
) -> None:
    """
    Update your "source-to-product" like projects using the Python module src2prod.

    PROJECT: the path of the project to update.
    """
# What is the target?
    if target == '':
        project = Path(project)
        target  = project.name.lower()

# readme: '' --> None
    if not readme:
        readme = None

# Do we have an "ignore" path?
    if ignore:
        ignore = Path(ignore)

# Let the class Project does the job.
    Project(
        project = project,
        source  = src,
        target  = target,
        ignore  = ignore,
        usegit  = usegit,
        readme  = readme,
    ).update(safemode = not notsafe)
