import click
import json
import sys
from sdccli.printer import print_list, print_item
from sdccli.usecases.scanning import alert as use_case

_item_keys = ["alertId", "name", "enabled", "description", "scope", "triggers",
              "notificationChannelNames", "createdAt", "updatedAt"]
_list_keys = ["alertId", "name", "enabled"]


@click.group(name='alert', short_help='Alert operations')
def alert():
    pass


@alert.command(name='add', short_help="Add an alert")
@click.argument('name', nargs=1)
@click.option('--description', nargs=1, help="The descprition of the alert.")
@click.option('--scope', nargs=1,
              help="An AND-composed string of predicates that selects the scope in which the alert will be "
                   """applied. (like: 'host.domain = "example.com" and container.image != "alpine:latest"')""")
@click.option('--nounscanned', is_flag=True, help="Disable unscanned image trigger'.")
@click.option('--nofailed', is_flag=True, help="Disable failed policy result trigger.")
@click.option('--noenable', is_flag=True, help="Whether this alert should actually be applied.")
@click.option('--notification', nargs=1, multiple=True, help="Notification channel id.")
@click.pass_obj
def add(cnf, name, description, scope, nounscanned, nofailed, noenable, notification):
    """
    NAME: The name of the alert.
    """
    try:
        res = use_case.add_scanning_alert(cnf.sdscanning, name,
                                          description=description,
                                          scope=scope,
                                          unscanned=not nounscanned,
                                          failed=not nofailed,
                                          enabled=not noenable,
                                          notification_channels=notification)
        cnf.formatter.format(res, "scanningAlert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='get', short_help="Get an alert")
@click.argument('alertid', nargs=1)
@click.pass_obj
def get(cnf, alertid):
    """
    ALERTID: Alert ID to get
    """
    try:
        res = use_case.get_alert_by_id(cnf.sdscanning, alertid)
        cnf.formatter.format(res, "scanningAlert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='list', short_help="List alerts")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sdscanning.list_alerts()
    try:
        res = use_case.list_scanning_alerts(cnf.sdscanning)
        cnf.formatter.format(res, "scanningAlertList")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='update', short_help="Update an alert")
@click.argument('alertid', nargs=1)
@click.argument('alertfile', type=click.Path(exists=True), nargs=1)
@click.pass_obj
def upd(cnf, alertid, alertfile):
    """
    ALERTID: Alert ID to get

    ALERTFILE: A file with a json description of the Alert
    """
    try:
        with open(alertfile) as f:
            alert = json.load(f)
    except Exception as error:
        print("Error parsing alert file (%s): %s" % (alertfile, str(error)))
        sys.exit(1)

    try:
        res = use_case.update_scanning_alert(cnf.sdscanning, alertid, alert)
        cnf.formatter.format(res, "scanningAlert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='del', short_help="Delete an alert")
@click.argument('alertid', nargs=1)
@click.pass_obj
def delete(cnf, alertid):
    """
    ALERTID: Alert ID to get
    """
    try:
        res = use_case.delete_scanning_alert(cnf.sdscanning, alertid)
    except Exception as ex:
        print(f"Error: {str(res)}")
        sys.exit(1)

    print("Success")
