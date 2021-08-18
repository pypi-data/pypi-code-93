from bokeh.models import ColumnDataSource, Tool, Inspection

from bokeh.core.properties import String, DashPattern, Color, Float
from bokeh.util import compiler as bokeh_comp


class MeasureTool(Inspection):
    """
    A measure tool for bokeh plots!
    """

    # https://github.com/bokeh/bokeh/issues/9412
    __view_module__ = "bokeh"

    measure_unit = String(default='', help='')
    line_dash = DashPattern(default='solid', help='')
    line_color = Color(default="black", help='')
    line_width = Float(default=1, help='')
    line_alpha = Float(default=1.0, help='')
