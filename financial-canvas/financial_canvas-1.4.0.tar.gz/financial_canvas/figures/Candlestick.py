from datetime import timedelta

from bokeh.models import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from financial_canvas.figures.constants import COLOR_PALLETE
from financial_canvas.figures.CustomFigure import CustomFigure


class Candlestick(CustomFigure):
    '''
    Interactive candlestick chart on canvas with y-range autoscale.

    Args:
        df: pandas DataFrame with datetime index and OHLC columns, 
        y_range_resize_columns (list of str): columns in df to resize y_range by
    '''
    def __init__(self,
                 df,
                 *,
                 selected_from=None,
                 inc_color=None,
                 dec_color=None,
                 x_range=None,
                 figure_args=None):

        # TODO: update dynamically
        self.y_range_resize_columns = ['open', 'high', 'low', 'close']

        super().__init__(df, selected_from=selected_from)

        inc = df.close > df.open
        dec = ~inc
        inc_df = df[inc]
        dec_df = df[dec]

        self.add_sources(inc_df, 'inc')
        self.add_sources(dec_df, 'dec')

        tooltips = [
            ('Date', '@index{%d/%m/%Y %H:%M}'),
            ('Open', '@open{%f}'),
            ('High', '@high{%f}'),
            ('Low', '@low{%f}'),
            ('Close', '@close{%f}'),
        ]

        formatters = {
            '@index': 'datetime',
            '@open': 'printf',
            '@high': 'printf',
            '@low': 'printf',
            '@close': 'printf',
        }

        # using only sources (not origins) to build initial graphs
        # if switching to bokeh CDSView needs to be changed
        inc_source = self.sources['inc'][0]
        dec_source = self.sources['dec'][0]
        full_source = self.sources['main'][0]
        bokeh_figure = self.get_figure_defaults()

        x_range = x_range if x_range else (full_source.data['index'][0],
                                           full_source.data['index'][-1])
        if figure_args is None:
            figure_args = {}
        p = bokeh_figure(
            x_axis_type="datetime",
            x_axis_location="above",
            toolbar_location='right',
            tools="pan,wheel_zoom,box_zoom,save",
            active_drag='pan',
            active_scroll='wheel_zoom',
            # need to set custom x_range here, because otherwise
            # the preview slider will crash with the following error:
            # ValueError: expected an instance of type Range1d, got DataRange1d(id='1006', ...) of type DataRange1d
            # also used to set up initial zoom if passed
            x_range=x_range,
            **figure_args)

        p.toolbar.logo = None
        p.x_range.min_interval = timedelta(days=1)

        inc_color = inc_color if inc_color else COLOR_PALLETE[5]
        dec_color = dec_color if dec_color else COLOR_PALLETE[0]

        ticks_formatter = DatetimeTickFormatter(years=["%Y"],
                                                days=["%d/%m/%Y"],
                                                months=["%m/%Y"],
                                                hours=["%H:%M"],
                                                minutes=["%H:%M"])

        # prep data source
        # Open - High - Low - Close
        width_ms = dict(
            day=86400, hour=3600, minute=60,
            second=1)[inc_source.data['index'].resolution] * 1000 * .85

        self.candle_width = width_ms

        p.add_tools(
            HoverTool(
                tooltips=tooltips,
                formatters=formatters,
                mode='vline',
                names=['inc_bar', 'dec_bar'],
            ))

        # candlestick chart
        p.segment('index',
                  'high',
                  'index',
                  'low',
                  legend_label='OHLC',
                  color=dec_color,
                  source=dec_source)
        p.segment('index',
                  'high',
                  'index',
                  'low',
                  legend_label='OHLC',
                  color=inc_color,
                  source=inc_source)

        p.vbar('index',
               width_ms,
               'open',
               'close',
               legend_label='OHLC',
               name='dec_bar',
               fill_color=dec_color,
               line_color=dec_color,
               source=dec_source)
        p.vbar('index',
               width_ms,
               'open',
               'close',
               legend_label='OHLC',
               name='inc_bar',
               fill_color=inc_color,
               line_color=inc_color,
               source=inc_source)

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
