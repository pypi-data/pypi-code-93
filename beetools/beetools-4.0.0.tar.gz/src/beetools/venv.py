
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

from pathlib import Path
import subprocess
import sys
from beetools import Archiver, script, tools

_path = Path(__file__)
_name = _path.stem
_VERSION = '3.2.0'


def activate(p_venv_base_dir, p_venv_name) -> str:
    '''Compile command to activate a virtual environment

    This method is useful in the exec_batch_in_session() method to invoke a virtual
    environment in a session to execute other commands in the virtual
    environment.

    Parameters
    ----------
    p_venv_base_dir
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.

    Returns
    -------
    str
        The command to activate the virtual environment depending on the
        operating system.

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    activate(get_tmp_dir(),'new-project')
    'source /tmp/new-project_env/bin/activate'

    '''
    if tools.get_os() in [tools.LINUX, tools.MACOS]:
        cmd = 'source {}'.format(
            get_dir(p_venv_base_dir, p_venv_name) / Path('bin', 'activate')
        )
    else:
        cmd = 'CALL {}'.format(
            get_dir(p_venv_base_dir, p_venv_name) / Path('Scripts', 'activate')
        )
    return cmd


def get_dir(p_venv_base_dir, p_name_pref) -> Path:
    '''Compile the virtual environment base folder in Bright Edge eServices format

    Parameters
    ----------
    p_venv_base_dir
        This is the "root" folder of the virtual environment will be
        creates in

    Returns
    -------
    Path
        Path object with virtual environment name

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.get_dir(beetools.get_tmp_dir(), 'new-project')
    PosixPath('/tmp/new-project_env')

    '''
    return p_venv_base_dir / Path('{}_env'.format(p_name_pref))


def install_in(p_venv_base_dir, p_venv_name, p_instructions, p_verbose=True):
    '''Execute (install) commands in a virtual environment

    Parameters
    ----------
    p_venv_base_dir
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.
    p_instructions
        Instructions to execute in virtual environment
    p_verbose
        Give feedback (or not)
        Default is True

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    # No proper doctest (<<<) because it is os dependent
    beetools.install_in( beetools.get_tmp_dir(),
                              'new-project',
                              ['echo Installing in VEnv','pip install wheel','echo Done!'])
    + sudo -i
    Installing in VEnv
    Done!
    + exit
    True

    '''
    switches = []
    script_name = 'install_in'
    if tools.get_os() == tools.LINUX:
        switches = ['-x']
        script_cmds = ['sudo -i << _EOF_']
    elif tools.get_os() == tools.WINDOWS:
        script_cmds = []
        if p_verbose:
            script_cmds.append('@ECHO OFF')
    else:
        script_cmds = []
        if p_verbose:
            script_cmds.append('@ECHO OFF')
    script_cmds.append('{}\n'.format(activate(p_venv_base_dir, p_venv_name)))
    for instr in p_instructions:
        script_cmds.append(instr)
    if tools.get_os() == tools.LINUX:
        script_cmds.append('_EOF_')
        script_cmds.append('exit')
    ret_code = script.exec_batch_in_session(
        script_cmds, p_script_name=script_name, p_verbose=p_verbose, p_switches=switches
    )
    return ret_code


def set_up(
    p_venv_base_dir,
    p_venv_name,
    p_package_list = None,
    p_verbose=True
) -> bool:
    '''Create a virtual environment with some defaults

    Parameters
    ----------
    p_venv_base_dir
        This is the "root" folder of the virtual environment will be
        creates in
    p_venv_name
        The name of the virtual environment.
    p_package_list
        List of packages to install

    Returns
    -------
    subprocess.CompletedProcess
    See https://docs.python.org/3.9/library/subprocess.html#subprocess.CompletedProcess

    Examples
    --------
    >>> from beetools import set_up, get_tmp_dir
    >>> set_up( get_tmp_dir(),'new-project',['pip','wheel'],p_verbose=False)
    True

    '''
    switches = []
    script_cmds = []
    if tools.get_os() == tools.WINDOWS:
        pip_cmd = 'pip'
    else:
        pip_cmd = 'pip3'
        switches = ['-x']
        script_cmds = ['sudo -i << _EOF_']
    script.exec_cmd(
        [
            'python',
            '-m',
            'venv',
            get_dir(p_venv_base_dir, p_venv_name),
        ],
        p_verbose=p_verbose,
    )
    script_name = 'set_up'
    script_cmds.append('{}\n'.format(activate(p_venv_base_dir, p_venv_name)))
    if not p_package_list:
        p_package_list = []
    for package in p_package_list:
        if package[0] == 'Web':
            script_cmds.append('{} install {}'.format(pip_cmd, package[1]))
        elif package[0] == 'Local':
            script_cmds.append(
                '{} install --find-links {} {}'.format(pip_cmd, package[2], package[1])
            )
    if tools.get_os() == tools.LINUX:
        script_cmds.append('_EOF_')
        script_cmds.append('exit')
    ret_code = script.exec_batch_in_session(
        script_cmds, p_script_name=script_name, p_verbose=p_verbose, p_switches=switches
    )
    return ret_code


def example_virtual_environment():
    '''Standard example to illustrate virtual environment tools.

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
    # Remove remains of any previous skeletons still hanging around.
    if tools.get_os() == tools.WINDOWS:
        p_cmd = ['rd', '/S', '/Q', get_dir(tools.get_tmp_dir(), venv_name)]
    else:
        p_cmd = ['rm', '-f', '-r', get_dir(tools.get_tmp_dir(), venv_name)]
    success = script.exec_cmd(p_cmd, p_crash=False, p_verbose=True)

    # Install a new venv including termcolor in a tmp directory
    venv_name = 'new-project'
    package_list = [['Web', 'termcolor'], ['Web', 'wheel']]
    success = (
        set_up(tools.get_tmp_dir(), venv_name, package_list, p_verbose=True)
        and success
    )

    # Install/upgrade in an existing venv
    instructions = [
        'ECHO Setting up the {} VEnv...'.format(venv_name),
        'pip install --upgrade wheel',
        'ECHO Done!',
    ]
    success = (
        install_in(tools.get_tmp_dir(), venv_name, instructions, p_verbose=True)
        and success
    )
    tools.result_rep(success, p_comment='Done')

    # Get the the venv activation command
    t_venv = activate(tools.get_tmp_dir(), venv_name)
    print('Cmd example:\t{}'.format(t_venv))
    success = t_venv and success
    return success


def do_examples(p_app_path=None, p_cls=True):
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
    b_tls = Archiver(__name__, _VERSION, __doc__.split('\n')[0], p_app_path)
    b_tls.print_header(p_cls=p_cls)
    success = example_virtual_environment() and success
    b_tls.print_footer()
    if success:
        return b_tls.archive_path
    return False


if __name__ == '__main__':
    do_examples(sys.argv[0])
# end __main__
