from .cmd import Cmd

import os
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader('pynecone', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Gen(Cmd):

    def __init__(self):
        super().__init__("gen")

    def gen_shell(self, name, commands, output_folder):
        template = env.get_template('shell.jinja')

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        path = os.path.join(output_folder, name.lower() + '.py')

        if not os.path.exists(path):
            with open(path, "w") as fh:
                fh.write(template.render(class_name=name.title(), name=name.lower(),
                                               names=[cmd.lower() for cmd in commands]))

            self.gen_cmds(commands, output_folder)
        else:
            print('file already exists at path {0} skipping'.format(path))

    def gen_cmd(self, name, output_folder):
        template = env.get_template('cmd.jinja')

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        path = os.path.join(output_folder, name.lower() + '.py')

        if not os.path.exists(path):
            with open(path, "w") as fh:
                fh.write(template.render(class_name=name.title(), name=name.lower()))
        else:
            print('file already exists at path {0} skipping'.format(path))

    def gen_handler(self, name, output_folder):
        template = env.get_template('handler.jinja')

        Path(output_folder).mkdir(parents=True, exist_ok=True)

        path = os.path.join(output_folder, name.lower() + '.py')

        if not os.path.exists(path):
            with open(path, "w") as fh:
                fh.write(template.render(class_name=name.title(), name=name.lower()))
        else:
            print('file already exists at path {0} skipping'.format(path))


    def gen_cmds(self, names, output_folder):
        for cmd_name in names:
            self.gen_cmd(cmd_name, output_folder)

    def add_arguments(self, parser):
        parser.add_argument('op', choices=['cmd', 'shell', 'handler'],
                            help="generate a command (default), a shell or a handler", default='cmd', const='cmd', nargs='?')
        parser.add_argument('names', help="command names", nargs='+')
        parser.add_argument('--output_folder', help="use the specified output folder", default=os.path.join(os.getcwd()))

    def run(self, args):
        if args.op == 'shell':
            self.gen_shell(args.names[0], args.names[1:], args.output_folder)
        elif args.op == 'handler':
            self.gen_handler(args.names[0], args.output_folder)
        else:
            self.gen_cmds(args.names, args.output_folder)

    def get_help(self):
        return 'generate a new command or shell'