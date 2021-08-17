from bokeh.plotting import figure, Figure
from bokeh.embed import components
from bokeh.models.tools import HoverTool
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter

import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(levelname)s: [%(name)s] %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def line_chart(x: list, line: list, height=300, width=400, sizing_mode=None) -> Figure:
    hover_tool = HoverTool(
        tooltips=[
            ("date", "$x{%F}"),
            ("value", "$y{%0.2f}"),
        ],
        formatters={
            '$x': 'datetime',
            '$y': 'printf',
        },
        mode='vline',
    )
    p = figure(
        plot_height=height,
        plot_width=width,
        sizing_mode=sizing_mode,
        tools=[hover_tool],
        toolbar_location=None,
    )
    p.line(x, line, legend_label="Temp.", line_width=2)
    p.legend.visible = False
    p.xaxis[0].formatter = DatetimeTickFormatter(months='%y/%m')
    p.yaxis[0].formatter = NumeralTickFormatter()
    return p


def line_circle_chart(x: list, line: list, circle: list, height=300, width=400, sizing_mode=None) -> Figure:
    """
    장고에서 종목 report의 price에서 사용하는 그래프
    x - 날짜
    y - 가격
    """
    hover_tool = HoverTool(
        tooltips=[
            ("date", "$x{%F}"),
            ("value", "$y{%0.2f}"),
        ],
        formatters={
            '$x': 'datetime',
            '$y': 'printf',
        },
        mode='vline',
    )

    p = figure(
        plot_height=height,
        plot_width=width,
        sizing_mode=sizing_mode,
        tools=[hover_tool],
        toolbar_location=None,
    )
    p.line(x, line, legend_label="Temp.", line_width=2)
    p.circle(x, circle, size=8)
    p.legend.visible = False
    p.xaxis[0].formatter = DatetimeTickFormatter(months='%y/%m')
    p.yaxis[0].formatter = NumeralTickFormatter()
    return p


def make_code(p: Figure) -> tuple:
    # Embedding Bokeh contents
    # https://docs.bokeh.org/en/latest/docs/user_guide/embed.html#userguide-embed
    script, div = components(p)
    return script, div
