"""
Contains useful commands for interacting
with the command line directly
"""

# NOTE: Do not import subprocess here, we only want one
# function to have it
import sys

from termcolor import colored

def get_output(completed_process):
    output = ""
    if completed_process.stdout is not None:
        output += completed_process.stdout
    if completed_process.stderr is not None:
        output += completed_process.stderr
    return output


def run_command(command_array):
    """
    An internal command that should be used to run all commands
    that run on the command line, so that output from failing
    commands can be captured.
    """
    import subprocess
    completed_process = subprocess.run(
        command_array, 
        # NOTE: we do not use the capture_output variable, as this doesn't work before
        # python 3.7, and we want users to be able to install before that
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        # NOTE: we use universal_newlines to get the result back as text, 
        # but we don't use text=True, because we want to work before 3.7 when
        # text was introduced. See here: https://stackoverflow.com/questions/41171791/how-to-suppress-or-capture-the-output-of-subprocess-run
        universal_newlines=True
    )
    if completed_process.returncode != 0:
        raise Exception(get_output(completed_process))

    # We default the stdout and stderr to empty strings if they are not strings, 
    # to make code that handles them have an easier time (they might be None)
    stdout = completed_process.stdout if isinstance(completed_process.stdout, str) else ''
    stderr = completed_process.stderr if isinstance(completed_process.stderr, str) else ''
    return stdout, stderr

def jupyter_labextension_list():
    """
    Returns the stdout, stderr pair for the currently
    installed jupyterlab extensions.
    """

    sys_call = [sys.executable, "-m", "jupyter", "labextension", "list"]
    return run_command(sys_call)


def uninstall_labextension(extension):
    """
    Uninstall a labextension
    """

    sys_call = [sys.executable, "-m", "jupyter", "labextension", "uninstall", extension]
    run_command(sys_call)


def uninstall_pip_packages(*packages):
    """
    This function uninstalls the given packages in a single pass
    using pip, through the command line.
    """

    sys_call = [sys.executable, "-m", "pip", "uninstall", "-y"]

    for package in packages:
        sys_call.append(package)
    
    run_command(sys_call)


def install_pip_packages(*packages):
    """
    This function installs the given packages in a single pass
    using pip, through the command line.

    https://stackoverflow.com/questions/12332975/installing-python-module-within-code
    """

    sys_call = [sys.executable, "-m", "pip", "install"]

    for package in packages:
        sys_call.append(package)
    sys_call.append('--upgrade')

    run_command(sys_call)

def upgrade_mito_installer():
    """
    Upgrades the mito installer package itself
    """
    run_command([sys.executable, "-m", "pip", "install", 'mitoinstaller', '--upgrade', '--no-cache-dir'])


def check_running_jlab_3_processes():
    """
    Returns true if there are running JLab 3 processes, 
    returns false if there are not.

    Useful for telling the user to refresh their servers
    if they install Mito
    """
    sys_call = [sys.executable, "-m", "jupyter", "server", "list"]
    stdout, stderr = run_command(sys_call)
    return len(stdout.strip().splitlines()) > 1

def check_running_jlab_not_3_processes():
    """
    Returns true if there are running JLab processes, 
    returns false if there are not.

    Useful for telling the user to refresh their servers
    if they install Mito
    """
    sys_call = [sys.executable, "-m", "jupyter", "notebook", "list"]
    stdout, stderr = run_command(sys_call)
    return len(stdout.strip().splitlines()) > 1

def check_running_jlab_processes():
    """
    Returns true if there are running JLab processes from any version
    returns false if there are not.
    """
    return check_running_jlab_3_processes() or check_running_jlab_not_3_processes()

def exit_with_error(install_or_upgrade, error=None):
    full_error = '\n\nSorry, looks like we hit a problem during {install_or_upgrade}. '.format(install_or_upgrade=install_or_upgrade) + \
        ('' if error is None else ("It seems we " + error + '.')) + \
        '\nWe\'re happy to help you fix it, just shoot an email to jake@sagacollab.com and copy in the output above.\n'

    print(colored(full_error, 'red'))
    exit(1)