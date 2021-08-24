import click
import json
import sys
from datetime import datetime
from sdccli.time import date_range_in_sec
from prettytable import PrettyTable, PLAIN_COLUMNS


@click.group(name='capture', short_help='Sysdig capture operations')
@click.option('--secure', is_flag=True, help='Work Sysdig Secure captures instead of Sysdig Monitor')
@click.pass_obj
def capture(cnf, secure):
    cnf.sd = cnf.sdsecure if secure else cnf.sdmonitor


@capture.command(name='add', short_help="Create a new sysdig capture. The capture will be immediately started.")
@click.argument('name', nargs=1)
@click.argument('hostname', nargs=1)
@click.option('--duration', nargs=1, type=click.INT, default=30, help="the duration of the capture, in seconds.")
@click.option('--filter', nargs=1, default="", help="a sysdig filter expression.")
@click.option('--folder', nargs=1, default="/", help="directory in the S3 bucket where the capture will be saved.")
@click.pass_obj
def add(cnf, name, hostname, duration, filter, folder):
    """
    NAME: the name of the capture.
    HOSTNAME: the hostname of the instrumented host where the capture will be taken.
    """
    ok, res = cnf.sd.create_sysdig_capture(hostname, name, duration, filter, folder)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_capture(res["dump"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@capture.command(name='list', short_help="List alerts")
@click.option('--duration', nargs=1, help="Duration to display the events from. (ex: 30M, 1H, 3D, 2W)")
@click.option('--start', nargs=1, help="Start of the time range.")
@click.option('--end', nargs=1, help="End of the time range.")
@click.option('--scope', nargs=1, help="this is a SysdigMonitor-like filter (e.g 'container.image=ubuntu'). When provided, events are filtered by their scope, so only a subset will be returned (e.g. 'container.image=ubuntu' will provide only events that have happened on an ubuntu container).")
@click.pass_obj
def list(cnf, duration, start, end, scope):
    try:
        from_sec, to_sec = date_range_in_sec(start, end, duration)
    except IndexError as ex:
        print("Error: {}".format(ex))
        sys.exit(1)

    ok, res = cnf.sd.get_sysdig_captures(
        from_sec=from_sec,
        to_sec=to_sec,
        scope_filter=scope)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_captures(res["dumps"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@capture.command(name='get', short_help="Fetch the state of a sysdig capture")
@click.argument('capture-id', nargs=1)
@click.pass_obj
def get(cnf, capture_id):
    """
    CAPTURE-ID: the capture id
    """
    ok, res = cnf.sd.poll_sysdig_capture({'id': capture_id})

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_capture(res["dump"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@capture.command(name='download', short_help="Download a sysdig capture")
@click.argument('capture-id', nargs=1)
@click.argument('file-scap', nargs=1, type=click.File('wb'))
@click.pass_obj
def download(cnf, capture_id, file_scap):
    """
    CAPTURE-ID: the capture id
    FILE-SCAP: the path of the file to save the capture to
    """
    ok, res = cnf.sd.download_sysdig_capture(capture_id)
    if ok:
        file_scap.write(res)
    else:
        print("Error: " + str(res))
        sys.exit(1)


def _print_capture(capture):
    print("{:25} {}".format("id:", capture["id"]))
    print("{:25} {}".format("name:", capture["name"][:-5]))
    if "error" in capture:
        print("{:25} {}".format("error:", capture["error"]))
    print("{:25} {}".format("hostname:", capture["agent"]["hostName"]))
    if "containerId" in capture:
        print("{:25} {}".format("container id:", capture["containerId"]))
    print("{:25} {}".format("time:", _format_time(capture)))
    print("{:25} {}".format("folder:", capture["folder"]))
    if capture["size"]:
        print("{:25} {}".format("size:", _size2str(capture["size"])))
    if capture["notificationInfo"]:
        print("{:25} {}".format("notification:", capture["notificationInfo"]))
    print("{:25} {}".format("status:", capture["status"]))
    if "policyEvents" in capture:
        event_ids = [e["policyId"] for e in capture["policyEvents"]]
        print("{:25} {}".format("policy ids:", event_ids))


def _print_captures(captures):
    t = PrettyTable(["id", "name", "hostname", "time", "status"])
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for capture in captures:
        values = []
        values.append(capture["id"])
        values.append(capture["name"][:-5])
        values.append(capture["agent"]["hostName"])
        values.append(_format_time(capture))
        values.append(capture["status"])
        t.add_row(values)
    print(t.get_string())


def _format_time(capture):
    date = str(_to_datetime(capture["dateRequested"]))
    if capture["dateReceived"]:
        duration = _to_seconds(capture["dateReceived"] - capture["dateRequested"])
        date += " ({:.0f} sec)".format(duration)
    return date


def _to_seconds(date):
    return date / 10**3


def _to_datetime(date):
    return datetime.utcfromtimestamp(_to_seconds(date))


def _size2str(size):
    for metric in ["B", "KiB", "MiB", "GiB"]:
        nsize = size / 1024
        if nsize < 1:
            return "{:.2f} {}".format(size, metric)
        size = nsize
    return "{:.2f} {}".format(size, metric)
