from typing import Union, Tuple, Dict, List, Optional, Any, Iterable
import numpy as np
from hein_robots.robotics import Location, Cartesian, Rotation


GridSpacingType = Union[Tuple[float, float], Union[float, float, float], Cartesian]


class LocationGroup:
    def __len__(self):
        return 0

    def __getitem__(self, item):
        return None

    def indexes(self) -> List[Any]:
        return []


class BaseGrid(LocationGroup):
    def __init__(self, rows: int, columns: int):
        self.rows = rows
        self.columns = columns
        self.location_grid: Optional[np.ndarray] = None

    def __len__(self):
        return len(self.location_grid)

    def __getitem__(self, item: Union[Tuple[int, int], int, str]) -> Union[Location, np.ndarray]:
        if isinstance(item, tuple):
            if len(item) != 2:
                raise TypeError(f'grid indices must be ints, 2-element tuples or strings, not {item.__class__.__name__}')

            return self.location_grid[item[0], item[1]]

        if isinstance(item, str):
            index = self.grid_index_numbers(item)
            return self.location_grid[index[1]][index[0]]

        if isinstance(item, (int, slice)):
            return self.location_grid[item]

        raise TypeError(f'grid indices must be ints, slices, 2-element tuples or strings, not {item.__class__.__name__}')

    @property
    def indexes(self) -> List[str]:
        indexes = []

        for row in range(self.rows):
            for column in range(self.columns):
                indexes.append(self.grid_index(column, row))

        return indexes

    @property
    def locations(self) -> Dict[str, Location]:
        return dict(zip(self.indexes, self.location_grid.flatten()))

    def grid_index_numbers(self, grid_index: str) -> Tuple[int, int]:
        column = ord(grid_index[0].upper()) - ord('A')
        row = int(grid_index[1:]) - 1

        return column, row

    def grid_index(self, column: int, row: int) -> str:
        column_letter = 'ABCDEFGHIJKLMNOPQRSTUVQXYZ'[column]
        return f'{column_letter}{row + 1}'

    def update(self):
        pass


class StaticGrid(BaseGrid):
    def __init__(self, locations: List[Location], rows: int, columns: int):
        BaseGrid.__init__(self, rows, columns)
        self.location_grid = np.array(locations)

        if rows * columns != len(locations):
            raise StaticGridInvalidLength(f"Cannot create StaticGrid, length of locations doesn't equal rows * columns")

    def __getitem__(self, item: Union[Tuple[int, int], int, str]) -> Union[Location, np.ndarray]:
        if isinstance(item, tuple):
            if len(item) != 2:
                raise TypeError(f'grid indices must be ints, 2-element tuples or strings, not {item.__class__.__name__}')

            return self.location_grid[item[0] * self.columns + item[1]]

        if isinstance(item, str):
            index = self.grid_index_numbers(item)
            return self.location_grid[index[1] * self.columns + index[0]]

        if isinstance(item, (int, slice)):
            return self.location_grid[item]

        raise TypeError(f'grid indices must be ints, slices, 2-element tuples or strings, not {item.__class__.__name__}')


class Grid(BaseGrid):
    @classmethod
    def from_locations(cls, top_left: Location, bottom_left: Location, bottom_right: Location, rows: int, columns: int) -> 'Grid':
        x = bottom_right.position - bottom_left.position
        y = top_left.position - bottom_left.position
        z = x.cross(y)
        # use a cross product to calculate a new y vector axis relative orthogonal to x and z, then project the given
        # y vector on to it to get a new orthogonal y axis with the proper length
        y_ortho = y.project(z.cross(x))
        x_spacing = x.magnitude / (columns - 1) if columns > 1 else 0.0
        y_spacing = y_ortho.magnitude / (rows - 1) if rows > 1 else 0.0

        # location = Location.from_xy(bottom_left.position, x, y_ortho)
        spacing = Cartesian(x_spacing, y_spacing)

        return cls(bottom_left, rows=rows, columns=columns, spacing=spacing)

    def __init__(self, location: Location, rows: int, columns: int, spacing: GridSpacingType, offset: Optional[Location] = None):
        BaseGrid.__init__(self, rows, columns)
        self.location = location
        self.offset = offset or Location()

        if isinstance(spacing, tuple):
            self.spacing = Cartesian(*spacing)
        elif isinstance(spacing, Cartesian):
            self.spacing = spacing
        else:
            raise GridSpacingError(f'Invalid grid spacing, must be a 2- or 3-element tuple or Cartesian: {spacing}')

        self.update()

    def update(self):
        base_grid = np.array([[Location(x, y, 0) for x in range(self.columns)] for y in range(self.rows)])
        self.location_grid = self.location * self.spacing.scale(base_grid) * self.offset


class GridError(Exception):
    pass


class GridSpacingError(GridError):
    pass


class StaticGridError(Exception):
    pass


class StaticGridInvalidLength(StaticGridError):
    pass
