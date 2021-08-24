import click
import json
import sys
from dateutil.parser import parse
from sdccli.printer import print_list


_list_keys = ["imageId", "tag", "repo", "policyEvalStatus"]


@click.group(name='runtime', short_help='Runtime operations')
def runtime():
    pass


@runtime.command(name='list', short_help="List runtime containers")
@click.option('--scope', nargs=1,
              help=("An AND-composed string of predicates that selects the scope in which the alert will be "
                    "applied. (like: 'kubernetes.namespace.name = \"example-java-app\" and "
                    "kubernetes.deployment.name = \"example-java-app-redis\"')"))
@click.option('--skip-policy', is_flag=True, help="No policy evaluations will be triggered for the images.")
@click.option('--start', nargs=1, help="Start of the time range.")
@click.option('--end', nargs=1, help="End of the time range.")
@click.pass_obj
def list(cnf, scope, skip_policy, start, end):
    start_time = None
    if start:
        start_time = parse(start).timestamp()
    end_time = None
    if end:
        end_time = parse(end).timestamp()

    ok, res = cnf.sdscanning.list_runtime(
        scope=scope,
        skip_policy_evaluation=skip_policy,
        start_time=start_time,
        end_time=end_time)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res["images"], _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)
