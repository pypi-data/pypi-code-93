'''Simple argparse.'''

# from pprint import pprint
import argparse
from argparse import Action, HelpFormatter
from typing import Iterable, Optional

import colorama
from colorama import Fore, Style

colorama.init()


class ArgufyHelpFormatter(HelpFormatter):
    '''Provide formatting for Argufy.'''

    # argparse.HelpFormatter(prog, max_help_position=80, width=130)

    def add_usage(
        self,
        usage: str,
        actions: Iterable[Action],
        groups: Iterable[argparse._ArgumentGroup],
        prefix: Optional[str] = 'usage: ',
    ) -> None:
        '''Format usage message.'''
        if prefix is not None:
            prefix = self.font(prefix)
        super(ArgufyHelpFormatter, self).add_usage(
            usage, actions, groups, prefix
        )

    @staticmethod
    def font(text: str, width: str = 'BRIGHT') -> str:
        '''Set the string thickness.'''
        return getattr(Style, width) + text + Style.RESET_ALL

    @staticmethod
    def shade(text: str, color: str = 'CYAN') -> str:
        '''Set the string color.'''
        return getattr(Fore, color.upper()) + text + Style.RESET_ALL

    # def _format_action_invocation(self, action: Action) -> str:
    #     '''Format arguments summary.'''
    #     # TODO: find alternative that does not modify action
    #     if isinstance(action, argparse._SubParsersAction):
    #         if action.choices is not None:
    #             for choice in list(action.choices):
    #                 parser = action.choices.pop(choice)
    #                 choice = self.shade(choice)
    #                 action.choices[choice] = parser
    #     return super(
    #         ArgufyHelpFormatter, self
    #     )._format_action_invocation(action)

    def _expand_help(self, action: Action) -> str:
        '''Format help message.'''
        if action.help:
            return self.shade(
                super(ArgufyHelpFormatter, self)
                ._expand_help(action)
                .rstrip('.')
                .lower(),
                'YELLOW',
            )
        else:
            return ''

    def _format_action(self, action: Action) -> str:
        '''Format arguments.'''
        if isinstance(action, argparse._SubParsersAction._ChoicesPseudoAction):
            subcommand = self.shade(
                self.font(self._format_action_invocation(action))
            )
            help_text = self._expand_help(action)
            # TODO: calculate correct spacing
            return f"    {subcommand.ljust(37)}{help_text}\n"
        else:
            # action.option_strings = [
            #     self.font(self.shade(option))
            #     for option in action.option_strings
            # ]
            return super(ArgufyHelpFormatter, self)._format_action(action)
