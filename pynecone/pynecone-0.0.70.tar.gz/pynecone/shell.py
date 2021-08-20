from abc import abstractmethod
from .cmd import Cmd

import argparse


class Shell(Cmd):

    def run(self, args=None):

        if args is None:
            parser = argparse.ArgumentParser(prog=self.name)
            self.add_arguments(parser)

            subparsers = parser.add_subparsers(dest='{0}_command'.format(self.name), help=self.get_help())

            for c in self.get_commands():
                c.setup(subparsers)
            args = parser.parse_args()

        if hasattr(args, '{0}_command'.format(self.name)):
            command_name = getattr(args, '{0}_command'.format(self.name))
            # print('looking for command {0}'.format(command_name))
            command = next(iter([c for c in self.get_commands() if c.name == command_name]), None)
            if command:
                return command.run(args)
            else:
                print("{0} is not a valid command".format(command_name))
                return None
        else:
            print('Unable to find a valid command')
            return None




    @abstractmethod
    def get_commands(self):
        return []

    def setup(self, subparsers, parent=None):
        parser = super().setup(subparsers)
        commands = self.get_commands()
        if commands:
            subsubparsers = parser.add_subparsers(dest='{0}_command'.format(self.name))
            for c in commands:
                c.setup(subsubparsers)

    def __call__(self, args):
        parser = argparse.ArgumentParser(prog=self.name)

        self.add_arguments(parser)
        subparsers = parser.add_subparsers(dest='{0}_command'.format(self.name), help=self.get_help())

        for c in self.get_commands():
            c.setup(subparsers)

        return self.run(parser.parse_args(args))
