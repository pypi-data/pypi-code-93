"""
We specify the installer as a list of steps that 
must run in order, for the installer.

Currently, we take the following steps:
1. First, try and install mitosheet3. Because mitosheet3 uses 
   JLab 3, we first check if the user has any conflicting
   JLab 2 dependencies installed. If they do, we abort. If they 
   don't, we update them to JLab 3.
2. Then, if the above installation of mitosheet3 fails for 
   any reason, we try to install mitosheet on JLab 2. 
3. If neither of them work, we give up, sadly. 
"""

from termcolor import colored
from mitoinstaller.commands import check_running_jlab_3_processes, install_pip_packages, jupyter_labextension_list, uninstall_labextension, uninstall_pip_packages, upgrade_mito_installer, exit_with_error
from mitoinstaller.log_utils import log, identify, log_step_failed
from mitoinstaller.user_install import (try_create_user_json_file, get_static_user_id)
from mitoinstaller import __version__

# SHARED UTILITIES

def initial_install_step_create_user(install_or_upgrade):
    static_user_id = get_static_user_id()

    # If the user has no static install ID, create one
    if static_user_id is None:
        try_create_user_json_file()    
    
    identify()
    log('{install_or_upgrade}_started'.format(install_or_upgrade=install_or_upgrade), {
        'mitoinstaller_version': __version__
    })

def get_extension_names_from_labextension_list_output(stdout, stderr):
    """
    Returns a list of the extension names installed from the stdout, stderr
    pair returned from the jupyter labextension list.

    If you run the command: `jupyter labextension list`, the output is: 
    ------
    JupyterLab v0.35.0
    Known labextensions:
    app dir: /Users/nate/saga-vcs/monorepo/mito/installer/venv/share/jupyter/lab
            @jupyter-widgets/jupyterlab-manager v0.38.1 enabled OK
    ------

    Note that part of this output prints to stdout, and other parts to stderr 
    (for some reason), so we append them with a newline so we make sure we 
    get all of the extensions correctly!
    """
    def is_extension_line(line):
        # Check that it has a version
        if len(line) == 0:
            return False

        if 'v' not in line:
            return False
        
        # Check that it is either enabled or disabled
        return 'enabled' in line or 'disabled' in line

    output = stdout + "\n" + stderr
    extension_lines = [line.strip() for line in output.splitlines() if is_extension_line(line)]
    extension_names = []
    for line in extension_lines:
        extension_names.append(line.split(" ")[0])

    return extension_names

def get_jupyterlab_metadata():
    """
    Helper function that returns a tuple of: (jupyterlab_version), (installed_extensions)

    If no JupyterLab is installed, returns (None, None)
    """
    try:
        from jupyterlab import __version__
    except Exception as e:
        # If this import fails, it must not be installed
        return None, None

    stdout, stderr = jupyter_labextension_list()
    extension_names = get_extension_names_from_labextension_list_output(stdout, stderr)
    return __version__, extension_names


def install_step_upgrade_mitoinstaller():
    upgrade_mito_installer()
    


# MITOSHEET 3 INSTALL STEPS

def install_step_mitosheet3_check_dependencies():
    """
    This is the most complex step in the installation process. It's
    goal is to check if the users existing installation can safely
    be upgraded to JLab 3.0. 

    To do this, it checks a variety of conditions, mostly around what
    version of JLab they have installed, and if this version of JLab has
    any installed dependencies (that we cannot safely upgrade).
    """

    jupyterlab_version, extension_names = get_jupyterlab_metadata()

    # If no JupyterLab is installed, we can continue with install, as
    # there are no conflict dependencies
    if jupyterlab_version is None:
        return
    
    # If JupyterLab 3 is installed, then we are are also good to go
    if jupyterlab_version.startswith('3'):
        return
    
    if len(extension_names) == 0:
        return
    elif len(extension_names) == 1 and extension_names[0] == 'mitosheet':
        uninstall_labextension('mitosheet')
        uninstall_pip_packages('mitosheet')
        log('uninstalled_mitosheet_labextension',
            {
                'jupyterlab_version': jupyterlab_version,
                'extension_names': extension_names
            }
        )
        return
    
    else:
        raise Exception('Installed extensions {extension_names}'.format(extension_names=extension_names))


def install_step_mitosheet3_install_mitosheet3():
    install_pip_packages('mitosheet3')


INSTALL_MITOSHEET3_STEPS = [
    {
        'step_name': 'Upgrading mitoinstaller',
        'execute': install_step_upgrade_mitoinstaller
    },
    {
        'step_name': 'Checking dependencies',
        'execute': install_step_mitosheet3_check_dependencies
    },
    {
        'step_name': 'Installing mitosheet3',
        'execute': install_step_mitosheet3_install_mitosheet3
    },
]


# MITOSHEET 2 INSTALL STEPS


def install_step_mitosheet_check_dependencies():
    jupyterlab_version, extension_names = get_jupyterlab_metadata()

    # If no JupyterLab is installed, we can continue with install, as
    # there are no conflict dependencies
    if jupyterlab_version is None:
        return
    
    # If JupyterLab 2 is installed, then we are are also good to go
    if jupyterlab_version.startswith('2'):
        return
    
    if len(extension_names) == 0:
        return
    elif len(extension_names) == 1 and extension_names[0] == 'mitosheet':
        return
    else:
        raise Exception('Installed extensions {extension_names}'.format(extension_names=extension_names))


def install_step_mitosheet_install_mitosheet():
    install_pip_packages('mitosheet')


def install_step_mitosheet_install_jupyter_widget_manager():
    from jupyterlab import commands
    commands.install_extension('@jupyter-widgets/jupyterlab-manager@2')


def install_step_mitosheet_rebuild_jupyterlab():
    from jupyterlab import commands
    commands.build()


INSTALL_MITOSHEET_STEPS = [
    {
        'step_name': 'Upgrading mitoinstaller',
        'execute': install_step_upgrade_mitoinstaller
    },
    {
        'step_name': 'Checking dependencies',
        'execute': install_step_mitosheet_check_dependencies
    },
    {
        'step_name': 'Installing mitosheet',
        'execute': install_step_mitosheet_install_mitosheet
    },
    {
        'step_name': 'Installing @jupyter-widgets/jupyterlab-manager@2',
        'execute': install_step_mitosheet_install_jupyter_widget_manager
    },
    {
        'step_name': 'Rebuilding JupyterLab',
        'execute': install_step_mitosheet_rebuild_jupyterlab
    },
]


def get_success_message(install_or_upgrade):
    """
    We show a different message depending on if this is an install or an upgrade,
    and we further tell the user different things if they have a currently running
    JLab instance (as they need to restart this)
    """
    running_jlab = check_running_jlab_3_processes()

    separator_line = '----------------------------------------------------------------------------'

    install_start = 'Mito has finished installing'
    upgrade_start = 'Mito has finished upgrading.'

    launch_jlab = 'Launch JupyterLab with:\t' + colored('python -m jupyter lab', 'green')
    relaunch_jlab = 'Please shut down the currently running JupyterLab and relaunch it to enable Mito'

    render_mitosheet = 'Then render a mitosheet following the instructions here: https://docs.trymito.io/how-to/creating-a-mitosheet'

    if not running_jlab:
        if install_or_upgrade == 'install':
            return '\n{separator_line}\n{install_start}\n\n{launch_jlab}\n\n{render_mitosheet}\n{separator_line}'.format(
                separator_line=separator_line,
                install_start=install_start,
                launch_jlab=launch_jlab,
                render_mitosheet=render_mitosheet,
            )
        else:
            return '\n{separator_line}\n{upgrade_start}\n\n{launch_jlab}\n\n{render_mitosheet}\n{separator_line}'.format(
                separator_line=separator_line,
                upgrade_start=upgrade_start,
                launch_jlab=launch_jlab,
                render_mitosheet=render_mitosheet,
            )
    else:
        if install_or_upgrade == 'install':
            return '\n{separator_line}\n{install_start}\n\n{relaunch_jlab}\n\n{render_mitosheet}\n{separator_line}'.format(
                separator_line=separator_line,
                install_start=install_start,
                relaunch_jlab=relaunch_jlab,
                render_mitosheet=render_mitosheet,
            )
        else:
            return '\n{separator_line}\n{upgrade_start}\n\n{relaunch_jlab}\n\n{render_mitosheet}\n{separator_line}'.format(
                separator_line=separator_line,
                upgrade_start=upgrade_start,
                relaunch_jlab=relaunch_jlab,
                render_mitosheet=render_mitosheet,
            )

def do_install_or_upgrade(install_or_upgrade):
    """
    install_or_upgrade is the workhorse of actually installing mito. It first attempts
    to install mitosheet3, and if that fails, installs mitosheet.

    install_or_upgrade should be 'install' or 'upgrade'

    Notably, the process for installing Mito initially and upgrading Mito are
    identical. As such, we reuse this function to upgrade, just with different
    error and logging messages.
    """
    print("Starting {install_or_upgrade}...".format(install_or_upgrade=install_or_upgrade))

    initial_install_step_create_user(install_or_upgrade)

    for idx, install_step in enumerate(INSTALL_MITOSHEET3_STEPS):
        try:
            # Print the install step name
            print(install_step['step_name'])
            # Actually execute the step
            install_step['execute']()
            # If we finish install, then tell the user, and exit
            if idx >= len(INSTALL_MITOSHEET3_STEPS) - 1:
                log('{install_or_upgrade}_finished_mitosheet3'.format(install_or_upgrade=install_or_upgrade), {'package': 'mitosheet3'})
                print(get_success_message(install_or_upgrade))
                exit(0)
        except SystemExit:
            exit(0)
        except:
            # Note: if mitosheet3 installation fails, we log it, but we do
            # not exit, as we want to continue and try to install mitosheet
            error_message = "Failed: " + install_step['step_name']
            log_step_failed(install_or_upgrade, 'mitosheet3', error_message)
            print(error_message)
            # We do break out of this loop!
            break

    for install_step in INSTALL_MITOSHEET_STEPS:
        try:
            print(install_step['step_name'])
            install_step['execute']()
        except:
            error_message = "Failed: " + install_step['step_name']
            log_step_failed(install_or_upgrade, 'mitosheet', error_message)
            exit_with_error(install_or_upgrade, error_message)

    log('{install_or_upgrade}_finished_mitosheet'.format(install_or_upgrade=install_or_upgrade), {'package': 'mitosheet'})
    print(get_success_message(install_or_upgrade))