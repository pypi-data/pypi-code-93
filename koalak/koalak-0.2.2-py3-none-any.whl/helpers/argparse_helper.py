import argparse


class ArgparseSubcmdHelper:
    """argparse class Helper for subcommands
    To add a subcommand x implement the following methods
        parser_x(self, parser)
        run_x(self, args)
        description_x: str

    cls attributes
    prog:
    _parser_main: add to the main parser
    _run_main(self, args): hook after parsing args, handling main variable before dispatch to subcmd
    """

    prog = None
    groups = None

    def _parser_main(self, parser):
        pass

    def _run_main(self, args):
        pass

    def _init_help(self):
        """If groups exist change the current help"""
        if not self.groups:
            return
        SPACES = "    "

        # header prog name and description
        help = f"usage: {self.prog} [-h] <subcommand>\n\n"
        prog_description = getattr(self, "description", "")
        help += f"{prog_description}\n\n"

        # get the longest command name for pretty print with tabulations
        grouped_commands_name = [
            cmd for e in self.groups.values() for cmd in e["commands"]
        ]
        all_commands_name = [e[4:] for e in dir(self) if e.startswith("run_")]
        ungrouped_printed_commands = [
            e for e in all_commands_name if e not in grouped_commands_name
        ]
        # max command length for pretty print (aligned)
        max_command_length = len(max(grouped_commands_name, key=len))

        # FIXME: check that ungrouped do not exist
        # add ungrouped commands
        if ungrouped_printed_commands:
            self.groups["ungrouped"] = {
                "commands": ungrouped_printed_commands,
                "description": "",
            }

        for group_name, group in self.groups.items():
            commands = group["commands"]
            group_description = group["description"]
            help += f"{group_name}: {group_description}\n"
            for cmd in commands:
                # check if the command exist!
                if not hasattr(self, f"run_{cmd}"):
                    raise TypeError(
                        f"Command {cmd!r} can't be in a group because it don't exist (consider implementing 'run_{cmd}')"
                    )
                description_command = getattr(self, f"description_{cmd}", "")
                help += f"{SPACES}{cmd.ljust(max_command_length)}{SPACES} {description_command}\n"
            help += "\n"

        # change the help function
        self.main_parser.print_help = lambda file=None: print(help, file=file)
        # self.main_parser.print_usage = self.main_parser.print_help

    def __init__(self):
        # create main parser
        self.main_parser = argparse.ArgumentParser(self.prog)

        # hook to add arguments for the main program
        self._parser_main(self.main_parser)

        # init the subcommande
        self.subparsers = self.main_parser.add_subparsers(dest="subcommand")
        for subcommand_name in [
            e[4:]
            for e in dir(self)
            if e.startswith("run_") and callable(getattr(self, e))
        ]:

            # get help if exist
            description = getattr(self, "description_" + subcommand_name, None)
            subparser = self.subparsers.add_parser(
                subcommand_name, help=description, description=description
            )
            parser_name = f"parser_{subcommand_name}"

            # add parser_<cmd> if exist (the parser_<cmd> is not required only run_<cmd> is)
            if hasattr(self, parser_name):
                parser_func = getattr(self, parser_name)
                parser_func(subparser)

        # TODO: see the case if parser_ is present but not run_
        # change help if groups attribute is present
        self._init_help()

    def parse_args(self, args=None):
        return self.main_parser.parse_args(args)

    def main(self, args=None):
        parsed_args = self.main_parser.parse_args(args)
        self._run_main(parsed_args)
        subcommand_name = parsed_args.subcommand
        if subcommand_name is None:
            self.main_parser.print_help()
            return
        try:
            subcommand = getattr(self, f"run_{subcommand_name}")
            if not callable(subcommand):
                raise TypeError(f"{subcommand_name} attribute must be callable")

        except AttributeError:
            if hasattr(self, f"parser_{subcommand_name}"):
                print(f"Command {subcommand_name} not implemented")
                self.main_parser.print_usage()
                return
            else:
                # FIXME: dead code, argparse handle this case
                print(f"Command {subcommand_name} don't exist")
                self.main_parser.print_usage()
                return
        subcommand(parsed_args)
        return
