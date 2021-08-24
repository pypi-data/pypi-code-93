import click
import json
import sys
from prettytable import PrettyTable, PLAIN_COLUMNS
from sdccli.time import date_range_in_sec, format_timestamp


@click.group(name='command', short_help="Sysdig Secure commands audit operations")
def command():
    pass


@command.command(name='list', short_help="List all commands")
@click.option('--duration', nargs=1, help="Duration to display the commands from. (ex: 30M, 1H, 3D, 2W)")
@click.option('--start', nargs=1, help="Start of the time range.")
@click.option('--end', nargs=1, help="End of the time range.")
@click.option('--scope', nargs=1, help="this is a SysdigMonitor-like filter (e.g 'container.image=ubuntu'). When provided, events are filtered by their scope, so only a subset will be returned (e.g. 'container.image=ubuntu' will provide only events that have happened on an ubuntu container).")
@click.option('--filter', nargs=1, help='this is a SysdigMonitor-like filter (e.g. command.comm="touch"). When provided, commands are filtered by some of their properties. Currently the supported set of filters is command.comm, command.cwd, command.pid, command.ppid, command.uid, command.loginshell.id, command.loginshell.distance')
@click.option('--limit', nargs=1, default=100, help='Maximum number of commands to list. If is not provided it will list up to 100 commands.')
@click.pass_obj
def list(cnf, duration, start, end, scope, filter, limit):
    try:
        from_sec, to_sec = date_range_in_sec(start, end, duration)
    except IndexError as ex:
        print("Error: {}".format(ex))
        sys.exit(1)

    ok, res = cnf.sdsecure.list_commands_audit(
        from_sec=from_sec,
        to_sec=to_sec,
        scope_filter=scope,
        command_filter=filter,
        metrics=["host.hostName"],
        limit=limit)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_commands(res['commands'])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@command.command(name='get', short_help="Get a command audit")
@click.argument('command-id', nargs=1)
@click.pass_obj
def get(cnf, command_id):
    """
    COMMAND-ID: the id of the command audit to get.
    """
    ok, res = cnf.sdsecure.get_command_audit(
        command_id,
        metrics=["host.hostName", "host.mac", "container.image"])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_command(res['command'])
    else:
        print("Error: " + str(res))
        sys.exit(1)


def _print_command(command):
    print("{:25} {}".format("id:", command["id"]))
    print("{:25} {}".format("time:", format_timestamp(command["timestamp"])))
    print("{:25} {}".format("command:", command["cmdline"]))
    print("{:25} {}".format("working directory:", command["cwd"]))
    host = "%s (%s)" % (command["metrics"][0], command["metrics"][1])
    print("{:25} {}".format("host:", host))
    if "containerId" in command:
        container = "%s (%s)" % (command["metrics"][2], command["containerId"])
        print("{:25} {}".format("container:", container))
    print("{:25} {}".format("pid:", command["pid"]))
    print("{:25} {}".format("ppid:", command["ppid"]))
    print("{:25} {}".format("user id:", command["uid"]))
    print("{:25} {}".format("shell id:", command["loginShellId"]))
    print("{:25} {}".format("shell distance:", command["loginShellDistance"]))


def _print_commands(commands):
    t = PrettyTable(["id", "time", "command", "host"])
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for command in commands:
        values = []
        values.append(command["id"])
        values.append(format_timestamp(command["timestamp"]))
        values.append(command["comm"])
        host = command["metrics"][0]
        if "containerId" in command:
            host += " > " + command["containerId"]
        values.append(host)
        t.add_row(values)
    print(t.get_string())
