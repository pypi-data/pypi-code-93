import tempfile
from typing import Optional, Union, Iterable, Text, IO, Any, Mapping
from unittest import TestCase

from click.testing import Result
from typer.testing import CliRunner as TyperCliRunner

from savvihub.api.savvihub import SavviHubClient
from savvihub.cli.commands.main import app
from savvihub.cli.git import GitRepository
from savvihub.cli.typer import Context
from savvihub.common import constants
from savvihub.common.utils import random_string


class CliRunner(TyperCliRunner):
    def invoke(
        self,
        args: Optional[Union[str, Iterable[str]]] = None,
        input: Optional[Union[bytes, Text, IO[Any]]] = None,
        env: Optional[Mapping[str, str]] = None,
        color: bool = False,
        allow_fail: bool = False,
        **extra: Any,
    ) -> Result:
        result = super().invoke(app, args, input, env, catch_exceptions=False, color=color, **extra)
        if not allow_fail:
            assert result.exit_code == 0, result.output
        return result


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        constants.TEST = True
        self._auto_savvi_init()
        self._monkey_patch(self.token, self.organization_name)
        self.runner = CliRunner()

    def _auto_savvi_init(self):
        # user init
        username = random_string()
        unauthorized_client = SavviHubClient()
        cli_token = unauthorized_client.signin_cli_token().cli_token
        jwt_token = unauthorized_client.signup_for_test_only(
            email=f'{username}@savvihub.test',
            username=username,
            name=username,
            password='testtest',
            invitation_token='invitation_token_for_cli_test',
        ).token

        jwt_client = SavviHubClient(auth_header={'Authorization': f'JWT {jwt_token}'})
        jwt_client.signin_confirm_for_test_only(cli_token=cli_token)

        check_signin_response = jwt_client.check_signin(cli_token)
        if not check_signin_response.signin_success:
            raise Exception('Signin Failed')

        # project init
        access_token_client = SavviHubClient(auth_header={'Authorization': f'Token {check_signin_response.access_token}'})
        organization_name = access_token_client.organization_list().organizations[0].name

        self.token = check_signin_response.access_token
        self.organization_name = organization_name

    @staticmethod
    def _monkey_patch(token, organization_name):
        class MockConfig:
            def __init__(self):
                self.token = token
                self.organization = organization_name

        def context_load(
            self,
            auth_required=False,
            user_required=False,
        ):
            mock_config = MockConfig()
            self.global_config = mock_config
            if auth_required:
                self.authenticated_client.verify_access_token()

            if user_required:
                self.user = self.authenticated_client.get_my_info()

        Context.load = context_load

        class MockGitRepo:
            @classmethod
            def enable(cls):
                GitRepository.check_revision_in_remote = cls.check_revision_in_remote
                GitRepository.get_commit_message = cls.get_commit_message
                GitRepository.get_current_diff_status = cls.get_current_diff_status
                GitRepository.get_current_diff_file = cls.get_current_diff_file
                GitRepository._get_remote_revision = cls.get_remote_revision

            def check_revision_in_remote(self, ref):
                return True

            def get_remote_revision(self):
                return 'dummy-ref', 'dummy-branch', False

            def get_commit_message(self, ref):
                return 'dummy-commit-message'

            def get_current_diff_status(self, ref):
                return True, {
                    'untracked': ['dummy-untracked-file.py', 'dummy-untracked-file.go'],
                    'uncommitted': ['dummy-uncommitted-file.py', 'dummy-uncommitted-file.go'],
                }

            def get_current_diff_file(self, git_ref, with_untracked=True):
                fp = tempfile.NamedTemporaryFile(suffix='.patch')
                fp.write('dummy-diff'.encode())
                return fp

        MockGitRepo.enable()
