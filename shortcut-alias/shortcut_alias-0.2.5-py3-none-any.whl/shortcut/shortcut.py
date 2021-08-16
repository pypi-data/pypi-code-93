from sys import path
from .exceptions import RequiredValue
from .options import Option
from .commands import Command
import pathlib
import yaml

class Shortcut:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.description = kwargs.get("description", None)
        self.cmd = kwargs.get("cmd", None)

        self.options = kwargs.get("options", {})
        self.commands = kwargs.get("commands", {})

        self._verify()

    def _verify(self):
        if not self.name:
            raise RequiredValue("'name' is a required value of a shortcut.")

        if not self.description:
            raise RequiredValue("'description' is a required value of a shortcut.")

        if not self.cmd:
            raise RequiredValue("'cmd' is a required value of a shortcut.")

    @staticmethod
    def new(file_contents):
        file_contents["options"] = [
            Option.new(name, option) 
                for name, option in file_contents.get("options", {}).items()
        ]

        if file_contents["commands"]:
            file_contents["commands"] = [
                Command.new(name, conf)
                    for name, conf in file_contents.get("commands", {}).items()
            ]
        else:
            raise RequiredValue("'commands' are a required value of a shortcut.")

        return Shortcut(**file_contents)

    @staticmethod
    def from_file(filepath):
        filepath = pathlib.Path(filepath)

        with filepath.open("r") as f:
            file_contents = yaml.safe_load(f.read())

        file_contents["options"] = [
            Option.new(name, option) 
                for name, option in file_contents.get("options", {}).items()
        ]

        if file_contents["commands"]:
            file_contents["commands"] = [
                Command.new(name, conf)
                    for name, conf in file_contents.get("commands", {}).items()
            ]
        else:
            raise RequiredValue("'commands' are a required value of a shortcut.")

        return Shortcut(**file_contents)


    def run_commands(self, variables):
        variables = {
            "option": vars(variables),
            "command": {} 
        }

        for command in self.commands:
            rc, output = command.run_command(variables)

            variables["command"][command.name] = {
                "return": rc,
                "output": output
            }

    def add_parser(self, parser=None):
        p = parser.add_parser(self.cmd, help=self.description)

        for option in self.options:
            option.add_option(p)
        
        return parser

    def __repr__(self):
        """ String representation of the class """
        items = []

        for k, v in self.__dict__.items():
            if "_" != k[0]:
                if "pass" in k:
                    v = '*' * len(v)
                
                if isinstance(v, str):
                    items.append(f"{k}='{v}'")
                else:
                    items.append(f"{k}={v}")

        items = ', '.join(items)

        return f"{self.__class__.__name__}({items})"