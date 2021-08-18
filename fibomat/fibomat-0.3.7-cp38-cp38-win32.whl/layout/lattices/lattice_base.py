from typing import Iterable, Union, Callable, Optional, Tuple, List, Type
import abc

import numpy as np

from fibomat.shapes import HollowArcSpline, ArcSplineCompatible, ArcSpline, Line
from fibomat.linalg import TransformableBase, Vector, DimVector
from fibomat.curve_tools import fill_with_lines
from fibomat.layout.layoutbase import LayoutBase
from fibomat.layout.utils import _round_towards_mean, _check_lattice_vectors
from fibomat.layout.groups.group_base import GroupBase


class LatticeBaseMixin(abc.ABC):
    _VectorType: Type[Union[Vector, DimVector]]

    @staticmethod
    def _gen_lattice_points(
        boundary: Union[HollowArcSpline, ArcSpline], u: Vector, v: Vector, center: Vector, seed: Vector
    ) -> Tuple[np.ndarray, np.ndarray]:
        boundary = boundary.translated_to(center)

        alpha = u.angle_about_x_axis

        # map alpha to [-pi/2, pi/2]
        if alpha < np.pi/2:
            pass
        elif np.pi/2 <= alpha < 1.5*np.pi:
            alpha -= np.pi
        else:
            alpha -= 2*np.pi

        pitch = (v - u.projected(v)).length

        lattice_planes = fill_with_lines(boundary, pitch=pitch, alpha=alpha, invert=False, seed=seed)

        # print(boundary, lattice_planes, seed)

        # translate seed point in first quadrant
        normalized_seed = Vector()

        # s = Sample()
        # s.add_annotation(boundary * U_('µm'))
        # for plane in lattice_planes:
        #     for line in plane:
        #         s.add_annotation(line * U_('µm'))
        #
        # s.plot()

        def lattice_points_on_line(line: Line):
            m = np.array([u, v]).T

            start_lattice_point = np.linalg.solve(m, line.start - center + seed)
            end_lattice_point = np.linalg.solve(m, line.end - center + seed)

            i_u_start, i_u_end = _round_towards_mean(start_lattice_point[0], end_lattice_point[0])

            # TODO: more tests on this!
            if abs(start_lattice_point[0] - end_lattice_point[0]) < 1:
                if not np.isclose(i_u_start, i_u_end):
                    raise ValueError

            # TODO: needed?
            assert np.isclose(start_lattice_point[1], end_lattice_point[1])
            assert np.isclose(start_lattice_point[1], np.rint(start_lattice_point[1]))

            if i_u_start <= i_u_end:
                i_u = np.arange(i_u_start, i_u_end + 1, dtype=int)
            else:
                i_u = np.arange(i_u_end, i_u_start + 1, dtype=int)[::-1]
            i_v = int(np.rint(start_lattice_point[1]))

            return i_u, i_v

        i_u_min = np.iinfo(int).max
        i_u_max = np.iinfo(int).min

        i_v_min = np.iinfo(int).max
        i_v_max = np.iinfo(int).min

        lattice_points = []

        for plane in lattice_planes:
            for line in plane:
                try:
                    points = lattice_points_on_line(line)
                except ValueError:
                    continue
                i_points_u, i_point_v = points

                i_u_min = min(i_u_min, np.min(i_points_u))
                i_u_max = max(i_u_max, np.max(i_points_u))

                i_v_min = min(i_v_min, i_point_v)
                i_v_max = max(i_v_max, i_point_v)

                lattice_points.append(np.c_[i_points_u, [i_point_v]*len(i_points_u)])

        lattice_points_uv = np.concatenate(lattice_points)
        lattice_points_xy = np.outer(lattice_points_uv[:, 0], u) + np.outer(lattice_points_uv[:, 1], v) - seed

        return lattice_points_uv, lattice_points_xy

    @classmethod
    def _generate_impl(
        cls,
        boundary: Union[HollowArcSpline, ArcSplineCompatible],
        u: Vector, v: Vector,
        center: Vector,
        element_gen: Callable,
        predicate: Optional[Union[Callable, List[Callable]]],
        explode: bool, remove_outliers: bool,
        scale_vec: Callable,
        unscale_vec: Callable,
        seed: Vector
    ):
        # check arguments
        if not isinstance(boundary, HollowArcSpline) and not isinstance(boundary, ArcSplineCompatible):
            raise TypeError('boundary must be HollowArcSpline or ArcSplineCompatible')

        if isinstance(boundary, ArcSplineCompatible):
            boundary = boundary.to_arc_spline()

        if not boundary.is_closed:
            raise ValueError('boundary must be closed shaped.')

        _check_lattice_vectors(u, v)

        if predicate is not None:
            if not isinstance(predicate, Iterable):
                predicate = (predicate,)

            if not all([callable(pred) for pred in predicate]):
                raise TypeError('predicate must be Callable or List[Callable].')

        explode = bool(explode)
        remove_outliers = bool(remove_outliers)

        # generate actual lattice site objects
        lattice_points_uv, lattice_points_xy = cls._gen_lattice_points(boundary, u, v, Vector(), seed)

        # shift uv points so that (0, 0) is in the upper left

        # min_u, min_v = np.min(lattice_points_uv, axis=0)

        lattice_points_uv -= np.min(lattice_points_uv, axis=0)

        elements = []
        for lattice_point_xy, lattice_point_uv in zip(lattice_points_xy, lattice_points_uv):
            lattice_site_element = element_gen(unscale_vec(lattice_point_xy), lattice_point_uv)

            if lattice_site_element:
                lattice_site_element = lattice_site_element.translated_to(unscale_vec(lattice_point_xy + center))

                if explode:
                    if isinstance(lattice_site_element, LayoutBase):
                        sub_elements = lattice_site_element._layout_elements()
                        if remove_outliers:
                            for sub_elem in sub_elements:
                                if boundary.contains(scale_vec(sub_elem.pivot)):
                                    elements.append(sub_elem)
                        else:
                            elements.extend(sub_elements)
                    else:
                        elements.append(lattice_site_element)
                else:
                    elements.append(lattice_site_element)

        # sort the points by predicate
        if predicate:
            if explode:
                lattice_elements_xy = np.array([elem.pivot for elem in elements])
            else:
                lattice_elements_xy = lattice_points_xy

            # todo: this looks weird
            sorted_indices = np.lexsort(tuple(pred(lattice_elements_xy) for pred in predicate))

            elements = [elements[i] for i in sorted_indices]

        return elements
