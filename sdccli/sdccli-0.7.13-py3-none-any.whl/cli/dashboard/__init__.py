import json
import sys

import click

from sdccli.cli.dashboard.panel import panel

import sdccli.usecases.dashboard.dashboard_v3 as use_case
import sdccli.usecases.settings.team as team_usecase


@click.group(name='dashboard', short_help='Sysdig Monitor dashboard operations')
def dashboard():
    pass


dashboard.add_command(panel)


@dashboard.command(name='add', short_help="Add a dashboard")
@click.argument('name', nargs=1)
@click.argument('templatefile', nargs=1, type=click.Path(exists=True))
@click.option('--scope', nargs=1, multiple=True,
              help="filter to apply to the dashboard; must be based on metadata available in Sysdig Monitor; Example: kubernetes.namespace.name in [prod, dev]")
@click.option('--public', is_flag=True, help="if set the new dashboard will be shared with public token.")
@click.pass_obj
def add(cnf, name, templatefile, scope, public):
    """
    NAME: name for the new dashboard

    TEMPLATEFILE: A file with a json with "layout" and "items" elements
    """
    try:
        with open(templatefile) as f:
            template = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (templatefile, str(error)))
        sys.exit(1)

    try:
        res = use_case.add_dashboard(cnf.sdmonitor, name, template, list(scope), public)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard.command(name='add-json', short_help="Add dashboards from a json file")
@click.argument('jsonfile', nargs=1, type=click.Path(exists=True))
@click.option('--ignore-sharing-settings', is_flag=True, help="Ignores the sharing settings configured in the JSON, "
                                                              "not sending them to the API")
@click.pass_obj
def add_json(cnf, jsonfile, ignore_sharing_settings):
    """
    JSONFILE: A file with a json description of one or multiple dashboards
    """
    try:
        with open(jsonfile) as f:
            dashboard_json = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (jsonfile, str(error)))
        sys.exit(1)

    try:
        res = use_case.add_json_dashboard(cnf.sdmonitor, dashboard_json, ignore_sharing_settings)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)

@dashboard.command(name='update-json', short_help="Update dashboards from a json file")
@click.argument('jsonfile', nargs=1, type=click.Path(exists=True))
@click.option('--ignore-sharing-settings', is_flag=True, help="Ignores the sharing settings configured in the JSON, "
                                                              "not sending them to the API")
@click.pass_obj
def update_json(cnf, jsonfile, ignore_sharing_settings):
    """
    JSONFILE: A file with a json description of one or multiple dashboards
    """
    try:
        with open(jsonfile) as f:
            dashboard_json = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (jsonfile, str(error)))
        sys.exit(1)

    try:
        res = use_case.update_json_dashboard(cnf.sdmonitor, dashboard_json, ignore_sharing_settings)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)

@dashboard.command(name='list', short_help="List all dashboards")
@click.pass_obj
def list_dashboards(cnf):
    try:
        res = use_case.list_dashboards(cnf.sdmonitor)
        cnf.formatter.format(res, "dashboardList")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard.command(name='get', short_help="Get dashboard")
@click.argument('dashboard', nargs=1)
@click.pass_obj
def get(cnf, dashboard):
    """
    DASHBOARD: The dashboard (id or name) to get
    """
    try:
        res = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor, dashboard)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard.command(name='del', short_help="Delete dashboards")
@click.argument('dashboards', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, dashboards):
    """
    DASHBOARDS: Dashboard id to delete
    """
    try:
        use_case.delete_dashboards_by_id(cnf.sdmonitor, dashboards)
        print("Success")
    except Exception as ex:
        print(f"Error deleting dashboard: {str(ex)}")


@dashboard.command(name='share', short_help="Share a dashboard")
@click.argument('dashboards', nargs=-1, required=True)
@click.option('--all-teams', is_flag=True, help="Share dashboard with all my teams")
@click.option('--team', nargs=1, help="Share dashboard with the selected team (name or ID)")
@click.option('-w', is_flag=True, help="Share the dashboard as read-write for the selected team(s). "
                                       "If not specified, it will be shared as read-only.")
@click.pass_obj
def share(cnf, dashboards, all_teams, team, w):
    errors = []
    mode = "w" if w else "r"
    for dboard in dashboards:
        try:
            dboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor, dboard)
        except Exception as ex:
            errors.append(ex)
            continue

        if all_teams:
            try:
                res = use_case.share_dashboard_with_all_teams(cnf.sdmonitor, dboard, mode)
                print(f"Shared {dboard['name']} with all teams")
            except Exception as ex:
                print(f"Could not share {dboard} with all teams")
                errors.append(ex.message)
        else:
            try:
                if team is None or team == "":
                    errors.append("Team not provided, specify one with --team or all with --all-teams")
                    break
                team = team_usecase.retrieve_team_by_name_or_id(cnf.sdmonitor, team)
                res = use_case.share_dashboard_with_team(cnf.sdmonitor, dboard, team["id"], mode)
                print(f"Shared {dboard['name']} with team {team['name']}")
            except Exception as ex:
                errors.append(ex.message)

    for error in errors:
        print(error)
    if len(errors) > 0:
        sys.exit(1)


@dashboard.command(name='unshare', short_help="Unshare a dashboard")
@click.argument('dashboards', nargs=-1, required=True)
@click.pass_obj
def share(cnf, dashboards):
    errors = []
    for dboard in dashboards:
        try:
            dboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor, dboard)
        except Exception as ex:
            errors.append(ex)
            continue

        try:
            use_case.unshare_dashboard(cnf.sdmonitor, dboard)
            print(f"Unshared {dboard['name']}")
        except Exception as ex:
            errors.append(ex.message)

    for error in errors:
        print(error)
    if len(errors) > 0:
        sys.exit(1)


@dashboard.command(name='fav', short_help="Favorite a dashboard")
@click.argument('dashboards', nargs=-1, required=True)
@click.pass_obj
def fav(cnf, dashboards):
    errors = []
    for dboard in dashboards:
        try:
            dboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor, dboard)
        except Exception as ex:
            errors.append(ex)
            continue

        try:
            use_case.favorite_dashboard(cnf.sdmonitor, dboard, True)
            print(f"{dboard['name']} is now favorite")
        except Exception as ex:
            errors.append(ex.message)

    for error in errors:
        print(error)
    if len(errors) > 0:
        sys.exit(1)


@dashboard.command(name='unfav', short_help="Unfavorite a dashboard")
@click.argument('dashboards', nargs=-1, required=True)
@click.pass_obj
def unfav(cnf, dashboards):
    errors = []
    for dboard in dashboards:
        try:
            dboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor, dboard)
        except Exception as ex:
            errors.append(ex)
            continue

        try:
            use_case.favorite_dashboard(cnf.sdmonitor, dboard, False)
            print(f"{dboard['name']} is now not favorite")
        except Exception as ex:
            errors.append(ex.message)

    for error in errors:
        print(error)
    if len(errors) > 0:
        sys.exit(1)