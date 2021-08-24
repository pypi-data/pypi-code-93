from abc import abstractmethod, ABC
from multiprocessing.pool import ThreadPool

import yaml

ORIGIN_SECURE_UI = 'Secure UI'
ORIGIN_SYSDIG = 'Sysdig'


class DumpUseCase(ABC):
    @abstractmethod
    def execute(self):
        pass

    @staticmethod
    def _sort_res(res):
        if isinstance(res, list):
            res.sort(key=lambda item: item["id"])

        elif isinstance(res, dict):
            for k, v in res.items():
                if isinstance(v, list) and len(v) > 0 and "id" in v[0]:
                    res[k].sort(key=lambda item: item["id"])


class DumpMonitorUseCase(DumpUseCase):
    def __init__(self, monitor, repository, formatter=yaml.dump):
        self._monitor = monitor
        self._repository = repository
        self._formatter = formatter


class DumpSecureUseCase(DumpUseCase):
    def __init__(self, secure, repository, formatter=yaml.dump):
        self._secure = secure
        self._repository = repository
        self._formatter = formatter


class DumpUsersUseCase(DumpMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.dump):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        ok, res = self._monitor.get_users()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "users", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpDashboardsUseCase(DumpMonitorUseCase):
    def __init__(self, monitor, repository):
        super().__init__(monitor, repository)

    def execute(self):
        ok, res = self._dashboard_getter()
        if not ok:
            return ok, res

        self._sort_res(res)

        res = [{"kind": "dashboards", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res

    def _dashboard_getter(self):
        ok, res = self._monitor.get_dashboards()
        if not ok:
            return ok, res

        ok, teams = self._monitor.get_teams()
        team_match = {team["id"]: team["name"] for team in teams} if ok else {}
        dashboards = []
        errors = []
        for ok, data in ThreadPool().map(self._monitor.get_dashboard, (db["id"] for db in res["dashboards"])):
            if ok:
                data["dashboard"]["teamName"] = team_match.get(data["dashboard"].get("teamId", 0))
                dashboards.append(data["dashboard"])
            else:
                errors.append(data)

        if len(errors) > 0:
            return False, errors

        return True, {"dashboards": dashboards}


class DumpAlertsUseCase(DumpMonitorUseCase):
    def __init__(self, monitor, repository):
        super().__init__(monitor, repository)

    def execute(self):
        ok, res = self._monitor.get_alerts()
        if not ok:
            return ok, res
        self._sort_res(res)

        ok, resNC = self._monitor.list_notification_channels()
        if not ok:
            return ok, resNC


        res = [{"kind": "alerts", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpTeamsMonitorUseCase(DumpMonitorUseCase):
    def __init__(self, monitor, repository):
        super().__init__(monitor, repository)

    def execute(self):
        ok, res = self._monitor.get_teams()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "monitor_teams", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpNotificationChannelsUseCase(DumpMonitorUseCase):
    def __init__(self, monitor, repository):
        super().__init__(monitor, repository)

    def execute(self):
        ok, res = self._monitor.list_notification_channels()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "notification_channels", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpTeamsSecureUseCase(DumpSecureUseCase):
    def __init__(self, secure, repository):
        super().__init__(secure, repository)

    def execute(self):
        ok, res = self._secure.get_teams()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "secure_teams", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpPoliciesUseCase(DumpSecureUseCase):
    def __init__(self, secure, repository):
        super().__init__(secure, repository)

    def execute(self):
        ok, res = self._secure.list_policies()
        if not ok:
            return ok, res
        self._sort_res(res)
        # Restorable policies are the ones created by the Secure UI and the ones provided by Sysdig.
        # This only happens with policies, with other resources only the ones created by Secure UI can be removed.
        restorable_policies = [policy for policy in res if policy['origin'] in [ORIGIN_SECURE_UI, ORIGIN_SYSDIG]]

        res = [{"kind": "policies", "version": 1, "spec": restorable_policies}]

        self._repository.write(self._formatter(res))
        return ok, res


class DumpUserCreatedRulesUseCase(DumpSecureUseCase):
    def __init__(self, secure, repository):
        super().__init__(secure, repository)

    def execute(self):
        ok, res = self._rules_getter()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "falco_rules", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res

    def _rules_getter(self):
        ok, res = self._get_user_created_rules()
        if not ok:
            return ok, res

        rules = []
        errors = []
        for ok, data in ThreadPool().map(self._secure.get_rule_id, (i["id"] for i in res)):
            if ok:
                rules.append(data)
            else:
                errors.append(data)

        if len(errors) > 0:
            return False, errors

        return True, rules

    # TODO: Move this to the python-sdc-client
    def _get_user_created_rules(self):
        ok, res = self._secure.list_rules()
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


class DumpUserCreatedFalcoMacrosUseCase(DumpSecureUseCase):
    def __init__(self, secure, repository):
        super().__init__(secure, repository)

    def execute(self):
        ok, res = self._falco_macros_getter()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "falco_macros", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res

    # TODO: Move this to the python-sdc-cli
    def _get_user_created_macros(self):
        ok, res = self._secure.list_falco_macros()
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

    def _falco_macros_getter(self):

        ok, res = self._get_user_created_macros()
        if not ok:
            return ok, res

        falco_macros = []
        errors = []
        for ok, data in ThreadPool().map(self._secure.get_falco_macro_id, (i['id'] for i in res)):
            if ok:
                falco_macros.append(data)
            else:
                errors.append(data)

        if len(errors) > 0:
            return False, errors
        return True, falco_macros


class DumpUserCreatedFalcoListsUseCase(DumpSecureUseCase):
    def __init__(self, secure, repository):
        super().__init__(secure, repository)

    def execute(self):
        ok, res = self._falco_lists_getter()
        if not ok:
            return ok, res
        self._sort_res(res)

        res = [{"kind": "falco_lists", "version": 1, "spec": res}]

        self._repository.write(self._formatter(res))
        return ok, res

    # TODO: Move this to the python-sdc-client
    def _get_user_created_lists(self):
        ok, res = self._secure.list_falco_lists()
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

    def _falco_lists_getter(self):
        ok, res = self._get_user_created_lists()
        if not ok:
            return ok, res

        falco_lists = []
        errors = []
        for ok, data in ThreadPool().map(self._secure.get_falco_list_id, (i["id"] for i in res)):
            if ok:
                falco_lists.append(data)
            else:
                errors.append(data)

        if len(errors) > 0:
            return False, errors

        return True, falco_lists


class DumpEverythingUseCase(object):
    def __init__(self, monitor, secure, repository):
        # Monitor
        self._dump_users_to_repository = DumpUsersUseCase(monitor, repository)
        self._dump_dashboards_to_repository = DumpDashboardsUseCase(monitor, repository)
        self._dump_alerts_to_repository = DumpAlertsUseCase(monitor, repository)
        self._dump_teams_monitor_to_repository = DumpTeamsMonitorUseCase(monitor, repository)
        self._dump_notification_channels_to_repository = DumpNotificationChannelsUseCase(monitor,
                                                                                         repository)
        # Secure
        self._dump_teams_secure_to_repository = DumpTeamsSecureUseCase(secure, repository)
        self._dump_policies_to_repository = DumpPoliciesUseCase(secure, repository)
        self._dump_rules_to_repository = DumpUserCreatedRulesUseCase(secure, repository)
        self._dump_falco_macros_to_repository = DumpUserCreatedFalcoMacrosUseCase(secure, repository)
        self._dump_falco_lists_to_repository = DumpUserCreatedFalcoListsUseCase(secure, repository)

    def execute(self):
        errors = []

        # Monitor
        ok, res = self._dump_users_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_dashboards_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_alerts_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_teams_monitor_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_notification_channels_to_repository.execute()
        if not ok:
            errors.append(res)

        # Secure
        ok, res = self._dump_teams_secure_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_policies_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_rules_to_repository.execute()
        if not ok:
            errors.append(res)

        ok, res = self._dump_falco_lists_to_repository.execute()
        if not ok:
            errors.append(res)

        if len(errors) > 0:
            return False, errors

        return True, []
