from rest_framework.renderers import JSONRenderer, BaseRenderer
from rest_framework_csv.renderers import CSVRenderer as BaseCSVRenderer


class TextRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "text"
    format_description = "text"

    def render(self, data, *args, **kwargs):
        if isinstance(data, dict):  # For instance used if the API returns an exception
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        return str(data)


class PrettyJsonRenderer(JSONRenderer):
    format = "json"
    format_description = "JSON"

    def render(self, data, *args, **kwargs):
        if str(data.__class__) == "<class 'pandas.core.frame.DataFrame'>":
            data = {
                "data": [
                    {k: v for k, v in zip(data.columns, row)} for row in data.values
                ]
            }

        return super().render(data, *args, **kwargs)

    def get_indent(self, accepted_media_type, renderer_context):
        return 4


class JsonStatRenderer(PrettyJsonRenderer):
    format = "json-stat"
    format_description = "JSON-stat"

    def render(self, data, *args, **kwargs):
        # We handle pandas DF but we do not want to had dependencies on it hence
        # It's up to the user to provide access to pyjstat
        if str(data.__class__) == "<class 'pandas.core.frame.DataFrame'>":
            from pyjstat import pyjstat
            import pandas

            def flatten_metrics_data_frame(data):
                json_stat_data = []
                # noqa: B301
                for _index, row in data.iterrows():
                    # noinspection PyCompatibility
                    # IDEs detect row.iteritems as a call
                    # to dict.iteritems which is not supported in py3,
                    # whereas it is pandas.Series.iteritems()
                    group_data = {
                        key: value
                        for key, value in row.iteritems()  # noqa: B301
                        if key != "metrics"
                    }
                    for metric, metric_value in row.metrics.items():
                        metric_data = {"metric": metric, "value": metric_value}
                        metric_data.update(group_data)
                        json_stat_data.append(metric_data)
                return pandas.DataFrame(json_stat_data)

            flatten_data_frame = flatten_metrics_data_frame(data)
            if len(flatten_data_frame.index) > 0:
                data = {"data": pyjstat.Dataset.read(flatten_data_frame)}
            else:
                data = {"data": []}

        return super().render(data, *args, **kwargs)


class CSVRenderer(BaseCSVRenderer):
    def __init__(self):
        pass

    def render(self, data, *args, **kwargs):
        if str(data.__class__) == "<class 'pandas.core.frame.DataFrame'>":
            data = [{k: v for k, v in zip(data.columns, row)} for row in data.values]

        return super().render(data, *args, **kwargs)

    media_type = "text"
    format = "csv"
    format_description = "CSV"


def renderer(*renderers):
    def add_renderers(view):
        view.renderer_classes = renderers
        return view

    return add_renderers
