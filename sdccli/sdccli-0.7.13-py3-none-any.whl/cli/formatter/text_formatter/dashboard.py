import json

from sdccli.printer import print_list as _print_list, print_item as _print_item


def formats():
    return {
        "dashboardList": print_dashboard_list,
        "dashboard": print_dashboard,
    }


_list_keys = ["id", "name", "username", "autoCreated", "shared", "public", "favorite"]
_item_keys = ["id", "name", "username", "autoCreated", "shared", "public", "favorite", "filterExpression"]


def print_dashboard(dashboard):
    _print_item(dashboard, _item_keys)
    if "widgets" not in dashboard:
        return

    print("Panels:")
    items = dashboard["widgets"]
    for item in items:
        if "metrics" in item:
            item["metrics"] = [m["id"] for m in item["metrics"]]
        else:
            item["metrics"] = []
    _print_list(items, ["", "name", "showAs", "metrics"])


def print_dashboard_list(response):
    _print_list(response, _list_keys)
