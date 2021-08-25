import getpass
import re

from argparse import ArgumentParser

import yaml

from quick.commands.base import ArgumentGroup
from quick.commands.base import Command
from quick.commands.base import Group


DOMAIN_RE = re.compile(r"https?://(www\.)?")


class CreateContext(Command):
    name = "create"
    help = "Create a new context"

    def execute(self):
        # Set host (prompt if not already given)
        host = self.args.host or input("Enter your host address: ")
        # Set api key (prompt if not already given)
        api_key = self.args.api_key or getpass.getpass(f"Enter the API key for {host}: ")
        context = self.args.context or context_from_host(host)
        self.config.create(context, host, api_key)

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        optional.add_argument(
            "--host",
            dest="host",
            type=str,
            help="Name of the host (prompted if not given)",
            required=False,
        )
        optional.add_argument(
            "--key",
            dest="api_key",
            metavar="API-KEY",
            type=str,
            help="API key of this quick instance (prompted if not given)",
            required=False,
        )
        optional.add_argument(
            "--context",
            type=str,
            help="Name of the context (defaults to host)",
            required=False,
        )


class DescribeContext(Command):
    name = "describe"
    help = "Display a context configuration"

    def execute(self):
        context = self.args.context or self.config.get_current_context()
        config = self.config.get_current_context_config(context)
        print(yaml.dump(config).strip())

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        optional.add_argument("--context", type=str, help="Select context (defaults to current one)", required=False)


class ListContexts(Command):
    name = "list"
    help = "List all context configurations"

    def execute(self):
        config = self.config.get_all()
        print(yaml.dump(config).strip())
        print("currentContext: " + self.config.get_current_context())

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        pass


class ActivateContext(Command):
    name = "activate"
    help = "Activate context"

    def execute(self):
        self.config.set_current_context(self.args.name)

    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        required.add_argument("name", metavar="NAME", type=str, help="Name of the context to activate")


class ContextGroup(Group):
    name = "context"
    help = "Manage quick configuration"

    sub_parser = [CreateContext, DescribeContext, ListContexts, ActivateContext]


def context_from_host(host: str) -> str:
    return DOMAIN_RE.sub("", host).strip().strip("/")
