import click
from datetime import datetime
from dateutil.parser import parse
import json
from types import SimpleNamespace


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args


def dict_to_namespace(dictionary):
    return json.loads(
        json.dumps(dictionary), object_hook=lambda item: SimpleNamespace(**item)
    )


def convert_time(time_str):
    if time_str:
        date = parse(time_str)
        # date = date.replace(tzinfo=None)
        return date


def date_format(date, second=False):
    format = "%y-%m-%d %H:%M"
    if second:
        format += ":%S"

    if date:
        return date.strftime(format)
