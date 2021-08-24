from sdcclient import SdMonitorClient

PANEL_VISUALIZATION_TIMECHART = "advancedTimechart"
PANEL_VISUALIZATION_NUMBER = "advancedNumber"


# TODO(fede): Move this to the Python SDK
def get_panels_from_dashboard(monitor: SdMonitorClient, dashboard_id):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    return res["dashboard"]["panels"]


# TODO(fede): Move this to the Python SDK
def delete_panel_from_dashboard(monitor: SdMonitorClient, dashboard_id, panel_id):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    res["dashboard"]["panels"] = [panel for panel in res["dashboard"]["panels"] if panel["id"] != panel_id]
    res["dashboard"]["layout"] = [layout for layout in res["dashboard"]["layout"] if layout["panelId"] != panel_id]

    ok, res = monitor.update_dashboard(res["dashboard"])
    if not ok:
        raise Exception(res)

# TODO(fede): Move this to the Python SDK
def create_panel_in_dashboard(monitor: SdMonitorClient, dashboard_id, panel_name, visualization, query):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    new_panel_id = res["dashboard"]["panels"][-1]["id"] + 1
    new_panel = {
        "id": new_panel_id,
        "type": visualization,
        "name": panel_name,
        "description": "",
        "advancedQueries": [
            {
                "enabled": True,
                "displayInfo": {
                    "displayName": "",
                    "timeSeriesDisplayNameTemplate": "",
                    "type": "lines"
                },
                "format": {
                    "unit": "%",
                    "inputFormat": "0-100",
                    "displayFormat": "auto",
                    "decimals": None,
                    "yAxis": "auto"
                },
                "query": query
            }
        ]
    }
    new_layout = {
        "panelId": new_panel_id,
        "x": 0,
        # Hackish way to position a panel, the API doesn't provide auto-position
        "y": len(res["dashboard"]["panels"]) * 12 + 12,
        "w": 12,
        "h": 6,
    }

    if visualization == PANEL_VISUALIZATION_TIMECHART:
        new_panel["axesConfiguration"] = {
            "bottom": {
                "enabled": True
            },
            "left": {
                "enabled": True,
                "displayName": None,
                "unit": "auto",
                "displayFormat": "auto",
                "decimals": None,
                "minValue": 0,
                "maxValue": None,
                "minInputFormat": "0-100",
                "maxInputFormat": "0-100",
                "scale": "linear"
            },
            "right": {
                "enabled": True,
                "displayName": None,
                "unit": "auto",
                "displayFormat": "auto",
                "decimals": None,
                "minValue": 0,
                "maxValue": None,
                "minInputFormat": "1",
                "maxInputFormat": "1",
                "scale": "linear"
            }
        }
        new_panel["legendConfiguration"] = {
            "enabled": True,
            "position": "right",
            "layout": "table",
            "showCurrent": True
        }
    if visualization == PANEL_VISUALIZATION_NUMBER:
        new_panel["numberThresholds"] = {
            "values": [],
            "base": {
                "severity": "none",
                "displayText": "",
            }
        }

    res["dashboard"]["panels"].append(new_panel)
    res["dashboard"]["layout"].append(new_layout)

    ok, res = monitor.update_dashboard(res["dashboard"])
    if not ok:
        raise Exception(res)

    return res["dashboard"]["panels"][-1]


# TODO(fede): Move this to the Python SDK
def get_queries_from_panel(monitor: SdMonitorClient, dashboard_id, panel_id):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    panel_list = [panel for panel in res["dashboard"]["panels"] if panel["id"] == panel_id]
    if len(panel_list) == 0:
        raise Exception(f"panel with id {panel_id} not found in dashboard {dashboard_id}")

    panel = panel_list[0]
    return [query["query"] for query in panel["advancedQueries"]]


# TODO(fede): Move this to the Python SDK
def add_query_to_panel(monitor: SdMonitorClient, dashboard_id, panel_id, query):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    panel_list = [panel for panel in res["dashboard"]["panels"] if panel["id"] == panel_id]
    if len(panel_list) == 0:
        raise Exception(f"panel with id {panel_id} not found in dashboard {dashboard_id}")

    panel = panel_list[0]
    if panel["type"] not in [PANEL_VISUALIZATION_TIMECHART]:
        raise Exception("cannot add query to this kind of panel")


    new_query = {
        "enabled": True,
        "displayInfo": {
            "displayName": "",
            "timeSeriesDisplayNameTemplate": "",
            "type": "lines"
        },
        "format": {
            "unit": "%",
            "inputFormat": "0-100",
            "displayFormat": "auto",
            "decimals": None,
            "yAxis": "auto"
        },
        "query": query
    }
    panel["advancedQueries"].append(new_query)

    ok, res = monitor.update_dashboard(res["dashboard"])
    if not ok:
        raise Exception(res)

    panel_list = [panel for panel in res["dashboard"]["panels"] if panel["id"] == panel_id]
    panel = panel_list[0]
    return [query["query"] for query in panel["advancedQueries"]]


# TODO(fede): Move this to the Python SDK
def del_query_from_panel(monitor: SdMonitorClient, dashboard_id, panel_id, query_id):
    ok, res = monitor.get_dashboard(dashboard_id)
    if not ok:
        raise Exception(res)

    panel_list = [panel for panel in res["dashboard"]["panels"] if panel["id"] == panel_id]
    if len(panel_list) == 0:
        raise Exception(f"panel with id {panel_id} not found in dashboard {dashboard_id}")

    panel = panel_list[0]

    if panel["type"] not in [PANEL_VISUALIZATION_TIMECHART, PANEL_VISUALIZATION_NUMBER]:
        raise Exception("removing queries from non-promql panels is not supported yet")

    if len(panel["advancedQueries"]) == 1:
        raise Exception(f"cannot remove the only query for a panel")

    if len(panel["advancedQueries"]) > (query_id + 1):
        raise Exception(f"query {query_id} not found in panel {panel_id} from dashboard {dashboard_id}")

    del panel["advancedQueries"][query_id]

    ok, res = monitor.update_dashboard(res["dashboard"])
    if not ok:
        raise Exception(res)

    panel_list = [panel for panel in res["dashboard"]["panels"] if panel["id"] == panel_id]
    panel = panel_list[0]
    return [query["query"] for query in panel["advancedQueries"]]

