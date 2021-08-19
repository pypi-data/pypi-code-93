# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import subprocess
import tempfile

from azureml.exceptions._azureml_exception import UserErrorException
from ._component_run_logger import Logger
from .._util._loggerfactory import _LoggerFactory, track


_logger = None


def _get_logger():
    global _logger
    if _logger is not None:
        return _logger
    _logger = _LoggerFactory.get_logger(__name__)
    return _logger


class CommandEnvironment(object):
    """
    Record command execution environment info.

    CommandEnvironment is used to store command execution environment when command execution in conda/container.
    For now CommandEnvironment required properties are conda, image and execution os type.
    """

    def __init__(self, conda_environment_name=None, image_name=None, os_type=None):
        self.conda_environment_name = conda_environment_name
        self.image_name = image_name
        self.os_type = os_type if os_type is not None else 'linux'

    def is_windows(self):
        return self.os_type.lower() == 'windows'


class ComponentEnvironment(CommandEnvironment):
    """
    Record and build component execution environment.

    ComponentEnvironment is used to record and build component execution environment. It will be used to build
    environment in component helper and send environment info to command execution. It has two interfaces,
    build_in_host and check_environment_exists, used to build environment.
    """

    def __init__(self, component):
        super().__init__(os_type=component._definition.environment.os)
        self.component = component
        # env is component environment
        self.env = None
        # register_image_name is the name of image registered in ACR
        self.register_image_name = None

    def build_in_host(self):
        """Build component environment in host."""
        raise NotImplementedError

    def check_environment_exists(self):
        """Check component environment exist in host."""
        raise NotImplementedError


class ComponentCondaEnvironment(ComponentEnvironment):
    """
    Record and build component conda environment.

    ComponentCondaEnvironment is used to store conda environment info and build conda in host.
    """
    def __init__(self, component, log_dir=None):
        super(ComponentCondaEnvironment, self).__init__(component)
        self.env = component._get_environment()
        if component._definition.environment.conda is None:
            raise UserErrorException(
                'Cannot initialize component conda since the conda of the component is not specified.')
        self.conda_environment_name = self.env.python.conda_dependencies._conda_dependencies['name']
        if not log_dir:
            log_dir = tempfile.gettempdir()
        self.log_path = os.path.join(log_dir, self.conda_environment_name + '.txt')

    def check_environment_exists(self):
        """Check cond environment exist in host."""
        return self._check_conda_environment_exists()

    def _check_conda_environment_exists(self):
        """
        Execute command 'conda env list' to check conda exists in host environment.

        :return: is_conda_environment_exists: If conda name exists, return True, else return False.
        :rtype: bool
        """
        try:
            # Before python3.7, because _winapi.CreateProcess used by subprocess is not thread-safe,
            # it may cause ValueError: embedded null character. This error does not occur when passing args as a list.
            # https://bugs.python.org/issue31446
            conda_version_output = subprocess.check_output(['conda', 'env', 'list'], stderr=subprocess.STDOUT)
            result = conda_version_output.decode("UTF-8")
            for line in result.split(os.linesep):
                if self.conda_environment_name in line:
                    return True
            return False
        except Exception as e:
            raise UserErrorException(
                'Execute conda command failed, please check conda is available in host, detail message: %s' % str(e))

    @track(_get_logger, is_long_running=True)
    def build_in_host(self):
        """
        Build conda environment in host and return conda environment path.

        :return: conda_name: If success build conda in host, return conda name.
        :rtype: str
        """
        with Logger(log_path=self.log_path) as logger:
            try:
                logger.print_to_terminal(
                    'Start building [ %s ] conda environment: %s\n' % (
                        self.component.name, self.conda_environment_name))
                self.env.build_local(self.component.workspace, useDocker=False)
            except:
                if '_TEST_ENV' in os.environ:
                    with open(self.log_path, 'r', encoding='utf-8') as f:
                        logger.print_to_terminal(f.read())
                raise UserErrorException(
                    'Build conda environment in host failed, please find failure reason from %s' % self.log_path)
            finally:
                logger.print_to_terminal(
                    'Finish building [ %s ] conda environment: %s\n' % (
                        self.component.name, self.conda_environment_name))
            if not self.check_environment_exists():
                # In azureml-environment-setup, using environment_path and environment_indicator to check environment
                # existence, and not the validity of environment_path's contents. When user remove environment built
                # by azureml and not completely deleted environment_path, azureml-environment-setup will mistakenly
                # believe environment exists and not build in host.

                # TODO add FAQ link to help user fix this situation.
                conda_env_path = (
                    '%%USERPROFILE%%/.azureml/envs/%s' if self.is_windows else '$HOME/.azureml/envs/%s') % \
                    self.conda_environment_name
                raise UserErrorException(
                    'Not found %s in conda environment list. Please delete residue folder of this conda env and retry.'
                    ' Residue folder path is %s' % (self.conda_environment_name, conda_env_path))
        return self.conda_environment_name


@track(_get_logger)
def get_component_environment(component, mode, log_path=None):
    """
    Get component environment

    :param component: Execution component
    :type component: azure.ml.componet.Component
    :param mode: Component run mode.
    :type mode: azure.ml.component._execution._component_run_helper.RunMode
    :param log_path: Component environment log path
    :type log_path: str
    :return: component_environment: Component environment info
    :rtype: azure.ml.component._execution._component_run_helper.ComponentEnvironment
    """
    from ._component_run_helper import RunMode
    if mode == RunMode.Docker:
        # generate ComponentImage
        from .._debug._image import ComponentImage
        component_environment = ComponentImage(component, log_path)
    elif mode == RunMode.Conda:
        # Generate ComponentCondaEnvironment
        component_environment = ComponentCondaEnvironment(component, log_path)
    else:
        # use host mode, generate ComponentEnvironment
        component_environment = ComponentEnvironment(component)
    return component_environment
