import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "type", "name", "enabled", "options"]
_list_keys = ["id", "name", "enabled"]


@click.group(name='notification', short_help='Sysdig notification channel operations')
def notification():
    pass


@notification.command(name='add', short_help="Create a new notification channel")
@click.argument('name', nargs=1)
@click.option('--email', nargs=1, multiple=True, required=True, help="Email recipients")
@click.pass_obj
def add(cnf, name, email):
    """
    NAME: the name of the notification channel to create.
    """
    ok, res = cnf.sd.create_email_notification_channel(name, email)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res["notificationChannel"], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@notification.command(name='list', short_help="List all notification channels")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sd.get_notification_ids()
    if not ok:
        print("Error: " + str(res))
        sys.exit(1)

    channels = []
    for id in res:
        ok, res = cnf.sd.get_notification_channel(id)
        if not ok:
            print("Error: " + str(res))
            sys.exit(1)
        channels.append(res)

    if cnf.json:
        print(json.dumps(channels, indent=4))
        return

    print_list(channels, _list_keys)


@notification.command(name='update', short_help="Update notification channel")
@click.argument('jsonfile', nargs=1, type=click.Path(exists=True))
@click.pass_obj
def upd(cnf, jsonfile):
    """
    JSONFILE: A file with a json description of the notification channel to update
    """
    try:
        with open(jsonfile) as f:
            notification = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (jsonfile, str(error)))
        sys.exit(1)

    ok, res = cnf.sd.update_notification_channel(notification)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res["notificationChannel"], _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@notification.command(name='get', short_help="Get a notification channel")
@click.argument('id', nargs=1)
@click.pass_obj
def get(cnf, id):
    """
    ID: the id to get
    """
    ok, res = cnf.sd.get_notification_channel(id)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@notification.command(name='del', short_help="Delete notification channels")
@click.argument('ids', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, ids):
    """
    IDS: The ids of the notification channels to delete
    """
    for id in ids:
        ok, res = cnf.sd.delete_notification_channel({"id": id})

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
