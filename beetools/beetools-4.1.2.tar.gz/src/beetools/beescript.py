
'''Tools for Bright Edge eServices developments & projects

These tools was designed for the use in the Bright Edge eServices echo system.
It defines methods and functions for general use purposes and standardization
in the Bright Edge eServices echo system.

The module define defaults for log levels, display on console, operating
system names and date formats.

The defaults are used in this module and across the Bright Edge eServices
echo system.  The module basically has

To Do
=====
1.  Better example on the logging integration
2.  Complete doctests for all methods & functions

'''

import configparser
import os
from pathlib import Path
import shlex
import subprocess
import sys
from termcolor import colored
from beetools.beearchiver import msg_info
from beetools import beeutils, beevenv

_PROJ_DESC = __doc__.split('\n')[0]
_PROJ_PATH = Path(__file__)
_PROJ_NAME = _PROJ_PATH.stem
_PROJ_VERSION = '3.2.0'


def exec_batch_in_session(
    p_script_cmds,
    p_switches=None,
    p_crash=True,
    p_script_name=False,
    p_verbose=False,
    p_shell=False,
) -> bool:
    '''Execute a script in the same session

    Useful when commands has to be exucuted in one session for instance if
    it a a virtual environment is envoked and the commands must be executed
    in the virtual environment.

    Parameters
    ----------
    p_script_cmds
        Commands to execute in a list
    p_switches
        Switches for the bash script.
        Default is None.
    p_crash
        Stop (crash) or continue execution should a command fail.
        Default is True
    p_script_name
        Name of the script to use
        Default is False and will be set to "do_bashs_cript_temp"
    p_verbose
        Give feedback (or not)
        Default is False
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is False

    Returns
    -------
    subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    tmp_test = get_tmp_dir() / 'test'
    tmp_t1 = tmp_test / 't1'
    cmd = ['mkdir -p {}'.format(tmp_t1), 'ls -l {}'.format(tmp_test), 'rm -R {}'.format(tmp_test)]
    exec_batch_in_session(cmd)
    '''
    if isinstance(p_switches, list):
        switches = p_switches
    elif isinstance(p_switches, str):
        switches = list(shlex.shlex(p_switches))
    else:
        switches = []
    if beeutils.get_os() in [beeutils.LINUX, beeutils.MACOS]:
        script = ['bash'] + switches
        ext = 'sh'
        contents = '#!/bin/bash\n'
    elif beeutils.get_os() == beeutils.WINDOWS:
        script = []
        ext = 'bat'
        contents = ''
    else:
        print(colored('Unknown OS ({})\nSystem terminated!'.format(beeutils.get_os()), 'red'))
        sys.exit()

    if not p_script_name:
        p_script_name = 'exec_batch_in_session_temp'
    batch_pth = beeutils.get_tmp_dir() / Path('{}.{}'.format(p_script_name, ext))
    script.append(str(batch_pth))
    contents += write_script(batch_pth, p_script_cmds)
    if beeutils.get_os() == beeutils.MACOS:
        batch_pth.chmod(0o777)
    if p_verbose:
        print(msg_info('==[Start {0}]====\n{1}==[ End {0} ]===='.format(batch_pth, contents)))
    compl_proc = exec_cmd(script, p_crash, p_verbose=p_verbose, p_shell=p_shell)
    if os.path.isfile(batch_pth):
        os.remove(batch_pth)
        pass
    return compl_proc


def exec_batch(p_batch, p_verbose = False):
    '''Execute a batch.

    Each command will be executed independantly of the previous one i.e it
    will be in a different session.
    Parameters
    ----------

    Returns
    -------
    bool
        If successful it returns True (subprocess.CompletedProcess = 0)
        alternatively it returns a subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import exec_batch
    >>> exec_batch([[ 'echo', 'Hello'],['echo','Goodbye']])
    True

    '''
    success = True
    # c_cmd = 1
    for cmd in p_batch:
        rc = exec_cmd(cmd, p_verbose = p_verbose)
        if rc is not True:
            success = False
    return success


def exec_cmd(p_cmd, p_crash=True, p_shell=None, p_verbose=False) -> bool:
    '''Execute a command line instruction on tools.LINUX or tools.WINDOWS

    Parameters
    ----------
    p_cmd
        Command to execute.  See See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
    p_crash
        Stop (crash) or continue execution should a command fail.
    p_shell
        Run the script in a shell.  See https://docs.python.org/3.9/library/subprocess.html#subprocess.run
        Default is None
    p_verbose
        Give feedback (or not)
        Default is False

    Returns
    -------
    bool
        If successful it returns True (subprocess.CompletedProcess = 0)
        alternatively it returns a subprocess.CompletedProcess
        See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import exec_cmd
    >>> exec_cmd([ 'echo', 'Hello'])
    True

    '''
    success = True
    p_cmd = [str(s) for s in p_cmd]
    inst_str = ' '.join(p_cmd)
    if p_verbose:
        print(msg_info('{}'.format(inst_str)))
    if beeutils.get_os() in [beeutils.LINUX, beeutils.MACOS] and not p_shell:
        shell = False
    elif beeutils.get_os() == beeutils.WINDOWS and not p_shell:
        shell = True
    elif beeutils.get_os() not in [beeutils.WINDOWS, beeutils.LINUX, beeutils.MACOS]:
        print(colored('Unknow OS ({})\nSystem terminated!'.format(beeutils.get_os()), 'red'))
        sys.exit()
    else:
        shell = p_shell
    try:
        comp_proc = subprocess.run(
            p_cmd, capture_output=False, shell=shell, check=False
        )
        comp_proc.check_returncode()
    except subprocess.CalledProcessError:
        print('\nCmd:\t{}\nrc:\t{}'.format(inst_str, comp_proc.returncode))
        if p_crash:
            print(colored('System terminated!', 'red'))
            sys.exit()
        else:
            print('Crash = False.  Execution will continue...')
    if comp_proc.returncode != 0:
        success = comp_proc.returncode
    return success


def write_script(p_pth, p_contents):
    '''Write a script to disk

    Parameters
    ----------
    p_pth
        Path to the script
    p_contents
        Contents of the script

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import beeutils, beevenv
    >>> beevenv.set_up(beeutils.get_tmp_dir(),'new-project',['pip','wheel'],p_verbose=False)
    True

    '''
    contents = ''
    for line in p_contents:
        if isinstance(line, list):
            contents += ' '.join(line) + '\n'
        else:
            contents += '{}\n'.format(line)
    p_pth.write_text(contents)
    return contents


def example_scripting():
    '''Standard example to illustrate standard use.

    Parameters
    ----------

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''
    success = True
    # Run a few commands in a script.  Useful when executing commands in a
    # venv in the same session.
    tmp_test = beeutils.get_tmp_dir() / 'test'
    tmp_t1 = tmp_test / 'T1'
    if beeutils.get_os() == beeutils.WINDOWS:
        batch = [
            'md {}'.format(tmp_t1),
            'dir /B {}'.format(tmp_test),
        ]
    else:
        batch = [
            'mkdir -p {}'.format(tmp_t1),
            'ls -l {}'.format(tmp_test),
        ]
    success = exec_batch_in_session(batch, p_verbose=False) and success

    # Execute some commands in a batch
    if beeutils.get_os() == beeutils.WINDOWS:
        cmds = [
            ['rd', '/S', '/Q', '{}'.format(tmp_t1)],
            ['md', '{}'.format(tmp_t1)],
            ['dir', '/B', '{}'.format(tmp_test)],
        ]
    else:
        cmds = [
            ['mkdir', '-p', '{}'.format(tmp_t1)],
            ['ls', '-l', '{}'.format(tmp_test)],
        ]
    success = exec_batch(cmds) and success

    # Write a script
    script_pth = beeutils.get_tmp_dir() / _PROJ_NAME
    cmds = [
        ['echo', 'Hello'],
        ['echo', 'Goodbye'],
    ]
    contents = write_script(script_pth, cmds)
    print(contents)

    # Create a few files to the previous example and the remove the tree
    t_file = tmp_test / Path('t.tmp')
    t_file.touch(mode=0o666, exist_ok=True)
    t_file = tmp_t1 / Path('t.tmp')
    t_file.touch(mode=0o666, exist_ok=True)
    success = beeutils.rm_tree(tmp_test, p_crash = True) and success

    # Attempt to remove a temporary locked file.
    venv_name = 'new-project'
    success = beeutils.rm_temp_locked_file(beevenv.get_dir(beeutils.get_tmp_dir(), venv_name)) and success

    # Read an option from an ini for a particular os and setup
    cnf = configparser.ConfigParser()
    cnf.read_dict(
        {
            'Folders': {
                'windows1_MyFolderOnSystem': 'c:\\Program Files',
                'windows2_MyFolderOnSystem': 'c:\\Program Files (x86)',
                'linux1_MyFolderOnSystem': '/usr/local/bin',
                'linux2_MyFolderOnSystem': '/bin',
                'macos1_MyFolderOnSystem': '/System',
                'macos2_MyFolderOnSystem': '/Application',
            }
        }
    )
    os_system_flder = beeutils.select_os_dir_from_config(cnf, 'Folders', 'MyFolderOnSystem')
    print(os_system_flder)
    success = os_system_flder and success
    beeutils.result_rep(success, p_comment= 'Done')
    return success


def do_examples(p_cls=True):
    '''Example to illustrate usage

    Parameters
    ----------
    p_app_path
        Path to the application module
    p_cls
        Clear the screen before start
        Default is True

    Returns
    -------
    bool
        Successful execution [ b_tls.archive_path | False ]

    Examples
    --------

    '''

    # Initiate the Archiver
    success = True
    b_tls = beeutils.Archiver(_PROJ_NAME, _PROJ_VERSION, _PROJ_DESC, _PROJ_PATH)
    b_tls.print_header(p_cls=p_cls)
    success = example_scripting() and success
    b_tls.print_footer()
    if success:
        return b_tls.arc_pth
    return False


if __name__ == '__main__':
    do_examples()
# end __main__
