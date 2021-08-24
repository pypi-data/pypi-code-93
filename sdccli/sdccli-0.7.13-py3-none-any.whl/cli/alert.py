import click
import json
import sys

from sdccli.usecases.alert import alert_add, alert_delete, alert_get, alert_update, alert_list, alert_add_json


@click.group(name='alert', short_help='Sysdig Monitor alert operations')
def alert():
    pass


@alert.command(name='add', short_help="Add an alert")
@click.argument('name', nargs=1)
@click.option('--description', nargs=1, default="",
              help="The alert description. This will appear in the Sysdig Monitor UI and in notification emails.")
@click.option('--severity', nargs=1, type=click.INT, default=4,
              help="syslog-encoded alert severity. This is a number from 0 to 7 where 0 means 'emergency' and 7 is 'debug'. (by default is 4)")
@click.option('--atleast', nargs=1, type=click.INT, default=600,
              help="the number of consecutive seconds the condition must be satisfied for the alert to fire. (by default is 600)")
@click.option('--condition', nargs=1, default="",
              help="the alert condition, as described here https://app.sysdigcloud.com/apidocs/#!/Alerts/post_api_alerts")
@click.option('--disable', is_flag=True, help="The alert will be disabled when created. (by default is enabled)")
@click.option('--segment', nargs=1, multiple=True,
              help="A segmentation criteria that can be used to apply the alert to multiple entities.")
@click.option('--segment-condition', nargs=1, default="ANY",
              help="When segment is specified (and therefore the alert will cover multiple entities) this field is used to determine when it will fire. In particular, you have two options for segment-condition: 'ANY' (the alert will fire when at least one of the monitored entities satisfies the condition) and 'ALL' (the alert will fire when all of the monitored entities satisfy the condition).")
@click.option('--user-filter', nargs=1, default="",
              help="a boolean expression combining Sysdig Monitor segmentation criteria that makes it possible to reduce the scope of the alert. For example: kubernetes.namespace.name='production' and container.image='nginx'")
@click.option('--notify', nargs=1,
              help="the type of notification you want this alert to generate. Options are 'EMAIL', 'SNS', 'PAGER_DUTY', 'SYSDIG_DUMP'")
@click.option('--annotation', nargs=1, multiple=True,
              help="a pair 'key=value' custom property that you can associate to this alert for automation or management reasons")
@click.option('--promql', is_flag=True,
              help="Define if the alert to be created follows the PromQL syntax")
@click.pass_obj
def add(cnf, name, description, severity, atleast, condition, disable, segment, segment_condition,
        user_filter, notify, annotation, promql):
    try:
        type = "PROMETHEUS" if promql else "MANUAL"
        res = alert_add(cnf.sdmonitor, name, description, severity, atleast, condition, disable, segment,
                        segment_condition, user_filter, notify, annotation, type)
        cnf.formatter.format(res, "alert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='add-json', short_help="Add an alert from a json file")
@click.argument('alertfile', type=click.Path(exists=True), nargs=1)
@click.pass_obj
def add_json(cnf, alertfile):
    """
    ALERTFILE: A file with a json alert description.
    """
    try:
        with open(alertfile) as f:
            alert = f.read()
    except Exception as error:
        print("Error parsing alert (%s): %s" % (alertfile, str(error)))
        sys.exit(1)

    try:
        res = alert_add_json(cnf.sdmonitor, json.loads(alert))
        cnf.formatter.format(res, "alert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='list', short_help="List all alerts")
@click.pass_obj
def list(cnf):
    try:
        res = alert_list(cnf.sdmonitor)
        cnf.formatter.format(res, "alertList")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='update', short_help="Update an alert")
@click.argument('alertfile', type=click.Path(exists=True), nargs=1)
@click.pass_obj
def upd(cnf, alertfile):
    """
    ALERTFILE: A file with a json alert description.
    """
    try:
        with open(alertfile) as f:
            alert = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (alertfile, str(error)))
        sys.exit(1)

    try:
        res = alert_update(cnf.sdmonitor, alert)
        cnf.formatter.format(res, "alert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='get', short_help="Get alert")
@click.argument('alert', nargs=1)
@click.pass_obj
def get(cnf, alert):
    try:
        res = alert_get(cnf.sdmonitor, alert)
        cnf.formatter.format(res, "alert")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@alert.command(name='del', short_help="Delete alerts")
@click.argument('alerts', nargs=-1, type=click.INT, required=True)
@click.pass_obj
def delete(cnf, alerts):
    try:
        alert_delete(cnf.sdmonitor, alerts)
        print("Success")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)
