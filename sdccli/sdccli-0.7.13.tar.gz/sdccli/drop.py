from multiprocessing.pool import ThreadPool

from sdcclient import SdSecureClient

from sdccli.falco_macro import SortMacrosByDepedency

ORIGIN_SECURE_UI = 'Secure UI'
ORIGIN_SYSDIG = 'Sysdig'


def dashboards(sdmonitor, remove_unowned=False):
    ok, data = sdmonitor.get_dashboards()
    if not ok:
        return False, data

    ok, userdata = sdmonitor.get_user_info()
    if not ok:
        return False, userdata

    username = userdata["user"]["username"]
    res = []
    dashboards = [dboard for dboard in data['dashboards'] if
                  remove_unowned or "username" in dboard and username in dboard["username"]]
    errors = []
    total = len(dashboards)
    for i, dashboard in enumerate(dashboards):
        print("[{}/{}] Removing dashboard {}... ".format(
            i + 1, total, dashboard['name'].strip()))
        removed, err = sdmonitor.delete_dashboard(dashboard)
        if removed:
            res.append(dashboard)
        else:
            errors.append(err)

    if errors:
        return False, errors

    return True, res


def alerts(sdmonitor):
    ok, data = sdmonitor.get_alerts()
    if not ok:
        return False, data

    res = []
    errors = []
    total = len(data['alerts'])
    for i, alert in enumerate(data['alerts'], start=1):
        print(f"[{i}/{total}] Removing alert {alert['name'].strip()}...")
        removed, err = sdmonitor.delete_alert(alert)
        if removed:
            res.append(alert)
        else:
            errors.append(err)

    if len(errors) > 0:
        return False, errors
    return True, res


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


def rules(sdsecure):
    ok, data = get_user_created_rules(sdsecure)
    if not ok:
        return False, data

    result = []
    errors = []
    total = len(data)
    for i, rule in enumerate(data, start=1):
        print(f"[{i}/{total}] Removing rule {rule['name'].strip()}...")
        ok, res = sdsecure.delete_rule(rule['id'])
        if not ok:
            errors.append(res)
            continue
        result.append(rule)

    if len(errors) > 0:
        return False, errors
    return True, result


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


def falco_lists(sdsecure: SdSecureClient):
    ok, data = get_user_created_lists(sdsecure)
    if not ok:
        return False, data

    errors = []
    result = []
    total = len(data)
    for i, flist in enumerate(data, start=1):
        print(f"[{i}/{total}] Removing falco list {flist['name'].strip()}...")
        ok, res = sdsecure.delete_falco_list(flist['id'])
        if not ok:
            errors.append(res)
            continue
        result.append(flist)

    if len(errors) > 0:
        return False, errors
    return True, result


# TODO: Move this method to the python-sdc-client
# This only creates a single API call
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


# TODO: Move this method to the python-sdc-client
# This creates N API calls where N is the number of user created macros.
# This is because the information retrieved by list_falco_macros() is incomplete.
# If one wants to retrieve the conditions of every macro and not only the names, they need to
# retrieve one by one.
def get_full_user_created_macros(secure: SdSecureClient):
    ok, macros = get_user_created_macros(secure)
    # usedCount field is always 0 no matter if this macro is being used in a policy or by other macro :/
    if not ok:
        return False, macros

    errors = []
    full_macros = []
    for ok, res in ThreadPool().map(secure.get_falco_macro_id, (macro['id'] for macro in macros)):
        if not ok:
            errors.append(res)
        else:
            full_macros.append(res)

    if len(errors) > 0:
        return False, errors
    return True, full_macros


def falco_macros(sdsecure: SdSecureClient):
    ok, macros = get_full_user_created_macros(sdsecure)
    if not ok:
        return False, macros

    sorted_macros_by_dependency = SortMacrosByDepedency(macros).sort()

    errors = []
    total = len(sorted_macros_by_dependency)
    for i, macro in enumerate(sorted_macros_by_dependency, start=1):
        print(f"[{i}/{total}] Removing falco macro {macro['name'].strip()}...")
        ok, res = sdsecure.delete_falco_macro(macro['id'])
        if not ok:
            errors.append(res)

    if len(errors) > 0:
        return False, errors

    return True, sorted_macros_by_dependency


def policies(sdsecure: SdSecureClient):
    ok, data = sdsecure.list_policies()
    if not ok:
        return False, data
    # Policies are the only resource that can be removed with an origin different from "Secure UI".
    # Policies from "Sysdig" can also be removed. This does not happen with rules, lists, etc.
    removable_policies = [policy for policy in data if policy['origin'] in [ORIGIN_SECURE_UI, ORIGIN_SYSDIG]]

    errors = []
    res = []
    total = len(removable_policies)

    for i, policy in enumerate(removable_policies, start=1):
        print(f"[{i}/{total}] Removing policy {policy['name'].strip()}... ")
        removed, err = sdsecure.delete_policy_id(policy['id'])
        if removed:
            res.append(policy)
        else:
            errors.append(err)

    if len(errors) > 0:
        return False, errors
    return True, res


def teams(sdmonitor):
    ok, data = sdmonitor.get_teams()
    if not ok:
        return False, data

    res = []
    errors = []
    mutable_teams = [team for team in data if not team['immutable'] and not team['default']]
    total = len(mutable_teams)
    for i, team in enumerate(mutable_teams, start=1):
        print(f"[{i}/{total}] Removing team {team['name'].strip()}... ")
        removed, err = sdmonitor.delete_team(team['name'])
        if removed:
            res.append(team)
        else:
            errors.append(res)

    if len(errors) > 0:
        return False, errors
    return True, res


def notification_channels(sdmonitor):
    ok, data = sdmonitor.list_notification_channels()
    if not ok:
        return False, data

    res = []
    total = len(data['notificationChannels'])
    for i, channel in enumerate(data['notificationChannels']):
        print("[{}/{}] Removing notification channel {}... ".format(
            i + 1, total, channel['name']))
        removed, err = sdmonitor.delete_notification_channel(channel)
        if removed:
            res.append(channel)
        else:
            print("Error: " + err)

    return True, res
