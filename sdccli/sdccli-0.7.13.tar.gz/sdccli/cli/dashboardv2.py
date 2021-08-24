import json
import sys

import click

import sdccli.helpers as helpers
import sdccli.usecases.dashboard.dashboard_v2 as use_case


@click.group(name='dashboard_v2', short_help='Sysdig Monitor dashboard operations')
def dashboard_v2():
    pass


@dashboard_v2.command(name='add', short_help="Add a dashboard")
@click.argument('name', nargs=1)
@click.argument('templatefile', nargs=1, type=click.Path(exists=True))
@click.option('--scope', nargs=1,
              help="filter to apply to the dashboard; must be based on metadata available in Sysdig Monitor; Example: *kubernetes.namespace.name='production' and container.image='nginx'*.")
@click.option('--shared', is_flag=True, help="if set the new dashboard will be a shared one.")
@click.option('--public', is_flag=True, help="if set the new dashboard will be shared with public token.")
@click.option('--annotation', nargs=1, multiple=True,
              help="a pair 'key=value' custom property that you can associate to this dashboard for automation or management reasons")
@click.pass_obj
def add(cnf, name, templatefile, scope, shared, public, annotation):
    """
    NAME: name for the new dashboard

    TEMPLATEFILE: A file with a json with "layout" and "items" elements
    """
    try:
        with open(templatefile) as f:
            template = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (templatefile, str(error)))
        sys.exit(1)

    try:
        annotations = helpers.annotation_arguments_to_map(annotation)
        res = use_case.add_dashboard(cnf.sdmonitor_v2, name, template, scope, shared, public, annotations)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard_v2.command(name='add-panel',
                      short_help="Adds a panel to the dashboard. A panel can be a time series, or a top chart (i.e. bar chart), or a number panel.")
@click.argument('dashboard', nargs=1)
@click.argument('name', nargs=1)
@click.option('--type', nargs=1, default="timeSeries",
              help="type of the new panel. Valid values are: 'timeSeries', 'top', 'number'")
@click.option('--metric', nargs=1, multiple=True, required=True,
              help="Specify a metric to show in the panel. A metric comes in the form of 'metricId:aggregation:groupKey'. A metricId is any of the entries that can "
                   "be found in the Metrics section of the Explore page in Sysdig Monitor. A grouping key is any of the entries that can be found in the Show or "
                   "Segment By sections of the Explore page in Sysdig Monitor. Note, certain panels allow certain combinations: timeSeries (1+ metrics or 1 metric + "
                   "grouping), top (1+ metrics or 1 metric + 1 grouping), number (1 metric only)")
@click.option('--scope', nargs=1,
              help="filter to apply to the dashboard; must be based on metadata available in Sysdig Monitor; Example: *kubernetes.namespace.name='production' and container.image='nginx'*.")
@click.option('--sort', nargs=1,
              help="Data sorting; The parameter is optional and it's a dictionary of ``metric`` and ``mode`` (it can be ``desc`` or ``asc``)")
@click.option('--limit', nargs=1, type=click.INT,
              help="This parameter sets the limit on the number of lines/bars shown in a 'timeSeries' or 'top' panel. In the case of more entities being available "
                   "than the limit, the top entities according to the sort will be shown. The default value is 10 for 'top' panels (for 'timeSeries' the default is "
                   "defined by Sysdig Monitor itself). Note that increasing the limit above 10 is not officially supported and may cause performance and rendering issues")
@click.option('--layout', nargs=1,
              help="Size and position of the panel. The dashboard layout is defined by a grid of 12 columns, each row height is equal to the column height. For example, "
                   "say you want to show 2 panels at the top: one panel might be 6 x 3 (half the width, 3 rows height) located in row 1 and column 1 (top-left corner of "
                   "the viewport), the second panel might be 6 x 3 located in row 1 and position 7. The location is specified by 'row:col:width:height'")
@click.pass_obj
def add_panel(cnf, dashboard, name, type, metric, scope, sort, limit, layout):
    """
    DASHBOARD: dashboard (id or name) to edit

    NAME: name of the new panel
    """
    try:
        dashboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor_v2, dashboard).raw()

        panel_builder = use_case.PanelBuilder()
        if layout:
            parts = layout.split(':')
            if len(parts) != 4:
                raise Exception("layout must be in the form of 'row:col:width:height'")
            panel_builder.with_layout(*parts)

        if metric:
            for m in metric:
                parts = m.split(':')
                panel_builder.with_metric(*parts)

        panel = panel_builder.with_name(name).with_type(type).with_scope(scope).with_limit(limit).with_sort(
            sort).build()

        dashboard = use_case.add_panel_to_dashboard(cnf.sdmonitor_v2, dashboard, panel)
        cnf.formatter.format(dashboard, "dashboard")

    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard_v2.command(name='add-json', short_help="Add dashboards from a json file")
@click.argument('jsonfile', nargs=1, type=click.Path(exists=True))
@click.pass_obj
def add_json(cnf, jsonfile):
    """
    JSONFILE: A file with a json description of one or multiple dashboards
    """
    try:
        with open(jsonfile) as f:
            dashboard_json = json.load(f)
    except Exception as error:
        print("Error parsing rules file (%s): %s" % (jsonfile, str(error)))
        sys.exit(1)

    try:
        res = use_case.add_json_dashboard(cnf.sdmonitor_v2, dashboard_json)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard_v2.command(name='list', short_help="List all dashboards")
@click.pass_obj
def list_dashboards(cnf):
    try:
        res = use_case.list_dashboards(cnf.sdmonitor_v2)
        cnf.formatter.format(res, "dashboardList")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard_v2.command(name='get', short_help="Get dashboard")
@click.argument('dashboard', nargs=1)
@click.pass_obj
def get(cnf, dashboard):
    """
    DASHBOARD: The dashboard (id or name) to get
    """
    try:
        res = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor_v2, dashboard)
        cnf.formatter.format(res, "dashboard")
    except Exception as ex:
        print(f"Error: {str(ex)}")
        sys.exit(1)


@dashboard_v2.command(name='del', short_help="Delete dashboards")
@click.argument('dashboards', nargs=-1, required=True)
@click.pass_obj
def delete(cnf, dashboards):
    """
    DASHBOARDS: Dashboard id to delete
    """
    try:
        use_case.delete_dashboards_by_id(cnf.sdmonitor_v2, dashboards)
        print("Success")
    except Exception as ex:
        print(f"Error deleting dashboard: {str(ex)}")


@dashboard_v2.command(name='del-panel', short_help="Removes a panel from the dashboard")
@click.argument('dashboard', nargs=1)
@click.argument('name', nargs=1)
@click.pass_obj
def delete_panel(cnf, dashboard, name):
    """
    DASHBOARD: dashboard (id or name) to delete the panel from

    NAME: name of the panel to find and remove
    """
    try:
        dboard = use_case.get_dashboard_by_id_or_name(cnf.sdmonitor_v2, dashboard)
        use_case.remove_panel_from_dashboard(cnf.sdmonitor_v2, dboard, name)
        print("Success")
    except Exception as ex:
        print(f"Error {str(ex)}")
        sys.exit(1)
