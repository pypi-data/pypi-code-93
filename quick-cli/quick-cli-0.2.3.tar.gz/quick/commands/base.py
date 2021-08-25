import re

from abc import ABC
from abc import abstractmethod
from argparse import ArgumentParser
from argparse import Namespace
from argparse import _ArgumentGroup
from argparse import _SubParsersAction
from typing import Iterable
from typing import Optional
from typing import Type

from quick_client import ApiClient
from quick_client import ApiException
from quick_client import Configuration
from quick_client import DefaultApi
from urllib3.exceptions import MaxRetryError

from quick.config import QuickConfig
from quick.exception import InvalidNameException
from quick.exception import NotInitializedException
from quick.exception import handle_error
from quick.parser import QuickHelpFormatter


SubParserAction = _SubParsersAction
ArgumentGroup = _ArgumentGroup


class Parsable(ABC):
    """
    Base class for argparse CLI subparser. Either a Group or Command.

    A Group contains multiple Parsable.
    A Command is always executable.

    :arg name (str) Name of this sub group or command
    :arg help (str) String shown when parent's help is called. This must be set!
    :arg description (str) Usage help shown when this Parsable's help is called. Defaults to help.
    """

    name: str
    help: str
    description: Optional[str] = None

    @abstractmethod
    def create_sub_parser(self, parent: SubParserAction):
        """
        Adds this parsable to parent

        :param parent: group to add subparser to
        """


class Command(Parsable, ABC):
    """
    CLI Subcommand that is executing an action.

    If you want to have further subcommands, see Group.
    """

    def __init__(self, config: Optional[QuickConfig] = None):
        self.config = config
        self.parser: Optional[ArgumentParser] = None

    def __call__(self, args: Namespace, **kwargs):
        self.args = args
        if self.config is None:
            self.config = QuickConfig()
        self.execute()

    @abstractmethod
    def execute(self):
        pass

    def create_sub_parser(self, parent: SubParserAction):
        self.description = self.description or self.help
        self.parser = parent.add_parser(
            self.name,
            description=self.description,
            help=self.help,
            formatter_class=QuickHelpFormatter,
        )
        required = self.parser.add_argument_group("Required")
        optional = self.parser.add_argument_group("Optional")
        self.add_args(self.parser, required, optional)
        self.add_common_args(optional)
        self.parser.set_defaults(func=self)

    @abstractmethod
    def add_args(self, parser: ArgumentParser, required: ArgumentGroup, optional: ArgumentGroup):
        pass

    def add_common_args(self, optional: ArgumentGroup):
        # optional.add_argument("--verbose", type=int, choices=range(0, 5), help="Verbosity level", default=0)
        optional.add_argument("--debug", action="store_true", help="Enable debug output")


class Group(Parsable, ABC):
    """
    Subcommand grouping multiple subcommands

    :arg sub_parser: All parser in this group
    """

    sub_parser: Iterable[Type[Parsable]]

    def create_sub_parser(self, parent: SubParserAction):
        self.description = self.description or self.help
        parser = parent.add_parser(
            self.name,
            description=self.description,
            help=self.help,
            formatter_class=QuickHelpFormatter,
        )
        sub_parser = parser.add_subparsers(title="Available commands", metavar="command [options ...]")
        for sub_class in self.sub_parser:
            sub_class().create_sub_parser(sub_parser)


class ManagerCommand(Command, ABC):
    """
    Abstract Command for interacting with a quick manager.

    Child command an use rely on a instantiated quick client and confi.
    """

    def __init__(self, config: Optional[QuickConfig] = None, client: Optional[DefaultApi] = None):
        super().__init__(config)
        self.client = client

    def __call__(self, args: Namespace, **kwargs):
        self.args = args
        if self.config is None:
            self.config = QuickConfig()
        if self.client is None:
            self.client = self.__create_client()
        try:
            self.execute()
        except ApiException as exception:
            handle_error(exception, self.client_error_message(exception))
        except MaxRetryError:
            print("Please check your host IP and try again. " "Set the IP using:\n\t$ quick init <HOST IP>\n")

    @abstractmethod
    def client_error_message(self, exception: ApiException) -> str:
        pass

    def __create_client(self) -> DefaultApi:
        if self.config is None:
            raise NotInitializedException

        host = self.config.get_host()
        api_key = self.config.get_api_key()
        configuration = Configuration(host=host, api_key={"X-API-Key": api_key})
        configuration.debug = self.args.debug
        with ApiClient(configuration=configuration) as api_client:
            return DefaultApi(api_client)

    def add_common_args(self, optional: ArgumentGroup):
        optional.add_argument(
            "--context",
            type=str,
            metavar="CONTEXT",
            help="Context of quick",
            required=False,
        )
        super().add_common_args(optional)

    def validate_deployment_name(self, name: str):
        """
        Checks whether a given name can be used in a Kubernetes deployment.

        see: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#dns-subdomain-names

        :param name: name of the deployment
        :raises InvalidNameException
        """
        if not bool(re.match(r"^(?![0-9]+$)(?!.*-$)(?!-)[a-z0-9-.]{1,253}(?<!_)$", name)):
            raise InvalidNameException()
