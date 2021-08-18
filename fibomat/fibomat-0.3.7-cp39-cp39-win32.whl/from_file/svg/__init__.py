from typing import List

import svgelements

from fibomat.shapes import Shape
from fibomat.utils import PathLike


def shapes_from_svg(file_path: PathLike) -> List[Shape]:
    svg = svgelements.SVG.parse(file_path)
    for elem in svg.elements():
        if elem == svg:
            raise RuntimeError
        if isinstance(elem, svgelements.Group):
            print('group')
        # print(elem)
