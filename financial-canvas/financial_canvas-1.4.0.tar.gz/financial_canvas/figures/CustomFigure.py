from functools import partial

from bokeh.plotting import figure as bokeh_figure
from bokeh.models import CustomJS
from financial_canvas.figures.utils import create_sources
from financial_canvas.figures.utils import read_file


class CustomFigure(object):
    '''
    A base class for creating bokeh figures that will filter. Bokeh 
    already has live data filtering capabilities through CDSViews but it has its drawbacks:
        * lines are not supported by filtered view bokeh, related bokeh issues:
            * https://github.com/bokeh/bokeh/issues/9388
            * https://github.com/bokeh/bokeh/issues/7070
        * y axis autoscale does not work with zoom
            * TODO: report to bokeh

    Sources and figure are extendable so that it's possible add new elements to the figure.

    Args:
        df (pandas.DataFrame): should have 'date_time' as index 
            (in pandas.DatetimeIndex format), main sources will be created from this df
            all columns will be added to sources
        file_name (str): Error code.
        file_name (int, optional): Error code.
        selected_from (pandas.Timestamp) date from which to select the short initially drawn source

    Attributes:
        sources (dict with tuples with bokeh.models.ColumnDataSource (source, origin)): 
            source - initial source that the chart will be made from 
                (short, before any js callback updates) 
            origin - large source, will be used to recreate source after inside JS callbacks
        p (bokeh.models.Figure): the plot with glyphs
        selected_from (pandas.Timestamp) date from which to select
    '''
    def __init__(self, df, *, selected_from=None):
        if selected_from is None:
            selected_from = df.index[0]
        self.sources = create_sources(df, selected_from=selected_from)
        self.selected_from = selected_from
        self.p = None

    def add_hover(self, columns):
        hover_tool = self.p.hover
        # hover_tool.tooltips = []
        # hover_tool.formatters = {}
        for column_name, pretty_name in columns.items():
            hover_tool.tooltips.extend([
                (pretty_name, '@' + column_name + '{%f}'),
            ])
            hover_tool.formatters.update({
                '@' + column_name: 'printf',
            })

    def get_figure_defaults(self):
        return partial(
            bokeh_figure,
            # even though "webgl" is advertised as the fastest engine
            # not using it here because it introduces a bug (TODO: report bug to bokeh repo)
            # when panning/zooming the window some glyphs like circles or diamonds can stay
            # where from previous view
            output_backend="canvas",
            # TODO: pass arguments to constructor
            plot_height=450,
            margin=(10, 10, 10, 10),
            height_policy='fixed',
            sizing_mode='stretch_width',
        )

    def y_axis_autorange(self):
        yaxis = self.p.left[0]
        yaxis.formatter.use_scientific = False

        if (self.y_range_resize_columns):
            y_axis_auto_range_callback = CustomJS(
                args=dict(
                    unique_name=id(self),
                    y_range=self.p.y_range,
                    # TODO: deal with multiple sources
                    source=self.sources['main'][0],
                    columns=self.y_range_resize_columns,
                ),
                code=read_file('y_axis_auto_range.js'))
            self.p.x_range.js_on_change('start', y_axis_auto_range_callback)
            self.p.x_range.js_on_change('end', y_axis_auto_range_callback)

    def add_sources(self, df, name):
        additional_sources = create_sources(df,
                                            selected_from=self.selected_from,
                                            name=name)
        self.sources.update(additional_sources)
        return self.sources
