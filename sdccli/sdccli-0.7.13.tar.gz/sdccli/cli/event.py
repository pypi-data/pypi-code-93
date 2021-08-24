import json
import sys
from datetime import datetime

import click
from prettytable import PrettyTable, PLAIN_COLUMNS

from sdccli.printer import print_item
from sdccli.time import format_timestamp, duration_to_timedelta


@click.group(name='event', short_help="Sysdig Monitor events operations")
def event():
    pass


@event.command(name='add', short_help="Add an event")
@click.argument('name', nargs=1)
@click.option('--description', nargs=1, help="a longer description offering detailed information about the event.")
@click.option('--severity', nargs=1, type=click.INT, help="syslog style from 0 (high) to 3 (low).")
@click.option('--filter', nargs=1,
              help="metadata, in Sysdig Monitor format, of nodes to associate with the event, e.g. ``host.hostName = 'ip-10-1-1-1' and container.name = 'foo'``.")
@click.option('--tag', nargs=1,
              help="A key=value that can be used to tag the event. Can be used for filtering/segmenting purposes in Sysdig Monitor.")
@click.pass_obj
def add(cnf, name, description, severity, filter, tag):
    """
    NAME: the name of the new event.
    """
    tags = None
    if tag:
        tags = {}
        for t in tag:
            (k, v) = t.split('=', 1) if '=' in t else ('', '')
            if not k or not v:
                print("tag format error - tags must be of the form (--tag key=value), found: {}".format(t))
                return
            tags[k] = v

    if severity is not None and not -1 < severity < 4:
        print("The severity values must be between 0 (high) and 3 (low), both included.")
        sys.exit(1)

    ok, res = cnf.sdmonitor.post_event(
        name,
        description=description,
        severity=severity,
        event_filter=filter,
        tags=tags)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_event(res["event"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@event.command(name='list', short_help="List all events")
@click.option('--duration', nargs=1, help="Duration to display the events from. (ex: 30M, 1H, 3D, 2W)")
@click.option('--limit', nargs=1, type=int, help="Max number of events to print. Default: 100")
@click.option('--name', nargs=1, help="Filter events by name.")
@click.pass_obj
def list_events(cnf, duration, limit, name):
    from_sec = to_sec = None
    if duration is not None:
        delta = duration_to_timedelta(duration)
        to_sec = datetime.now()
        from_sec = to_sec - delta

    if limit is None:
        limit = 100

    ok, res = cnf.sdmonitor.get_events(
        name=name,
        from_s=from_sec,
        to_s=to_sec,
        limit=limit)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_events(res["events"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@event.command(name='get', short_help="Get an event")
@click.argument('event-id', nargs=1)
@click.pass_obj
def get(cnf, event_id):
    """
    EVENT-ID: the id of the event to display
    """
    ok, res = cnf.sdmonitor.get_event(event_id)
    if not ok:
        print("Error: " + str(res))
        sys.exit(1)

    if cnf.json:
        print(json.dumps(res["event"], indent=4))
        return

    _print_event(res["event"])


@event.command(name='del', short_help="Delete events")
@click.argument('events', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, events):
    """
    EVENTS: Event ids to delete
    """
    for event in events:
        ok, res = cnf.sdmonitor.delete_event({"id": event})

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


def _print_events(events):
    t = PrettyTable(["id", "severity", "name", "date", "source"])
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for event in events:
        values = []
        values.append(event["id"])
        values.append(event["severity"])
        values.append(event["name"])
        values.append(format_timestamp(event["timestamp"]))
        if "source" in event:
            values.append(event["source"])
        elif "type" in event and event["type"]:
            values.append(event["type"].lower())
        else:
            values.append("NONE")
        t.add_row(values)
    print(t.get_string())


def _print_event(event):
    print_item(event, ["name", "id", "severityLabel", "description", "filter"])
    print("{:25} {}".format("date:", format_timestamp(event["timestamp"])))
    if "tags" in event and "source" in event["tags"]:
        print("{:25} {}".format("source:", event["tags"]["source"]))
