from bokeh.models import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from financial_canvas.figures.constants import COLOR_PALLETE
from financial_canvas.figures.CustomFigure import CustomFigure
from bokeh.models import Span, Scatter
import seaborn as sns


class MultiCircle(CustomFigure):
    '''
    A figure with multiple circles. Each cirlce color corresponds to each column name
    docs for the form of the points: https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/scatter.html#bokeh.models.glyphs.Scatter
    '''
    def __init__(self,
                 df,
                 columns,
                 *,
                 selected_from=None,
                 figure_args=None,
                 scatter_args=None,
                 colors=None,
                 x_range=None):
        # TODO: update dynamically
        self.y_range_resize_columns = columns

        if figure_args is None:
            figure_args = {}

        if scatter_args is None:
            scatter_args = {}

        if selected_from is None:
            selected_from = df.index[0]

        if colors is None:
            colors = sns.color_palette("colorblind", len(columns)).as_hex()

        super().__init__(df, selected_from=selected_from)

        tooltips = [
            ('Date', '@index{%d/%m/%Y  %H:%M}'),
        ]

        formatters = {
            '@index': 'datetime',
        }

        for column_name in columns:
            tooltips.append((column_name, '@' + column_name + '{%f}'))
            formatters.update({'@' + column_name: 'printf'})

        # using only sources (not origins) to build initial graphs
        # if switching to bokeh CDSView needs to be changed
        full_source = self.sources['main'][0]
        bokeh_figure = self.get_figure_defaults()

        x_range = x_range if x_range else (full_source.data['index'][0],
                                           full_source.data['index'][-1])
        p = bokeh_figure(
            x_axis_type="datetime",
            # x_axis_location="above",
            toolbar_location='right',
            tools="pan,wheel_zoom,box_zoom,save",
            active_drag='pan',
            active_scroll='wheel_zoom',
            # need to set custom x_range here, because otherwise
            # the preview slider will crash with the following error:
            # ValueError: expected an instance of type Range1d, got DataRange1d(id='1006', ...) of type DataRange1d
            # also used to set up initial zoom if passed
            x_range=x_range,
            **figure_args,
        )

        p.toolbar.logo = None

        ticks_formatter = DatetimeTickFormatter(years=["%Y"],
                                                days=["%d/%m/%Y"],
                                                months=["%m/%Y"],
                                                hours=["%H:%M"],
                                                minutes=["%H:%M"])

        p.add_tools(
            HoverTool(
                tooltips=tooltips,
                formatters=formatters,
                mode='vline',
                names=[columns[0]],
            ))

        # zero horizontal line
        zero_hline = Span(location=0,
                          dimension='width',
                          line_color='gray',
                          line_dash='dashed',
                          line_width=1)
        p.add_layout(zero_hline)

        radius_ms = dict(day=86400, hour=3600, minute=60,
                         second=1)[df.index.resolution] * 1000 * .85
        for column, color in zip(columns, colors):
            # TODO: make resizable circles on zoom
            # specifying radius breaks onhover behavor
            updated_scatter_args = dict(
                x='index',
                y=column,
                legend_label=column,
                name=column,
                color=color,
                size=6,
                source=full_source,
            )
            updated_scatter_args.update(scatter_args)
            p.circle(**updated_scatter_args, )

        # legend
        p.legend.location = "top_left"
        p.legend.click_policy = "hide"

        # layout
        # TODO: add to defaults
        p.xaxis.formatter = ticks_formatter
        p.axis.minor_tick_line_color = None
        p.axis.major_tick_line_color = None
        p.outline_line_color = None
        p.axis.axis_line_width = 0
        p.axis.major_tick_out = 8
        p.axis.major_tick_in = 0

        self.p = p
        self.y_axis_autorange()
