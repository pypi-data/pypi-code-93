from abc import ABC, abstractmethod

import yaml

import sdccli.drop as drop
import sdccli.restore as restore


def _same_dict(d1, d2, skip_keys):
    if (d1.keys() - skip_keys) != (d2.keys() - skip_keys):
        return False

    for k in d1.keys():
        if k in skip_keys:
            continue
        if d1[k] != d2[k]:
            return False

    return True


class RemoveUseCase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute(self):
        pass


class RestoreUseCase(ABC):
    def __init__(self, repository, formatter=yaml.safe_load):
        self._repository = repository
        self._formatter = formatter

    @abstractmethod
    def execute(self):
        pass

    def _load_data_from_repo(self, kind):
        file_data = self._formatter(self._repository.read())
        if file_data is None:
            return []
        file_data = [data["spec"] for data in file_data if data["kind"] == kind]
        return file_data


class RestoreMonitorUseCase(RestoreUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        self._monitor = monitor
        super().__init__(repository, formatter)


class RestoreSecureUseCase(RestoreUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        self._secure = secure
        super().__init__(repository, formatter)


class RestoreUsersUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("users")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, data = self._monitor.get_users()
        if not ok:
            return False, data

        existing_user_list = [user["username"] for user in data]
        errors = []
        users_to_invite = [user for user in file_data if not user["username"] in existing_user_list]
        total = len(users_to_invite)
        for i, user in enumerate(users_to_invite):
            print("[{}/{}] Creating user {}... ".format(i + 1, total, user['username']))
            ok, res = self._monitor.create_user_invite(user["username"], user.get("firstName", ""),
                                                       user.get("lastName", ""),
                                                       user["systemRole"])
            if not ok:
                errors.append("couldn't recreate user {} : {}\n".format(user["username"], res))

        if len(errors) != 0:
            return False, errors
        return True, None


class RestoreNotificationChannelsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("notification_channels")
        file_data = [item for sublist in file_data for item in sublist['notificationChannels']]  # Flatten lists

        _, res = self._monitor.list_notification_channels()
        existing_channels = {n['name']: n for n in res['notificationChannels']}

        return restore.notification_channels(file_data, self._monitor, existing_channels)


class RemoveAndRestoreNotificationChannelsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("notification_channels")
        file_data = [item for sublist in file_data for item in sublist['notificationChannels']]  # Flatten lists

        drop.notification_channels(self._monitor)
        return restore.notification_channels(file_data, self._monitor, existing_channels={})


class RestoreOwnedDashboardsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("dashboards")
        file_data = [item for sublist in file_data for item in sublist['dashboards']]  # Flatten lists

        ok, res = self._monitor.get_dashboards()
        if not ok:
            return False, 'Error restoring dashboards: {}'.format(res)

        existing_dashboards = {d['name']: d for d in res['dashboards']}

        return restore.dashboards(file_data, self._monitor, existing_dashboards, restore_unowned=False)


class RestoreAllDashboardsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("dashboards")
        file_data = [item for sublist in file_data for item in sublist['dashboards']]  # Flatten lists

        ok, res = self._monitor.get_dashboards()
        if not ok:
            return False, 'Error restoring dashboards: {}'.format(res)

        existing_dashboards = {d['name']: d for d in res['dashboards']}

        return restore.dashboards(file_data, self._monitor, existing_dashboards, restore_unowned=True)


class RemoveOwnedAndRestoreOwnedDashboardsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("dashboards")
        file_data = [item for sublist in file_data for item in sublist['dashboards']]  # Flatten lists

        ok, res = drop.dashboards(self._monitor, remove_unowned=False)
        if not ok:
            return ok, res
        return restore.dashboards(file_data, self._monitor, existing_dashboards={}, restore_unowned=False)


class RemoveAllAndRestoreAllDashboardsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("dashboards")
        file_data = [item for sublist in file_data for item in sublist['dashboards']]  # Flatten lists

        ok, res = drop.dashboards(self._monitor, remove_unowned=True)
        if not ok:
            return ok, res
        return restore.dashboards(file_data, self._monitor, existing_dashboards={}, restore_unowned=True)


class RestoreAlertsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("alerts")
        file_data = [item for sublist in file_data for item in sublist['alerts']]  # Flatten lists

        return restore.alerts(file_data, self._monitor)


class RemoveAndRestoreAlertsUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("alerts")
        file_data = [item for sublist in file_data for item in sublist['alerts']]  # Flatten lists

        ok, res = drop.alerts(self._monitor)
        if not ok:
            return False, res

        return restore.alerts(file_data, self._monitor)


class RestoreTeamsMonitorUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("monitor_teams")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.teams(file_data, self._monitor)


class RemoveAndRestoreTeamsMonitorUseCase(RestoreMonitorUseCase):
    def __init__(self, monitor, repository, formatter=yaml.safe_load):
        super().__init__(monitor, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("monitor_teams")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.teams(self._monitor)
        if not ok:
            return False, res

        return restore.teams(file_data, self._monitor)


class RestoreTeamsSecureUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("secure_teams")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.teams(file_data, self._secure)


class RemoveAndRestoreTeamsSecureUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("secure_teams")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.teams(self._secure)
        if not ok:
            return False, res

        return restore.teams(file_data, self._secure)


class RestoreFalcoMacrosUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_macros")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.falco_macros(file_data, self._secure)


class RemoveAndRestoreFalcoMacrosUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_macros")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.falco_macros(self._secure)
        if not ok:
            return False, res
        return restore.falco_macros(file_data, self._secure)


class RestoreFalcoListsUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_lists")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.falco_lists(file_data, self._secure)


class RemoveAndRestoreFalcoListsUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_lists")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.falco_lists(self._secure)
        if not ok:
            return False, res
        return restore.falco_lists(file_data, self._secure)


class RestoreFalcoRulesUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_rules")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.rules(file_data, self._secure)


class RemoveAndRestoreFalcoRulesUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("falco_rules")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.rules(self._secure)
        if not ok:
            return False, res
        return restore.rules(file_data, self._secure)


class RestorePoliciesUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("policies")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        return restore.policies(file_data, self._secure)


class RemoveAndRestorePoliciesUseCase(RestoreSecureUseCase):
    def __init__(self, secure, repository, formatter=yaml.safe_load):
        super().__init__(secure, repository, formatter)

    def execute(self):
        file_data = self._load_data_from_repo("policies")
        file_data = [item for sublist in file_data for item in sublist]  # Flatten lists

        ok, res = drop.policies(self._secure)
        if not ok:
            return False, res

        return restore.policies(file_data, self._secure)


class RemoveSecureUseCase(RemoveUseCase):
    def __init__(self, secure):
        self._secure = secure


class RemovePoliciesUseCase(RemoveSecureUseCase):
    def __init__(self, secure):
        super().__init__(secure)

    def execute(self):
        return drop.policies(self._secure)


class RemoveFalcoRulesUseCase(RemoveSecureUseCase):
    def __init__(self, secure):
        super().__init__(secure)

    def execute(self):
        return drop.rules(self._secure)


class RemoveFalcoListsUseCase(RemoveSecureUseCase):
    def __init__(self, secure):
        super().__init__(secure)

    def execute(self):
        return drop.falco_lists(self._secure)


class RemoveFalcoMacrosUseCase(RemoveSecureUseCase):
    def __init__(self, secure):
        super().__init__(secure)

    def execute(self):
        return drop.falco_macros(self._secure)
