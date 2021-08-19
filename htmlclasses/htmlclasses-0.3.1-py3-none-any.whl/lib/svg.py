from dataclasses import dataclass
from typing import Optional, NamedTuple

from htmlclasses import E


class Point(NamedTuple):
    x: float
    y: float

    def __abs__(self):
        x = self.x
        y = self.y
        return (x * x + y * y) ** 0.5


def build_line(
        *,
        point_from: tuple[float, float],
        point_to: tuple[float, float],
        color: str,
        width: str,
        marker_start_id: Optional[str] = None,
        marker_end_id: Optional[str] = None,
        dotted=False,
        ):

    class line(E):
        x1, y1 = point_from
        x2, y2 = point_to
        stroke = color
        stroke_width = width
        if marker_start_id:
            marker_start = f'url(#{marker_start_id})'
        if marker_end_id:
            marker_end = f'url(#{marker_end_id})'
        if dotted:
            stroke_dasharray = width

    return line


def build_axes(
        x_range: tuple[float, float],
        y_range: tuple[float, float],
        x_axis_length: float,
        y_axis_length: float,
        y_axis_name: str,
        x_axis_name: str,
        ):
    # TODO support for units of length

    scale = Point(
        x_axis_length / (x_range[1] - x_range[0]),
        y_axis_length / (y_range[1] - y_range[0]),
    )

    x_start, x_end = x_range
    y_start, y_end = y_range

    for a, b in [(x_start, x_end), (y_start, y_end)]:
        if b <= a:
            raise ValueError(
                'Axes must start at low value and end end at higher.'
                + f' Got: start:{a}, end:{b}'
            )

    x_range_greater_than_0 = x_start > 0
    x_range_less_than_0 = x_end < 0
    y_range_greater_than_0 = y_start > 0
    y_range_less_than_0 = y_end < 0

    dotted_len = 40  # why?
    arrow_size = 5  # why?
    left_margin = 5  # why?
    text_height = 20  # why?
    top_margin = arrow_size * 2 + 5 + text_height  # why * 2? why 5?

    if x_range_greater_than_0:
        x_intersection = dotted_len / 2
    elif x_range_less_than_0:
        x_intersection = x_axis_length + dotted_len / 2
    else:
        x_fraction_on_left_side = -x_start / (x_end - x_start)
        x_intersection = x_axis_length * x_fraction_on_left_side

    if y_range_greater_than_0:
        y_intersection = y_axis_length + dotted_len / 2 + arrow_size
    elif y_range_less_than_0:
        y_intersection = dotted_len / 2 + arrow_size
    else:
        y_fraction_on_left_side = -y_start / (y_end - y_start)
        y_intersection = y_axis_length * y_fraction_on_left_side + arrow_size

    if x_range_greater_than_0:
        x_lines_kwargs = dict(
            dotted_x_line=dict(
                point_from=Point(0, y_intersection),
                point_to=Point(dotted_len, y_intersection),
                dotted=True,
            ),
            x_line=dict(
                point_from=Point(dotted_len, y_intersection),
                point_to=Point(dotted_len + x_axis_length, y_intersection),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
        )
    elif x_range_less_than_0:
        x_lines_kwargs = dict(
            x_line=dict(
                point_from=Point(0, y_intersection),
                point_to=Point(x_axis_length, y_intersection),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
            dotted_x_line=dict(
                point_from=Point(x_axis_length, y_intersection),
                point_to=Point(dotted_len + x_axis_length, y_intersection),
                marker_end_id='arrow',
                dotted=True,
            ),
        )
    else:
        x_lines_kwargs = dict(
            x_line=dict(
                point_from=Point(0, y_intersection),
                point_to=Point(x_axis_length, y_intersection),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
        )

    if y_range_greater_than_0:
        y_lines_kwargs = dict(
            y_line=dict(
                point_from=Point(x_intersection, arrow_size + y_axis_length),
                point_to=Point(x_intersection, arrow_size),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
            dotted_y_line=dict(
                point_from=Point(
                    x_intersection,
                    arrow_size + y_axis_length + dotted_len,
                ),
                point_to=Point(x_intersection, arrow_size + y_axis_length),
                dotted=True,
            ),
        )
    elif y_range_less_than_0:
        y_lines_kwargs = dict(
            dotted_y_line=dict(
                point_from=Point(x_intersection, arrow_size + dotted_len),
                point_to=Point(x_intersection, arrow_size),
                marker_end_id='arrow',
                dotted=True,
            ),
            y_line=dict(
                point_from=Point(
                    x_intersection,
                    arrow_size + y_axis_length + dotted_len,
                ),
                point_to=Point(x_intersection, arrow_size + dotted_len),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
        )
    else:
        y_lines_kwargs = dict(
            y_line=dict(
                point_from=Point(x_intersection, arrow_size + y_axis_length),
                point_to=Point(x_intersection, arrow_size),
                marker_end_id='value-marker',
                marker_start_id='value-marker',
            ),
        )

    def draw_line(kwargs):
        return build_line(color='black', width=2, **kwargs)

    x_line = x_lines_kwargs['x_line']
    # mypy getting confused...
    x0_marker: Point = x_line['point_from']  # type: ignore[assignment]
    x1_marker: Point = x_line['point_to']  # type: ignore[assignment]

    y_line = y_lines_kwargs['y_line']
    y0_marker: Point = y_line['point_from']  # type: ignore[assignment]
    y1_marker: Point = y_line['point_to']  # type: ignore[assignment]

    text_offset = Point(20, 20)

    class g(E):

        transform = f'translate({left_margin} {top_margin})'

        class text:

            TEXT = f'{y_axis_name} ({x_axis_name})'
            y = -text_height

        class defs(E):

            class marker:
                id = 'arrow'
                viewBox = f'0 0 {arrow_size * 2} {arrow_size * 2}'
                refX = 0
                refY = arrow_size / 2
                markerWidth = arrow_size * 2
                markerHeight = arrow_size * 2
                orient = 'auto-start-reverse'

                class path:
                    d = (
                            f'M 0 {arrow_size * 0.2}'
                            + f' L {arrow_size} {arrow_size / 2}'
                            + f' L 0 {arrow_size * 0.8} z'
                    )

            class marker:
                id = 'value-marker'
                viewBox = '0 0 10 10'
                refX = 0.25
                refY = 2.5
                orient = 'auto'
                markerWidth = 10
                markerHeight = 10

                class line:
                    x1, y1 = (0, 5)
                    x2, y2 = (0, 0)
                    stroke = 'black'
                    stroke_width = 1

        line = draw_line(x_lines_kwargs['x_line'])
        if x_range_less_than_0 or x_range_greater_than_0:
            line = draw_line(x_lines_kwargs['dotted_x_line'])

        line = draw_line(y_lines_kwargs['y_line'])
        if y_range_less_than_0 or y_range_greater_than_0:
            line = draw_line(y_lines_kwargs['dotted_y_line'])

        class text:

            TEXT = f'{x_range[0]:.2f}'
            x = x0_marker.x
            y = x0_marker.y + text_offset.y

        class text:

            TEXT = f'{x_range[-1]:.2f}'
            x = x1_marker.x
            y = x1_marker.y + text_offset.y

        class text:

            TEXT = f'{y_range[0]:.2f}'
            x = y0_marker.x + text_offset.x
            y = y0_marker.y

        class text:

            TEXT = f'{y_range[-1]:.2f}'
            x = y1_marker.x + text_offset.x
            y = y1_marker.y

        META = AxesMeta(
                svg_translation=Point(left_margin, top_margin),
                translation=Point(x_intersection, y_intersection),
                scale=scale,
                )

    return g


@dataclass(frozen=True)
class AxesMeta:

    svg_translation: Point
    translation: Point
    scale: Point


class _Points(list):

    def __init__(self, xys):
        super().__init__(xys)
        self.xs, self.ys = zip(*self)
        self.max_x = max(self.xs)
        self.min_x = min(self.xs)
        self.max_y = max(self.ys)
        self.min_y = min(self.ys)


# class _MultiPlotData(list):

    # def __init__(self, multi_plot_data):
        # super().__init__(map(_Points, multi_plot_data))
        # self.max_x = max(pd.max_x for pd in self)
        # self.min_x = min(pd.min_x for pd in self)
        # self.max_y = max(pd.max_y for pd in self)
        # self.min_y = min(pd.min_y for pd in self)


def build_plot(
        *,
        points,
        x_axis_length,
        y_axis_length,
        y_axis_name,
        x_axis_name,
        ):

    points = _Points(points)

    axes = build_axes(
        x_range=(points.min_x, points.max_x),
        y_range=(points.min_y, points.max_y),
        x_axis_length=y_axis_length,
        y_axis_length=x_axis_length,
        y_axis_name=y_axis_name,
        x_axis_name=x_axis_name,
    )
    svg_translation = axes.META.svg_translation
    scale = axes.META.scale
    translation = axes.META.translation

    class g(E):
        g = axes

        class g(E):

            transform = (
                    f'translate({svg_translation.x} {svg_translation.y})'
                    )

            polyline = build_polyline(
                (
                    x * scale.x + translation.x,
                    -y * scale.y + translation.y
                )
                for x, y in points
            )

    return g


def build_polyline(points_):

    class polyline:
        points = ' '.join(f'{x},{y}' for x, y in points_)
        fill = 'none'
        stroke = 'black'

    return polyline
