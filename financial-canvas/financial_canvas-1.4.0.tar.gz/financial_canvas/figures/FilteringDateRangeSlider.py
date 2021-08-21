from financial_canvas.figures.constants import DAY_IN_MILLIS
from financial_canvas.figures.utils import read_file

from bokeh.models import (DateRangeSlider, CustomJS)


class FilteringDateRangeSlider(object):
    '''
    Does not have any sources, not a figure even (TODO: make separate module?), 
        updates sources and x range of the target figure.

    Args:
        target_figure (figures.CustomFigure): (optional) if passed will be resized with slider.

    Attributes:
        s (bokeh.models.DateRangeSlider): 
    '''
    def __init__(self, target_figure=None):

        preselected_index = target_figure.sources['main'][0].data['index']
        all_data_index = target_figure.sources['main'][1].data['index']
        date_range_slider = DateRangeSlider(
            title="Select period to render",
            value=(preselected_index[0], preselected_index[-1]),
            start=all_data_index[0],
            end=all_data_index[-1],
            step=DAY_IN_MILLIS,
        )

        resizable_sources = list(target_figure.sources.values())
        date_range_slider.js_on_change(
            "value",
            CustomJS(args=dict(
                sources_and_origins=resizable_sources,
                x_range=target_figure.p.x_range,
            ),
                     code=read_file('update_render_range.js')))

        self.s = date_range_slider
