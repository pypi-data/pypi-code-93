from sdcclient.monitor import DashboardsClientV3


class Panel:
    def __init__(self, name, type, scope, metrics, sort, layout_dict, limit):
        self.name = name
        self.type = type
        self.scope = scope
        self.metrics = metrics
        self.sort = sort
        self.layout_dict = layout_dict
        self.limit = limit


class PanelBuilder:
    def __init__(self):
        self._name = "Panel"
        self._type = "timeSeries"
        self._scope = None
        self._metrics = []
        self._layout_dict = None
        self._sort = "desc"
        self._limit = None

    def with_layout(self, row, col, width, height):
        self._layout_dict = {
            "row": row,
            "col": col,
            "size_x": width,
            "size_y": height
        }
        return self

    def with_metric(self, id, time=None, group=None):
        if not id:
            raise Exception(f"cannot build a panel without id")
        metric_dict = {'id': id}
        if time and group:
            metric_dict["aggregations"] = {}
            metric_dict["aggregations"]['time'] = time
            metric_dict["aggregations"]['group'] = group
        self._metrics.append(metric_dict)
        return self

    def with_name(self, name):
        self._name = name
        if not name or not isinstance(name, str):
            raise Exception(f"name invalid or empty: '{name}'")
        return self

    def with_type(self, type):
        valid_types = ['timeSeries', 'top', 'number']
        if type not in valid_types:
            raise Exception(f"invalid type {type}, must be one of {valid_types}")
        self._type = type
        return self

    def with_scope(self, scope):
        self._scope = scope
        return self

    def with_limit(self, limit):
        if limit and limit > 10:
            raise Exception(f"invalid limit {limit} higher than the max of 10, could cause rendering problems")
        self._limit = limit
        return self

    def with_sort(self, sort):
        self._sort = sort
        return self

    def build(self):
        return Panel(name=self._name,
                     type=self._type,
                     scope=self._scope,
                     metrics=self._metrics,
                     sort=self._sort,
                     layout_dict=self._layout_dict,
                     limit=self._limit)


def add_dashboard(monitor, name, template, scope, public):
    ok, res = monitor.create_dashboard_from_template(
        name, template, scope,
        public=public)

    if not ok:
        raise Exception(res)
    return res["dashboard"]


def list_dashboards(monitor):
    ok, res = monitor.get_dashboards()

    if not ok:
        raise Exception(res)

    return res["dashboards"]


def delete_dashboards_by_id(monitor, ids):
    for id in ids:
        ok, res = monitor.delete_dashboard({"id": id})
        if not ok:
            raise Exception(res)


def get_dashboard_by_id_or_name(monitor, dashboard):
    try:
        # By ID
        id = int(dashboard)
        ok, res = monitor.get_dashboards()
        if not ok:
            raise Exception(res)

        for d in res["dashboards"]:
            if id == d["id"]:
                ok, res = monitor.get_dashboard(d["id"])
                if not ok:
                    raise Exception(res)
                return res["dashboard"]

        raise Exception(f"no dashboard with id {id}")
    except ValueError:
        # By Name
        ok, res = monitor.find_dashboard_by(dashboard)
        if not ok:
            raise Exception(res)

        if len(res) == 0:
            raise Exception(f"no dashboard with name '{dashboard}' found")

        ok, res = monitor.get_dashboard(res[0]["dashboard"]["id"])
        if not ok:
            raise Exception(res)
        return res["dashboard"]


def add_panel_to_dashboard(monitor, dashboard, panel):
    ok, res = monitor.add_dashboard_panel(
        dashboard, panel.name, panel.type, panel.metrics,
        scope=panel.scope,
        sort_direction=panel.sort,
        limit=panel.limit,
        layout=panel.layout_dict)
    if not ok:
        raise Exception(res)

    return res["dashboard"]


def add_json_dashboard(monitor, dashboard):
    result = ""

    def add_json(monitor, dboard):
        dboard['timeMode'] = {'mode': 1}
        dboard['time'] = {'last': 2 * 60 * 60 * 1000000, 'sampling': 2 * 60 * 60 * 1000000}
        ok, res = monitor.create_dashboard_with_configuration(dboard)
        if ok:
            return "Created dashboard {}".format(dboard['name'])
        else:
            raise Exception("Error creating the dashboard {}: {}".format(dboard['name'], res))

    if isinstance(dashboard, list):
        for db in dashboard:
            result += add_json(monitor, db) + "\n"
    elif isinstance(dashboard, dict):
        result = add_json(monitor, dashboard)
    else:
        raise Exception("Unsupported JSON format")

    return result


def remove_panel_from_dashboard(monitor, dashboard, name):
    ok, res = monitor.remove_dashboard_panel(dashboard, name)

    if not ok:
        raise Exception("Error deleting dashboard ({}): {}".format(id, res))
