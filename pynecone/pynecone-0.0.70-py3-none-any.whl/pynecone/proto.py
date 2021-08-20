from .shell import Shell
from .cmd import Cmd


class ProtoShell(Shell):

        def __init__(self, name, commands, helpmsg):
            super().__init__(name)
            self.commands = commands
            self.helpmsg = helpmsg

        def get_commands(self):
            return self.commands

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return self.helpmsg


class ProtoCmd(Cmd):

    def __init__(self,
                 name,
                 helpmsg,
                 lambda_of_args=lambda args: args):
        super().__init__(name)
        self.lambda_of_args = lambda_of_args
        self.helpmsg = helpmsg

    def add_arguments(self, parser):
        pass

    def get_help(self):
        return self.helpmsg

    def run(self, args):
        return self.lambda_of_args(args)

