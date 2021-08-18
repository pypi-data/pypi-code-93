from os import write
from typing import List, Optional, Dict, Any, Union, TextIO
import itertools
import pathlib
import tempfile
import webbrowser

import bokeh.models as bm
import bokeh.plotting as bp
import bokeh.layouts as bl
import bokeh.embed as be
import bokeh.resources as br
from bokeh.embed import file_html
from bokeh.resources import INLINE

import PIL.Image

import numpy as np

from jinja2 import Template

from fibomat.backend import BackendBase
from fibomat.backend.backendbase import shape_type, ShapeNotSupportedError
from fibomat.default_backends._bokeh_site import BokehSite, ShapeType
from fibomat import shapes
from fibomat.linalg import Vector, DimVector, DimVectorLike
from fibomat.site import Site
from fibomat.pattern import Pattern
from fibomat.utils import PathLike
from fibomat.shapes.rasterizedpoints import RasterizedPoints
from fibomat.raster_styles.rasterstyle import RasterStyle
from fibomat.units import LengthUnit, TimeUnit, LengthQuantity, U_, Q_, has_length_dim, scale_factor
from fibomat.shapes import Shape, DimShape
from fibomat.mill import Mill
from fibomat.default_backends.measuretool import MeasureTool


from bokeh.resources import JSResources
from bokeh.core.templates import JS_RESOURCES


_old_js_raw = getattr(JSResources, 'js_raw')

here = pathlib.Path(__file__).parent.resolve()
with open(here / 'bokeh-measuretool.min.js') as fp_js:
    _custom_ext_js = fp_js.read()

def _js_raw_patched(self):
    raw = _old_js_raw.fget(self)
    raw.append(_custom_ext_js)
    return raw

setattr(JSResources, 'js_raw', property(_js_raw_patched))

# would be nicer, but impractical because every bokeh template must be fixed..
# maybe set_cache_hook/getcache_hook could be used
# # stolen from https://docs.bokeh.org/en/latest/docs/user_guide/embed.html#standard-template and modified to include measure tool js
# FILE_TEMPLATE = Template("""
# {% from macros import embed %}

# <!DOCTYPE html>
# <html lang="en">
#   {% block head %}
#   <head>
#     {% block inner_head %}
#       <meta charset="utf-8">
#       <title>{% block title %}{{ title | e if title else "Bokeh Plot" }}{% endblock %}</title>
#       {% block preamble %}{% endblock %}
#       {% block resources %}
#         {% block css_resources %}
#           {{ bokeh_css | indent(8) if bokeh_css }}
#         {% endblock %}
#         {% block js_resources %}
#           {{ bokeh_js | indent(8) if bokeh_js }}
#         {% endblock %}
#         <script type="text/javascript">
#         {{ measure_tool | safe | indent(8) }}
#         </script>
#       {% endblock %}
#       {% block postamble %}{% endblock %}
#     {% endblock %}
#   </head>
#   {% endblock %}
#   {% block body %}
#   <body>
#     {% block inner_body %}
#       {% block contents %}
#         {% for doc in docs %}
#           {{ embed(doc) if doc.elementid }}
#           {% for root in doc.roots %}
#             {% block root scoped %}
#               {{ embed(root) | indent(10) }}
#             {% endblock %}
#           {% endfor %}
#         {% endfor %}
#       {% endblock %}
#       {{ plot_script | indent(8) }}
#     {% endblock %}
#   </body>
#   {% endblock %}
# </html>
# """
# )

# class _RenderWrapper:
#     def render(self, *args, **kwargs):
#         here = pathlib.Path(__file__).parent.resolve()
#         with open(here / 'bokeh-measuretool.min.js') as fp_js:
#             custom_js = fp_js.read()

#         return FILE_TEMPLATE.render(*args, measure_tool=custom_js, **kwargs)


class StubRasterStyle(RasterStyle):
    def __init__(self, dimension: int):
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def rasterize(
        self,
        dim_shape: DimShape,
        mill: Mill,
        out_length_unit: LengthUnit,
        out_time_unit: TimeUnit
    ) -> RasterizedPoints:
        pass


class BokehImage(DimShape):
    def __init__(self, file: PathLike, image_pixel_scale: LengthQuantity, center: Optional[DimVector] = None):
        self._file = file

        if not has_length_dim(image_pixel_scale):
            raise ValueError('image_pixel_scale must have length dimension')

        self._image_pixel_scale = image_pixel_scale

        image = PIL.Image.open(file).convert('RGBA')

        self._width, self._height = image.size

        self._width *= image_pixel_scale.m
        self._height *= image_pixel_scale.m

        if center is not None:
            self._center = DimVector(center)
        else:
            self._center = DimVector()

        self._image_data = np.asarray(image)

        super().__init__(self, image_pixel_scale.units)

    @property
    def shape(self):
        return self

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def center(self):
        return self._center

    @property
    def data(self):
        return self._image_data

    def _impl_translate(self, trans_vec: DimVectorLike) -> None:
        raise NotImplementedError

    def _impl_rotate(self, theta: float) -> None:
        raise NotImplementedError

    def _impl_scale(self, trans_vec: DimVectorLike) -> None:
        raise NotImplementedError

    def _impl_mirror(self, trans_vec: DimVectorLike) -> None:
        raise NotImplementedError


class BokehBackendBase(BackendBase):
    @shape_type(BokehImage)
    def bokeh_image(self, ptn: Pattern[BokehImage]):
        raise ShapeNotSupportedError


class BokehBackend(BokehBackendBase):
    """
    The default backend for plotting projects, based on the bokeh library.
    All shapes defined in fibomat library are supported.

    .. note:: :class:`~fibomat.shapes.arc.shapes.Arc` and :class:`~fibomat.shapes.curve.shapes.Curve` are rasterized during plotting
              due to lack of supported of the HoverTool for this shapes in the bokeh library. The pitch can be defined
              via the `rasterize_pitch` parameter.
    """
    name = 'bokeh'

    def __init__(
            self, *,
            unit: Optional[LengthUnit] = None,
            title: Optional[str] = None,
            hide_sites: bool = False,
            rasterize_pitch: Optional[LengthQuantity] = None,
            fullscreen: bool = True,
            legend: bool = True,
            cycle_colors: bool = True,
            image_alpha: float = .75,
            **kwargs
    ):
        """
        Args:
            unit (units.UnitType, optional): used unit for plotting, default to units.U_('µm')
            title (str, optional): title of plot, default to ''
            hide_sites (bool, optional): if true, sides' outlines are not shown, default to false
            rasterize_pitch (units.QuantityType. optional): curve_tools.rasterize pitch for shapes.Arc, ... and shapes.Curve, default to units.Q_('0.01 µm')
            fullscreen (bool, optional): if true, plot will be take the whole page, default to True
            cycle_colors (bool): if True, different sites get different colors.
            image_alpha (float): alpha value (transparency) of images, default to 0.75
        """
        super().__init__(**kwargs)

        if unit:
            if not has_length_dim(unit):
                raise ValueError('unit\'s dimension must by [length].')
            self._unit = unit
        else:
            self._unit = U_('µm')

        if title:
            self._title = str(title)
        else:
            self._title = ''

        self._hide_sites = bool(hide_sites)

        if rasterize_pitch:
            if not has_length_dim(rasterize_pitch):
                raise ValueError('rasterize_pitch\'s dimension must by [length].')
            self._rasterize_pitch = rasterize_pitch
        else:
            self._rasterize_pitch = Q_('0.001 µm')

        self._fullscreen = bool(fullscreen)
        self._legend = bool(legend)

        self._cycle_colors = cycle_colors

        self._bokeh_sites: List[BokehSite] = []
        self._annotation_site = BokehSite(
            site_index=-1,
            plot_unit=self._unit,
            dim_center=DimVector(),
            rasterize_pitch=self._rasterize_pitch,
            description='Annotations'
        )
        self._image_annotation: Optional[BokehImage] = None
        self._image_alpha = float(image_alpha)
        self.fig: Optional[bp.Figure] = None

    def process_site(self, site: Site):
        self._bokeh_sites.append(
            BokehSite(
                site_index=len(self._bokeh_sites),
                plot_unit=self._unit,
                dim_center=site.center,
                rasterize_pitch=self._rasterize_pitch,
                cycle_colors=self._cycle_colors,
                dim_fov=site.fov,
                description=site.description
            )
        )
        super().process_site(site)

    def process_pattern(self, ptn: Pattern) -> None:
        super().process_pattern(ptn)

    def process_unknown(self, ptn: Pattern) -> None:
        bbox = ptn.dim_shape.shape.bounding_box
        bbox_ptn = Pattern(
            dim_shape=shapes.Rect(bbox.width, bbox.height, 0, bbox.center) * ptn.dim_shape.unit,
            mill=ptn.mill,
            raster_style=ptn.raster_style,
            **ptn.kwargs  # True if 'annotation' in ptn.kwargs else False
        )
        self._filled_curve(bbox_ptn)

    def _collect_plot_data(self, shape_type: ShapeType) -> Dict[str, Any]:
        # https://stackoverflow.com/a/40826547
        keys = BokehSite.plot_data_keys
        data_dicts = [site.plot_data[shape_type] for site in self._bokeh_sites]
        data_dicts.append(self._annotation_site.plot_data[shape_type])
        return {key: list(itertools.chain(*[data_dict[key] for data_dict in data_dicts])) for key in keys}

    @staticmethod
    def _create_datasources(extra_keys: Optional[List[str]] = None):
        keys = BokehSite.plot_data_keys if not extra_keys else BokehSite.plot_data_keys + extra_keys

        def _create():
            return bm.ColumnDataSource({key: [] for key in keys})

        return {'spots': _create(), 'non_filled': _create(), 'filled': _create()}



    @staticmethod
    def _create_renderers(fig, data_sources):
        spot_glyphs = fig.circle_x(
            x='x', y='y',
            fill_color='color', line_color='color', fill_alpha=.25,
            legend_group='site_id',
            size=10,
            source=data_sources['spots']
        )

        non_filled_curve_glyphs = fig.multi_line(
            xs='x', ys='y',
            line_color='color', line_width=2,
            legend_group='site_id',
            source=data_sources['non_filled']
        )

        filled_curve_glyphs = fig.multi_polygons(
            xs='x', ys='y',
            line_width=2,
            fill_color='color', line_color='color', fill_alpha='fill_alpha',
            hatch_pattern='hatch_pattern',
            legend_group='site_id',
            source=data_sources['filled']

        )

        return {'spots': spot_glyphs, 'non_filled': non_filled_curve_glyphs, 'filled': filled_curve_glyphs}

    def _plot_impl(self, data_sources):
        spot_data = self._collect_plot_data(ShapeType.SPOT)
        non_filled = self._collect_plot_data(ShapeType.NON_FILLED_CURVE)
        filled = self._collect_plot_data(ShapeType.FILLED_CURVE)

        data_sources['spots'].stream(spot_data)
        data_sources['non_filled'].stream(non_filled)
        data_sources['filled'].stream(filled)

        return {
            'spots': len(spot_data['x']),
            'non_filled': len(non_filled['x']),
            'filled': len(filled['x'])
        }


    def plot(self):
        tooltips = [
            # ('type', 'shape'),
            ('shape', '@shape_prop'),
            # ('collection_index', '@collection_index'),
            ('mill', '@mill'),
            ('raster style', '@raster_style'),
            ('site', '@site_id'),
            ('description', '@description')
            # ('mill_settings', '@mill_settings'),
        ]

        site_tooltips = [
            # ('site', '@site'),
            ('description', '@description')
        ]

        fig = bp.figure(
            title=self._title,
            x_axis_label=f'x / {self._unit:~P}', y_axis_label=f'y / {self._unit:~P}',
            match_aspect=True,
            sizing_mode='stretch_both' if self._fullscreen else 'stretch_width',
            tools="pan,wheel_zoom,reset,save"
        )

        fig.add_tools(
            MeasureTool(
                measure_unit=f'{self._unit:~P}',  # line_color=bc.groups.red.Crimson, line_width=3  # bpal.all_palettes['Colorblind'][4][3]
            )
        )

        fig.add_tools(bm.BoxZoomTool(match_aspect=True))

        data_sources = self._create_datasources()
        renderers = self._create_renderers(fig, data_sources)

        self._plot_impl(data_sources)

        # spot_glyphs = fig.circle_x(
        #     x='x', y='y',
        #     fill_color='color', line_color='color', fill_alpha=.25,
        #     legend_group='site_id',
        #     size=10,
        #     source=bm.ColumnDataSource(self._collect_plot_data(ShapeType.SPOT))
        # )

        # non_filled_curve_glyphs = fig.multi_line(
        #     xs='x', ys='y',
        #     line_color='color', line_width=2,
        #     legend_group='site_id',
        #     source=bm.ColumnDataSource(self._collect_plot_data(ShapeType.NON_FILLED_CURVE))
        # )

        # filled_curve_glyphs = fig.multi_polygons(
        #     xs='x', ys='y',
        #     line_width=2,
        #     fill_color='color', line_color='color', fill_alpha='fill_alpha',
        #     hatch_pattern='hatch_pattern',
        #     legend_group='site_id',
        #     source=bm.ColumnDataSource(self._collect_plot_data(ShapeType.FILLED_CURVE))
        # )

        # images
        if self._image_annotation:
            image = self._image_annotation

            center = image.center.vector_as(self._unit)

            input_offset_x = bm.Spinner(title="Image x", low=-100000, high=100000, step=0.01, value=center.x, width=80)
            input_offset_y = bm.Spinner(title="Image y", low=-100000, high=100000, step=0.01, value=center.y, width=80)

            image_center = image.center.vector_as(self._unit)
            image_scale = scale_factor(self._unit, image.unit)
            width = image.width * image_scale
            height = image.height * image_scale
            
            image_data = image.data.view(dtype=np.uint32).reshape(image.data.shape[:2])[::-1,:]
 
            rendered_image = fig.image_rgba(
                image=[image_data],
                x=image_center.x - width/2,
                y=image_center.y - width/2,
                dw=width,
                dh=height,
                # anchor="center",
                global_alpha=self._image_alpha
            )

            input_offset_x.js_link('value', rendered_image.glyph, 'x')
            input_offset_y.js_link('value', rendered_image.glyph, 'y')

        # layers
        # https://github.com/bokeh/bokeh/issues/9087
        if not self._hide_sites:
            site_glyphs = fig.multi_polygons(
                xs='x', ys='y',
                line_width=2,
                fill_color='color', line_color='color', fill_alpha='fill_alpha', line_alpha='fill_alpha',
                legend_group='site_id',
                source=bm.ColumnDataSource(self._collect_plot_data(ShapeType.SITE))
            )

            site_glyphs_hover = bm.HoverTool(
              renderers=[site_glyphs],
              tooltips=site_tooltips,
              point_policy='follow_mouse'
            )
            fig.add_tools(site_glyphs_hover)

        # hover tool for shapes
        # add shape hover tool after site hovertool so it is rendered on top of the site tooltip
        shape_glyphs_hover = bm.HoverTool(
            # renderers=[
            #     spot_glyphs, non_filled_curve_glyphs,  filled_curve_glyphs
            # ],
            renderers=list(renderers.values()),
            tooltips=tooltips, point_policy='follow_mouse'
        )
        fig.add_tools(shape_glyphs_hover)

        def sorter(item):
            value = item.label['value']
            if value == 'Annotations':
                return -1
            else:
                return int(value.split(',')[0].split(' ')[1])

        legend_tmp = {x.label['value']: x for x in fig.legend.items}.values()
        fig.legend.items.clear()
        fig.legend.items.extend(sorted(
            legend_tmp,
            key=sorter
        ))

        fig.legend.visible = self._legend

        if self._image_annotation:
            self.fig = bl.column([bl.row([input_offset_x, input_offset_y]), fig], width_policy='max')
        else:
            self.fig = fig

    # def _gen_html(self, use_cdn: bool):
    #     resources = br.CDN if use_cdn else br.INLINE
    #     return be.file_html(models=self.fig, resources=resources, title=self._title, template=_RenderWrapper())

    def show(self):
        # with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as fp:
        #     fp.write(self._gen_html(True))
        #     fp.flush()
        #     webbrowser.open(fp.name)
        bp.show(self.fig)

    def save(self, filename: PathLike, use_cdn: bool = False):       
        # with open(filename, 'w') as fp:
        #     fp.write(self._gen_html(use_cdn))
        resources = br.CDN if use_cdn else br.INLINE
        bp.save(self.fig, filename, resources=resources)

    def spot(self, ptn: Pattern[shapes.Spot]) -> None:
        if '_annotation' in ptn.kwargs:
            self._annotation_site.spot(ptn)
        else:
            self._bokeh_sites[-1].spot(ptn)

    def _non_filled_curve(self, ptn):
        if '_annotation' in ptn.kwargs:
            self._annotation_site.non_filled_curve(ptn)
        else:
            self._bokeh_sites[-1].non_filled_curve(ptn)

    def _filled_curve(self, ptn):
        if '_annotation' in ptn.kwargs:
            self._annotation_site.filled_curve(ptn)
        else:
            self._bokeh_sites[-1].filled_curve(ptn)

    def _filled_curve_with_holes(self, ptn):
        if '_annotation' in ptn.kwargs:
            self._annotation_site.filled_curve_with_holes(ptn)
        else:
            self._bokeh_sites[-1].filled_curve_with_holes(ptn)

    def _dispatch_pattern(self, ptn):
        if not ptn.dim_shape.shape.is_closed:
            self._non_filled_curve(ptn)
        elif isinstance(ptn.dim_shape.shape, shapes.HollowArcSpline):
            self._filled_curve_with_holes(ptn)
        elif ptn.raster_style.dimension < 2:
            self._non_filled_curve(ptn)
        else:
            self._filled_curve(ptn)

    def line(self, ptn: Pattern[shapes.Line]) -> None:
        self._dispatch_pattern(ptn)

    def polyline(self, ptn: Pattern[shapes.Polyline]) -> None:
        self._dispatch_pattern(ptn)

    def arc(self, ptn: Pattern[shapes.Arc]) -> None:
        self._dispatch_pattern(ptn)

    def arc_spline(self, ptn: Pattern[shapes.ArcSpline]) -> None:
        self._dispatch_pattern(ptn)

    def polygon(self, ptn: Pattern[shapes.Polygon]) -> None:
        self._dispatch_pattern(ptn)

    def rect(self, ptn: Pattern[shapes.Rect]) -> None:
        self._dispatch_pattern(ptn)

    def ellipse(self, ptn: Pattern[shapes.Ellipse]) -> None:
        self._dispatch_pattern(ptn)

    def circle(self, ptn: Pattern[shapes.Circle]) -> None:
        self._dispatch_pattern(ptn)

    def rasterized_points(self, ptn: Pattern[shapes.RasterizedPoints]):
        rect = shapes.Rect.from_bounding_box(ptn.dim_shape.shape.bounding_box)

        new_pattern = Pattern(
            dim_shape=rect * ptn.dim_shape.unit,
            mill=ptn.mill,
            raster_style=ptn.raster_style,
            description=ptn.description,
            **ptn.kwargs
        )

        if '_annotation' in ptn.kwargs:
            self._annotation_site.filled_curve(new_pattern, hatch_pattern='/')
        else:
            self._bokeh_sites[-1].filled_curve(new_pattern, hatch_pattern='/')

    def hollow_arc_spline(self, ptn: Pattern[shapes.HollowArcSpline]) -> None:
        self._dispatch_pattern(ptn)

    def bokeh_image(self, ptn: Pattern[BokehImage]):
        if '_annotation' in ptn.kwargs:
            if not self._image_annotation:
                self._image_annotation = ptn.dim_shape
            else:
                raise RuntimeError('currently, only one image is supported.')
        else:
            raise RuntimeError('BokehImage can only added to annotation site')
