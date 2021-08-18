from __future__ import print_function

from .GlueSessionsConstants import *
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class

@magics_class
class KernelMagics(Magics):

    def __init__(self, shell, data, kernel):
        super(KernelMagics, self).__init__(shell)
        self.data = data
        self.kernel = kernel

    @line_magic('iam_role')
    def set_iam_role(self, glue_role_arn):
        self._validate_magic()
        self.kernel._send_output(f'Current glue_role_arn is {self.kernel.get_glue_role_arn()}')
        self.kernel.set_glue_role_arn(glue_role_arn)
        self.kernel._send_output(f'glue_role_arn has been set to {glue_role_arn}.')

    @line_magic('idle_timeout')
    def set_idle_timeout(self, idle_timeout=None):
        self._validate_magic()
        self.kernel._send_output(f'Current idle_timeout is {self.kernel.get_idle_timeout()}')
        self.kernel.set_idle_timeout = idle_timeout
        self.kernel._send_output(f'idle_timeout has been set to {idle_timeout} minutes.')

    @line_magic('reauthenticate')
    def reauthenticate(self, line=None):
        glue_role_arn = self.kernel.get_glue_role_arn()
        if line:
            glue_role_arn = line
        self.kernel._send_output(f'IAM role has been set to {glue_role_arn}. Reauthenticating.')
        new_client = self.kernel.authenticate(glue_role_arn=glue_role_arn, profile=self.kernel.get_profile())
        self.kernel.glue_client = new_client
        self.kernel.create_session()

    @line_magic('new_session')
    def new_session(self, line=None):
        self.kernel.delete_session()
        self.kernel._send_output(f'Creating new session.')
        new_client = self.kernel.authenticate(glue_role_arn=self.kernel.get_glue_role_arn(), profile=self.kernel.get_profile())
        self.kernel.glue_client = new_client
        self.kernel.create_session()

    @line_magic('profile')
    def set_profile(self, profile):
        self._validate_magic()
        self.kernel._send_output(f'Previous profile: {self.kernel.get_profile()}')
        self.kernel._send_output(f'Setting new profile to: {profile}')
        self.kernel.set_profile(profile)

    @line_magic('status')
    def get_status(self, line=None):
        if not self.kernel.get_session_id():
            self.kernel._send_output('There is no current session.')
            return
        status = self.kernel.get_current_session_status()
        duration = self.kernel.get_current_session_duration_in_seconds()
        role = self.kernel.get_current_session_role()
        session_id = self.kernel.get_current_session()['Id']
        created_on = self.kernel.get_current_session()['CreatedOn']
        self.kernel._send_output(f'Session ID: {session_id}')
        self.kernel._send_output(f'Status: {status}')
        self.kernel._send_output(f'Duration: {duration} seconds')
        self.kernel._send_output(f'Role: {role}')
        self.kernel._send_output(f'CreatedOn: {created_on}')

    @line_magic('list_sessions')
    def list_sessions(self, line=None):
        if not self.kernel.get_session_id():
            self.kernel._send_output('There is no current session.')
            return
        ids = self.kernel.get_sessions().get('Ids')
        self.kernel._send_output(f'There are currently {len(ids)} active sessions:')
        for id in ids:
            self.kernel._send_output(id)

    @line_magic('delete_session')
    def delete_session(self, line=None):
        if not self.kernel.get_session_id():
            self.kernel._send_output('There is no current session.')
            return
        self.kernel.delete_session()
        self.kernel._send_output(f'Deleted session.')

    @line_magic('session_id')
    def set_session_id(self, line=None):
        if not self.kernel.get_session_id():
            self.kernel._send_output('There is no current session.')
        else:
            self.kernel._send_output(f'Current active Session ID: {self.kernel.get_session_id()}')
        self.kernel.set_new_session_id(line)
        self.kernel._send_output(f'Setting session ID to {self.kernel.get_new_session_id()}. You must connect to a session with this ID before this ID becomes the active Session ID.')


    @line_magic('enable_glue_datacatalog')
    def set_enable_glue_datacatalog(self, line=None):
        self._validate_magic()
        self.kernel._send_output("Enabling Glue DataCatalog")
        self.kernel.set_enable_glue_datacatalog()

    @line_magic('extra_py_files')
    def set_extra_py_files(self, line=None):
        self._validate_magic()
        self.kernel._send_output("Adding the following:")
        for s3_path in line.split(','):
            self.kernel._send_output(s3_path)
        self.kernel.set_extra_py_files(line)

    @line_magic('additional_python_modules')
    def set_additional_python_modules(self, line=None):
        self._validate_magic()
        self.kernel._send_output("Adding the following:")
        for s3_path in line.split(','):
            self.kernel._send_output(s3_path)
        self.kernel.set_additional_python_modules(line)

    @line_magic('extra_jars')
    def set_extra_jars(self, line=None):
        self._validate_magic()
        self.kernel._send_output("Adding the following:")
        for s3_path in line.split(','):
            self.kernel._send_output(s3_path)
        self.kernel.set_extra_jars(line)

    @line_magic('temp_dir')
    def set_temp_dir(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f"Setting temporary directory to: {line}")
        self.kernel.set_temp_dir(line)

    @line_magic('connections')
    def set_connections(self, line=None):
        self._validate_magic()
        self.kernel._send_output("Adding the following:")
        for connection in line.split(','):
            self.kernel._send_output(connection)
        self.kernel.set_connections(line)

    @line_magic('endpoint')
    def set_endpoint(self, line=None):
        self.kernel._send_output(f'Previous endpoint: {self.kernel.get_endpoint_url()}')
        self.kernel._send_output(f'Setting new endpoint to: {line}')
        self.kernel.set_endpoint_url(line)

    @line_magic('region')
    def set_region(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f'Previous region: {self.kernel.get_region()}')
        self.kernel._send_output(f'Setting new region to: {line}')
        self.kernel.set_region(line)

    @line_magic('max_capacity')
    def set_max_capacity(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f'Previous max capacity: {self.kernel.get_max_capacity()}')
        self.kernel._send_output(f'Setting new max capacity to: {float(line)}')
        self.kernel.set_max_capacity(line)

    @line_magic('number_of_workers')
    def set_number_of_workers(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f'Previous number of workers: {self.kernel.get_number_of_workers()}')
        self.kernel._send_output(f'Setting new number of workers to: {int(line)}')
        self.kernel.set_number_of_workers(line)

    @line_magic('worker_type')
    def set_worker_type(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f'Previous worker type: {self.kernel.get_worker_type()}')
        self.kernel._send_output(f'Setting new worker type to: {line}')
        self.kernel.set_worker_type(line)

    @line_magic('security_config')
    def set_security_config(self, line=None):
        self._validate_magic()
        self.kernel._send_output(f'Previous security_config: {self.kernel.get_security_config()}')
        self.kernel._send_output(f'Setting new security_config to: {line}')
        self.kernel.set_security_config(line)

    @line_magic('disconnect')
    def disconnect(self, line=None):
        self.kernel.disconnect()

    @line_magic('reconnect')
    def reconnect(self, line=None):
        self.kernel.reconnect(line)

    @line_magic('job_type')
    def set_job_type(self, line=None):
        self.kernel.set_job_type(line)

    @cell_magic('sql')
    def run_sql(self, line=None, cell=None):
        if line == 'show':
            code = f'spark.sql(\'{cell.rstrip()}\').show()'
            self.kernel.do_execute(code, False, True, None, False)
        else:
            code = f'spark.sql(\'{cell.rstrip()}\')'
            self.kernel.do_execute(code, False, True, None, False)

    @cell_magic('configure')
    def configure(self, line=None, cell=None):
        self._validate_magic()
        self.kernel.configure(cell)

    @line_magic('help')
    def help(self, line=None):
        self.kernel._send_output(HELP_TEXT)

    def _validate_magic(self):
        session_id = self.kernel.get_session_id()
        if session_id:
            self.kernel._send_output(f"You are already connected to session {session_id}. Your change will not reflect in the current session, but it will affect future new sessions. \n")
