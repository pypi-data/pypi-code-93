from typing import List


class Vector3:

    def __init__(self, x: float, y: float, z: float, _type: str = ''):
        self._type = 'vector3'
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vector3):
            return other.x == self.x and other.y == self.y and other.z == self.z
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Vector3<x={self.x}, y={self.y}, z={self.z}>"


class Pose:

    def __init__(self, position: Vector3, rotation: Vector3, name: str = '', _type: str = ''):
        self._type = 'pose'
        self.name = name
        self.position = position
        self.rotation = rotation

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Pose):
            return other.name == self.name and other.position == self.position and other.rotation == self.rotation
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Pose<name={self.name}, position={self.position}, orientation={self.rotation}>"

    def to_dict(self) -> dict:
        return {'x': self.position.x, 'y': self.position.y, 'z': self.position.z,
                'rx': self.rotation.x, 'ry': self.rotation.y, 'rz': self.rotation.z}

    @staticmethod
    def from_dict(pose: dict) -> 'Pose':
        return Pose(Vector3(pose.get('x', 0.0), pose.get('y', 0.0), pose.get('z', 0.0)),
                    Vector3(pose.get('rx', 0.0), pose.get('ry', 0.0), pose.get('rz', 0.0)), name=pose.get('name', ''))


class Poses:

    def __init__(self, poses: List[Pose], connected: bool = False, _type: str = ''):
        self._type = 'poses'
        self.connected = connected
        self.poses = poses

    def add(self, pose: Pose):
        self.poses.append(pose)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Poses):
            return other.connected == self.connected and other.poses == self.poses
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f"Poses<connected={self.connected}, poses={self.poses}>"
