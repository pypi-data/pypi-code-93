from .exceptions import RequiredValue
from .options import Option
from .commands import Command
from . import SETTINGS, VARIABLES, convert_all_sets, attempt_type_convert
import pathlib
import os
import yaml

__author__ = "Matt Limb <matt.limb17@gmail.com>"

class Shortcut:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.description = kwargs.get("description", None)
        self.cmd = kwargs.get("cmd", None)
        self.config = convert_all_sets(kwargs.get("config", {}))
        self.options = kwargs.get("options", {})
        self.commands = kwargs.get("commands", [])
        self.variables = kwargs.get("variables", {})
        self.env = kwargs.get("env", {})

        self._verify()

    def _verify(self):
        if not self.name:
            raise RequiredValue("'name' is a required value of a shortcut.")

        if not self.cmd:
            raise RequiredValue("'cmd' is a required value of a shortcut.")

        for key, value in self.env.items():
            self.env[key] = os.environ.get(value, None)

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
        shortcusts = []

        with filepath.open("r") as f:
            file_contents = yaml.safe_load_all(f.read())

        for content in file_contents:
            content["options"] = [
                Option.new(name, option) 
                    for name, option in content.get("options", {}).items()
            ]

            if content["commands"]:
                content["commands"] = [
                    Command.new(name, conf)
                        for name, conf in content.get("commands", {}).items()
                ]
            else:
                raise RequiredValue("'commands' are a required value of a shortcut.")

            shortcusts.append(Shortcut(**content))
        
        return shortcusts

    def run_commands(self):
        SETTINGS.update(self.config)
        
        vars = dict(**VARIABLES)
        vars["variables"].update(self.variables)
        vars["variables"]["env"].update(self.env)

        for command in self.commands:
            rc, output = command.run_command(vars)
            
            if not command.background:
                vars["commands"][command.name] = {
                    "returns": attempt_type_convert(rc),
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