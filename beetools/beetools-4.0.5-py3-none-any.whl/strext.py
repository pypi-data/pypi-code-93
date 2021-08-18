
'''Tools for Bright Edge eServices developments & projects

Extention to the str built-in class

To Do
=====
1.

'''


# import configparser
# import datetime
# import inspect
import logging
# import os
from pathlib import Path
# import shlex
# import shutil
# import subprocess
# import sys
# from termcolor import colored
import beetools

_path = Path(__file__)
_name = _path.stem
_VERSION = '0.0.1'


class StrExt(str):
    '''Create an extension of the str builtin class
    '''

    def __init__(
        self,
        p_parent_log_name,
    ):
        '''Initialize the object

        Parameters
        ----------
        p_parent_log_name
            Name of the parent logger i.e. calling application

        Returns
        -------

        Examples
        --------
        >>> au = Archiver(__name__, _VERSION, __doc__, p_app_path=Path(__file__))

        '''

        self.success = True
        self.log_name = '{}.{}'.format(p_parent_log_name, _name)
        self.logger = logging.getLogger(self.log_name)

    def abc(self):
        pass

def example_1():
    '''Example 1

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    '''
    success = True
    return success


def example_2():
    '''Example 2.

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    '''
    success = True
    return success

def do_examples():
    '''Do example to illustrate usage

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    '''

    # Initate the Archiver
    success = True
    b_tls = beetools.Archiver(_name, _VERSION, __doc__.split('\n')[0], p_app_path)
    b_tls.print_header()
    # success = example_virtual_environment() and success
    success = example_1() and success
    success = example_2() and success
    b_tls.print_footer()
    return success


if __name__ == '__main__':
    do_examples()
