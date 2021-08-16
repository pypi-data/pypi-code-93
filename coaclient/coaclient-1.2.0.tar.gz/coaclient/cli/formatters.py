"""
CoaClient Help formatter for CLI factory
"""

from argparse import (
    RawTextHelpFormatter,
    ArgumentDefaultsHelpFormatter
)

__all__ = (
    "RawTextArgsHelpFormatter",
)


class RawTextArgsHelpFormatter(RawTextHelpFormatter,
                               ArgumentDefaultsHelpFormatter):
    """
    RawTextArgsHelpFormatter - Formatter for print help information
    """

    def _format_action_invocation(self, action):
        if not action.option_strings:
            default = self._get_default_metavar_for_positional(action)
            metavar, = self._metavar_formatter(action, default)(1)
            return metavar

        # if the Optional doesn't take a value, format is:
        #    -s, --long
        if action.nargs == 0:
            return ', '.join(action.option_strings)

        # if the Optional takes a value, format is:
        #    -s, --long ARGS
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return '%s %s' % (
            ', '.join(action.option_strings), args_string
        )
