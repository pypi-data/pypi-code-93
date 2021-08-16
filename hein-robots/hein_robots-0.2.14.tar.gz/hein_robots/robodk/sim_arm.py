from typing import Any, Optional, List, Union
from robolink import Robolink, Pose
from robodk import Pose_2_Fanuc, Fanuc_2_Pose, Pose_2_TxyzRxyz, TxyzRxyz_2_Pose, transl, rotx, roty, rotz
from hein_robots.robotics import Units, Location, Cartesian, Orientation
from hein_robots.base.robot_arms import RobotArm


class SimArm(RobotArm):
    @staticmethod
    def pose_to_location(pose) -> Location:
        # pose_list = Pose_2_TxyzRxyz(pose)
        # return Location(Cartesian(*pose_list[:3]), Orientation(*pose_list[3:], units=Units.RADIANS).convert_units(Units.DEGREES))
        fanuc = Pose_2_Fanuc(pose)
        return Location(Cartesian(*fanuc[:3]), Orientation(*fanuc[3:]))

    @staticmethod
    def location_to_pose(location: Location):
        # return transl(*location.position) * rotx(location.rx) * roty(location.ry) * rotz(location.rz)
        # pose = TxyzRxyz_2_Pose([*location.position, *location.orientation.convert_units(Units.RADIANS)])
        # return pose
        fanuc = [*location.position, *location.orientation]
        # swap rx and ry for fanuc
        # fanuc[3], fanuc[4] = fanuc[4], fanuc[3]
        return Fanuc_2_Pose(fanuc)

    def __init__(self, host: str = 'localhost', robot_name: str = 'Robot', gripper_name: str = 'Gripper', gripper_span: float = 50.0, default_velocity: float = 250.0, max_velocity: float = 500.0):
        self.rdk = Robolink(host)
        self.arm = self.rdk.Item(robot_name)
        self.gripper = self.rdk.Item(gripper_name)
        self._connected = True
        self._default_velocity = default_velocity
        self._max_velocity = max_velocity
        self.gripper_span = gripper_span

        self.arm.setPoseFrame(self.arm.PoseFrame())
        self.arm.setPoseTool(self.arm.PoseTool())

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def max_velocity(self) -> float:
        return self._max_velocity

    @max_velocity.setter
    def max_velocity(self, value: float):
        self._max_velocity = value

    @property
    def default_velocity(self) -> float:
        return self._default_velocity

    @default_velocity.setter
    def default_velocity(self, value: float):
        self._default_velocity = value

    @property
    def acceleration(self) -> float:
        return 0.0

    @property
    def velocity(self) -> float:
        return 0.0

    @property
    def location(self) -> Location:
        return self.pose_to_location(self.arm.Pose())

    @property
    def joint_positions(self) -> List[float]:
        return self.arm.Joints().list()

    @property
    def joint_count(self) -> int:
        return len(self.joint_positions)

    def stop(self):
        self.arm.Stop()

    def pause(self):
        self.arm.Pause()

    def home(self, wait: bool = True):
        self.arm.MoveJ(self.arm.JointsHome(), blocking=wait)

    def move_to_location(self, location: Location,
                         velocity: Optional[float] = None, acceleration: Optional[float] = None,
                         relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        if relative:
            location = self.location * location

        if velocity is None:
            velocity = self.default_velocity

        self.arm.setSpeed(velocity)
        pose = self.location_to_pose(location)
        self.arm.MoveL(pose, blocking=wait)

    def move_joints(self, *actuator_positions: float,
                    velocity: Optional[float] = None, acceleration: Optional[float] = None,
                    relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        self.arm.MoveJ(actuator_positions, blocking=wait)

    def open_gripper(self, position: Optional[Union[float, bool]] = None, wait: bool = True, timeout: Optional[float] = None):
        if position is None:
            position = 0.0
        elif isinstance(position, bool):
            position = 0.0 if position else 1.0

        position_mm = (1 - position) * self.gripper_span
        self.gripper.MoveJ([position_mm], blocking=wait)
