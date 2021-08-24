from sdccli.printer import print_item, print_list

_item_keys = ["alertId", "name", "enabled", "description", "scope", "triggers",
              "notificationChannelIds", "createdAt", "updatedAt"]
_list_keys = ["alertId", "name", "enabled"]


def formats():
    return {
        "scanningAlertList": format_scanning_alert_list,
        "scanningAlert": format_scanning_alert,
    }


def format_scanning_alert(alert):
    print_item(alert, _item_keys)


def format_scanning_alert_list(alert_list):
    print_list(alert_list, _list_keys)
