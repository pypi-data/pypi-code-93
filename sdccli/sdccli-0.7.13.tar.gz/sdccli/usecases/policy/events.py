from sdcclient import SdSecureClient

from sdccli.time import duration_to_seconds


def retrieve_all_policy_events(secure: SdSecureClient, duration=None, scope=None, severity=None, type=None,
                               search=None, limit=None):
    if not duration:
        duration = "3D"

    if not limit:
        limit = 50

    duration_sec = duration_to_seconds(duration)
    if duration_sec is None:
        raise ValueError("The specified duration is incorrect")

    if duration_sec < 600:
        raise ValueError("The minimum duration is 10 minutes (10M)")

    filtering = []

    if scope:
        filtering.append(scope)

    if severity:
        number_severities = []
        sevs = set(sev.strip().lower() for sev in severity.split(","))

        if "high" in sevs:
            number_severities.extend([0, 1, 2, 3])
        if "med" in sevs:
            number_severities.extend([4, 5])
        if "low" in sevs:
            number_severities.append(6)
        if "info" in sevs:
            number_severities.append(7)

        text_severities = [f'"{sev}"' for sev in number_severities]

        severity_filter = f"severity in ({','.join(text_severities)})"
        filtering.append(severity_filter)

    if type:
        types_str = [f'"{t.strip().lower()}"'
                     for t in type.split(",")]
        type_filter = f"originator in ({','.join(types_str)})"
        filtering.append(type_filter)

    if search:
        search_filter = f'freeText in ("{search}")'
        filtering.append(search_filter)

    filter = " and ".join(filtering) if filtering else None
    all_events = []
    ok, res = secure.get_policy_events_duration(duration_sec=duration_sec, filter=filter)
    if not ok:
        raise Exception(res)

    all_events.extend(res["data"])

    while res["data"] and len(res["data"]) == res["ctx"]["limit"] and len(all_events) < limit:
        ok, res = secure.get_more_policy_events(res["ctx"])
        if not ok:
            raise Exception(res)
        all_events.extend(res["data"])

    return all_events[:limit]


def retrieve_policy_event_by_id(secure: SdSecureClient, event_id):
    ok, res = secure.get_policy_event(event_id)
    if not ok:
        raise Exception(res)

    return res
