from typing import Optional, Tuple, Union

from grgr import _R
from grgr.dev import dict_to_rargs
from grgr.dev.typing import T, U
from grgr.ggplot2.basic import Aesthetic, GGPlot
from grgr.ggplot2.facet import Facet
from grgr.ggplot2.layer import Layer
from grgr.ggplot2.scale import Appearance
from grgr.ggplot2.theme import Theme, ThemeElement
from numpy import array, ndarray, str_
from numpy.typing import NDArray
from pandas import DataFrame


# Basics
def ggplot(data: Optional[DataFrame] = None,
           mapping: Optional[Aesthetic] = None,
           **kwargs):
    return GGPlot(data, mapping, **kwargs)


def aes(x: Optional[Union[str, ndarray]] = None,
        y: Optional[Union[str, ndarray]] = None,
        **kwargs) -> Aesthetic:
    return Aesthetic(x, y, **kwargs)


def ggsave(filename: str,
           plot: Optional[GGPlot] = None,
           width: Optional[int] = None,
           height: Optional[int] = None,
           dpi: Optional[int] = None,
           **kwargs):
    s = str()
    pyargs = locals()
    pyargs.update(**kwargs)
    rargs = dict_to_rargs(pyargs, ["s"])
    rcode = f"ggsave({rargs})"
    _R(rcode)


# Layer
def geom_abline(slope: float = 1., intercept: float = 0.) -> Layer:
    return Layer("geom_abline", slope=slope, intercept=intercept)


def geom_hline(yintercept: float) -> Layer:
    return Layer("geom_hline", yintercept=yintercept)


def geom_vline(xintercept: float) -> Layer:
    return Layer("geom_hline", xintercept=xintercept)


def geom_bar(data: Optional[DataFrame] = None,
             mapping: Optional[Aesthetic] = None,
             **kwargs):
    return Layer("geom_bar", data, mapping, **kwargs)


def geom_boxplot(data: Optional[DataFrame] = None,
                 mapping: Optional[Aesthetic] = None,
                 **kwargs):
    return Layer("geom_boxplot", data, mapping, **kwargs)


def geom_density(data: Optional[DataFrame] = None,
                 mapping: Optional[Aesthetic] = None,
                 **kwargs):
    return Layer("geom_density", data, mapping, **kwargs)


def geom_density_2d(data: Optional[DataFrame] = None,
                    mapping: Optional[Aesthetic] = None,
                    **kwargs):
    return Layer("geom_density_2d", data, mapping, **kwargs)


def geom_histogram(data: Optional[DataFrame] = None,
                   mapping: Optional[Aesthetic] = None,
                   **kwargs):
    return Layer("geom_histogram", data, mapping, **kwargs)


def geom_errorbar(data: Optional[DataFrame] = None,
                  mapping: Optional[Aesthetic] = None,
                  **kwargs):
    return Layer("geom_errorbar", data, mapping, **kwargs)


def geom_line(data: Optional[DataFrame] = None,
              mapping: Optional[Aesthetic] = None,
              **kwargs):
    return Layer("geom_line", data, mapping, **kwargs)


def geom_point(data: Optional[DataFrame] = None,
               mapping: Optional[Aesthetic] = None,
               **kwargs):
    return Layer("geom_point", data, mapping, **kwargs)


def geom_ribbon(data: Optional[DataFrame] = None,
                mapping: Optional[Aesthetic] = None,
                **kwargs):
    return Layer("geom_ribbon", data, mapping, **kwargs)


def geom_area(data: Optional[DataFrame] = None,
              mapping: Optional[Aesthetic] = None,
              **kwargs):
    return Layer("geom_area", data, mapping, **kwargs)


def geom_violin(data: Optional[DataFrame] = None,
                mapping: Optional[Aesthetic] = None,
                **kwargs):
    return Layer("geom_violin", data, mapping, **kwargs)


# Scales
def labs(title: Optional[str] = None,
         subtitle: Optional[str] = None,
         caption: Optional[str] = None,
         tag: Optional[str] = None,
         alt: Optional[str] = None,
         alt_insight: Optional[str] = None,
         **kwargs) -> Appearance:
    return Appearance("labs",
                      title=title,
                      subtitle=subtitle,
                      caption=caption,
                      tag=tag,
                      alt=alt,
                      alt_insight=alt_insight,
                      **kwargs)


def xlab(label: str) -> Appearance:
    return Appearance("xlab", label=label)


def ylab(label: str) -> Appearance:
    return Appearance("xlab", label=label)


def ggtitle(label, subtitle: Optional[str] = None) -> Appearance:
    return Appearance("ggtitle", label=label, subtitle=subtitle)


def lims(x: Optional[Tuple[T, T]], y: Optional[Tuple[U, U]]) -> Appearance:
    return Appearance("lims", x=array(x), y=array(y))


def xlim(x: Tuple[T, T]) -> Appearance:
    return Appearance("xlim", array(x))


def ylim(y: Tuple[T, T]) -> Appearance:
    return Appearance("ylim", array(y))


def scale_color_continuous(colorscale: str = '"gradient"') -> Appearance:
    return Appearance("scale_color_continuous", type=colorscale)


def scale_fill_continuous(colorscale: str = '"gradient"') -> Appearance:
    return Appearance("scale_fill_continuous", type=colorscale)


def scale_color_discrete(colorscale: str = '"gradient"') -> Appearance:
    return Appearance("scale_color_discrete", type=colorscale)


def scale_fill_discrete(colorscale: str = '"gradient"') -> Appearance:
    return Appearance("scale_fill_discrete", type=colorscale)


def scale_color_gradient(low: str, high: str, **kwargs) -> Appearance:
    return Appearance("scale_color_gradient", low=low, high=high, **kwargs)


def scale_fill_gradient(low: str, high: str, **kwargs) -> Appearance:
    return Appearance("scale_fill_gradient", low=low, high=high, **kwargs)


def scale_color_gradient2(low: str, mid: str, high: str,
                          **kwargs) -> Appearance:
    return Appearance("scale_color_gradient2",
                      low=low,
                      mid=mid,
                      high=high,
                      **kwargs)


def scale_fill_gradient2(low: str, mid: str, high: str,
                         **kwargs) -> Appearance:
    return Appearance("scale_fill_gradient2",
                      low=low,
                      mid=mid,
                      high=high,
                      **kwargs)


def scale_color_gradientn(colors: NDArray[str_], **kwargs) -> Appearance:
    return Appearance("scale_color_gradientn", colors=colors, **kwargs)


def scale_fill_gradientn(colors: NDArray[str_], **kwargs) -> Appearance:
    return Appearance("scale_fill_gradientn", colors=colors, **kwargs)


# Facets
def facet_grid(*args, **kwargs) -> Facet:
    return Facet("facet_grid", *args, **kwargs)


def facet_wrap(*args, **kwargs) -> Facet:
    return Facet("facet_wrap", *args, **kwargs)


# Themes
def theme(**kwargs):
    return Theme("theme", **kwargs)


def theme_bw(**kwargs):
    return Theme("theme_bw", **kwargs)


def theme_classic(**kwargs):
    return Theme("theme_classic", **kwargs)


def margin(top: float = 0.,
           right: float = 0.,
           bottom: float = 0.,
           left: float = 0.,
           unit: str = "pt") -> ThemeElement:
    return ThemeElement("margin", t=top, r=right, b=bottom, l=left, unit=unit)


def element_blank():
    return ThemeElement("element_blank")


def element_rect(fill: Optional[str] = None,
                 color: Optional[str] = None,
                 size: Optional[float] = None,
                 linetype: Optional[str] = None,
                 **kwargs):
    return ThemeElement("element_rect",
                        fill=fill,
                        color=color,
                        size=size,
                        linetype=linetype,
                        **kwargs)


def element_line(color: Optional[str] = None,
                 size: Optional[float] = None,
                 linetype: Optional[str] = None,
                 **kwargs):
    return ThemeElement("element_line",
                        color=color,
                        size=size,
                        linetype=linetype,
                        **kwargs)


def element_text(family: Optional[str] = None,
                 color: Optional[str] = None,
                 size: Optional[float] = None,
                 angle: Optional[float] = None,
                 **kwargs):
    return ThemeElement("element_text",
                        family=family,
                        color=color,
                        size=size,
                        angle=angle,
                        **kwargs)
