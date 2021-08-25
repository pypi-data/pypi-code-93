"""Utility Luigi object for Queenbee local execution.

QueenbeeTask is a wrapper around luigi.Task which is used by queenbee-local to
execute Queenbee-specific task. You probably don't need to use this module in your code.
"""
import logging
import logging.config
import subprocess
import socket
import pathlib
import os
import shutil
import tempfile
import platform
import json

import luigi

# importing all the methods to make it easy for the extensions to grab them all from here
from .helper import parse_input_args, to_snake_case, update_params, _change_permission, \
    _copy_artifacts, to_camel_case, tab_forward


SYSTEM = platform.system()


class QueenbeeTask(luigi.Task):

    """
    A Luigi task to run a single command as a subprocess.

    Luigi has a subclass for running external programs

    https://luigi.readthedocs.io/en/stable/api/luigi.contrib.external_program.html
    https://github.com/spotify/luigi/blob/master/luigi/contrib/external_program.py

    But:
        * It doesn't allow setting up the environment for the command
        * It doesn't support piping
        * It doesn't support progress reporting

    QueenbeeTask:

        * simplifies the process of writing commands
        * captures stdin / stdout
        * supports piping
    """

    def _get_log_folder(self, folder):
        """A hack to find the log file!"""
        folder = pathlib.Path(folder)
        log_file = pathlib.Path(folder, '__logs__', 'logs.cfg')
        if log_file.exists():
            return log_file.as_posix()
        else:
            return self._get_log_folder(folder.parent)

    @property
    def log_config(self):
        return self._get_log_folder(self.initiation_folder)

    def get_interface_logger(self):
        logger = logging.getLogger('luigi-interface')
        if not logger.handlers:
            # load the logs from shared config file
            # This is an issue in Windows with multiple processors
            # https://github.com/spotify/luigi/issues/2247
            logging.config.fileConfig(self.log_config)
        return logger

    @property
    def input_artifacts(self):
        """Task's input artifacts.

        These artifacts will be copied to execution folder before executing the command.
        """
        return []

    @property
    def output_artifacts(self):
        """Task's output artifacts.

        These artifacts will be copied to study folder from execution folder after the
        task is done.
        """
        return []

    @property
    def output_parameters(self):
        """Task's output parameters.

        These parameters will be copied to study folder from execution folder after the
        task is done.
        """
        return []

    def command(self):
        """An executable command which will be passed to subprocess.Popen

        Overwrite this method.
        """
        raise NotImplementedError(
            'Command method must be overwritten in every subclass.'
        )

    def _copy_input_artifacts(self, dst):
        """Copy input artifacts to destination folder.

        Args:
            dst: Execution folder.
        """
        logger = self.get_interface_logger()
        for art in self.input_artifacts:
            logger.info(
                f"{self.__class__.__name__}: copying input artifact {art['name']} from "
                f"{art['from']} ..."
            )
            try:
                _copy_artifacts(art['from'], os.path.join(dst, art['to']))
            except TypeError as e:
                is_optional = art.get('optional', False)
                if is_optional:
                    continue
                raise TypeError(
                    f'Failed to copy input artifact: {art["name"]}\n{e}'
                )
        logger.info(
            f"{self.__class__.__name__}: finished copying artifacts..."
        )

    def _create_optional_output_artifacts(self, dst):
        """Create a dummy place holder for optional output artifacts.

        Args:
            dst: Execution folder
        """
        logger = self.get_interface_logger()
        for art in self.output_artifacts:
            is_optional = art.get('optional', False)
            if not is_optional:
                continue
            artifact = pathlib.Path(dst, art['from'])
            if artifact.exists():
                continue
            if 'type' not in art:
                logger.exception(
                    f"{self.__class__.__name__}: Optional artifact {art['name']} is "
                    "missing type key. Try to regenerate the recipe with a newer "
                    "version of queenbee-luigi."
                )
            output_type = art['type']
            logger.info(
                f"{self.__class__.__name__}: creating an empty {output_type} for "
                f"optional artifact {art['name']} at {artifact} ..."
            )
            if output_type == 'folder':
                artifact.mkdir(parents=True, exist_ok=True)
            else:
                artifact.write_text('')

    def _copy_output_artifacts(self, src):
        """Copy output artifacts to project folder.

        Args:
            src: Execution folder.
        """
        logger = self.get_interface_logger()
        for art in self.output_artifacts:
            logger.info(
                f"{self.__class__.__name__}: copying output artifact {art['name']} "
                f"to {art['to']} ..."
            )
            try:
                _copy_artifacts(os.path.join(src, art['from']), art['to'])
            except Exception:
                is_optional = art.get('optional', False)
                if is_optional:
                    continue
                logger.exception(
                    f"Failed to copy output artifact: {art['name']} to {art['to']} ..."
                )

    def _copy_output_parameters(self, src):
        """Copy output parameters to project folder.

        Args:
            src: Execution folder.
        """
        logger = self.get_interface_logger()
        for art in self.output_parameters:
            logger.info(
                f"{self.__class__.__name__}: copying output parameters {art['name']} "
                f"to {art['to']} ..."
            )
            _copy_artifacts(os.path.join(src, art['from']), art['to'])

    @property
    def _is_debug_mode(self):
        if '__debug__' not in self._input_params:
            return False
        return self._input_params['__debug__']

    def _get_dst_folder(self, command):
        debug_folder = self._is_debug_mode
        dst_dir = tempfile.TemporaryDirectory()
        dst = dst_dir.name
        if debug_folder:
            dst_dir = os.path.join(debug_folder, os.path.split(dst_dir.name)[-1])
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir, exist_ok=True)

            if SYSTEM == 'Windows':
                file_name = 'command.bat'
                content = '%s\npause' % command
            else:
                file_name = 'command.sh'
                content = '#!/bin/bash\nfunction pause(){\n\tread -p "$*"\n}' \
                    '\n%s\npause \'Press [Enter] key to continue...\'\n' % command

            command_file = os.path.join(dst_dir, file_name)
            with open(command_file, 'w') as outf:
                outf.write(content)

            os.chmod(command_file, 0o777)
            dst = dst_dir
        return dst_dir, dst

    def run(self):
        logger = self.get_interface_logger()

        # replace ' with " for Windows systems and vise versa for unix systems
        command = self.command()
        if SYSTEM == 'Windows':
            command = command.replace('\'', '"')
        else:
            command = command.replace('"', '\'')

        cur_dir = os.getcwd()
        dst_dir, dst = self._get_dst_folder(command)
        os.chdir(dst)

        self._copy_input_artifacts(dst)
        logger.info(f'Started running {self.__class__.__name__}...')

        p = subprocess.Popen(
            command, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, shell=True, env=os.environ
        )

        for line in iter(p.stdout.readline, b''):
            msg = line.decode('utf-8').strip()
            logger.info(msg)

        p.communicate()

        if p.returncode != 0:
            err_msg = f'\n\nFailed task: {self.__class__.__name__}.\n' \
                'Run the command with --debug key to debug the workflow.\n\n'
            logger.error(err_msg)
            raise ValueError(err_msg)

        # copy the results file back
        self._create_optional_output_artifacts(dst)
        self._copy_output_artifacts(dst)
        self._copy_output_parameters(dst)
        # change back to initial directory
        os.chdir(cur_dir)
        # delete the temp folder content
        try:
            dst_dir.cleanup()
            shutil.rmtree(dst_dir.name)
        except Exception:
            # folder is in use or running in debug mode
            # this is a temp folder so not deleting is not a major issue
            pass
        logger.info(f'Finished running {self.__class__.__name__}...')

    @staticmethod
    def load_input_param(input_param):
        """This function tries to import the values from a file as a Task input
            parameter.

        It first tries to import the content as a dictionary assuming the input file is
        a JSON file. If the import as JSON fails it will import the content as string and
        split them by next line. If there are several items it will return a list,
        otherwise it will return a single item.
        """
        content = ''
        with open(input_param, 'r') as param:
            try:
                content = json.load(param)
            except json.decoder.JSONDecodeError:
                # not a JSON file
                pass
            else:
                return content
        with open(input_param, 'r') as param:
            content = param.read().splitlines()
            if len(content) == 1:
                content = content[0]
        return content


def local_scheduler():
    """Check if luigi Daemon is running.

    If it does then return False otherwise return True.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 8082))
    except Exception:
        # luigi is running
        local_schedule = False
    else:
        # print('Using local scheduler')
        local_schedule = True
    finally:
        sock.close()
        return local_schedule


LOGS_CONFIG = """
[formatters]
keys: default

[loggers]
keys: root, luigi-interface

[handlers]
keys: console, logfile

[formatter_default]
format: %(asctime)s %(levelname)s: %(message)s
datefmt:%Y-%m-%d %H:%M:%S

[handler_console]
class: StreamHandler
args: [sys.stdout,]
formatter: default

[handler_logfile]
class: FileHandler
args: ['WORKFLOW.LOG',]
formatter: default

[logger_root]
level: WARNING
handlers: console, logfile
qualname: root
propagate=0

[logger_luigi-interface]
level: DEBUG
handlers: console, logfile
qualname: luigi-interface
propagate=0
"""
