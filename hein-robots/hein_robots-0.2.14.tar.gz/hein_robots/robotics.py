from typing import Optional, Tuple, Union, Dict
import math
from enum import Enum
import numpy as np
from scipy.spatial.transform import Rotation


class RoboticsError(Exception):
    pass


class RoboticsUnitConversionError(RoboticsError):
    pass


class Units(Enum):
    METERS = 'meters'
    MILLIMETERS = 'millimeters'
    DEGREES = 'degrees'
    RADIANS = 'radians'


class Robotics:
    _precendence = 0


class Vector(Robotics):
    def __init__(self, *values: float):
        self._values = np.array([float(v) for v in values])

    def __str__(self):
        return f'{self.__class__.__name__}({", ".join([f"{v:.4}" for v in self._values])})'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return self._values.__iter__()

    def __getitem__(self, item):
        if isinstance(item, slice):
            # slicing always returns a vector
            return Vector(*self._values.__getitem__(item))

        return self._values.__getitem__(item)

    def __setitem__(self, key, value):
        return self._values.__setitem__(key, value)

    def __contains__(self, item):
        return self._values.__contains__(item)

    def __add__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__radd__(self)

        return self.__class__(*self._values.__add__(other))

    def __radd__(self, other):
        if isinstance(other, Vector):
            return self.__class__(*self._values.__radd__(other._values))

        return self.__class__(*self._values.__radd__(other))

    def __sub__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__rsub__(self)

        return self.__class__(*self._values.__sub__(other))

    def __rsub__(self, other):
        if isinstance(other, Vector):
            return other.__class__(*self._values.__rsub__(other._values))

        return self.__class__(*self._values.__rsub__(other))

    def __mul__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__rmul__(self)

        if isinstance(other, (np.ndarray, list)):
            return np.vectorize(self.__mul__, otypes=[object])(other)

        return self.__class__(*self._values.__mul__(other))

    def __rmul__(self, other):
        if isinstance(other, Vector):
            return other.__class__(*self._values.__rmul__(other._values))

        if isinstance(other, (np.ndarray, list)):
            return np.vectorize(self.__rmul__, otypes=[object])(other)

        return self.__class__(*self._values.__rmul__(other))

    def __neg__(self):
        return self.__class__(*self._values.__neg__())

    def __pos__(self):
        return self.__class__(*self._values.__pos__())

    def __abs__(self):
        return self.__class__(*self._values.__abs__())

    def __invert__(self):
        return self.__class__(*self._values.__invert__())

    def __eq__(self, other: 'Vector'):
        if not isinstance(other, Vector):
            return False

        for equal in np.isclose(self._values, other._values):
            if not equal:
                return False

        return True

    @property
    def array(self) -> np.ndarray:
        return self._values

    @property
    def vector(self) -> 'Vector':
        return Vector(*self._values)

    def dot(self, value: Union['Vector', np.ndarray]) -> 'Vector':
        return self.__class__(*np.dot(self, value))

    def cross(self, value: Union['Vector', np.ndarray]) -> 'Vector':
        return self.__class__(*np.cross(self, value))


class Cartesian(Vector):
    _precendence = 1

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        super().__init__(x, y, z)

    def __str__(self):
        return f'{self.__class__.__name__}(x={self.x:.4}, y={self.y:.4}, z={self.z:.4})'

    @property
    def homogeneous(self) -> Vector:
        return Vector(*self._values, 1)

    @property
    def x(self) -> float:
        return self._values[0]

    @x.setter
    def x(self, value: float):
        self._values[0] = value

    @property
    def y(self) -> float:
        return self._values[1]

    @y.setter
    def y(self, value: float):
        self._values[1] = value

    @property
    def z(self) -> float:
        return self._values[2]

    @z.setter
    def z(self, value: float):
        self._values[2] = value

    @property
    def normalized(self) -> 'Cartesian':
        normalized = self._values / np.linalg.norm(self._values)
        return Cartesian(*normalized)

    @property
    def dict(self) -> Dict[str, float]:
        return {
            'x': self._values[0], 'y': self._values[1], 'z': self._values[2]
        }

    @property
    def magnitude(self):
        return np.linalg.norm(self._values)

    def translate(self, x: Union[float, 'Cartesian'] = 0.0, y: float = 0.0, z: float = 0.0) -> 'Cartesian':
        if isinstance(x, Cartesian):
            return self + x

        return self + Cartesian(x, y, z)

    def scale(self, value: Union[float, 'Frame', 'Cartesian', np.ndarray, list]) -> Union['Cartesian', 'Frame', np.ndarray, list]:
        if isinstance(value, Cartesian):
            return value.__class__(self.x * value.x, self.y * value.y, self.z * value.z)

        if isinstance(value, Frame):
            return value.__class__(self.scale(value._position), value._orientation)

        if isinstance(value, (np.ndarray, list)):
            return np.vectorize(self.scale)(value)

        return self * value

    def project(self, onto: 'Cartesian') -> 'Cartesian':
        scalar_projection = np.dot(self._values, onto._values) / onto.magnitude ** 2
        return self.__class__(*(scalar_projection * onto))

    def copy(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        return self.__class__(
            x=self.x if x is None else x,
            y=self.y if y is None else y,
            z=self.z if z is None else z,
        )

    def convert_mm_to_m(self) -> 'Cartesian':
        return self * 0.001

    def convert_m_to_mm(self) -> 'Cartesian':
        return self * 1000.0


class Orientation(Vector):
    _precendence = 2

    @classmethod
    def from_matrix(cls, rotation_matrix: np.array) -> 'Orientation':
        orientation = cls()
        orientation.update_from_rotation(Rotation.from_matrix(rotation_matrix[:3, :3]))

        return orientation

    @classmethod
    def from_axis_angle(cls, axis: Cartesian, angle: float) -> 'Orientation':
        rotation_vector = axis.normalized * np.deg2rad(angle)

        return cls.from_rotation_vector(rotation_vector)

    @classmethod
    def from_rotation_vector(cls, rotation_vector: Cartesian) -> 'Orientation':
        orientation = cls()
        orientation.update_from_rotation(Rotation.from_rotvec(rotation_vector._values))

        return orientation

    @classmethod
    def from_xyz(cls, x: Cartesian, y: Cartesian, z: Cartesian) -> 'Orientation':
        rotation_matrix = np.identity(3)
        rotation_matrix[:, 0] = x.normalized.array
        rotation_matrix[:, 1] = y.normalized.array
        rotation_matrix[:, 2] = z.normalized.array

        return cls.from_matrix(rotation_matrix)

    @classmethod
    def from_xy(cls, x: Cartesian, y: Cartesian) -> 'Orientation':
        z = x.cross(y)
        y_normal = z.cross(x)  # recalculate the y axis to ensure all 3 axes are normal
        return cls.from_xyz(x, y_normal, z)

    @classmethod
    def from_xz(cls, x: Cartesian, z: Cartesian) -> 'Orientation':
        y = z.cross(x)
        z_normal = x.cross(y)
        return cls.from_xyz(x, y, z_normal)

    @classmethod
    def from_yz(cls, y: Cartesian, z: Cartesian) -> 'Orientation':
        x = y.cross(z)
        y_normal = z.cross(x)
        return cls.from_xyz(x, y_normal, z)

    def __init__(self, rx: float = 0.0, ry: float = 0.0, rz: float = 0.0, units: Units = Units.DEGREES):
        self.units = units
        self._values = np.array([float(rx), float(ry), float(rz)])
        self._rotation: Rotation = Rotation.from_euler('xyz', [rx, ry, rz], degrees=(self.units == Units.DEGREES))

    def __str__(self):
        return f'{self.__class__.__name__}(rx={self.rx:.4}, ry={self.ry:.4}, rz={self.rz:.4})'

    def __repr__(self):
        return str(self)

    def __mul__(self, other):
        if isinstance(other, Frame):
            return other.__class__.from_matrix(np.dot(self.matrix_4x4, other.matrix))

        if isinstance(other, Orientation):
            return self.__class__.from_matrix(np.dot(self.matrix, other.matrix))

        if isinstance(other, Vector):
            return other.__class__(*(np.dot(self.matrix, other._values)))

        if isinstance(other, np.ndarray):
            return other.__class__(*np.dot(self.matrix, other))

        return self.__class__(self._values.__mul__(other))

    def __rmul__(self, other):
        if isinstance(other, Frame):
            return other.__class__.from_matrix(np.dot(self.matrix, other.matrix_4x4))

        if isinstance(other, Orientation):
            return self.__class__.from_matrix(np.dot(other.matrix, self.matrix))

        if isinstance(other, Vector):
            return other.__class__(*(np.dot(other._values, self.matrix)))

        if isinstance(other, np.ndarray):
            return other.__class__(*np.dot(other, self.matrix))

        return self.__class__(self._values.__rmul__(other))

    def __invert__(self):
        return self.__class__(*self._rotation.inv().as_euler('xyz', degrees=(self.units == Units.DEGREES)))

    @property
    def rx(self) -> float:
        return self._values[0]

    @rx.setter
    def rx(self, value: float):
        self._values[0] = value
        self.update()

    @property
    def ry(self) -> float:
        return self._values[1]

    @ry.setter
    def ry(self, value: float):
        self._values[1] = value
        self.update()

    @property
    def rz(self) -> float:
        return self._values[2]

    @rz.setter
    def rz(self, value: float):
        self._values[2] = value
        self.update()

    @property
    def matrix(self) -> np.ndarray:
        return self._rotation.as_matrix()

    @matrix.setter
    def matrix(self, value: np.ndarray):
        self.update_from_rotation(Rotation.from_matrix(value))

    @property
    def matrix_4x4(self) -> np.array:
        # pad the bottom-right side of the matrix with 1 row and column
        padded = np.pad(self.matrix, (0, 1))
        # make sure the bottom-right cell is 1.0
        padded[3, 3] = 1.0

        return padded

    @property
    def rotation_vector(self) -> Cartesian:
        return Cartesian(*self._rotation.as_rotvec())

    @rotation_vector.setter
    def rotation_vector(self, value: Cartesian):
        self.update_from_rotation(Rotation.from_rotvec(value))

    @property
    def axis(self) -> Cartesian:
        return self.rotation_vector.normalized

    @axis.setter
    def axis(self, value: Cartesian):
        self.rotation_vector = value.normalized * self._rotation.magnitude()

    @property
    def angle(self) -> float:
        return np.rad2deg(self._rotation.magnitude())

    @angle.setter
    def angle(self, value: float):
        self.rotation_vector = self.axis * np.deg2rad(value)

    @property
    def dict(self) -> Dict[str, float]:
        return {
            'rx': self._values[0], 'ry': self._values[1], 'rz': self._values[2]
        }

    def rotate(self, rx: Union[float, Cartesian, 'Frame', 'Orientation'] = 0.0, ry: float = 0.0, rz: float = 0.0) -> Union[Cartesian, 'Frame', 'Orientation']:
        if isinstance(rx, (Orientation, Cartesian, Frame)):
            return self * rx

        return self * Orientation(rx, ry, rz)

    def update(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None):
        if x is None and y is None and z is None:
            values = self._values
        else:
            updated = [x, y, z]
            values = [updated[i] if updated[i] is not None else self._values[i] for i in range(len(updated))]

        self._rotation: Rotation = Rotation.from_euler('xyz', values, degrees=(self.units == Units.DEGREES))

    def copy(self, rx: Optional[float] = None, ry: Optional[float] = None, rz: Optional[float] = None):
        return self.__class__(
            rx=self.rx if rx is None else rx,
            ry=self.ry if ry is None else ry,
            rz=self.rz if rz is None else rz,
        )

    def update_from_rotation(self, rotation: Rotation):
        self._rotation = rotation
        self._values = rotation.as_euler('xyz', degrees=(self.units == Units.DEGREES))

    def convert_units(self, units: Units) -> 'Orientation':
        if self.units == units:
            return self

        if self.units == Units.DEGREES and units == Units.RADIANS:
            return Orientation(*np.radians(self.array))

        if self.units == Units.RADIANS and units == Units.DEGREES:
            return Orientation(*np.degrees(self.array))

        raise RoboticsUnitConversionError(f'Cannot convert from {self.units.name} to {units.name}')

    def convert_to_radians(self) -> 'Orientation':
        if self.units == Units.RADIANS:
            return self.copy()

        return self.__class__(*np.radians(self._values), units=Units.RADIANS)

    def convert_to_degrees(self) -> 'Orientation':
        if self.units == Units.DEGREES:
            return self.copy()

        return self.__class__(*np.degrees(self._values), units=Units.DEGREES)


class Frame(Robotics):
    _precendence = 3

    @classmethod
    def from_matrix(cls, matrix: np.ndarray) -> 'Frame':
        position_col = matrix[:4, 3:][:3]  # first 3 elements of the 4th column
        position = position_col.transpose()[0]  # rotate and grab the first row
        orientation_matrix = matrix[:3, :3]

        return cls(Cartesian(*position), Orientation.from_matrix(orientation_matrix))

    @classmethod
    def from_xyz(cls, position: Cartesian, x: Cartesian, y: Cartesian, z: Cartesian) -> 'Frame':
        return cls(position, Orientation.from_xyz(x, y, z))

    @classmethod
    def from_xy(cls, position: Cartesian, x: Cartesian, y: Cartesian) -> 'Frame':
        return cls(position, Orientation.from_xy(x, y))

    @classmethod
    def from_xz(cls, position: Cartesian, x: Cartesian, z: Cartesian) -> 'Frame':
        return cls(position, Orientation.from_xz(x, z))

    @classmethod
    def from_yz(cls, position: Cartesian, y: Cartesian, z: Cartesian) -> 'Frame':
        return cls(position, Orientation.from_yz(y, z))

    def __init__(self, x: Union[Cartesian, float] = 0.0, y: Union[Orientation, float] = 0.0, z: float = 0.0,
                 rx: float = 0.0, ry: float = 0.0, rz: float = 0.0):
        if isinstance(x, Cartesian):
            self._position = x
            self._orientation = y if isinstance(y, Orientation) else Orientation(rx, ry, rz)
        else:
            self._position = Cartesian(x, y, z)
            self._orientation = Orientation(rx, ry, rz)

    def __str__(self):
        p = self._position
        o = self._orientation
        return f'{self.__class__.__name__}(x={p.x:.4}, y={p.y:.4}, z={p.z:.4}, rx={o.rx:.4}, ry={o.ry:.4}, rz={o.rz:.4})'

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__radd__(self)

        if isinstance(other, Frame):
            return self.__class__(self._position + other._position, self._orientation + other._orientation)

        if isinstance(other, Orientation):
            return self.__class__(self._position, self._orientation + other)

        if isinstance(other, (Vector, np.ndarray)):
            return self.__class__(self._position + other, self._orientation)

        raise TypeError(f"Can't add frame by value of type '{other.__class__.__name__}'")

    def __radd__(self, other):
        if isinstance(other, Frame):
            return self.__class__(other._position + self._position, other._orientation + self._orientation)

        if isinstance(other, Orientation):
            return self.__class__(self._position, other + self._orientation)

        if isinstance(other, (Vector, np.ndarray)):
            return self.__class__(other + self._position, self._orientation)

        raise TypeError(f"Can't add frame by value of type '{other.__class__.__name__}'")

    def __sub__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__rsub__(self)

        if isinstance(other, Frame):
            return self.__class__(self._position - other._position, self._orientation - other._orientation)

        if isinstance(other, Orientation):
            return self.__class__(self._position, self._orientation - other)

        if isinstance(other, (Vector, np.ndarray)):
            return self.__class__(self._position - other, self._orientation)

        raise TypeError(f"Can't subtract frame by value of type '{other.__class__.__name__}'")

    def __rsub__(self, other):
        if isinstance(other, Frame):
            return self.__class__(other._position - self._position, other._orientation - self._orientation)

        if isinstance(other, Orientation):
            return self.__class__(self._position, other - self._orientation)

        if isinstance(other, (Vector, np.ndarray)):
            return self.__class__(other - self._position, self._orientation)

        raise TypeError(f"Can't subtract frame by value of type '{other.__class__.__name__}'")

    def __mul__(self, other):
        if isinstance(other, Robotics) and other._precendence > self._precendence:
            return other.__rmul__(self)

        if isinstance(other, Frame):
            return self.__class__.from_matrix(np.dot(self.matrix, other.matrix))

        if isinstance(other, Orientation):
            return self.__class__.from_matrix(np.dot(self.matrix, other.matrix_4x4))

        if isinstance(other, Cartesian):
            transformed = np.dot(self.matrix, Cartesian(*other).homogeneous)
            return other.__class__(*transformed[:3])

        if isinstance(other, (Vector, np.ndarray, list)):
            return np.vectorize(self.__mul__)(other)

        raise TypeError(f"Can't multiply frame by value of type '{other.__class__.__name__}'")

    def __rmul__(self, other):
        if isinstance(other, Frame):
            return self.__class__.from_matrix(np.dot(other.matrix, self.matrix))

        if isinstance(other, Orientation):
            return self.__class__.from_matrix(np.dot(other.matrix_4x4, * self.matrix))

        if isinstance(other, Cartesian):
            transformed = np.dot(Cartesian(*other).homogeneous, self.matrix)
            return other.__class__(*transformed[:3])

        if isinstance(other, (Vector, np.ndarray, list)):
            return np.vectorize(self.__rmul__)(other)

        raise TypeError(f"Can't multiply frame by value of type '{other.__class__.__name__}'")

    def __eq__(self, other: 'Frame'):
        if not isinstance(other, Frame):
            return False

        return other._position == self._position and other._orientation == self._orientation

    @property
    def matrix(self) -> np.ndarray:
        frame_matrix = self._orientation.matrix_4x4
        frame_matrix[:4, 3] = self._position.homogeneous.array

        return frame_matrix

    @property
    def dict(self) -> Dict[str, float]:
        return {**self._position.dict, **self._orientation.dict}

    @property
    def inverse(self) -> 'Frame':
        return self.__class__.from_matrix(np.linalg.inv(self.matrix))

    @property
    def x(self) -> float:
        return self._position.x

    @x.setter
    def x(self, value: float):
        self._position.x = value

    @property
    def y(self) -> float:
        return self._position.y

    @y.setter
    def y(self, value: float):
        self._position.y = value

    @property
    def z(self) -> float:
        return self._position.z

    @z.setter
    def z(self, value: float):
        self._position.z = value

    @property
    def rx(self) -> float:
        return self._orientation.rx

    @rx.setter
    def rx(self, value: float):
        self._orientation.rx = value

    @property
    def ry(self) -> float:
        return self._orientation.ry

    @ry.setter
    def ry(self, value: float):
        self._orientation.ry = value

    @property
    def rz(self) -> float:
        return self._orientation.rz

    @rz.setter
    def rz(self, value: float):
        self._orientation.rz = value

    @property
    def array(self) -> np.ndarray:
        return np.array([*self._position, *self._orientation])

    def translate(self, x: Union[float, 'Cartesian'] = 0.0, y: float = 0.0, z: float = 0.0) -> 'Frame':
        return self.__class__(self._position.translate(x, y, z), self._orientation)

    def rotate(self, rx: Union[float, 'Orientation'] = 0.0, ry: float = 0.0, rz: float = 0.0) -> 'Frame':
        return self.__class__(self._position, self._orientation.rotate(rx, ry, rz))

    def scale(self, value: Union[float, 'Frame', 'Cartesian', np.ndarray, list]) -> Union[
        'Cartesian', 'Frame', np.ndarray, list]:
        if isinstance(value, Frame):
            return value.__class__(self._position.scale(value._position), self._orientation)

        if isinstance(value, Cartesian):
            return self.__class__(self._position.scale(value), self._orientation)

        if isinstance(value, (np.ndarray, list)):
            return np.vectorize(self.scale)(value)

    def copy(self, x: Optional[float] = None, y: Optional[float] = None, z: Optional[float] = None,
             rx: Optional[float] = None, ry: Optional[float] = None, rz: Optional[float] = None):
        return self.__class__(
            x=self.x if x is None else x,
            y=self.y if y is None else y,
            z=self.z if z is None else z,
            rx=self.rx if rx is None else rx,
            ry=self.ry if ry is None else ry,
            rz=self.rz if rz is None else rz,
        )

    def convert_mm_to_m(self) ->'Frame':
        return self.__class__(self._position.convert_mm_to_m(), self._orientation)

    def convert_m_to_mm(self) ->'Frame':
        return self.__class__(self._position.convert_m_to_mm(), self._orientation)


class Location(Frame):
    @property
    def position(self) -> Cartesian:
        return self._position

    @position.setter
    def position(self, value: Cartesian):
        self._position = value

    @property
    def orientation(self) -> Orientation:
        return self._orientation

    @orientation.setter
    def orientation(self, value: Orientation):
        self._orientation = value

    def relative_to(self, location: Frame) -> 'Location':
        return location * self


class Twist(Frame):
    @property
    def linear(self) -> Cartesian:
        return self._position

    @linear.setter
    def linear(self, value: Cartesian):
        self._position = value

    @property
    def angular(self) -> Orientation:
        return self._orientation

    @angular.setter
    def angular(self, value: Orientation):
        self._orientation = value


class Wrench(Frame):
    @property
    def linear(self) -> Cartesian:
        return self._position

    @linear.setter
    def linear(self, value: Cartesian):
        self._position = value

    @property
    def angular(self) -> Orientation:
        return self._orientation

    @angular.setter
    def angular(self, value: Orientation):
        self._orientation = value
