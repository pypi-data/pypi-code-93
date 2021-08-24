def alert_add(monitor, name, description, severity, atleast, condition, disable, segment, segment_condition,
              user_filter, notify, annotation, type):
    annotations = {}
    if annotation:
        for a in annotation:
            try:
                (k, v) = a.split('=', 1)
                if k and v:
                    annotations[k] = v
                else:
                    return [False, "Error: found null in key or value"]
            except Exception:
                return [False,
                        f"Error: annotation format error - annotations must be of the form (--annotation key=value), "
                        "found: {a}"]

    ok, res = monitor.create_alert(
        name=name,
        description=description,
        severity=severity,
        for_atleast_s=atleast,
        condition=condition,
        segmentby=segment if segment else [],
        segment_condition=segment_condition,
        user_filter=user_filter,
        notify=notify,
        enabled=not disable,
        annotations=annotations,
        type=type)

    if not ok:
        raise Exception(res)

    return res['alert']


def alert_get(monitor, alert):
    alert_id = None
    try:
        alert_id = int(alert)
    except ValueError:
        pass

    ok, res = monitor.get_alerts()
    if not ok:
        raise Exception(res)

    for alert_itr in res['alerts']:
        if alert == alert_itr['name'] or (alert_id is not None and alert_id == alert_itr['id']):
            return alert_itr

    raise Exception(f"no alert with id {alert_id}"
                    if alert_id is not None else
                    f"no alert with name {alert}")


def alert_update(monitor, alert):
    ok, res = monitor.update_alert(alert)
    if not ok:
        raise Exception(res)
    return res['alert']


def alert_list(monitor):
    ok, res = monitor.get_alerts()
    if not ok:
        raise Exception(res)

    return res['alerts']


def alert_delete(monitor, alerts):
    removed_alerts = []
    for alert_id in alerts:
        ok, res = monitor.delete_alert({"id": alert_id})
        removed_alerts.append({"id": alert_id})
        if not ok:
            raise Exception(res)


def alert_add_json(monitor, alert_to_create_json):
    ok, res = monitor.create_alert(alert_obj=alert_to_create_json)
    if not ok:
        raise Exception(res)

    return res['alert']
