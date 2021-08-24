import click
import json
import sys
from sdccli.printer import print_list, print_item


_item_keys = ["id", "name", "description", "default", "show", "filter", "canUseSysdigCapture", "canUseCustomEvents", "canUseAwsMetrics"]
_list_keys = ["id", "name", "default", "userCount"]


@click.group(name='team', short_help='Sysdig team operations')
def team():
    pass


@team.command(name='add', short_help="Create a new team")
@click.argument('name', nargs=1)
@click.option('--member', nargs=1, multiple=True, help="a user name or pair user-name=team-role of a member of the team")
@click.option('--filter', nargs=1, default='', help="the scope that this team is able to access within Sysdig Monitor.")
@click.option('--description', nargs=1, default='', help="describes the team that will be created.")
@click.option('--show', nargs=1, default='host', help="possible values are *host*, *container*.")
@click.option('--theme', nargs=1, default='#7BB0B2', help="the color theme that Sysdig will use when displaying the team. In #RRGGBB form.")
@click.option('--perm-capture', is_flag=True, help="if True, this team will be allowed to take sysdig captures.")
@click.option('--perm-custom-events', is_flag=True, help="if True, this team will be allowed to view all custom events from every user and agent.")
@click.option('--perm-aws-data', is_flag=True, help="if True, this team will have access to all AWS metrics and tags, regardless of the team's scope.")
@click.pass_obj
def add(cnf, name, member, filter, description, show, theme, perm_capture, perm_custom_events, perm_aws_data):
    """
    NAME: the name of the team to create.
    """
    memberships = None
    if member:
        memberships = {}
        for m in member:
            if '=' in m:
                (k, v) = m.split('=', 1)
                memberships[k] = v
            else:
                memberships[m] = "ROLE_TEAM_EDIT"

    ok, res = cnf.sd.create_team(
        name,
        memberships=memberships,
        filter=filter,
        description=description,
        show=show,
        theme=theme,
        perm_capture=perm_capture,
        perm_custom_events=perm_custom_events,
        perm_aws_data=perm_custom_events)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_team(res["team"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='del-member', short_help="Remove a member from a team")
@click.argument('team', nargs=1)
@click.argument('user-name', nargs=1)
@click.pass_obj
def del_member(cnf, team, user_name):
    """
    TEAM: the name of the team to remove the member from.
    USER-NAME: the name of the user to remove.
    """
    ok, res = cnf.sd.remove_memberships(team, [user_name])

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='add-member', short_help="Add a member to a team")
@click.argument('team', nargs=1)
@click.argument('user-name', nargs=1)
@click.option('--role', nargs=1, default='ROLE_TEAM_EDIT', help="The role for the user in the team. (default 'ROLE_TEAM_EDIT')")
@click.pass_obj
def add_member(cnf, team, user_name, role):
    """
    TEAM: the name of the team to add the member to.
    USER-NAME: the name of the user to add.
    """
    ok, res = cnf.sd.save_memberships(team, memberships={user_name: role})

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print("Success")
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='list', short_help="List all teams")
@click.pass_obj
def list(cnf):
    ok, res = cnf.sd.get_teams()

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        print_list(res, _list_keys)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='update', short_help="Update the team")
@click.argument('name', nargs=1)
@click.option('--member', nargs=1, multiple=True, help="a user name or pair user-name=team-role of a member of the team")
@click.option('--filter', nargs=1, default=None, help="the scope that this team is able to access within Sysdig Monitor.")
@click.option('--description', nargs=1, default='', help="describes the team that will be created.")
@click.option('--show', nargs=1, default='host', help="possible values are *host*, *container*.")
@click.option('--theme', nargs=1, default='#7BB0B2', help="the color theme that Sysdig will use when displaying the team. In #RRGGBB form.")
@click.option('--perm-capture', is_flag=True, help="if True, this team will be allowed to take sysdig captures.")
@click.option('--perm-custom-events', is_flag=True, help="if True, this team will be allowed to view all custom events from every user and agent.")
@click.option('--perm-aws-data', is_flag=True, help="if True, this team will have access to all AWS metrics and tags, regardless of the team's scope.")
@click.pass_obj
def upd(cnf, name, member, filter, description, show, theme, perm_capture, perm_custom_events, perm_aws_data):
    """
    NAME: the name of the team to update.
    """
    memberships = None
    if member:
        memberships = {}
        for m in member:
            if '=' in m:
                (k, v) = m.split('=', 1)
                memberships[k] = v
            else:
                memberships[m] = "ROLE_TEAM_EDIT"

    ok, res = cnf.sd.edit_team(
        name,
        memberships=memberships,
        filter=filter,
        description=description,
        show=show,
        theme=theme,
        perm_capture=perm_capture,
        perm_custom_events=perm_custom_events,
        perm_aws_data=perm_custom_events)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_team(res["team"])
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='get', short_help="Get team")
@click.argument('team', nargs=1)
@click.pass_obj
def get(cnf, team):
    """
    TEAM: the team name or id to get
    """
    try:
        id = int(team)
        ok, res = cnf.sd.get_teams()
        if ok:
            found = False
            for t in res:
                if id == t['id']:
                    res = t
                    found = True
                    break
            if not found:
                print("Error: no team with id {}".format(id))
                sys.exit(1)
                return
    except ValueError:
        ok, res = cnf.sd.get_team(team)

    if cnf.json:
        print(json.dumps(res, indent=4))
        return

    if ok:
        _print_team(res)
    else:
        print("Error: " + str(res))
        sys.exit(1)


@team.command(name='del', short_help="Delete users")
@click.argument('names', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, names):
    """
    NAMES: The names of the teams to delete
    """
    for name in names:
        ok, res = cnf.sd.delete_team(name)

        if not ok:
            print("Error: " + str(res))
            sys.exit(1)

    print("Success")


def _print_team(team):
    print_item(team, _item_keys)
    print("{:25} {}".format("Entry point:", team["entryPoint"]["module"]))
    print("")
    print_list(team["userRoles"], ["userId", "userName", "role", "admin"])
