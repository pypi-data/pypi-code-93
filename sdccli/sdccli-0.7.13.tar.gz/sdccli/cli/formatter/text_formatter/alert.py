from sdccli.printer import print_list, print_item


def format_alert_list(data):
    print_list(data, ["id", "name", "type", "enabled", "severityLabel"])


def format_alert(data):
    print_item(data,
               ["id", "name", "description", "type", "enabled", "severityLabel", "segmentBy", "segmentCondition",
                "condition", "timespan"])


def formats():
    return {
        "alertList": format_alert_list,
        "alert": format_alert,
    }
