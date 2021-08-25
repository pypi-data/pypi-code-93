from argparse import Namespace, ArgumentParser
from typing import Optional


class ConsoleCommand:
    def configure(self, argument_parser: ArgumentParser):
        pass

    def get_command(self) -> str:
        raise Exception("Command name must be defined: {}".format(self.__class__))

    def get_description(self) -> Optional[str]:
        return None

    def run(self, input_args: Namespace):
        raise Exception("Command main method run() must be defined")
