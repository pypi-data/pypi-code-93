from financial_canvas.figures.CustomFigure import CustomFigure

from bokeh.models import RangeTool


class PreviewSlider(CustomFigure):
    '''
    Creates preview slider at the bottom of the main figure. The first df should always contain
    close column.

    Args:
        target_figure (figures.CustomFigure): (optional) if passed will be resized with slider.
    '''
    def __init__(self, df, *, selected_from=None, target_figure=None):
        super().__init__(df, selected_from=selected_from)

        bokeh_figure = self.get_figure_defaults()

        p = bokeh_figure(
            title=
            "Drag the middle and edges of the selection box to change the range above",
            plot_height=125,
            x_axis_type="datetime",
            y_axis_type=None,
            tools="",
            toolbar_location=None,
            background_fill_color="#efefef")

        if target_figure:
            range_tool = RangeTool(x_range=target_figure.p.x_range)
            range_tool.overlay.fill_color = "navy"
            range_tool.overlay.fill_alpha = 0.2
            p.add_tools(range_tool)
            p.toolbar.active_multi = range_tool
            self.sources = target_figure.sources

        p.scatter(
            'index',
            'close',
            size=1,
            source=self.sources['main'][0],
        )

        # layout
        p.ygrid.grid_line_color = None

        self.p = p
