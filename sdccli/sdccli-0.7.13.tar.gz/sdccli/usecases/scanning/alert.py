from sdcclient import SdScanningClient


def add_scanning_alert(scanning, name, description, scope, unscanned, failed, enabled, notification_channels):
    ok, res = scanning.add_alert(
        name=name,
        description=description,
        scope=scope,
        triggers={'unscanned': unscanned, 'failed': failed},
        enabled=enabled,
        notification_channels=notification_channels)
    if not ok:
        raise Exception(res)

    return res


def get_alert_by_id(scanning, alert_id):
    ok, res = scanning.get_alert(alert_id)
    if not ok:
        raise Exception(res)
    return res


def list_scanning_alerts(scanning: SdScanningClient):
    ok, res = scanning.list_alerts()
    if not ok:
        return Exception(res)

    return res["alerts"]


def update_scanning_alert(scanning: SdScanningClient, alert_id, alert_data):
    ok, res = scanning.update_alert(alert_id, alert_data)
    if not ok:
        raise Exception(res)
    return res;


def delete_scanning_alert(scanning: SdScanningClient, alert_id):
    ok, res = scanning.delete_alert(alert_id)
    if not ok:
        raise Exception(res)
    return res;
