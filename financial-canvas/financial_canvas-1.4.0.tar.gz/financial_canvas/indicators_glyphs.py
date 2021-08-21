'''
Glyphs for indicators drawn on top of Candlestick chart
'''

from financial_canvas.figures.constants import COLOR_PALLETE, DAY_IN_MILLIS
from bokeh.models import LabelSet, CustomJS


def up_traingle(candlestick, y_column_name='open', color='green'):
    candlestick.y_range_resize_columns.extend([y_column_name])
    source = candlestick.sources['main'][0]
    # TODO: fix width
    candlestick.p.triangle(
        x='index',
        y=y_column_name,
        # width=width,
        # size=width,
        size=10,
        color=color,
        source=source,
        legend_label=y_column_name,
    )


def down_triangle(candlestick, y_column_name='open', color='red'):
    candlestick.y_range_resize_columns.extend([y_column_name])
    source = candlestick.sources['main'][0]
    # TODO: fix width
    # width = candlestick.candle_width * 0.25
    # candlestick.p.diamond(
    #     x='index',
    #     y=y_column_name,
    #     width=width,
    #     source=source,
    #     legend_label=y_column_name,
    # )

    candlestick.p.inverted_triangle(
        x='index',
        y=y_column_name,
        # width=width,
        # size=width,
        size=10,
        color=color,
        source=source,
        legend_label=y_column_name,
    )


def annotations(candlestick, column_name, y_column_name="open"):
    source = candlestick.sources['main'][0]
    renderer = candlestick.p.rect(
        color='black',
        legend_label='BUY/SELL',
    )

    labels = LabelSet(
        x='index',
        y=y_column_name,
        text=column_name,
        x_offset=0,
        y_offset=10,
        source=source,
        render_mode='canvas',
        background_fill_color='white',
        text_baseline='middle',
        text_align="center",
    )
    candlestick.p.add_layout(labels)
    renderer.js_on_change(
        'visible',
        CustomJS(args=dict(ls=labels), code="ls.visible = cb_obj.visible;"))


def line(custom_figure, column_name, color=None):
    color = color if color else COLOR_PALLETE[2]
    custom_figure.y_range_resize_columns.extend([column_name])

    custom_figure.p.line(
        'index',
        column_name,
        legend_label=column_name,
        color=color,
        line_width=1.5,
        source=custom_figure.sources['main'][0],
    )

    hover_tool = custom_figure.p.hover
    hover_tool.tooltips.extend([
        (column_name, '@' + column_name + '{%f}'),
    ])
    hover_tool.formatters.update({
        '@' + column_name: 'printf',
    })


def line_circles(candlestick, column_name, color=None):
    color = color if color else COLOR_PALLETE[2]
    candlestick.y_range_resize_columns.extend([column_name])

    width_ms = dict(day=86400, hour=3600, minute=60, second=1)[
        candlestick.sources['main'][0].data['index'].resolution] * 500 * .85

    candlestick.p.scatter('index',
                          column_name,
                          legend_label=column_name,
                          radius=width_ms,
                          color=color,
                          source=candlestick.sources['main'][0])

    candlestick.p.line(
        'index',
        column_name,
        legend_label=column_name,
        color=color,
        line_width=1.5,
        source=candlestick.sources['main'][0],
    )

    hover_tool = candlestick.p.hover
    hover_tool.tooltips.extend([
        (column_name, '@' + column_name + '{%f}'),
    ])
    hover_tool.formatters.update({
        '@' + column_name: 'printf',
    })


def line_ma_st(candlestick):
    ma_color = COLOR_PALLETE[4]
    st_color = COLOR_PALLETE[1]
    candlestick.y_range_resize_columns.extend(['MA', 'ST'])

    candlestick.p.scatter('index',
                          'MA',
                          legend_label='MA',
                          radius=750000,
                          color=ma_color,
                          source=candlestick.sources['main'][0])

    candlestick.p.scatter('index',
                          'ST',
                          legend_label='ST',
                          radius=750000,
                          color=st_color,
                          source=candlestick.sources['main'][0])

    candlestick.p.line(
        'index',
        'MA',
        legend_label='MA',
        color=ma_color,
        source=candlestick.sources['main'][0],
    )
    candlestick.p.line(
        'index',
        'ST',
        legend_label='ST',
        color=st_color,
        source=candlestick.sources['main'][0],
    )

    hover_tool = candlestick.p.hover
    hover_tool.tooltips.extend([
        ('MA', '@MA{%f}'),
        ('ST', '@ST{%f}'),
    ])
    hover_tool.formatters.update({
        '@MA': 'printf',
        '@ST': 'printf',
    })


def strategy_indicators(candlestick, line_column, circles_column):
    # Indicator 1 (the orange line) is just a continuous line
    indicator_1_color = COLOR_PALLETE[2]

    candlestick.y_range_resize_columns.extend([line_column])

    candlestick.p.line(
        'index',
        line_column,
        legend_label=line_column,
        color=indicator_1_color,
        line_width=1.5,
        source=candlestick.sources['main'][0],
    )

    candlestick.p.circle(
        'index',
        f'{circles_column}_position',
        legend_label=circles_column,
        # radius=1000 * 60 * 15,
        size=5,
        color=f'{circles_column}_color',
        source=candlestick.sources['main'][0],
    )

    hover_tool = candlestick.p.hover
    hover_tool.tooltips.extend([
        (line_column, '@' + line_column + '{%f}'),
        (circles_column, '@' + circles_column + '{%f}'),
    ])
    hover_tool.formatters.update({
        f'@{line_column}': 'printf',
        f'@{circles_column}': 'printf',
    })


def strategy_indicators_linear(candlestick, line_column, colored_column, df):
    # Indicator 1 (the orange line) is just a continuous line
    indicator_1_color = COLOR_PALLETE[2]

    candlestick.y_range_resize_columns.extend([line_column, colored_column])

    candlestick.p.line(
        'index',
        line_column,
        legend_label=line_column,
        color=indicator_1_color,
        line_width=1.5,
        source=candlestick.sources['main'][0],
    )

    # if making differently colored lines:
    # we cannot use a single or 2 line glyphs because
    # the line is not connected
    # it's either multi_line https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/multi_line.html
    # but then we will need to rethink date range slicing
    # ~~or it's multiple different sources for each consecutive continuous line~~ (nope, this is not working out at all,
    # very slow build and there is a json parsing error in the browser)
    # or a segment https://docs.bokeh.org/en/latest/docs/reference/models/glyphs/segment.html
    # but with segment it's not clear how to draw a point of one
    candlestick.p.line(
        'index',
        colored_column,
        legend_label=colored_column,
        color='#c0c0c0',
        line_width=1.5,
        source=candlestick.sources['main'][0],
    )

    # also adding circles for lines of length == 1
    candlestick.p.circle(
        'index',
        colored_column,
        legend_label=colored_column,
        # line_width=1.5,
        size=5,
        color=f'{colored_column}_color',
        source=candlestick.sources['main'][0],
    )

    hover_tool = candlestick.p.hover
    hover_tool.tooltips.extend([
        (line_column, '@' + line_column + '{%f}'),
        (colored_column, '@' + colored_column + '{%f}'),
    ])
    hover_tool.formatters.update({
        f'@{line_column}': 'printf',
        f'@{colored_column}': 'printf',
    })
