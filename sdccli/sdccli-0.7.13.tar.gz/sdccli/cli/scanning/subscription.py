import click
import json
import sys
from sdccli.printer import print_list


_list_keys = ["subscription_key", "subscription_type", "active"]


@click.group(name='subscription', short_help='Subscription operations')
def subscription():
    pass


@subscription.command(name='activate', short_help="Activate a subscription")
@click.argument('subscription_type', nargs=1)
@click.argument('subscription_key', nargs=1, required=False)
@click.pass_obj
def activate(cnf, subscription_type, subscription_key):
    """
    SUBSCRIPTION_TYPE: Type of subscription. Valid options:

      - tag_update: Receive notification when new image is pushed

      - policy_eval: Receive notification when image policy status changes

      - vuln_update: Receive notification when vulnerabilities are added, removed or modified

    SUBSCRIPTION_KEY: Fully qualified name of tag to subscribe to. Eg. docker.io/library/alpine:latest
    """
    ok, res = cnf.sdscanning.activate_subscription(subscription_type, subscription_key)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)


@subscription.command(name='list', short_help="List all current subscriptions")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sdscanning.list_subscription()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@subscription.command(name='deactivate', short_help="Deactivate a subscription")
@click.argument('subscription_type', nargs=1)
@click.argument('subscription_key', nargs=1, required=False)
@click.pass_obj
def deactivate(cnf, subscription_type, subscription_key):
    """
    SUBSCRIPTION_TYPE: Type of subscription. Valid options:

      - tag_update: Receive notification when new image is pushed

      - policy_eval: Receive notification when image policy status changes

      - vuln_update: Receive notification when vulnerabilities are added, removed or modified

    SUBSCRIPTION_KEY: Fully qualified name of tag to subscribe to. Eg. docker.io/library/alpine:latest
    """
    ok, res = cnf.sdscanning.deactivate_subscription(subscription_type, subscription_key)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)
