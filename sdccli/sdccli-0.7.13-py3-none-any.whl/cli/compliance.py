import click
import json
import sys
from datetime import datetime
from sdccli.printer import print_list, print_item
from prettytable import PrettyTable, PLAIN_COLUMNS


_item_keys = ["id", "name", "schedule", "scope", "moduleName", "enabled"]
_list_keys = _item_keys


@click.group(name='compliance', short_help='Sysdig Secure compliance operations')
def compliance():
    pass


@compliance.command(name='add', short_help="Add a compliance task")
@click.argument('name', nargs=1)
@click.option('--scope', nargs=1, help="The agent will only run the task on hosts matching this scope or on hosts where containers match this scope.")
@click.option('--schedule', nargs=1, default="06:00:00Z/PT12H", help="The frequency at which this task should run. Expressed as an ISO 8601 Duration <https://en.wikipedia.org/wiki/ISO_8601#Durations>")
@click.option('--module', nargs=1, default="docker-bench-security", help="The name of the module that implements this task. Separate from task name in case you want to use the same module to run separate tasks with different scopes or schedules. [ 'docker-bench-security', 'kube-bench' ]")
@click.option('--disabled', nargs=1, is_flag=True, help="Disable this task to don't run as defined by its schedule.")
@click.pass_obj
def add(cnf, name, scope, schedule, module, disabled):
    """
    NAME: The name of the task e.g. 'Check Docker Compliance'.
    """
    ok, res = cnf.sdsecure.add_compliance_task(
        name,
        module_name=module,
        schedule=schedule,
        scope=scope,
        enabled=not disabled)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='list', short_help="List compliance tasks")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sdsecure.list_compliance_tasks()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='results', short_help="Get the list of compliance results")
@click.argument('filter', nargs=1, required=False)
@click.option('--limit', nargs=1, default=50, help='Maximum number of compliacne results to list. If is not provided it will list up to 50 results.')
@click.pass_obj
def results(cnf, filter, limit):
    """
    FILTER: an optional case insensitive filter used to match against the completed task name and return matching results.
    """
    if filter is None:
        filter = ""
    ok, res = cnf.sdsecure.list_compliance_results(filter=filter, limit=limit)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_results(res["results"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='result', short_help="Get the result of one compliance run")
@click.argument('result-id', nargs=1)
@click.option('--section', nargs=1, type=click.INT, help="Display only the tests in the selected seccion (1-7)")
@click.option('--level', nargs=1, default="warn", help="Display only the tests with status level higher or equal to the provided one. Valid levels are: [fail, warn, pass, info]")
@click.option('--remediation', is_flag=True, help="Display the information on how to remediate the issue")
@click.option('--csv', is_flag=True, help="Get result-id in csv format")
@click.pass_obj
def result(cnf, result_id, section, level, remediation, csv):
    """
    RESULT-ID: id of a compliance result to display
    """
    if csv:
        ok, res = cnf.sdsecure.get_compliance_results_csv(result_id)
        if ok:
            print(res)
            return
    else:
        ok, res = cnf.sdsecure.get_compliance_results(result_id)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_result(res, section, level, remediation)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='get', short_help="Get a compliance task")
@click.argument('task', nargs=1, type=click.INT)
@click.pass_obj
def get(cnf, task):
    """
    TASK: compliance task id to get
    """
    ok, res = cnf.sdsecure.get_compliance_task(task)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='update', short_help="Update a compliance task")
@click.argument('task', nargs=1, type=click.INT)
@click.option('--name', nargs=1, help="The name of the task e.g. 'Check Docker Compliance'.")
@click.option('--scope', nargs=1, help="The agent will only run the task on hosts matching this scope or on hosts where containers match this scope.")
@click.option('--schedule', nargs=1, default="06:00:00Z/PT12H", help="The frequency at which this task should run. Expressed as an ISO 8601 Duration <https://en.wikipedia.org/wiki/ISO_8601#Durations>")
@click.option('--module', nargs=1, default="docker-bench-security", help="The name of the module that implements this task. Separate from task name in case you want to use the same module to run separate tasks with different scopes or schedules. [ 'docker-bench-security', 'kube-bench' ]")
@click.option('--disabled', nargs=1, is_flag=True, help="Disable this task to don't run as defined by its schedule.")
@click.pass_obj
def update(cnf, task, name, scope, schedule, module, disabled):
    """
    TASK: compliance task id to update
    """
    ok, res = cnf.sdsecure.update_compliance_task(
        task,
        name=name,
        module_name=module,
        schedule=schedule,
        scope=scope,
        enabled=not disabled)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_item(res, _item_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@compliance.command(name='del', short_help="Delete compliance tasks")
@click.argument('tasks', nargs=-1, type=click.INT, required=True)
@click.pass_obj
def delete(cnf, tasks):
    """
    TASKS: compliance task ids to delete
    """
    for task in tasks:
        ok, res = cnf.sdsecure.delete_compliance_task(task)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


def _print_result(result, section, level, remediation):
    print_item(result, ["id", "name", "risk", "hostMac"])
    print("{:25} {}/{}/{}".format("Tests fail/warn/pass:", result["failCount"], result["warnCount"], result["passCount"]))
    date = datetime.utcfromtimestamp(result["timestampNs"] / 10**9)
    print("{:25} {}".format("Completed on:", date))

    levels = ["fail", "warn", "pass", "info"]
    valid_levels = levels[:levels.index(level) + 1]
    for test in result["tests"]:
        if section and int(test["sectionId"]) != section:
            continue

        test_results = [r for r in test["results"] if r["status"] in valid_levels]
        if not test_results:
            continue

        print("\n{}. {}".format(test["sectionId"], test["description"]))
        for result in test_results:
            print("{:4} {} - {}".format(result["testNumber"], result["status"], result["description"]))
            if result["items"]:
                print("{}{} {}".format(" " * 5, result["details"], result["items"]))
            if remediation and result["remediation"]:
                print("{}{}".format(" " * 5, result["remediation"]))


def _print_results(results):
    t = PrettyTable(["id", "risk", "name", "host mac", "date", "tests"])
    t.set_style(PLAIN_COLUMNS)
    t.align = 'l'

    for result in results:
        values = []
        values.append(result["id"])
        values.append(result["risk"])
        values.append(result["taskName"])
        values.append(result["hostMac"])
        date = datetime.utcfromtimestamp(result["timestampNs"] / 10**9)
        values.append(date)
        tests = "{}/{}".format(result["passCount"], result["testsRun"])
        values.append(tests)
        t.add_row(values)
    print(t.get_string())
