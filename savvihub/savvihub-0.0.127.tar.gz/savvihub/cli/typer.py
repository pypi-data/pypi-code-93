from collections import defaultdict
import os
import sys
import traceback
from cached_property import cached_property
from typing import Optional

import click
import typer

from openapi_client import ResponseMyUser, ResponseProjectInfo
from savvihub.api.exceptions import NotFoundAPIException, InvalidTokenAPIException
from savvihub.cli.config_loader import GlobalConfigLoader
from savvihub.cli.exceptions import ExitException
from savvihub.cli.utils import get_default_organization
from savvihub.common.constants import DEBUG
from savvihub.exceptions import SavviHubException


class Context(typer.Context):
    global_config = None
    project_config = None
    git_repo = None

    user: Optional[ResponseMyUser] = None
    project: Optional[ResponseProjectInfo] = None

    store = {}
    spec = defaultdict(dict)

    def __init__(self, auth_required=False, user_required=False, **kwargs):
        super().__init__(**kwargs)
        self.load(auth_required=auth_required, user_required=user_required)

    def load(self, auth_required=False, user_required=False):
        self.global_config = self.load_global_config()
        try:
            if auth_required:
                self.authenticated_client.verify_access_token()
            if user_required:
                self.user = self.authenticated_client.get_my_info()
        except (NotFoundAPIException, InvalidTokenAPIException):
            typer.echo('Token expired. You should run `savvihub login` first.')
            sys.exit(1)

    @cached_property
    def authenticated_client(self):
        from savvihub.api.savvihub import SavviHubClient
        return SavviHubClient(auth_header={'Authorization': f'Token {self.token}'})

    @cached_property
    def token(self):
        access_token = os.environ.get('SAVVIHUB_ACCESS_TOKEN', None)
        if access_token:
            return access_token
        if self.global_config.token:
            return self.global_config.token
        raise ExitException('Login required. You should run `savvihub login` first.')

    @cached_property
    def organization(self):
        if self.token and self.global_config.organization:
            return self.authenticated_client.organization_read(self.global_config.organization)

        organization = get_default_organization(self.authenticated_client)
        self.global_config.organization = organization.name
        return organization

    @staticmethod
    def load_global_config():
        return GlobalConfigLoader()


class ExceptionMixin:
    def main(self, *args, **kwargs):
        try:
            return super().main(*args, **kwargs)
        except SavviHubException as e:
            if DEBUG:
                typer.echo(traceback.format_exc())

            if e.message:
                typer.echo(e.message)
            sys.exit(e.exit_code)
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception as e:
            if DEBUG:
                typer.echo(traceback.format_exc())

            import sentry_sdk
            sentry_sdk.capture_exception(e)
            sentry_sdk.flush()

            typer.echo('An unexpected exception occurred. (`pip install --upgrade savvihub` might resolve this issue)')
            sys.exit(1)


class Command(ExceptionMixin, click.Command):
    def make_context(self, info_name, args, parent=None, **extra):
        for key, value in self.context_settings.items():
            if key not in extra:
                extra[key] = value

        ctx = Context(command=self, info_name=info_name, parent=parent, **extra)
        with ctx.scope(cleanup=False):
            self.parse_args(ctx, args)

        return ctx

    def parse_args(self, ctx, args):
        if not args and self.no_args_is_help and not ctx.resilient_parsing:
            typer.echo(ctx.get_help(), color=ctx.color)
            ctx.exit()

        parser = self.make_parser(ctx)
        opts, args, _ = parser.parse_args(args=args)

        params = self.params
        help_option = self.get_help_option(ctx)
        if help_option is not None:
            params = [help_option] + params

        # Overridden to change the order of parameter executions
        for param in sorted(params, key=lambda p: not p.is_eager):
            value, args = param.handle_parse_result(ctx, opts, args)

        if args and not ctx.allow_extra_args and not ctx.resilient_parsing:
            ctx.fail(
                "Got unexpected extra argument{} ({})".format(
                    "s" if len(args) != 1 else "", " ".join(args)
                )
            )

        ctx.args = args
        return args


class Group(ExceptionMixin, click.Group):
    pass


class Typer(typer.Typer):
    def __init__(self, *args, **kwargs):
        super().__init__(cls=Group, *args, **kwargs)

    def command(self, auth_required=False, user_required=False, **kwargs):
        if kwargs.get('context_settings') is None:
            kwargs['context_settings'] = {}

        kwargs['context_settings'].update({
            'auth_required': auth_required,
            'user_required': user_required,
        })

        return super().command(cls=Command, **kwargs)

    def add_typer(self, *args, **kwargs):
        super().add_typer(cls=Group, *args, **kwargs)
