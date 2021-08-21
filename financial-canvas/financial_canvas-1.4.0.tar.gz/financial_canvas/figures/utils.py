from bokeh.models import ColumnDataSource

import importlib.resources as pkg_resources
from .. import js_callbacks


def create_sources(df, selected_from=None, name='main'):
    sources = {}

    def get_bokeh_source(df):
        dict_source = {'index': df.index}
        for column in df.columns:
            dict_source[column] = df[column]
        return ColumnDataSource(dict_source)

    source_df = df[df.index >= selected_from] if selected_from else df
    source = get_bokeh_source(source_df)
    origin = get_bokeh_source(df)

    sources.update({
        name: (source, origin),
    })

    return sources


def read_file(file_name):
    return pkg_resources.read_text(js_callbacks, file_name)
