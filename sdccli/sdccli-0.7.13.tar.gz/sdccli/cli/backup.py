from pathlib import Path

import click
import yaml
import os
import os.path
import sys
from sdccli import drop
from sdccli import restore
from sdccli.usecases.backup import *


@click.group(name='backup', short_help="Backup operations")
def backup():
    pass


@backup.command(name='dump', short_help="Dumps all the information from Monitor and Secure to a directory.")
@click.option('-f', 'overwrite', is_flag=True, help="Overwrite file if it already exists")
@click.argument('backup-file', nargs=1)
@click.argument('section', nargs=-1)
@click.pass_obj
def dump(cnf, overwrite, backup_file, section):
    """
    BACKUP_FILE: File where the data must be saved to.

    SECTION: Restore only the specified section. Valid values: dashboards, notification_channels, alerts, users, teams_monitor, teams_secure, policies, falco_rules, falco_lists, falco_macros
    """
    backup_file_path = Path(backup_file)
    if backup_file_path.exists() and not overwrite:
        print("Error: file {} already exists. Use -f if you want to overwrite it.".format(backup_file))
        sys.exit(1)

    if not backup_file_path.parent.exists():
        backup_file_path.parent.mkdir(parents=True)

    if backup_file_path.exists() and not backup_file_path.is_file():
        print("Error: {} is not file".format(backup_file))
        sys.exit(1)

    repository = open(backup_file, mode='w')
    use_cases_to_execute = []

    if not section or 'dashboards' in section:
        use_cases_to_execute.append(DumpDashboardsUseCase(cnf.sdmonitor, repository))

    if not section or 'notification_channels' in section:
        use_cases_to_execute.append(DumpNotificationChannelsUseCase(cnf.sdmonitor, repository))

    if not section or 'alerts' in section:
        use_cases_to_execute.append(DumpAlertsUseCase(cnf.sdmonitor, repository))

    if not section or 'users' in section:
        use_cases_to_execute.append(DumpUsersUseCase(cnf.sdmonitor, repository))

    if not section or 'teams_monitor' in section:
        use_cases_to_execute.append(DumpTeamsMonitorUseCase(cnf.sdmonitor, repository))

    if not section or 'teams_secure' in section:
        use_cases_to_execute.append(DumpTeamsSecureUseCase(cnf.sdsecure, repository))

    if not section or 'policies' in section:
        if cnf.sdsecure.policy_v2:
            use_cases_to_execute.append(DumpPoliciesUseCase(cnf.sdsecure, repository))
        else:
            use_cases_to_execute.append(DumpPoliciesUseCase(cnf.sdsecure_v1, repository))

    if not section or 'falco_rules' in section:
        use_cases_to_execute.append(DumpUserCreatedRulesUseCase(cnf.sdsecure, repository))

    if not section or 'falco_lists' in section:
        use_cases_to_execute.append(DumpUserCreatedFalcoListsUseCase(cnf.sdsecure, repository))

    if not section or 'falco_macros' in section:
        use_cases_to_execute.append(DumpUserCreatedFalcoMacrosUseCase(cnf.sdsecure, repository))

    errors = []
    for use_case in use_cases_to_execute:
        ok, res = use_case.execute()
        if not ok:
            errors.append(res)

    if len(errors) > 0:
        for error in errors:
            print(error)
        sys.exit(1)
    sys.exit(0)


@backup.command(name='check', short_help="Checks if something has changed in the remote environment "
                                         "comparing it with the backed up version")
@click.argument('backup-path', nargs=1)
@click.pass_obj
def check(cnf, backup_path):
    """
    BACKUP_PATH: Directory where the data must be saved to.
    """
    if not os.path.isdir(backup_path):
        print("Error: {} is not a correct directory".format(backup_path))
        sys.exit(1)

    for name, func in _getters(cnf).items():
        filename = os.path.join(backup_path, name + ".json")
        with open(filename) as file:
            ok, remote_data = func()
            if not ok:
                print("could not retrieve {}: {}".format(name, remote_data))
                continue

            local_data = json.load(file)
            equal = _are_jsons_equal(local_data, remote_data)
            if not equal:
                print("%s differ" % name)


@backup.command(name='restore', short_help="Restores all the information dumped from 'backup' to Monitor and Secure.")
@click.argument('backup-file', nargs=1)
@click.argument('section', nargs=-1)
@click.option('--full', is_flag=True, help="Drop and restore everything from the sections specified. "
                                           "If not specified only items that are different in the backup than in the remote will be restored.")
@click.option('--all-users', is_flag=True, help="Restore dashboards even if you are not the owner "
                                                "(may duplicate the dashboards if they already exist in the environment)")
@click.pass_obj
def restore_from_backup(cnf, backup_file, section, full, all_users):
    """
    BACKUP_PATH: File where the data must be restored from.

    SECTION: Restore only the specified section. Valid values: dashboards, notification_channels, alerts, users, teams_monitor, teams_secure, policies, falco_rules, falco_lists, falco_macros.
    """
    if not os.path.isfile(backup_file):
        print("Error: {} is not a correct backup file".format(backup_file))
        sys.exit(1)

    sdmonitor = cnf.sdmonitor
    sdsecure = cnf.sdsecure

    use_cases_to_execute = []

    if not section or 'dashboards' in section:
        if full:
            if all_users:
                use_cases_to_execute.append(
                    RemoveAllAndRestoreAllDashboardsUseCase(sdmonitor, open(backup_file, mode='r')))
            else:
                use_cases_to_execute.append(
                    RemoveOwnedAndRestoreOwnedDashboardsUseCase(sdmonitor, open(backup_file, mode='r')))
        else:
            if all_users:
                use_cases_to_execute.append(RestoreAllDashboardsUseCase(sdmonitor, open(backup_file, mode='r')))
            else:
                use_cases_to_execute.append(RestoreOwnedDashboardsUseCase(sdmonitor, open(backup_file, mode='r')))

    if not section or 'notification_channels' in section:
        if full:
            use_cases_to_execute.append(
                RemoveAndRestoreNotificationChannelsUseCase(sdmonitor, open(backup_file, mode='r')))
        else:
            use_cases_to_execute.append(RestoreNotificationChannelsUseCase(sdmonitor, open(backup_file, mode='r')))

    if not section or 'alerts' in section:
        if full:
            use_cases_to_execute.append(RemoveAndRestoreAlertsUseCase(sdmonitor, open(backup_file, mode='r')))
        else:
            use_cases_to_execute.append(RestoreAlertsUseCase(sdmonitor, open(backup_file, mode='r')))

    if not section or 'users' in section:
        use_cases_to_execute.append(RestoreUsersUseCase(sdmonitor, open(backup_file, mode='r')))

    if not section or 'teams_monitor' in section:
        if full:
            use_cases_to_execute.append(RemoveAndRestoreTeamsMonitorUseCase(sdmonitor, open(backup_file, mode='r')))
        else:
            use_cases_to_execute.append(RestoreTeamsMonitorUseCase(sdmonitor, open(backup_file, mode='r')))

    if not section or 'teams_secure' in section:
        if full:
            use_cases_to_execute.append(RemoveAndRestoreTeamsSecureUseCase(sdsecure, open(backup_file, mode='r')))
        else:
            use_cases_to_execute.append(RestoreTeamsSecureUseCase(sdsecure, open(backup_file, mode='r')))

    if full:
        if not section or 'policies' in section:
            use_cases_to_execute.append(RemovePoliciesUseCase(sdsecure))
        if not section or 'falco_rules' in section:
            use_cases_to_execute.append(RemoveFalcoRulesUseCase(sdsecure))
        if not section or 'falco_macros' in section:
            use_cases_to_execute.append(RemoveFalcoMacrosUseCase(sdsecure))
        if not section or 'falco_lists' in section:
            use_cases_to_execute.append(RemoveFalcoListsUseCase(sdsecure))

    if not section or 'falco_lists' in section:
        use_cases_to_execute.append(RestoreFalcoListsUseCase(sdsecure, open(backup_file, mode='r')))
    if not section or 'falco_macros' in section:
        use_cases_to_execute.append(RestoreFalcoMacrosUseCase(sdsecure, open(backup_file, mode='r')))
    if not section or 'falco_rules' in section:
        use_cases_to_execute.append(RestoreFalcoRulesUseCase(sdsecure, open(backup_file, mode='r')))
    if not section or 'policies' in section:
        use_cases_to_execute.append(RestorePoliciesUseCase(sdsecure, open(backup_file, mode='r')))

    errors = []
    for use_case in use_cases_to_execute:
        ok, res = use_case.execute()
        if not ok:
            errors.append(res)

    if len(errors) > 0:
        for error in errors:
            print(error)
        sys.exit(1)
    sys.exit(0)


def _are_jsons_equal(json1, json2):
    def ordered(o):
        if isinstance(o, dict):
            return sorted((k, ordered(v)) for k, v in o.items())
        if isinstance(o, list):
            return sorted(ordered(x) for x in o)
        return o

    return ordered(json1) == ordered(json2)
