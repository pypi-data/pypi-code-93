from _exception import *
import _interactions
command_dict: dict = {}


class Command:
    def __init__(self, func=None, *args, **kwargs):
        self.func = func
        self.name = kwargs.get('name'),
        self.aliases = kwargs.get('aliases'),
        self.slash = kwargs.get('slash'),
        self.prefix = kwargs.get('prefix'),

    def add_command(self, fx):
        if not isinstance(fx, Command):
            raise TypeError("Not instance of <class 'command'>")

        if isinstance(self, Command):
            fx.parent = self

        if fx.name[0] in command_dict:
            raise CommandRegistrationError().error()

        command_dict[fx.name[0]] = fx.func
        for alias in fx.aliases[0]:
            if alias in command_dict.keys():
                self.remove_command(fx.name[0])
                raise CommandRegistrationError().error()
            command_dict[alias] = fx.func
        _interactions.Log("Command Successfully registered")
        return "Command Successfully Registered"

    def remove_command(self, name):
        cmd = command_dict.pop(name, None)

        if cmd is None:
            return None

        if name in cmd.aliases:
            return cmd

        for alias in cmd.aliases:
            __cmd__ = command_dict.pop(alias, None)
            if __cmd__ not in (None, cmd):
                command_dict[alias] = __cmd__
        return cmd


### EVENTS ###
event_dict = {}
