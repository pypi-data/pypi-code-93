import json

import requests
from sdcclient import SdSecureClient, SdMonitorClient
from sdcclient._common import _SdcCommon

from sdccli.falco_macro import SortMacrosByDepedency

ORIGIN_SECURE_UI = "Secure UI"


def dashboards(file_data, sdmonitor, existing_dashboards, restore_unowned):
    errors = []
    ok, userdata = sdmonitor.get_user_info()
    if not ok:
        return False, userdata

    username = userdata["user"]["username"]
    dashboards = [dboard for dboard in file_data if
                  restore_unowned or "username" in dboard and username in dboard["username"]]
    total = len(dashboards)
    for i, dashboard in enumerate(dashboards):
        name = dashboard['name']
        print("[{}/{}] Creating dashboard {}... ".format(i + 1, total, name.strip()))
        if name in existing_dashboards:
            if same_dict(dashboard, existing_dashboards[name],
                         ['id', 'customerId', 'teamId',
                          'userId', 'username', 'autoCreated', 'publicToken']):
                print("      already exists, skip")
                continue
            else:
                sdmonitor.delete_dashboard(existing_dashboards[name])

        dashboard['id'] = None
        dashboard['version'] = None

        # We need to update the team IDs in case the old ones have been removed
        if dashboard.get("teamName") is not None:
            ok, res = sdmonitor.get_team(dashboard.get("teamName"))
            if ok:
                dashboard["teamId"] = res["id"]
        if "sharingSettings" in dashboard:
            for setting in dashboard["sharingSettings"]:
                if setting["member"]["name"] is not None:
                    ok, res = sdmonitor.get_team(setting["member"]["name"])
                    if ok:
                        setting["member"]["id"] = res["id"]

        ok, result = sdmonitor.create_dashboard_with_configuration(dashboard)
        if not ok:
            errors.append("couldn't recreate dashboard " + name + ': ' + result)

    if len(errors) != 0:
        return False, errors
    return True, None


def alerts(file_data, monitor: SdMonitorClient):
    errors = []
    total = len(file_data)
    ok, res = monitor.get_alerts()
    if not ok:
        return False, res
    existing_alerts = {alert['name']: alert for alert in res['alerts']}

    ok, res = monitor.list_notification_channels()
    if not ok:
        return False, res
    existing_notification_channels = {nc['name']: nc['id'] for nc in res['notificationChannels']}

    for i, alert in enumerate(file_data, start=1):
        name = alert['name']
        alert['notificationChannelIds'] = []
        for nc in alert.get('notificationChannelNames', []):
            if nc in existing_notification_channels:
                alert['notificationChannelIds'].append(existing_notification_channels[nc])
            else:
                print(f"  Warning: The Notification Channel '{nc}' does not exist in the environment, "
                      f"the restored alert won't be assigned to this NC.")
        print(f"[{i}/{total}] Creating alert {name}... ")
        if name in existing_alerts:
            if same_dict(alert, existing_alerts[name],
                         ['id', 'teamId', 'autoCreated',
                          'notificationChannelNames', 'notificationCount', 'invalidMetrics',
                          'valid']):
                print("      already exists, skip")
                continue
            else:
                ok, res = monitor.delete_alert(existing_alerts[name])
                if not ok:
                    errors.append(res)
                    continue

        ok, result = monitor.create_alert(alert_obj=alert)
        if not ok:
            errors.append(result)

    if len(errors) > 0:
        return False, errors
    return True, None


def users(sdcommon, filename):
    '''
    Restores users without dropping the existing ones
    '''
    with open(filename) as file:
        file_data = json.load(file)

        existing_user_list = []
        ok, data = sdcommon.get_users()
        if not ok:
            return False, data

        existing_user_list = [user["username"] for user in data]

        errors = []
        users = [user for user in file_data if not user["username"] in existing_user_list]
        total = len(users)
        for i, user in enumerate(users):
            print("[{}/{}] Creating user {}... ".format(i + 1, total, user['username']))
            ok, res = sdcommon.create_user_invite(user["username"], user.get("firstName", ""), user.get("lastName", ""),
                                                  user["systemRole"])
            if not ok:
                errors.append("couldn't recreate user " + user["username"] + " : " + res)

        if len(errors) != 0:
            return False, errors
        return True, None


# TODO: Move this to the python-sdc-client
def get_user_created_rules(secure: SdSecureClient):
    ok, res = secure.list_rules()
    if not ok:
        return False, res

    user_created_rules = []
    for list in res:
        for j, id in enumerate(list['ids']):
            if list['publishedBys'][j]['origin'] == ORIGIN_SECURE_UI:
                user_rules = list.copy()

                user_rules['id'] = list['ids'][j]
                del user_rules['ids']

                user_rules['publishedBy'] = list['publishedBys'][j]
                del user_rules['publishedBys']

                user_created_rules.append(user_rules)

    return True, user_created_rules


def rules(file_data, sdsecure: SdSecureClient):
    errors = []
    total = len(file_data)
    ok, existing_rules = get_user_created_rules(sdsecure)
    if not ok:
        return False, existing_rules

    existing_rules = {l['name']: l for l in existing_rules}
    for i, rule in enumerate(file_data, start=1):
        name = rule["name"]
        print(f"[{i}/{total}] Creating rule {name}... ")
        if name in existing_rules:
            ok, erule = sdsecure.get_rule_id(existing_rules[name]['id'])
            if not ok:
                errors.append(erule)
                continue

            if same_dict(rule, erule,
                         ['id', 'filename', 'origin', 'sysdig',
                          'versionId']):
                print("      already exists, skip")
                continue

            ok, res = sdsecure.update_rule(erule['id'], rule['details'], rule['description'], rule['tags'])
            if not ok:
                errors.append(res)
            continue

        ok, result = sdsecure.add_rule(name, rule["details"], rule["description"], rule["tags"])
        if not ok:
            errors.append("couldn't recreate rule " + name + ': ' + result)

    if len(errors) > 0:
        return False, errors
    return True, None


# TODO: Move this to the python-sdc-client
def get_user_created_lists(secure: SdSecureClient):
    ok, res = secure.list_falco_lists()
    if not ok:
        return False, res

    user_created_lists = []
    for list in res:
        for j, id in enumerate(list['ids']):
            if list['publishedBys'][j]['origin'] == ORIGIN_SECURE_UI:
                user_list = list.copy()

                user_list['id'] = list['ids'][j]
                del user_list['ids']

                user_list['publishedBy'] = list['publishedBys'][j]
                del user_list['publishedBys']

                user_created_lists.append(user_list)

    return True, user_created_lists


# FIXME: Remove this as soon as the PR is merged in the python-sdc-client
def _add_falco_list(self, name, items, append=False):
    '''**Description**
        Create a new list

    **Arguments**
        - name: A name for this object. Should exactly be the value of the "list" property of the yaml object.
        - items: the array of items as represented in the yaml List.

    **Success Return Value**
        A JSON object representing the falco list.
    '''
    flist = {
        "name": name,
        "items": {
            "items": items
        },
        "append": append,
    }
    res = self.http.post(self.url + '/api/secure/falco/lists', data=json.dumps(flist), headers=self.hdrs,
                         verify=self.ssl_verify)
    return self._request_result(res)


def falco_lists(file_data, secure: SdSecureClient):
    errors = []
    total = len(file_data)
    ok, existing_lists = get_user_created_lists(secure)
    if not ok:
        return False, existing_lists
    existing_lists = {l['name']: l for l in existing_lists}
    for i, falco_list in enumerate(file_data, start=1):
        name = falco_list["name"]
        print(f"[{i}/{total}] Creating falco list {name}... ")
        if name in existing_lists:
            ok, elist = secure.get_falco_list_id(existing_lists[name]['id'])
            if not ok:
                errors.append(elist)
                continue

            if same_dict(
                    falco_list, elist,
                    ['id', 'filename', 'origin', 'sysdig', 'versionId']) and elist['items']['items'] == \
                    falco_list['items']['items']:
                print("      already exists, skip")
                continue

            ok, res = secure.update_falco_list(elist['id'], falco_list['items']['items'])
            if not ok:
                errors.append(res)
            continue

        ok, result = _add_falco_list(secure, name=name, items=falco_list['items']['items'], append=falco_list['append'])
        if not ok:
            errors.append(f"couldn't recreate falco list {name}: {result}")

    if len(errors) > 0:
        return False, errors
    return True, None


# TODO: Move this method to the python-sdc-client
def get_user_created_macros(secure: SdSecureClient):
    ok, res = secure.list_falco_macros()
    if not ok:
        return False, res

    user_created_macros = []
    for macro in res:
        for j, id in enumerate(macro['ids']):
            if macro['publishedBys'][j]['origin'] == ORIGIN_SECURE_UI:
                user_macro = macro.copy()

                user_macro['id'] = macro['ids'][j]
                del user_macro['ids']

                user_macro['publishedBy'] = macro['publishedBys'][j]
                del user_macro['publishedBys']

                user_created_macros.append(user_macro)

    return True, user_created_macros


# FIXME: Please, avoid evil hacks and send a PR
def _add_falco_macro(self, name, condition, append=False):
    '''**Description**
        Create a new macro

    **Arguments**
        - name: A name for this object. Should exactly be the value of the "macro" property of the yaml object.
        - condition: the full condition text exactly as represented in the yaml file.

    **Success Return Value**
        A JSON object representing the falco macro.
    '''
    macro = {
        "name": name,
        "condition": {
            "components": [],
            "condition": condition
        },
        "append": append
    }
    res = requests.post(self.url + '/api/secure/falco/macros', data=json.dumps(macro), headers=self.hdrs,
                        verify=self.ssl_verify)
    return self._request_result(res)


def falco_macros(file_data, sdsecure: SdSecureClient):
    # Falco macros must be created in order of dependency
    file_data = SortMacrosByDepedency(file_data).sort(reverse=True)
    errors = []
    total = len(file_data)
    ok, existing_macros = get_user_created_macros(sdsecure)

    existing_macros = {macro["name"]: macro for macro in existing_macros}
    for i, macro in enumerate(file_data, start=1):
        name = macro["name"]
        print(f"[{i}/{total}] Creating falco macro {name}... ")
        if name in existing_macros:
            ok, emacro = sdsecure.get_falco_macro_id(existing_macros[name]['id'])
            if not ok:
                errors.append(emacro)
                continue
            if same_dict(
                    macro, emacro,
                    ['id', 'filename', 'origin', 'sysdig', 'versionId']) and \
                    emacro['condition']['condition'] == macro['condition']['condition']:
                print("      already exists, skip")
                continue

            sdsecure.update_falco_macro(emacro['id'], macro['condition']['condition'])
            continue

        ok, result = _add_falco_macro(sdsecure, name=name, condition=macro["condition"]["condition"],
                                      append=macro['append'])
        if not ok:
            errors.append("couldn't recreate falco macro " + name + ': ' + result)

    if len(errors) != 0:
        return False, errors
    return True, None


def policies(file_data, secure: SdSecureClient):
    errors = []

    ok, existing_policies = secure.list_policies()
    if not ok:
        return False, existing_policies

    existing_policies = {policy['name']: policy for policy in existing_policies}
    total = len(file_data)
    for i, policy in enumerate(file_data, start=1):
        name = policy['name']
        print(f"[{i}/{total}] Creating policy {name}... ")
        if name in existing_policies:
            if same_dict(policy, existing_policies[name],
                         ['name', 'description', 'ruleNames', 'actions', 'notificationChannelIds', 'origin',
                          'versionId']):
                print("      already exists, skip")
                continue
            else:
                ok, result = secure.update_policy(
                    id=existing_policies[name]['id'],
                    name=policy['name'],
                    description=policy['description'],
                    rule_names=policy['ruleNames'],
                    actions=policy['actions'],
                    scope=policy['scope'] if 'scope' in policy else None,
                    severity=policy['severity'],
                    enabled=policy['enabled'],
                    notification_channels=policy['notificationChannelIds']
                )
                if not ok:
                    errors.append(result)
                continue

        ok, result = secure.add_policy(
            name,
            policy['description'],
            rule_names=policy['ruleNames'],
            actions=policy['actions'],
            scope=policy['scope'] if 'scope' in policy else None,
            severity=policy['severity'],
            enabled=policy['enabled'],
            notification_channels=policy['notificationChannelIds'],
            type=policy.get('type', 'falco')
        )
        if not ok:
            errors.append(result)

    if len(errors) > 0:
        return False, errors
    return True, None


# TODO: Remove this, we do not support priorities anymore
def policy_priorities(sdsecure, filename, ids_changed=None):
    with open(filename) as file:
        file_data = json.load(file)
        del file_data["priorities"]["createdOn"]
        del file_data["priorities"]["modifiedOn"]

        errors = []

        if ids_changed is not None:
            oldIdsChanged = set([int(key) for key in ids_changed.keys()])
            priorityList = file_data["priorities"]["policyIds"]
            for i, oldId in enumerate(priorityList):
                if oldId in oldIdsChanged:
                    priorityList[i] = int(ids_changed[str(oldId)])

            file_data["priorities"]["policyIds"] = priorityList

        print("Retrieving current version of the priorities... ")
        ok, res = sdsecure.get_policy_priorities()
        if not ok:
            errors.append("couldn't retrieve the current version of the priorities: " + res)
            return False, errors  # without the current version we can't restore the priorities
        else:
            current_version = res["priorities"]["version"]
            file_data["priorities"]["version"] = current_version

        print("Restoring policy priorities... ")
        ok, result = sdsecure.set_policy_priorities(json.dumps(file_data))
        if not ok:
            errors.append("couldn't restore policy priorities: " + result)

        if len(errors) != 0:
            return False, errors
        else:
            return True, None


def teams(file_data, sdcommon: _SdcCommon):
    errors = []
    total = len(file_data)

    okTeams, res = sdcommon.get_teams()
    if not okTeams:
        return False, res

    existing_teams = {team['name']: team for team in res}
    mutable_teams = [team for team in file_data if not team['immutable']]
    total = len(mutable_teams)
    for i, team in enumerate(mutable_teams, start=1):
        print(f"[{i}/{total}] Creating team {team['name'].strip()}... ")
        memberships = {member['userName']: member['role'] for member in team['userRoles']}
        filter = team['filter'] if 'filter' in team else ''
        description = team['description'] if 'description' in team else ''
        if team['name'] in existing_teams:
            ok, result = sdcommon.edit_team(name=team['name'],
                                            memberships=memberships,
                                            filter=filter,
                                            description=description,
                                            show=team['show'],
                                            theme=team['theme'],
                                            perm_capture=team['canUseSysdigCapture'],
                                            perm_custom_events=team['canUseCustomEvents'],
                                            perm_aws_data=team['canUseAwsMetrics'])
        else:
            ok, result = sdcommon.create_team(name=team['name'],
                                              memberships=memberships,
                                              filter=filter,
                                              description=description,
                                              show=team['show'],
                                              theme=team['theme'],
                                              perm_capture=team['canUseSysdigCapture'],
                                              perm_custom_events=team['canUseCustomEvents'],
                                              perm_aws_data=team['canUseAwsMetrics'])

        if not ok:
            if "409" in result:  # Team already existing, not an error
                print("Team " + team['name'] + " already exists")
                continue
            errors.append("couldn't recreate team " + team['name'] + ': ' + result)

    if len(errors) != 0:
        return False, errors
    return True, None


def notification_channels(file_data, sdmonitor, existing_channels):
    errors = []
    ids_changed = {}
    total = len(file_data)
    for i, channel in enumerate(file_data):
        id = channel["id"]
        name = channel["name"] if "name" in channel else ""
        type = channel["type"] if "type" in channel else ""
        print("[{}/{}] Creating notification channel {} of type {}... ".format(i + 1, total, name, type))
        if name in existing_channels:
            if same_dict(channel, existing_channels[name],
                         ['id']):
                print("      already exists, skip")
                ids_changed[str(id)] = str(existing_channels[name]['id'])
                continue
            else:
                sdmonitor.delete_notification_channel(existing_channels[name])

        del channel["teamId"]
        ok, result = sdmonitor.create_notification_channel(channel)
        if not ok:
            errors.append("couldn't recreate team " + channel['name'] + ': ' + result)
        else:
            ids_changed[str(id)] = str(result["notificationChannel"]["id"])

    if errors:
        return False, errors
    return True, ids_changed


def user_falco_rules(sdsecure, filename):
    with open(filename) as file:
        file_data = json.load(file)
        print('Restoring user falco rules...')
        ok, result = sdsecure.set_user_falco_rules(file_data["userRulesFile"]["content"])
        if not ok:
            return False, result
        return True, None


def same_dict(d1, d2, skip_keys):
    if (d1.keys() - skip_keys) != (d2.keys() - skip_keys):
        return False

    for k in d1.keys():
        if k in skip_keys:
            continue
        if d1[k] != d2[k]:
            return False

    return True
