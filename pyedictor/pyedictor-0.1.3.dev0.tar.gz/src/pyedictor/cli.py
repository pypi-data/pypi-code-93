"""
Operations for using EDICTOR from Python
"""
import importlib.util
import lingpy
import argparse
from pyedictor.sqlite import get_lexibase
import json
from pathlib import Path

class CommandMeta(type):
    """
    A metaclass which keeps track of subclasses, if they have all-lowercase names.
    """
    __instances = []

    def __init__(self, name, bases, dct):
        super(CommandMeta, self).__init__(name, bases, dct)
        if name == name.lower():
            self.__instances.append(self)

    def __iter__(self):
        return iter(self.__instances)


class Command(metaclass=CommandMeta):
    """Base class for subcommands of the lingpy command line interface."""
    help = None

    @classmethod
    def subparser(cls, parser):
        """Hook to define subcommand arguments."""
        return

    def output(self, args, content):
        if args.output_file:
            lingpy.util.write_text_file(args.output_file, content)
        else:
            print(content)

    def __call__(self, args):
        """Hook to run the subcommand."""
        raise NotImplemented()


def _cmd_by_name(name):
    for cmd in Command:
        if cmd.__name__ == name:
            return cmd()



def add_option(parser, name_, default_, help_, short_opt=None, **kw):
    names = ['--' + name_]
    if short_opt:
        names.append('-' + short_opt)

    if isinstance(default_, bool):
        kw['action'] = 'store_false' if default_ else 'store_true'
    elif isinstance(default_, int):
        kw['type'] = float
    elif isinstance(default_, float):
        kw['type'] = float
    kw['default'] = default_
    kw['help'] = help_
    parser.add_argument(*names, **kw)


class wordlist(Command):
    """
    Convert a dataset to EDICTOR's sqlite format.
    """

    @classmethod
    def subparser(cls, p):
        add_option(
                p,
                "dataset",
                Path("cldf", "cldf-metadata.json"),
                "Path to the CLDF metadata file.",
                short_opt="d"
                )
        add_option(
                p,
                "preprocessing",
                None,
                "path to the module to preprocess the data",
                short_opt="p"
                )
        add_option(
                p,
                "namespace",
                '{"language_id": "doculect", "concept_name": "concept",'
                '"value": "value", "form": "form", "segments": "tokens",'
                '"comment": "note"}',
                "namespace and columns you want to extract"
                )
        add_option(
                p,
                "name",
                "dummy",
                "name of the dataset you want to create",
                short_opt="n"
                )
        add_option(
                p,
                "addon",
                None,
                "expand the namespace",
                short_opt="a")
        add_option(
                p,
                "sqlite",
                False,
                "convert to SQLITE format"
                )

    def __call__(self, args):
        namespace = json.loads(args.namespace)
        if args.addon:
            for row in args.addon.split(','):
                s, t = row.split(':')
                namespace[s] = t
        
        columns = [x for x in list(namespace)]
        if args.preprocessing:
            spec = importlib.util.spec_from_file_location(
                    "prep",
                    args.preprocessing)
            prep = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(prep)
            preprocessing = prep.run
        else:
            preprocessing = None
        get_lexibase(
                args.dataset,
                args.name,
                columns=columns,
                namespace=namespace,
                preprocessing=preprocessing, 
                lexibase=args.sqlite)

            
def get_parser():
    # basic parser for lingpy
    parser = argparse.ArgumentParser(
        description=main.__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest="subcommand")
    for cmd in Command:
        subparser = subparsers.add_parser(
            cmd.__name__,
            help=(cmd.__doc__ or '').strip().split('\n')[0],
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        cmd.subparser(subparser)
        cmd.help = subparser.format_help()

    return parser


def main(*args):
    """
    EDICTOR command line interface.
    """
    args = get_parser().parse_args(args or None)
    return _cmd_by_name(args.subcommand)(args)




