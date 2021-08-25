import os
import re

from biolib import cli_utils
from biolib.app.utils import run_job
from biolib.biolib_api_client import JobState
from biolib.biolib_api_client.app_types import App, AppVersionSlim
from biolib.biolib_api_client.biolib_job_api import BiolibJobApi
from biolib.app.completed_process import CompletedProcess
from biolib.app.types import SemanticVersion, ParsedAppUri
from biolib.biolib_api_client.biolib_app_api import BiolibAppApi
from biolib.biolib_binary_format import ModuleInput
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class BioLibApp:

    def __init__(self, uri: str):
        parsed_uri = self._parse_uri(uri)

        self._app: App = BiolibAppApi.fetch_by_name(parsed_uri['account_handle'], parsed_uri['name'])

        if parsed_uri['version'] is None:
            self._selected_app_version: AppVersionSlim = self._app['active_version']
        else:
            parsed_version: SemanticVersion = parsed_uri['version']

            for version in self._app['app_versions']:
                if (
                        version['major'] == parsed_version['major'] and
                        version['minor'] == parsed_version['minor'] and
                        version['patch'] == parsed_version['patch']
                ):
                    self._selected_app_version = version
                    break

            if self._selected_app_version is None:
                raise Exception('Could not find application version referenced in URI')

        # TODO: Consider logging semantic app version here
        logger.info(f"Loaded package: {self._app['account_handle']}/{self._app['name']}")

    def __call__(self, args=None, stdin=None, files=None):
        module_input_serialized = self._get_serialized_module_input(args, stdin, files)

        job = BiolibJobApi.create(self._selected_app_version['public_id'])
        BiolibJobApi.update_state(job['public_id'], JobState.IN_PROGRESS.value)

        try:
            module_output = run_job(job, module_input_serialized)

            cli_utils.write_output_files(mapped_output_files=module_output['files'])

            try:
                BiolibJobApi.update_state(job_id=job['public_id'], state=JobState.COMPLETED.value)
            except Exception as error:  # pylint: disable=broad-except
                logger.warning(f'Could not update job state to completed:\n{error}')

            return CompletedProcess(
                exitcode=module_output['exit_code'],
                stderr=module_output['stderr'],
                stdout=module_output['stdout'],
            )

        except BioLibError as exception:
            logger.error(f'Compute failed with: {exception.message}')
            try:
                BiolibJobApi.update_state(job_id=job['public_id'], state=JobState.FAILED.value)
            except Exception as error:  # pylint: disable=broad-except
                logger.warning(f'Could not update job state to failed:\n{error}')

            raise exception

    @staticmethod
    def _get_serialized_module_input(args=None, stdin=None, files=None) -> bytes:
        if args is None:
            args = []

        if stdin is None:
            stdin = b''

        if isinstance(args, str):
            args = list(filter(lambda p: p != '', args.split(' ')))

        if not isinstance(args, list):
            raise Exception('The given input arguments must be list or str')

        if isinstance(stdin, str):
            stdin = stdin.encode('utf-8')

        if files is None:
            files = []
            for idx, arg in enumerate(args):
                if os.path.isfile(arg):
                    files.append(arg)
                    args[idx] = arg.split('/')[-1]

        cwd = os.getcwd()
        files_dict = {}

        for file in files:
            path = file
            if not file.startswith('/'):
                # make path absolute
                path = cwd + '/' + file

            arg_split = path.split('/')
            file = open(path, 'rb')
            path = '/' + arg_split[-1]

            files_dict[path] = file.read()
            file.close()

        module_input_serialized: bytes = ModuleInput().serialize(stdin=stdin, arguments=args, files=files_dict)
        return module_input_serialized

    @staticmethod
    def _parse_uri(uri: str) -> ParsedAppUri:
        uri_regex = r'((https:\/\/)?biolib\.com\/)?(?P<account>[\w-]+)\/(?P<name>[\w-]+)(\/version\/' \
                    r'(?P<version>(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)))?(\/)?'

        matches = re.search(uri_regex, uri)
        if matches is None:
            raise Exception('Application URI was incorrectly formatted. Please use the format: account_handle/app_name')

        return ParsedAppUri(
            account_handle=matches.group('account'),
            name=matches.group('name'),
            version=None if not matches.group('version') else SemanticVersion(
                major=int(matches.group('major')),
                minor=int(matches.group('minor')),
                patch=int(matches.group('patch')),
            )
        )
