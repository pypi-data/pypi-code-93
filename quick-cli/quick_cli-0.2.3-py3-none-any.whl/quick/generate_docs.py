import argparse
import dataclasses

from argparse import ArgumentParser
from argparse import _SubParsersAction
from typing import List
from typing import Optional

from quick.driver import create_quick_parser


@dataclasses.dataclass
class Argument:
    name: str
    help: Optional[str]
    prog: Optional[str]


class ArgumentGroup:
    def __init__(self, headline: Optional[str], arguments=None):
        if arguments is None:
            arguments = []
        self.headline = headline
        self.arguments = arguments

    def add_argument(self, arg: Argument):
        self.arguments.append(arg)


class CLIParser:
    def __init__(
        self,
        prog: str,
        name: str,
        description: Optional[str],
        usage: str,
        argument_groups: Optional[List[ArgumentGroup]] = None,
        children: Optional[List["CLIParser"]] = None,
    ):
        if argument_groups is None:
            argument_groups = []
        if children is None:
            children = []
        self.prog = prog
        self.name = name
        self.description = description
        self.usage = usage
        self.argument_groups = argument_groups
        self.children = children

    def add_group(self, group: ArgumentGroup):
        self.argument_groups.append(group)

    def add_child(self, subparser: "CLIParser"):
        self.children.append(subparser)


def to_markdown(parser: ArgumentParser):
    print(f"# Documentation - {parser.prog} CLI")
    parsed_parser = extract(parser, "quick")
    print("## Content")
    print_toc(parsed_parser)
    print("## Commands")
    print_group(parsed_parser)


def extract(parser: ArgumentParser, name: str) -> CLIParser:
    parent = CLIParser(
        parser.prog,
        name,
        parser.description,
        parser.format_usage().lstrip("usage: ").rstrip(),
    )

    for action_group in parser._action_groups:
        if action_group.title == "optional arguments" or action_group.title == "required arguments":
            continue

        if len(action_group._group_actions) == 0:
            continue

        group = ArgumentGroup(action_group.title)
        for arg in action_group._group_actions:
            # subcommands detected
            if isinstance(arg, _SubParsersAction):
                for action in arg._choices_actions:
                    subparser = arg.choices[action.dest]
                    # recursion LETS GO
                    child = extract(subparser, action.dest)
                    parsed_arg = Argument(action.dest, action.help, subparser.prog)
                    group.add_argument(parsed_arg)
                    parent.add_child(child)
            elif arg.help is not argparse.SUPPRESS:
                # optional (prefix --)?
                if len(arg.option_strings) > 0:
                    name = ", ".join(arg.option_strings)
                else:
                    name = arg.dest
                parsed_arg = Argument(name, arg.help, None)
                group.add_argument(parsed_arg)
        parent.add_group(group)
    return parent


def print_toc(parser: CLIParser, indent: int = 0):
    for sub in parser.children:
        indentation = " " * indent
        print(f"{indentation}* [`{sub.name}`](#{sub.prog.replace(' ', '-')})")
        print_toc(sub, indent + 2)


def print_group(parser: CLIParser, recursion=0):
    if recursion == 1:
        print("---")
    print(f"### `{parser.prog}`")
    print(parser.description)
    print()

    print("**Usage:**\n")
    print(f"```\n{parser.usage}\n```")

    for argument_group in parser.argument_groups:
        print(f"**{argument_group.headline}:**\n")
        for arg in argument_group.arguments:
            if arg.prog is None:
                print(f"* `{arg.name}`: {arg.help}")
            else:
                print(f"* [`{arg.name}`](#{arg.prog.replace(' ', '-')}): {arg.help}")
        print()

    for child in parser.children:
        print_group(child, recursion + 1)


if __name__ == "__main__":
    quick_parser = create_quick_parser()
    to_markdown(quick_parser)
