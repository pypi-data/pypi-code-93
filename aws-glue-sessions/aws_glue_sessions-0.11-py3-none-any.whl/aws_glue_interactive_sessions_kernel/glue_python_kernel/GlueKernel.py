import uuid

try:
    from asyncio import Future
except ImportError:
    class Future(object):
        """A class nothing will use."""

import json
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import boto3
import botocore
from botocore.credentials import RefreshableCredentials
from botocore.session import get_session
from dateutil.tz import tzlocal

from ..glue_kernel_utils.GlueSessionsConstants import *
from hdijupyterutils.ipythondisplay import IpythonDisplay
from ipykernel.ipkernel import IPythonKernel
from IPython import get_ipython
from ..glue_kernel_utils.KernelMagics import KernelMagics


class GlueKernel(IPythonKernel):
    time_out = float('inf')
    session_id = None
    new_session_id = None
    glue_client = None
    implementation = 'Python Glue Session'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    language_info = {
        'name': 'Python_Glue_Session',
        'mimetype': 'text/x-python',
        'codemirror_mode': {'name': 'python', 'version': 3},
        'pygments_lexer': 'python3',
        'file_extension': '.py',
    }
    session_language = "python"
    ipython_display = None

    def __init__(self, **kwargs):
        super(GlueKernel, self).__init__(**kwargs)
        self.glue_role_arn = None
        self.profile = None
        self.endpoint_url = None
        self.region = None
        self.default_arguments = {
            "--enable-glue-datacatalog": "true"
        }
        self.enable_glue_datacatalog = None
        self.extra_py_files = None
        self.extra_jars = None
        self.additional_python_modules = None
        self.connections = defaultdict()
        self.security_config = None
        self.session_name = "AssumeRoleSession"
        self.max_capacity = None
        self.number_of_workers = 5
        self.worker_type ='G.1X'
        self.temp_dir = None
        self.job_type = "glueetl"
        self.idle_timeout = None

        if not self.ipython_display:
            self.ipython_display = IpythonDisplay()

        self._register_magics()

    async def do_execute(self, code: str, silent: bool, store_history=True, user_expressions=None, allow_stdin=False):
        code = await self._execute_magics(code, silent, store_history, user_expressions, allow_stdin)
        statement_id = None

        if not code:
            return await self._complete_cell()

        # Create glue client and session
        try:
            if not self.glue_client:

                # Attempt to retrieve default profile if a profile is not already set
                if not self.get_profile() and botocore.session.Session().full_config['profiles'].get('default'):
                    self.set_profile('default')

                self.glue_client = self.authenticate(glue_role_arn=self.get_glue_role_arn(), profile=self.get_profile())

            if not self.get_session_id() or self.get_current_session_status() in UNHEALTHY_SESSION_STATUS:
                self.create_session()
        except Exception as e:
            self.ipython_display.send_error(f'Exception encountered while creating session: {e} \n')
            self._print_traceback(e)
            return await self._complete_cell()

        try:
            # Run statement
            statement_id = self.glue_client.run_statement(SessionId=self.get_session_id(), Code=code)["Id"]
            start_time = time.time()

            try:
                while time.time() - start_time <= self.time_out:
                    statement = self.glue_client.get_statement(SessionId=self.get_session_id(), Id=statement_id)["Statement"]
                    if statement["State"] in FINAL_STATEMENT_STATUS:
                        statement_output = statement["Output"]
                        status = statement["State"]
                        reply_content = {
                            "execution_count": statement["Id"],
                            'user_expressions': {},
                            "payload": []
                        }

                        if status == AVAILABLE_STATEMENT_STATUS:
                            if statement_output["Status"] == "ok":
                                reply_content["status"] = u'ok'
                                self._send_output(statement_output["Data"]["TextPlain"])
                            else:
                                reply_content["status"] = u'error'
                                reply_content.update({
                                    u'traceback': statement_output["Traceback"],
                                    u'ename': statement_output["ErrorName"],
                                    u'evalue': statement_output["ErrorValue"],
                                })
                                self._send_output(f"{statement_output['ErrorName']}: {statement_output['ErrorValue']}")
                        elif status == ERROR_STATEMENT_STATUS:
                            self.ipython_display.send_error(statement_output)
                        elif status == CANCELLED_STATEMENT_STATUS:
                            self._send_output("This statement is cancelled")

                        return reply_content

                    time.sleep(WAIT_TIME)

                self.ipython_display.send_error(f"Timeout occurred with statement (statement_id={statement_id})")

            except KeyboardInterrupt:
                self._send_output(
                    f"Execution Interrupted. Attempting to cancel the statement (statement_id={statement_id})"
                )
                self._cancel_statement(statement_id)

        except Exception as e:
            self.ipython_display.send_error(f'Exception encountered while running statement: {e} \n')
            self._print_traceback(e)
            self._cancel_statement(statement_id)
            return await self._complete_cell()

    def authenticate(self, glue_role_arn=None, profile=None):
        # either an IAM role for Glue must be provided or a profile must be set
        if not glue_role_arn and not profile:
            raise ValueError(f'Neither glue_role_arn nor profile were provided')
        # region must be set
        if not self.get_region():
            raise ValueError(f'Region must be set.')
        # If we are using a custom endpoint
        if not self.get_endpoint_url():
            self.set_endpoint_url(f"https://glue.{self.get_region()}.amazonaws.com")
        if glue_role_arn:
            self.set_glue_role_arn(glue_role_arn)
        if profile:
            return self._authenticate_with_profile()
        else:
            self._send_output(f'Authenticating with environment variables and user-defined glue_role_arn: {glue_role_arn}')
            self.sts_client = boto3.Session().client('sts',
                                                     region_name = self.get_region(),
                                                     endpoint_url = self.get_endpoint_url())

            session_credentials = RefreshableCredentials.create_from_metadata(
                metadata=self._refresh(),
                refresh_using=self._refresh,
                method="sts-assume-role",
            )
            session = get_session()
            session._credentials = session_credentials
            session.set_config_variable("region", self.get_region())
            autorefresh_session = boto3.Session(botocore_session=session, region_name = self.get_region())

            return autorefresh_session.client("glue",
                                              region_name = self.get_region(),
                                              endpoint_url = self.get_endpoint_url())

    def _authenticate_with_profile(self):
        self._send_output(f'Authenticating with profile={self.get_profile()}')

        if self.get_profile() not in boto3.session.Session().available_profiles:
            raise ValueError(f'Profile {self.get_profile()} not defined in config')

        custom_role_arn = self._retrieve_from_aws_config('glue_role_arn')

        # Check if a glue_role_arn is defined in the profile and a custom glue_role_arn hasn't been defined
        if not self.get_glue_role_arn() and custom_role_arn is not None:
            self._send_output(f'glue_role_arn retrieved from profile: {custom_role_arn}')
            self.set_glue_role_arn(custom_role_arn)
        else:
            if self.get_glue_role_arn() is not None:
                self._send_output(f'glue_role_arn defined by user: {self.get_glue_role_arn()}')
            else:
                raise ValueError(f'glue_role_arn not present in profile and was not defined by user')

        self.sts_client = boto3.Session(profile_name=self.get_profile()).client('sts', region_name=self.get_region())

        session_credentials = RefreshableCredentials.create_from_metadata(
            metadata=self._refresh(),
            refresh_using=self._refresh,
            method="sts-assume-role",
        )
        session = get_session()
        session._credentials = session_credentials
        session.set_config_variable("region", self.get_region())
        autorefresh_session = boto3.Session(botocore_session=session, region_name = self.get_region())

        return autorefresh_session.client("glue",
                                          region_name = self.get_region(),
                                          endpoint_url = self.get_endpoint_url())

    def _retrieve_from_aws_config(self, key):
        custom_profile_session = botocore.session.Session(profile=self.get_profile())
        return custom_profile_session.full_config['profiles'][self.get_profile()].get(key)

    def _get_configs_from_profile(self):
        if not self.get_region():
            config_region = self._retrieve_from_aws_config('region')
            if config_region:
                self.set_region(config_region)
        if not self.get_glue_role_arn():
            config_glue_role_arn = self._retrieve_from_aws_config('glue_role_arn')
            if config_glue_role_arn:
                self.set_glue_role_arn(config_glue_role_arn)

    def configure(self, configs_json):
        updated_configs = dict()
        try:
            configs = json.loads("[" + configs_json + "]")[0]
            if 'profile' in configs:
                self.set_profile(configs.get('profile'))
                updated_configs['profile'] = configs.get('profile')
            if 'endpoint' in configs:
                self.set_endpoint_url(configs.get('endpoint'))
                updated_configs['endpoint'] = configs.get('endpoint')
            if 'region' in configs:
                self.set_region(configs.get('region'))
                updated_configs['region'] = configs.get('region')
            if 'iam_role' in configs:
                self.set_glue_role_arn(configs.get('iam_role'))
                updated_configs['iam_role'] = configs.get('iam_role')
            if 'session_id' in configs:
                self.set_new_session_id(configs.get('session_id'))
                updated_configs['session_id'] = configs.get('session_id')
            if 'max_capacity' in configs:
                self.set_max_capacity(configs.get('max_capacity'))
                updated_configs['max_capacity'] = configs.get('max_capacity')
            if 'number_of_workers' in configs:
                self.set_number_of_workers(configs.get('number_of_workers'))
                updated_configs['number_of_workers'] = configs.get('number_of_workers')
            if 'worker_type' in configs:
                self.set_worker_type(configs.get('worker_type'))
                updated_configs['worker_type'] = configs.get('worker_type')
            if 'extra_py_files' in configs:
                self.set_extra_py_files(configs.get('extra_py_files'))
                updated_configs['extra_py_files'] = configs.get('extra_py_files')
            if 'additional_python_modules' in configs:
                self.set_additional_python_modules(configs.get('additional_python_modules'))
                updated_configs['additional_python_modules'] = configs.get('additional_python_modules')
            if 'extra_jars' in configs:
                self.set_extra_jars(configs.get('extra_jars'))
                updated_configs['extra_jars'] = configs.get('extra_jars')
            if 'connections' in configs:
                self.set_connections(configs.get('connections'))
                updated_configs['connections'] = configs.get('connections')
            if 'enable_glue_datacatalog' in configs:
                self.set_enable_glue_datacatalog()
                updated_configs['enable_glue_datacatalog'] = configs.get('enable_glue_datacatalog')
            if 'security_config' in configs:
                self.set_security_config(configs.get('security_config'))
                updated_configs['security_config'] = configs.get('security_config')
            if 'extra_py_files' in configs:
                self.set_temp_dir(configs.get('temp_dir'))
                updated_configs['temp_dir'] = configs.get('temp_dir')
        except Exception as e:
            self.ipython_display.send_error(f'The following exception was encountered while parsing the configurations provided: {e} \n')
            self._print_traceback(e)
        if not updated_configs:
            self.ipython_display.send_error("No valid configuration values were provided.")
        else:
            self._send_output(f'The following configurations have been updated: {updated_configs}')

    def do_shutdown(self, restart):
        self.delete_session()
        return self._do_shutdown(restart)

    def _do_shutdown(self, restart):
        return super(GlueKernel, self).do_shutdown(restart)

    def set_profile(self, profile):
        self.profile = profile
        # Pull in new configs from profile
        self._get_configs_from_profile()

    def set_glue_role_arn(self, glue_role_arn):
        self.glue_role_arn = glue_role_arn

    def get_profile(self):
        return self.profile

    def get_glue_role_arn(self):
        return self.glue_role_arn

    def get_sessions(self):
        return self.glue_client.list_sessions()

    def get_session_id(self):
        return self.session_id

    def get_new_session_id(self):
        return self.new_session_id

    def set_session_id(self, session_id):
        self.session_id = session_id

    def set_new_session_id(self, new_session_id=None):
        self.new_session_id = self._generate_session_id(new_session_id)

    def set_endpoint_url(self, endpoint_url):
        self.endpoint_url = endpoint_url

    def get_endpoint_url(self):
        return self.endpoint_url

    def set_region(self, region):
        self.region = region

    def get_region(self):
        return self.region

    def set_job_type(self, job_type):
        self.job_type = job_type

    def get_job_type(self):
        return self.job_type

    def get_default_arguments(self):
        if self.get_enable_glue_datacatalog() is not None:
            self.default_arguments['--enable-glue-datacatalog'] = self.get_enable_glue_datacatalog()
        if self.get_extra_py_files() is not None:
            self.default_arguments['--extra-py-files'] = self.get_extra_py_files()
        if self.get_extra_jars() is not None:
            self.default_arguments['--extra-jars'] = self.get_extra_jars()
        if self.get_additional_python_modules() is not None:
            self.default_arguments['--additional-python-modules'] = self.get_additional_python_modules()
        if self.get_temp_dir() is not None:
            self.default_arguments['--TempDir'] = self.get_temp_dir()

        if self.default_arguments:
            self._send_output(f'Applying the following default arguments:')
            for arg, val in self.default_arguments.items():
                self._send_output(f'{arg} {val}')
        return self.default_arguments

    def get_enable_glue_datacatalog(self):
        return self.enable_glue_datacatalog

    def set_enable_glue_datacatalog(self):
        self.enable_glue_datacatalog = 'true'

    def get_extra_py_files(self):
        return self.extra_py_files

    def set_extra_py_files(self, extra_py_files):
        self.extra_py_files = extra_py_files

    def get_extra_jars(self):
        return self.extra_jars

    def set_extra_jars(self, extra_jars):
        self.extra_jars = extra_jars

    def get_additional_python_modules(self):
        return self.additional_python_modules

    def set_additional_python_modules(self, modules):
        self.additional_python_modules = modules

    def get_connections(self):
        return self.connections

    def set_connections(self, connections):
        self.connections["Connections"] = list(connections.split(','))

    def get_session_name(self):
        return self.session_name

    def get_max_capacity(self):
        return self.max_capacity

    def set_max_capacity(self, max_capacity):
        self.max_capacity = float(max_capacity)
        self.number_of_workers = None
        self.worker_type = None

    def get_number_of_workers(self):
        return self.number_of_workers

    def set_number_of_workers(self, number_of_workers):
        self.number_of_workers = int(number_of_workers)
        self.max_capacity = None

    def get_worker_type(self):
        return self.worker_type

    def set_worker_type(self, worker_type):
        self.worker_type = worker_type
        self.max_capacity = None

    def get_security_config(self):
        return self.security_config

    def set_security_config(self, security_config):
        self.security_config = security_config

    def get_temp_dir(self):
        return self.temp_dir

    def set_temp_dir(self, temp_dir):
        self.temp_dir = temp_dir

    def get_idle_timeout(self):
        return self.idle_timeout

    def set_idle_timeout(self, idle_timeout):
        self.idle_timeout = idle_timeout

    def get_session_id_prefix(self):
        return self._retrieve_from_aws_config('session_id_prefix');

    def _generate_session_id(self, custom_id=None):
        prefix = self.get_session_id_prefix();
        if prefix:
            if not custom_id:
                return f"{prefix}-{uuid.uuid4()}"
            return f"{prefix}-{custom_id}"
        else:
            if not custom_id:
                self.ipython_display.send_error(f'Either session ID, session ID prefix, or both values must be set. \n')
            return custom_id

    def disconnect(self):
        if self.get_session_id():
            session_id = self.get_session_id()
            self.set_session_id(None)
            self._send_output(f'Disconnected from session {session_id}')
        else:
            self.ipython_display.send_error(f'Not currently connected to a session. \n')

    def reconnect(self, session_id):
        if self.get_session_id():
            self.disconnect()
        self._send_output(f'Trying to connect to {session_id}')
        self.set_session_id(session_id)
        # Verify that this session exists.
        try:
            # TODO: create glue client if it doesn't exist
            self.glue_client.get_session(Id=self.get_session_id())
            self._send_output(f'Connected to {session_id}')
        except Exception as e:
            self.ipython_display.send_error(f'Exception encountered while connecting to session: {e} \n')
            self._print_traceback(e)

    def _refresh(self):
        # Refresh tokens by calling assume_role again
        params = {
            # "RoleArn": self.get_glue_role_arn(),
            # "RoleSessionName": self.get_session_name(),
            "DurationSeconds": 3600,
        }
        try:
            response = self.sts_client.get_session_token(**params).get("Credentials")
            credentials = {
                "access_key": response.get("AccessKeyId"),
                "secret_key": response.get("SecretAccessKey"),
                "token": response.get("SessionToken"),
                "expiry_time": response.get("Expiration").isoformat(),
            }
            return credentials
        except Exception as e:
            self._send_output('Attempting to use existing AssumeRole session credentials.')
            session = boto3.Session()
            response = session.get_credentials()
            credentials = {
                "access_key": response.access_key,
                "secret_key": response.secret_key,
                "token": response.token,
                "expiry_time": datetime(2099, 1, 1, ).replace(tzinfo=timezone.utc).isoformat(),
            }
            return credentials

    def create_session(self):
        self._send_output("Trying to create a Glue session for the kernel.")
        if self.get_max_capacity() and (self.get_number_of_workers() and self.get_worker_type()):
            raise ValueError(f'Either max_capacity or worker_type and number_of_workers must be set, but not both.')

        # Generate new session ID with UUID if no custom ID is set
        if not self.get_new_session_id():
            self.set_new_session_id()
            if not self.get_new_session_id():
                raise ValueError(f'Session ID was not set.')


        self._send_output(f"Worker Type: {self.get_worker_type()}")
        self._send_output(f"Number of Workers: {self.get_number_of_workers()}")
        self._send_output(f"Session ID: {self.get_new_session_id()}")

        additional_args = self._get_additional_arguments()

        self.set_session_id(self.glue_client.create_session(
            Role=self.get_glue_role_arn(),
            DefaultArguments=self.get_default_arguments(),
            Connections=self.get_connections(),
            Id=self.get_new_session_id(),
            Command={
                "Name": self.get_job_type(),
                "PythonVersion": "3"
            },
        **additional_args)["Session"]["Id"])

        self._send_output(f'Waiting for session {self.get_session_id()} to get into ready status...')
        is_ready = False
        start_time = time.time()
        while time.time() - start_time <= self.time_out and not is_ready:
            if self.get_current_session_status() == READY_SESSION_STATUS:
                is_ready = True
            time.sleep(WAIT_TIME)

        if not is_ready:
            self.ipython_display.send_error(f"Session failed to reach ready status in {self.time_out}s")
        else:
            self._send_output(f"Session {self.get_session_id()} has been created")

    def _get_additional_arguments(self):
        additional_args = {}
        if self.get_max_capacity():
            additional_args['MaxCapacity'] = self.get_max_capacity()
        if self.get_number_of_workers():
            additional_args['NumberOfWorkers'] = self.get_number_of_workers()
        if self.get_worker_type():
            additional_args['WorkerType'] = self.get_worker_type()
        if self.get_security_config():
            additional_args['SecurityConfiguration'] = self.get_security_config()
        if self.get_idle_timeout():
            additional_args['IdleTimeout'] = self.get_idle_timeout()
        return additional_args

    def delete_session(self):
        if self.get_session_id():
            try:
                self._send_output(f'Terminating session: {self.get_session_id()}')
                # TODO: how do we delete session if our security token expires?
                self.glue_client.delete_session(Id=self.get_session_id())
                self.glue_client = None
                self.set_session_id(None)
            except Exception as e:
                self.ipython_display.send_error(f'Exception encountered while terminating session {self.get_session_id()}: {e} \n')
                self._print_traceback(e)


    def _cancel_statement(self, statement_id: str):
        if not statement_id:
            return

        try:
            self.glue_client.cancel_statement(SessionId=self.get_session_id(), Id=statement_id)
            start_time = time.time()
            is_ready = False

            while time.time() - start_time <= self.time_out and not is_ready:
                status = self.glue_client.get_statement(SessionId=self.get_session_id(), Id=statement_id)["Statement"]["State"]

                if status == CANCELLED_STATEMENT_STATUS:
                    self._send_output(f"Statement {statement_id} has been cancelled")
                    is_ready = True

                time.sleep(WAIT_TIME)

            if not is_ready:
                self.ipython_display.send_error(f"Failed to cancel the statement {statement_id}")
        except Exception as e:
            self.ipython_display.send_error(f'Exception encountered while canceling statement {statement_id}: {e} \n')
            self._print_traceback(e)

    def get_current_session_status(self):
        try:
            return self.get_current_session()["Status"]
        except Exception as e:
            self.ipython_display.send_error(f'Failed to retrieve session status \n')

    def get_current_session_duration_in_seconds(self):
        try:
            time_in_seconds =  datetime.now(tzlocal()) - self.get_current_session()["CreatedOn"]
            return time_in_seconds.total_seconds()
        except Exception as e:
            self.ipython_display.send_error(f'Failed to retrieve session duration \n')

    def get_current_session_role(self):
        try:
            return self.get_current_session()["Role"]
        except Exception as e:
            self.ipython_display.send_error(f'Failed to retrieve session role \n')

    def get_current_session(self):
        if self.get_session_id() is None:
            self.ipython_display.send_error(f'No current session.')
        else:
            try:
                current_session = self.glue_client.get_session(Id=self.get_session_id())["Session"]
                return NOT_FOUND_SESSION_STATUS if not current_session else current_session
            except Exception as e:
                self.ipython_display.send_error(f'Exception encountered while retrieving session: {e} \n')
                self._print_traceback(e)

    def _send_output(self, output):
        stream_content = {'name': 'stdout', 'text': f"{output}\n"}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    async def _do_execute(self, code, silent, store_history, user_expressions, allow_stdin):
        res = await self._execute_cell(code, silent, store_history, user_expressions, allow_stdin)
        return res

    async def _execute_cell(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        reply_content = await self._execute_cell_for_user(code, silent, store_history, user_expressions, allow_stdin)
        return reply_content

    async def _execute_cell_for_user(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        result = await super(GlueKernel, self).do_execute(code, silent, store_history, user_expressions, allow_stdin)
        if isinstance(result, Future):
            result = result.result()
        return result

    async def _execute_magics(self, code, silent, store_history, user_expressions, allow_stdin):
        try:
            magic_lines = 0
            lines = code.splitlines()
            for line in lines:
                # If there is a cell magic, we simply treat all the remaining code as part of the cell magic
                if any(line.startswith(cell_magic) for cell_magic in CELL_MAGICS):
                    code = '\n'.join(lines[magic_lines:])
                    await self._do_execute(code, silent, store_history, user_expressions, allow_stdin)
                    return None
                # If we encounter a line magic, we execute this line magic and continue
                if line.startswith("%") or line.startswith("!"):
                    await self._do_execute(line, silent, store_history, user_expressions, allow_stdin)
                    magic_lines += 1
                # We ignore comments and empty lines
                elif line.startswith("#") or not line:
                    magic_lines += 1
                else:
                    break
            code = '\n'.join(lines[magic_lines:])
            return code
        except Exception as e:
            self.ipython_display.send_error(f'Exception encountered: {e} \n')
            self._print_traceback(e)
            return await self._complete_cell()

    async def _complete_cell(self):
        """A method that runs a cell with no effect. Call this and return the value it
        returns when there's some sort of error preventing the user's cell from executing; this
        will register the cell from the Jupyter UI as being completed."""
        return await self._execute_cell("None", False, True, None, False)

    def _register_magics(self):
        ip = get_ipython()
        magics = KernelMagics(ip, '', self)
        ip.register_magics(magics)

    def _print_traceback(self, e):
        traceback.print_exception(type(e), e, e.__traceback__)

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=GlueKernel)
