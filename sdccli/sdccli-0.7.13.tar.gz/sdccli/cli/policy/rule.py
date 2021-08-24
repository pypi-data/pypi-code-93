import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "name", "description", "details", "tags", "filename"]
_list_keys = ["ids", "name", "ruleType"]


@click.group(name='rule', short_help='Sysdig Secure policy rule operations')
def rule():
    pass


@rule.command(name='add-container', short_help="Add a container rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--not-matching', is_flag=True, help="The rule matches if the container does not match any of the items in the list.")
@click.option('--container', nargs=1, multiple=True)
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_container(cnf, name, description, not_matching, container, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'containers': {
            'items': container if container else [],
            'matchItems': not not_matching
        },
        'ruleType': 'CONTAINER'
    }
    add(cnf, name, description, details, tag)


@rule.command(name='add-file', short_help="Add a file system rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--rw-not-matching', is_flag=True, help="The rule matches if the read/write path does not match any of the items in the list.")
@click.option('--rw-path', nargs=1, multiple=True, help="read/write path")
@click.option('--ro-not-matching', is_flag=True, help="The rule matches if the read only path does not match any of the items in the list.")
@click.option('--ro-path', nargs=1, multiple=True, help="read only path")
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_file(cnf, name, description, rw_not_matching, rw_path, ro_not_matching, ro_path, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'readPaths': {
            'items': ro_path if ro_path else [],
            'matchItems': not ro_not_matching
        },
        'readWritePaths': {
            'items': rw_path if rw_path else [],
            'matchItems': not rw_not_matching
        },
        'ruleType': 'FILESYSTEM'
    }
    add(cnf, name, description, details, tag)


@rule.command(name='add-network', short_help="Add a network rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--inbound-deny', is_flag=True, help="If set all inbound connection attempts match this rule")
@click.option('--outbound-deny', is_flag=True, help="If set all outbound connection attempts match this rule")
@click.option('--tcp-not-matching', is_flag=True, help="The rule matches if the tcp port does not match any of the items in the list.")
@click.option('--tcp-port', nargs=1, multiple=True, help="tcp port")
@click.option('--udp-not-matching', is_flag=True, help="The rule matches if the udp port does not match any of the items in the list.")
@click.option('--udp-port', nargs=1, multiple=True, help="udp port")
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_network(cnf, name, description, inbound_deny, outbound_deny, tcp_not_matching, tcp_port, udp_not_matching, udp_port, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'allInbound': inbound_deny,
        'allOutbound': outbound_deny,
        'tcpListenPorts': {
            'items': tcp_port if tcp_port else [],
            'matchItems': not tcp_not_matching
        },
        'udpListenPorts': {
            'items': udp_port if udp_port else [],
            'matchItems': not udp_not_matching
        },
        'ruleType': 'NETWORK'
    }
    add(cnf, name, description, details, tag)


@rule.command(name='add-process', short_help="Add a process rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--not-matching', is_flag=True, help="The rule matches if the process does not match any of the items in the list.")
@click.option('--process', nargs=1, multiple=True)
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_process(cnf, name, description, not_matching, process, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'processes': {
            'items': process if process else [],
            'matchItems': not not_matching
        },
        'ruleType': 'PROCESS'
    }
    add(cnf, name, description, details, tag)


@rule.command(name='add-syscall', short_help="Add a syscall rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--not-matching', is_flag=True, help="The rule matches if the syscall does not match any of the items in the list.")
@click.option('--syscall', nargs=1, multiple=True)
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_syscall(cnf, name, description, not_matching, syscall, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'syscalls': {
            'items': syscall if syscall else [],
            'matchItems': not not_matching
        },
        'ruleType': 'SYSCALL'
    }
    add(cnf, name, description, details, tag)


@rule.command(name='add-falco', short_help="Add a falco rule")
@click.argument('name', nargs=1)
@click.argument('description', nargs=1)
@click.option('--condition', nargs=1, help="the full condition text exactly as represented in the yaml file")
@click.option('--output', nargs=1, help="A string describing the output string to generate when this rule matches an event. Should exactly match the output property of the rule's output field")
@click.option('--priority', nargs=1, default="warning", help="The falco rule's priority. This is only included so the resulting rule can be converted back to yaml easily. For the purposes of policy events, the policy's severity should be used instead of this value. [ emergency, alert, critical, error, warning, notice, informational, debug ]")
@click.option('--source', nargs=1, default="syscall", help="The kinds of events this rule should run on. Note that this is different that the file containing the rule. This is naming an event source. [ k8s_audit, syscall ]")
@click.option('--tag', nargs=1, multiple=True, help="A rule tag.")
@click.pass_obj
def add_falco(cnf, name, description, condition, output, priority, source, tag):
    """
    NAME: the name of the new rule.

    DESCRIPTION: Description of rule
    """
    details = {
        'append': False,
        'condition': {
            'components': [],
            'condition': condition
        },
        'output': output,
        'priority': priority,
        'source': source,
        'ruleType': 'FALCO'
    }
    add(cnf, name, description, details, tag)


def add(cnf, name, description, details, tags):
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.add_rule(
        name,
        details=details,
        description=description,
        tags=tags if tags else [])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@rule.command(name='list', short_help="List all rules")
@click.pass_obj
def lst(cnf):
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    ok, res = cnf.sdsecure.list_rules()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@rule.command(name='get', short_help="Get rule")
@click.argument('rule', nargs=1)
@click.pass_obj
def get(cnf, rule):
    """
    RULE: Rule (id or name) to get
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    try:
        id = int(rule)
        ok, res = cnf.sdsecure.get_rule_id(id)
    except ValueError:
        ok, res = cnf.sdsecure.get_rules_group(rule)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        if isinstance(res, list):
            for rule in res:
                print_item(rule, _item_keys)
        else:
            print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@rule.command(name='update', short_help="Update rule")
@click.argument('rule', nargs=1)
@click.option('--description', nargs=1, default="", help="Description of rule")
@click.option('--details', nargs=1, help="The rule descrption in a json format")
@click.option('--tag', nargs=1, multiple=True, help="A rule tag. It will replace the tags defined in the rule.")
@click.pass_obj
def upd(cnf, rule, description, details, tag):
    """
    RULES: Rule id to update
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    detail_dict = json.loads(details)
    ok, res = cnf.secure.update_rule(
        rule,
        details=detail_dict,
        description=description,
        tags=tag if tag else [])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@rule.command(name='del', short_help="Delete rules")
@click.argument('rules', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, rules):
    """
    RULES: Rule id to delete
    """
    if not cnf.sdsecure.policy_v2:
        print("Error: Sysdig Secure doesn't support policy API v2")
        sys.exit(1)

    for rule in rules:
        ok, res = cnf.sdsecure.delete_rule(rule)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")
