# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Main SLC library API entry point."""

import os
import shutil
import tempfile
import six

_SLC_instance = None
def get_instance():
    """Return current instanceof of SpirentSLC"""
    return _SLC_instance


from sys import platform as _platform
from . import config as cfg
from .exception import SLCError
from .internal.protocol import ProtocolSocket
from .project import Project
from .builtin_sessions import BuiltinSession
from .python_name import python_name
from .session_response import SessionActionResponse, DelegatingResponse
from .session_profile import _to_property_group

if _platform == "win32" or _platform == "win64":
    try:
        from ctypes import create_unicode_buffer, windll
        def _to_long_name(file_name):
            if not ('~' in file_name and os.path.exists(file_name)):
                return file_name
            try:
                buf = create_unicode_buffer(32768)
                rv = windll.kernel32.GetLongPathNameW(file_name.encode('utf-8').decode('mbcs'), buf, 32768)
                if rv == 0 or rv > 260:
                    return file_name
                ret_file_name = buf.value
                if os.path.exists(ret_file_name):
                    return ret_file_name
            except: # any exception should be skipped
                pass
            return file_name
    except ImportError:
        def _to_long_name(file_name):
            return file_name
else:
    def _to_long_name(file_name):
        return file_name

try:
    import subprocess
    from subprocess import DEVNULL # Python 3.x
except ImportError:
    DEVNULL = open(os.devnull, 'wb')

_DEBUG_SLC = False

try:
    from urlparse import urlparse
except ImportError:
    # in Python 3, urlparse renamed to urllib.parse
    # pylint: disable=no-name-in-module,import-error
    from urllib.parse import urlparse

# pylint: disable=invalid-name

class _SLC(object):
    """A private class to represent SLC.

    Objects of this class should not be created directly, but rather obtained via the init() function below.
    """

    def __init__(self, isLocal, host, port, agent_path, itar_path, license_server):
        self._closed = False
        global _SLC_instance

        if _SLC_instance:
            raise SLCError('Multiple instances of SLC are not supported')

        self._agent_path = agent_path

        self.agent_log_file = None

        if isLocal:
            if agent_path.endswith('/') or agent_path.endswith('\\'):
                # remove last '/' from path
                agent_path = agent_path[:-1]

            if _platform == "darwin":
                # we need to check path is correct for macos
                if os.path.isdir(agent_path) and not agent_path.endswith('/Contents/Eclipse'):
                    agent_path += '/Contents/Eclipse/'

            agent_jre = agent_path + os.sep + 'jre'

            java_bin = None
            self.temp_dir =  _to_long_name(tempfile.mkdtemp('velocity_agent'))
            self.agent_data_dir = self.temp_dir + os.sep + '@no'
            self.agent_log_file_name = self.temp_dir + os.sep + 'agent.log'
            self.agent_log_file = open(self.agent_log_file_name, 'w')

            tmp_param = '-Djava.io.tmpdir=' + tempfile.gettempdir()
            if _platform == "linux" or _platform == "linux2":
                # linux
                java_bin = agent_jre +'/bin/java'
            elif _platform == "darwin":
                # MAC OS X
                java_bin = agent_jre +'/Contents/Home/jre/bin/java'
            elif _platform == "win32":
                # Windows
                java_bin = agent_jre +'\\bin\\java.exe'
            elif _platform == "win64":
                # Windows 64-bit
                java_bin = agent_jre +'\\bin\\java.exe'

            if not os.path.isfile(java_bin):
                java_bin = 'java'

            if os.path.isfile(agent_path):
                agent_path = os.path.dirname(agent_path)
            if not os.path.isdir(agent_path):
                raise SLCError('Agent is not found at: ' + agent_path + "\nAborting... Please verify: SPIRENT_SLC_AGENT_PATH environemnt variable")

            self.agent_args = [java_bin,
                          '-Xmx512M',
                          '-Dfile.encoding=UTF-8',
                          '-XX:MaxMetaspaceSize=128M',
                          '-Dorg.eclipse.emf.ecore.plugin.EcorePlugin.doNotLoadResourcesPlugin=true',
                          '-Djava.awt.headless=true',
                          tmp_param,
                          '-jar', agent_path + os.sep + 'plugins' + os.sep +
                            'org.eclipse.equinox.launcher_1.5.700.v20200207-2156.jar',
                          '-consoleLog', '-data', self.agent_data_dir]
            self.agent_extra_args = [   '--agentVelocityHost', host,
                                        '--sfAgentServerPort', str(port),
                                        '--listeningMode', 'library',
                                        '--sfAgentDisableSslValidation']


            if license_server != None:
                self.agent_extra_args.append('--licenseServer')
                self.agent_extra_args.append(license_server)
            else:
                raise SLCError('Please specify a valid SPIRENT_SLC_LICENSE_SERVER environment variable value in format host[:port]')

            if itar_path != None:
                # print('add itar_path:', itar_path)
                self.agent_extra_args.append('--itar')
                self.agent_extra_args.append(itar_path)

            if cfg.is_verbose_mode():
                print('--->Agent verbose output\n')
                print("JAVA_BIN: " + str(java_bin))
                print("Starting velocity agent:\nPATH:" + str(agent_path))
                print("LOG FILE: " + str(self.agent_log_file.name))
                print("ITARPATH:" + str(itar_path))
                print("ARGUMENTS:\n\t" + '\n\t'.join(self.agent_extra_args))
                print('--->')

            final_args = self.agent_args + self.agent_extra_args
            self.agent_log_file.write('Starting java with arguments:\n' + ' '.join(final_args) + '\n\n\n')
            self.agent_log_file.flush()

            self._agent_process = subprocess.Popen( final_args, stdin=None, stderr=subprocess.STDOUT, stdout=self.agent_log_file, shell=False)
            self._agent_type = "local"
        else:
            self._agent_process = None

            # agent type will be updated based on information retrieved from agent itself.
            self._agent_type = 'remote'
        self._protosock = None
        try:
            self._protosock = ProtocolSocket(host, port, cfg.get_agent_start_timeout(), self._agent_process)
        except:
            if self.agent_log_file != None:
                # Be sure we try terminate started agent

                print('\n\nERROR:\nFailure during Velocity Agent startup. Please refer to a log file created:\n\'' + self.agent_log_file_name + '\'')
                self.agent_log_file.close()

                ## Read and display last 50 lines of log.

                with open(self.agent_log_file_name, 'r') as file:
                    lines = file.readlines()
                    if len(lines) > 50:
                        lines = lines[-50:]

                    msg = '\n'.join(lines)
                    print('\nLast lines of Velocoty Agent log:\n',msg)

                self.agent_log_file = None
                # Also terminate velocity agent if error is happed during connection
                self.close()
            raise

        self._responses = dict()
        self._sessions = dict()
        self._projects = dict()
        self._sync_projects()

        self.sessions = BuiltinSession(self._protosock, self._agent_type)

        _SLC_instance = self

    def _sync_projects(self):
        processed = []
        for project in self._protosock.list_projects():
            # TODO: All spaces in the name of a project or any other characters that are not legal in a Python identifier should be replaced by underscores
            # TODO: duplicates after replacing
            py_project_name = python_name(project)
            processed.append(py_project_name)
            if not py_project_name in self._projects.keys():
                self._projects[py_project_name] = Project(project, self._protosock, self._agent_type)

        # Remove all projects not available anymore
        for project in list(self._projects.keys()):
            if not project in processed:
                del self._projects[project]


    def list(self):
        """Returns a list of names of all projects."""
        self._sync_projects()
        return self._projects.keys()

    def __dir__(self):
        """ return a list of methods available to project"""
        if hasattr(super,'__dir__'):
            super_dir = super.__dir__(self)
        else:
            super_dir = []
        res = super_dir + list(self.list())
        return res

    def open(self, projectName):
        """Opens a project.

        Arguments:
        projectName -- project name.

        Returns the project. If project name is None, empty or not present in the projects' list, raises ValueError.
        """
        projectName = python_name(projectName)
        if not projectName in self._projects:
            raise SLCError('Failed to find project with name: ' + projectName)
        return self._projects[projectName].open()

    def encrypt(self, value):
        """Returns an encrypted value that is used as masked property value.
        """
        return self._protosock.encrypt(value)

    def __getitem__(self, key):
        """
            Allow to return a project by name and call open() over it.
        """
        if self._protosock is None:
            return None

        prj = self._projects.get(key)
        if prj:
            return prj

        return None

    def __getattr__(self, key):
        """
            Allow to return a project by name and call open() over it.
        """
        ret = self[key]
        if ret == None:
            raise AttributeError(key)
        return ret

    def __del__(self):
        """ A proper destruction of SLC used structures"""
        self.close()

    def close(self):
        """Closes SLC.

        Underlying connections are dropped (if any) and processes are terminated (if any).
        """

        if self._closed:
            return

        global _SLC_instance

        if _SLC_instance is None:
            return

        _SLC_instance = None

        self._closed = True

        if cfg.is_verbose_mode():
            print("Closing SLC...")


        protosock = self._protosock
        self._protosock = None
        if protosock:
            protosock.close()

        p = self._agent_process
        self._agent_process = None
        if p:
            p.kill()
            if six.PY2:
                p.wait()
            else:
                p.wait(timeout=30)

        # remove Agent logs
        if self.agent_log_file != None:
            self.agent_log_file.close()
            os.remove(self.agent_log_file_name)
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            self.agent_log_file_name = None
            self.agent_log_file = None
    def __enter__(self):
        """ SLC could be used with 'with' as section. """
        return self

    def __exit__(self, *args):
        """ Automatically close then leave with section. """
        self.close()


    def is_open(self):
        """ Check if SLC connection is alive"""
        return self._protosock != None and self._protosock.is_open()

    def response(self, response_body=None, properties=None):
        if response_body:
            message = self._protosock.map_response(response_body, _to_property_group(properties))
            return SessionActionResponse(message)
        return DelegatingResponse(self, properties)

    def char_command(self, char_code):
        message = self._protosock.char_command(char_code)
        return SessionActionResponse(message)

    def jsonselect_command(self, json, query):
        message = self._protosock.jsonselect_command(json, query)
        return SessionActionResponse(message)

    def velocity_command(self, subcommand, *argv):
        message = self._protosock.velocity_command(subcommand, *argv)
        return SessionActionResponse(message)

    def xpath_eval_command(self, query):
        message = self._protosock.xpath_eval_command(query)
        return SessionActionResponse(message)

    def info_command(self, subcommand, *argv):
        message = self._protosock.info_command(subcommand, *argv)
        return SessionActionResponse(message)

    def file_path_to_uri_command(self, path):
        message = self._protosock.file_path_to_uri_command(path)
        return SessionActionResponse(message)

    def file_uri_to_path_command(self, uri):
        message = self._protosock.file_uri_to_path_command(uri)
        return SessionActionResponse(message)

    def tbml_command(self, subcommand, *argv):
        message = self._protosock.tbml_command(subcommand, *argv)
        return SessionActionResponse(message)

    def decrypt(self, value):
        message = self._protosock.decrypt(value)
        return SessionActionResponse(message).text

    def quote(self, uri):
        message = self._protosock.quote(uri)
        return SessionActionResponse(message)

def _parse_host_port(host_port):
    """Parse a "host:port" string and returns (host, port) pair

    Arguments:
    host_port -- a string of the "host:port" format

    Return (host, port) pair. If the given string does not comply with the pattern "host:port", one or both components
    of the pair returned may be None.
    """

    url = urlparse('http://' + host_port)       # we need some schema for urlparse to work
    return (url.hostname, url.port)


def init(host=None, agent_path=None, itar_path=None, license_server=None, license_proxy=None, password=None):
    """Initialises and returns an SLC object.

    Arguments:
    host -- SLC host to connect to in a form of 'host:port' string. Env var: SPIRENT_SLC_HOST. Default: 'local', which
            means the library is to run its own instance of the Velocity agent.
            If env var: SPIRENT_SLC_PORT_OVERRIDE is specified and host is localhost, port will be changed to value
            from environment variable. This is required for execurion of testcase from Velocity.


    password -- password to connect to SLC. Env var: SPIRENT_SLC_PASSWORD. Default: no password.

    agent_path -- path to the 'velocity-agent' executable. Env var: SPIRENT_SLC_AGENT_PATH.
                  Default: find 'velocity-agent' in PATH.
                  If the agent is not found, and 'host' specifies 'local', SLCError is raised.
    itar_path -- path to location of local itar's. will use ITAR_PATH environment variable if not specified.
                In case of relative path, current working directory will be used to construct absolute path.

    license_server -- a host[:port] of license server.

    license_proxy -- a deprecated parameter, will not take any effect since v7.2.

    All arguments are optional. If something is not specified, the value is taken from the respective environment
    variable. If the respective environment variable is not set, the respective default value is used.

    Returns an SLC object.

    Only one SLC object (or none at all) may exist at a time. First time this function is called, it is created.
    After that, unless the object is closed via it's close() method, the same object is returned.
    If the returned object gets closed, the next init() call will create a new one.
    """

    if _SLC_instance:
        return _SLC_instance

    if not host:
        host = cfg.get_agent_host_port()

    isLocal = host == 'local'
    if isLocal:
        host = cfg.get_local_agent_host_port()

    host, port = _parse_host_port(host)

    override_port = cfg.get_local_agent_port_override()
    if (host == "localhost" or host == "127.0.0.1") and override_port != '0':
        port = override_port

    if not agent_path:
        agent_path = cfg.get_agent_path()
    if not agent_path and isLocal:
        raise SLCError('agentPath is not specified and SPIRENT_SLC_AGENT_PATH environment variable is not set')

    if itar_path is None:
        itar_path = cfg.get_itar_path()
    else:
        # Check if it is relative path we need to add current script directory
        if not os.path.isabs(itar_path):
            itar_path = os.getcwd() + os.sep + itar_path

    if license_server is None:
        license_server = cfg.get_license_server()

    return _SLC(isLocal, host, port, agent_path, itar_path, license_server)
