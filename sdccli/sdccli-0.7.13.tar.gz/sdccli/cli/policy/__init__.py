import json
import sys
import time
from datetime import datetime

import click
from dateutil.parser import parse
from prettytable import PrettyTable, PLAIN_COLUMNS

import sdccli.usecases.policy.events as use_case
from sdccli.cli.policy.falco_list import falco_list
from sdccli.cli.policy.falco_macro import falco_macro
from sdccli.cli.policy.rule import rule
from sdccli.printer import print_list, print_item
from sdccli.time import duration_to_seconds

_item_keys_v1 = ["id", "name", "description", "falcoConfiguration", "actions", "scope", "notificationChannelIds"]
_list_keys_v1 = ["id", "name", "severity", "isBuiltin", "notificationChannelIds"]
_item_keys = ["id", "name", "description", "type", "severity", "enabled", "scope", "ruleNames", "actions",
              "notificationChannelIds"]
_list_keys = ["id", "name", "type", "severity", "enabled"]


@click.group(name='policy', short_help='Sysdig Secure policy operations')
def policy():
    pass


policy.add_command(rule)
policy.add_command(falco_list)
policy.add_command(falco_macro)


@policy.command(name='add', short_help="Add a policy")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--rule', nargs=1, multiple=True,
              help="Rule name. It must be name instead of id, as the rules list view is by name, to account for multiple rules having the same name.")
@click.option('--action', nargs=1, multiple=True, help="It can be a stop, pause and/or capture action")
@click.option('--scope', nargs=1,
              help="Where the policy is being applied- Container, Host etc.. (example: 'container.image.repository = sysdig/agent')")
@click.option('--severity', nargs=1, default=0, type=click.INT,
              help="How severe is this policy when violated. Range from 0 to 7 included.")
@click.option('--notenabled', is_flag=True, help=" If the policy should not be considered")
@click.option('--notification', nargs=1, multiple=True, help="Notification channel id to subscribe to the policy.")
@click.option('--type', nargs=1, default="falco", type=click.STRING, help="Policy type, it can be one of: falco, list_matching, k8s_audit, aws_cloudvision")
@click.pass_obj
def add(cnf, name, description, rule, action, scope, severity, notenabled, notification, type):
    """
    NAME: the name of the new policy.

    DESCRIPTION: Description of policy
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2, use add-json instead")
        sys.exit(1)


    ok, res = cnf.sdsecure.add_policy(
        name, description,
        rule_names=rule,
        actions=action,
        scope=scope,
        severity=severity,
        enabled=not notenabled,
        notification_channels=notification,
        type=type)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='add-json', short_help="Add a policy from a json file")
@click.argument('policyfile', type=click.Path(exists=True), nargs=1)
@click.pass_obj
def add_json(cnf, policyfile):
    """
    POLICYFILE: A file with a json list of PolicyRule elements (while creating/updating a policy, new rule IDs will be created backend side)
    """
    try:
        with open(policyfile) as f:
            policy = f.read()
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (policyfile, str(error)))
        sys.exit(1)

    if cnf.sdsecure.policy_v2:
        ok, res = cnf.sdsecure.add_policy_json(policy)
    else:
        ok, res = cnf.sdsecure_v1.add_policy(policy)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if cnf.sdsecure.policy_v2:
            print_item(res, _item_keys)
        else:
            print_item(res["policy"], _item_keys_v1)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name="events", short_help="Get policy events")
@click.option('--duration', nargs=1, help="Duration to display the events from. The minimum is 10 minutes. "
                                          "(ex: 30M, 1H, 3D, 2W). Default: 3D.")
@click.option('--scope', nargs=1, help="this is a Sysdig Monitor-like filter (e.g 'kubernetes.cluster.name in "
                                       "(\"prod\", \"dev\")'). When provided, events are filtered by their scope, so "
                                       "only a subset will be returned (e.g. 'container.image.repo=\"ubuntu\"' will "
                                       "provide only events that have happened on an ubuntu container).")
@click.option('--severity', nargs=1, help="Filter by severity. Valid ones are: 'high', 'med', 'low', 'info'. "
                                          "Multiple ones can be specified if separated by commas. (e.g. 'med,low,info')")
@click.option('--type', nargs=1, help="Filter by event originator. Valid ones are: 'scanning', 'policy'. "
                                      "Multiple ones can be specified if separated by commas. (e.g. 'scanning,policy')")
@click.option('--search', nargs=1, help="Search by event title or label")
@click.option('--limit', nargs=1, type=click.INT, help="Limit the amount of events retrieved. Default: 50")
@click.argument('event-id', nargs=1, required=False)
@click.pass_obj
def events(cnf, event_id, duration, scope, severity, type, search, limit):
    try:
        if event_id:
            event = use_case.retrieve_policy_event_by_id(cnf.sdsecure, event_id)
            cnf.formatter.format(event, "policyEventV1")
            return


        events = use_case.retrieve_all_policy_events(cnf.sdsecure, duration, scope, severity, type, search, limit)
        cnf.formatter.format(events, "policyEventV1List")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@policy.command(name='events_old', short_help="Get policy events (Use only on old onprem installations)")
@click.argument('event-id', nargs=1, required=False)
@click.option('--duration', nargs=1, help="Duration to display the events from. (ex: 30M, 1H, 3D, 2W)")
@click.option('--start', nargs=1, help="Start of the time range.")
@click.option('--end', nargs=1, help="End of the time range.")
@click.option('--sampling', nargs=1, type=click.INT, default=60000000,
              help="sample all policy events using sampling interval.")
@click.option('--aggregate', nargs=1, multiple=True, default=['ruleType'],
              help="Specifies how to aggregate events (sampling does not need to be specified, because when it's "
                   "present it automatically means events will be aggregated). This field can either be a scope "
                   "metric or a policyEvent field but (currently) not a mix of the two. When policy events fields "
                   "are specified, only these can be used: severity, agentId, containerId, policyId, ruleType.")
@click.option('--scope', nargs=1,
              help="this is a SysdigMonitor-like filter (e.g 'container.image=ubuntu'). When provided, events are "
                   "filtered by their scope, so only a subset will be returned (e.g. 'container.image=ubuntu' will "
                   "provide only events that have happened on an ubuntu container).")
@click.option('--event-filter', nargs=1,
              help="this is a SysdigMonitor-like filter (e.g. policyEvent.policyId=3). When provided, events are "
                   "filtered by some of their properties. Currently the supported set of filters is "
                   "policyEvent.all(which can be used just with matches, policyEvent.policyId, policyEvent.id, "
                   "policyEvent.severity, policyEvent.ruleTye, policyEvent.ruleSubtype.")
@click.pass_obj
def events_old(cnf, event_id, duration, start, end, sampling, aggregate, scope, event_filter):
    """
    EVENT-ID: id of an event to display, if not provided a list of events will be displayed
    """
    kwargs = {
        "sampling": sampling,
        "aggregations": aggregate,
        "scope_filter": scope,
        "event_filter": event_filter
    }
    if duration:
        duration_sec = duration_to_seconds(duration)
        if duration_sec is None:
            return

        if event_id:
            ok, res = cnf.policy_events_client_old.get_policy_events_id_duration(event_id, duration_sec, **kwargs)
        else:
            ok, res = cnf.policy_events_client_old.get_policy_events_duration(duration_sec, **kwargs)

    else:
        if end:
            end_time = parse(end).timestamp()
        else:
            end_time = time.time()
        if start:
            start_time = parse(start).timestamp()
        else:
            start_time = end_time - (60 * 60)  # 1 hour

        if event_id:
            ok, res = cnf.policy_events_client_old.get_policy_events_id_range(event_id, start_time, end_time, **kwargs)
        else:
            ok, res = cnf.policy_events_client_old.get_policy_events_range(start_time, end_time, **kwargs)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if event_id:
            _print_event(res["data"]["policyEvent"])
        else:
            _print_events(res["data"]["policyEvents"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='list', short_help="List all policies")
@click.pass_obj
def list(cnf):
    if cnf.sdsecure.policy_v2:
        ok, res = cnf.sdsecure.list_policies()
    else:
        ok, res = cnf.sdsecure_v1.list_policies()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if cnf.sdsecure.policy_v2:
            print_list(res, _list_keys)
        else:
            print_list(res['policies'], _list_keys_v1)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='update', short_help="Update a policy")
@click.argument('id', nargs=1)
@click.option('--name', nargs=1, help="A short name for the policy")
@click.option('--description', nargs=1, help="Description of policy")
@click.option('--rule', nargs=1, multiple=True, help="Rule name. It will replace the rules defined in the policy")
@click.option('--action', nargs=1, multiple=True,
              help="It can be a stop, pause and/or capture action. It will replace the actions defined in the policy")
@click.option('--scope', nargs=1,
              help="Where the policy is being applied- Container, Host etc.. (example: 'container.image.repository = sysdig/agent')")
@click.option('--severity', nargs=1, type=click.INT,
              help="How severe is this policy when violated. Range from 0 to 7 included.")
@click.option('--notenabled', is_flag=True, help=" If the policy should not be considered")
@click.option('--notification', nargs=1, multiple=True, help="Notification channel id to subscribe to the policy.")
@click.pass_obj
def upd(cnf, id, name, description, rule, action, scope, severity, notenabled, notification):
    """
    ID: the id of the policy to update
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2, use add-json instead")
        sys.exit(1)

    if not rule:
        rule = None
    if not action:
        action = None
    if not notification:
        notification = None
    ok, res = cnf.sdsecure.update_policy(
        id,
        name=name,
        description=description,
        rule_names=rule,
        scope=scope,
        severity=severity,
        enabled=not notenabled,
        notification_channels=notification)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='update-json', short_help="Update a policy form a json file")
@click.argument('policyfile', type=click.Path(exists=True), nargs=1)
@click.pass_obj
def upd_json(cnf, policyfile):
    """
    POLICYFILE: A file with a json list of PolicyRule elements
    """
    try:
        with open(policyfile) as f:
            policy = f.read()
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (policyfile, str(error)))
        sys.exit(1)

    if cnf.sdsecure.policy_v2:
        ok, res = cnf.sdsecure.update_policy_json(policy)
    else:
        ok, res = cnf.sdsecure_v1.update_policy(policy)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if cnf.sdsecure.policy_v2:
            print_item(res, _item_keys)
        else:
            print_item(res["policy"], _item_keys_v1)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='update-default', short_help="Create default policies using the current system falco rules")
@click.pass_obj
def update_default(cnf):
    """
    Create a set of default policies using the current system falco rules file as a reference. For every falco rule in the system
    falco rules file, one policy will be created. The policy will take the name and description from the name and description of
    the corresponding falco rule. If a policy already exists with the same name, no policy is added or modified. Existing
    policies will be unchanged.
    """
    if cnf.sdsecure.policy_v2:
        ok, res = cnf.sdsecure.create_default_policies()
    else:
        ok, res = cnf.sdsecure_v1.create_default_policies()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if cnf.sdsecure.policy_v2:
            print_list(res, _list_keys)
        else:
            print_list(res['policies'], _list_keys_v1)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='get', short_help="Get policy")
@click.argument('policy', nargs=1)
@click.pass_obj
def get(cnf, policy):
    """
    POLICY: Policy (id or name) to get
    """
    sdsecure = cnf.sdsecure
    if not cnf.sdsecure.policy_v2:
        sdsecure = cnf.sdsecure_v1

    try:
        id = int(policy)
        ok, res = sdsecure.get_policy_id(id)
    except ValueError:
        ok, res = sdsecure.get_policy(policy)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if cnf.sdsecure.policy_v2:
            print_item(res, _item_keys)
        else:
            print_item(res["policy"], _item_keys_v1)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@policy.command(name='del', short_help="Delete policies")
@click.argument('policies', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, policies):
    """
    POLICIES: Policy (id or name) to delete
    """
    sdsecure = cnf.sdsecure
    if not cnf.sdsecure.policy_v2:
        sdsecure = cnf.sdsecure_v1

    for policy in policies:
        try:
            id = int(policy)
            ok, res = sdsecure.delete_policy_id(id)
        except ValueError:
            ok, res = sdsecure.delete_policy_name(policy)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


@policy.command(name='get-falco', short_help="Get a falco rules file")
@click.argument('outfile', type=click.File('w'), default=sys.stdout)
@click.option('--default', is_flag=True,
              help="Get the default falco rules file. (if not set the custom falco rules will be displayed)")
@click.pass_obj
def get_falco(cnf, outfile, default):
    """
    OUTFILE: File to write the rules into. If none is given the rules will be printed in stdout.
    """
    if default:
        ok, res = cnf.sdsecure.get_system_falco_rules()
    else:
        ok, res = cnf.sdsecure.get_user_falco_rules()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if not ok:
        print("Error: " + str(res))
        sys.exit(1)

    if default:
        outfile.write(res["systemRulesFile"]["content"])
    else:
        outfile.write(res)


@policy.command(name='set-falco', short_help="Set a falco rules file")
@click.argument('falcofile', type=click.File('r'), default=sys.stdin)
@click.option('--default', is_flag=True,
              help="Set the default falco rules file. (if not set the custom falco rules will be setted)")
@click.pass_obj
def set_falco(cnf, falcofile, default):
    """
    FALCOFILE: File with the falco rules. See the Falco wiki <https://github.com/draios/falco/wiki/Falco-Rules> for documentation on the falco rules format.
    """
    rules = falcofile.read()
    if default:
        ok, res = cnf.sdsecure.set_system_falco_rules(rules)
    else:
        ok, res = cnf.sdsecure.set_user_falco_rules(rules)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if not ok:
        print("Error: " + str(res))
        sys.exit(1)

    print("Success")


def _print_event(event):
    print_item(event, ["id", "name", "description"])
    if event["isAggregated"]:
        ts_start = _timestamp2datetime(event["minTimestamp"])
        ts_end = _timestamp2datetime(event["maxTimestamp"])
        print("{:25} {} - {}".format("time range:", ts_start, ts_end))
        rule_types = [t["element"] for t in event["ruleTypes"]]
        print("{:25} {}".format("Rule types:", rule_types))
        policy_ids = ["%s (%d)" % (p["element"], p["count"]) for p in event["policyIds"]]
        print("{:25} {}".format("policy ids:", policy_ids))
    else:
        timestamp = _timestamp2datetime(event["timestamp"])
        print("{:25} {}".format("timestamp:", timestamp))
        print("{:25} {:d}".format("policy id:", event["policyId"]))
    if event["isAggregated"]:
        print("\noutput:")
        for output in event["outputs"]:
            ocurrences = "(%d ocurrences) " % output["count"] if output["count"] > 1 else ""
            print("* {}{}".format(ocurrences, output["element"]))
    else:
        print("{:25} {}".format("output:", event["output"]))


def _print_events(events):
    t = PrettyTable(["id", "count", "severity", "name", "type"])
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for event in events:
        values = []
        values.append(event["id"])
        if event["isAggregated"]:
            values.append(event["aggregatedCount"])
            values.append(event["maxSeverity"])
        else:
            values.append(1)
            values.append(event["severity"])
        values.append(event["name"])
        if event["isAggregated"]:
            values.append(event["aggregatedMetrics"][1])
        else:
            values.append(event["ruleType"])
        t.add_row(values)
    print(t.get_string())


def _timestamp2datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp / 10 ** 6)
