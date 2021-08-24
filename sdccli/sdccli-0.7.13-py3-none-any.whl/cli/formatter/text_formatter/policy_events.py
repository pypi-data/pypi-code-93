from datetime import datetime

from dateutil import parser

from sdccli.printer import print_list, print_item

_severity_mapping = ["HIGH", "HIGH", "HIGH", "HIGH", "MED", "MED", "LOW", "INFO"]


def formats():
    return {
        "policyEventV1List": print_policy_events_v1,
        "policyEventV1": print_policy_event_v1
    }


def print_policy_event_v1(event):
    event["date"] = datetime.strftime(parser.parse(event["timestamp"]), "%Y-%m-%d %H:%M:%S %Z")
    event["type"] = event["originator"]
    event["severity"] = _severity_mapping[event["severity"]]
    ruleTags = event["content"].get("ruleTags", []) or []
    event["tags"] = ", ".join(ruleTags)
    event["output"] = event["content"].get("output", "")
    print_item(event, ["id", "name", "description", "date", "type", "severity", "output", "tags"])

    if "fields" in event["content"]:
        print("fields:")
        max_size = max(len(k) for k in event["content"]["fields"].keys())
        for key, value in event["content"]["fields"].items():
            print(f"  {key:{max_size}}  {value}")

    if "image" in event["content"]:
        print("image:")

        max_size = max(len(k) for k in event["content"]["image"].keys())
        for key, value in event["content"]["image"].items():
            print(f"  {key:{max_size}}  {value}")



    if "labels" in event:
        print("labels:")
        max_size = max(len(k) for k in event["labels"].keys())
        for key, value in event["labels"].items():
            print(f"  {key:{max_size}}  {value}")


def print_policy_events_v1(data):
    if not data:
        print("No policy events found")

    policy_events = [{
        "id": event["id"],
        "name": event["name"],
        "severity": _severity_mapping[event["severity"]],
        "type": event["originator"],
        "date": datetime.strftime(parser.parse(event["timestamp"]), "%Y-%m-%d %H:%M:%S %Z"),
    } for event in data]

    print_list(policy_events, ["id", "name", "severity", "type", "date"])
