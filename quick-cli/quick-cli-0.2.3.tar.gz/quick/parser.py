import argparse
import sys

from gettext import gettext as _


class QuickArgParser(argparse.ArgumentParser):
    """
    Custom quick arg parser

    The arg parser customizes the error message. It includes a pointer to the help argument.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This will trigger an error message if the sub command is missing
        self.set_defaults(func=lambda x: self.error("No subcommand specified."))

    def error(self, message):
        """
        Prints a usage message incorporating the message to stderr and
        exits.

        :param message: str
        """
        self.print_usage(sys.stderr)
        help_msg = "See '" + self.prog + " -h' for help.\n"
        args = {"message": message, "help": help_msg}
        self.exit(2, _("\nError: %(message)s\n%(help)s") % args)


class QuickHelpFormatter(argparse.HelpFormatter):
    """
    Custom quick help formatter

    The formatter customizes the displayed help message by:
        - omitting the help argument from optional arguments
        - displaying the metavar only once in lower case and enclosed in angle brackets
    """

    def __init__(self, prog, **kwargs):
        super().__init__(prog, width=120, max_help_position=45, **kwargs)

    def add_argument(self, action):
        # Don't add the help action to arguments. It is displayed on error messages.
        if not isinstance(action, argparse._HelpAction):
            super().add_argument(action)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            (metavar,) = self._metavar_formatter(action, action.dest)(1)
            return metavar
        else:
            parts = []
            if action.nargs == 0:
                parts.extend(action.option_strings)
            # format as "-o, --option <metavar>"
            else:
                default = action.dest.upper()
                args_string = self._format_args(action, default)
                for option_string in action.option_strings:
                    parts.append("%s" % option_string)
                parts[-1] += " <%s>" % args_string.lower()
            return ", ".join(parts)


class ArgsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        args = {}
        if not isinstance(values, (list,)):
            values = (values,)
        for value in values:
            # only split at first '=' to allow args contain '=' as well
            i = value.find("=")
            n, v = value[:i], value[i + 1 :]
            args[n] = v
        setattr(namespace, self.dest, args)
