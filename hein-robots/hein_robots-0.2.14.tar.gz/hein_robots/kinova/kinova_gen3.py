from typing import Optional, List, Union
import time
from hein_robots.robotics import Location, Twist, Wrench, Cartesian, Orientation, Units, Frame
from hein_robots.base import robot_arms
from hein_robots.kinova.kinova_gripper import KinovaGripper
from hein_robots.kinova.kortex import KortexConnection, Base_pb2, ControlConfig_pb2


class KinovaGen3Arm(robot_arms.RobotArm):
    GRIPPER_VELOCITY_STOP_THRESHOLD = 0.01
    GRIPPER_STOP_WAIT_TIME = 1.5
    GRIPPER_WAIT_DELAY = 0.05

    def __init__(self, host: str = '192.168.1.10', port: int = 10000, username: str = 'admin', password: str = 'admin', connect: bool = True,
                 default_velocity: float = 250, max_velocity: float = 500, gripper_default_velocity: float = 0.5, gripper_default_force: float = 0.5,
                 position_units: str = Units.MILLIMETERS):
        super().__init__(default_velocity=default_velocity, max_velocity=max_velocity, gripper_default_velocity=gripper_default_velocity,
                         gripper_default_force=gripper_default_force, position_units=position_units)
        self.connection = KortexConnection(host, port, username=username, password=password, connect=connect)
        self.gripper = KinovaGripper(self.connection)
        self.last_feedback = None
        self.last_feedback_time = 0
        self.last_gripper_feedback = None
        self.last_gripper_feedback_time = 0
        self._position_units = position_units
        self._joint_count: Optional[int] = None
        self._default_velocity = default_velocity
        self._max_velocity = max_velocity

    @property
    def position_units(self) -> str:
        return self._position_units

    @position_units.setter
    def position_units(self, value: str):
        self._position_units = value

    @property
    def connected(self) -> bool:
        return self.connection.connected

    @property
    def feedback(self):
        # feedback only updates at 1khz, so cache if needed
        if self.last_feedback is not None and time.time() - self.last_feedback_time < 0.001:
            return self.last_feedback

        self.last_feedback =  self.connection.cyclic_client.RefreshFeedback()
        return self.last_feedback

    @property
    def gripper_feedback(self):
        return self.gripper.gripper_feedback

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
        if value < 0 or value > self.max_velocity:
            raise robot_arms.RobotArmInvalidVelocityError(f'Invalid velocity: {value} m/s, must be less than {self.max_velocity} m/s')

        self._default_velocity = value

    @property
    def acceleration(self) -> float:
        return Cartesian(self.feedback.imu_acceleration_x, self.feedback.imu_acceleration_y, self.feedback.imu_acceleration_z).magnitude

    @property
    def velocity(self) -> float:
        return self.twist.linear.magnitude

    @property
    def location(self) -> Location:
        pose = self.feedback.base
        location = Location(
            Cartesian(pose.tool_pose_x, pose.tool_pose_y, pose.tool_pose_z),
            Orientation(pose.tool_pose_theta_x, pose.tool_pose_theta_y, pose.tool_pose_theta_z)
        )

        return location.convert_m_to_mm() if self.position_units == Units.MILLIMETERS else location

    @property
    def twist(self) -> Twist:
        pose = self.feedback.base
        twist = Twist(
            Cartesian(pose.tool_twist_linear_x, pose.tool_twist_linear_y, pose.tool_twist_linear_z),
            Orientation(pose.tool_twist_angular_x, pose.tool_twist_angular_y, pose.tool_twist_angular_z)
        )

        return twist.convert_m_to_mm() if self.position_units == Units.MILLIMETERS else twist

    @property
    def wrench(self) -> Wrench:
        pose = self.feedback.base
        wrench = Wrench(
            Cartesian(pose.tool_external_wrench_force_x, pose.tool_external_wrench_force_y, pose.tool_external_wrench_force_z),
            Orientation(pose.tool_external_wrench_torque_x, pose.tool_external_wrench_torque_y, pose.tool_external_wrench_torque_z)
        )

        return wrench.convert_m_to_mm() if self.position_units == Units.MILLIMETERS else wrench

    @property
    def joint_positions(self) -> List[float]:
        joints = self.feedback.actuators
        return [joint.position for joint in joints]

    @property
    def joint_count(self):
        if self._joint_count is not None:
            return self._joint_count

        self._joint_count = self.connection.client.GetActuatorCount().count
        return self._joint_count

    @property
    def gripper_position(self) -> float:
        return self.gripper.position

    @property
    def gripper_velocity(self) -> float:
        return self.gripper.velocity

    @property
    def tool_configuration(self) -> ControlConfig_pb2.ToolConfiguration:
        return self.connection.control_client.GetToolConfiguration()

    @property
    def tool_offset(self) -> Location:
        tool_transform = self.tool_configuration.tool_transform
        return Location(tool_transform.x, tool_transform.y, tool_transform.z, tool_transform.theta_x, tool_transform.theta_y, tool_transform.theta_z).convert_m_to_mm()

    @tool_offset.setter
    def tool_offset(self, value: Location):
        offset_m = value.convert_mm_to_m()
        tool_configuration = self.tool_configuration
        tool_configuration.tool_transform.x = offset_m.x
        tool_configuration.tool_transform.y = offset_m.y
        tool_configuration.tool_transform.z = offset_m.z
        tool_configuration.tool_transform.theta_x = offset_m.rx
        tool_configuration.tool_transform.theta_y = offset_m.ry
        tool_configuration.tool_transform.theta_z = offset_m.rz
        self.connection.control_client.SetToolConfiguration(tool_configuration)

    @property
    def tool_mass(self) -> float:
        return self.tool_configuration.tool_mass

    @tool_mass.setter
    def tool_mass(self, value: float):
        tool_configuration = self.tool_configuration
        tool_configuration.tool_mass = value
        self.connection.control_client.SetToolConfiguration(tool_configuration)

    def connect(self):
        self.connection.connect()
        self.set_servo_mode(Base_pb2.SINGLE_LEVEL_SERVOING)

    def disconnect(self):
        self.connection.disconnect()

    def set_servo_mode(self, mode: int):
        servo_mode = Base_pb2.ServoingModeInformation()
        servo_mode.servoing_mode = mode
        self.connection.client.SetServoingMode(servo_mode)

    def stop(self):
        self.connection.client.Stop()

    def pause(self):
        self.connection.client.PauseAction()

    def resume(self):
        self.connection.client.ResumeAction()

    def emergency_stop(self):
        self.connection.client.ApplyEmergencyStop()

    def clear_faults(self):
        self.connection.client.ClearFaults()

    def home(self, wait: bool = True):
        self.connection.execute_existing_action('Home', Base_pb2.REACH_JOINT_ANGLES, wait=wait)

    def set_tool(self, offset: Location, mass_kg: float):
        tool_transform = ControlConfig_pb2.CartesianTransform
        tool_transform.x = offset.x
        tool_transform.y = offset.y
        tool_transform.z = offset.z
        tool_transform.theta_x = offset.rx
        tool_transform.theta_y = offset.ry
        tool_transform.theta_z = offset.rz

        tool_config = ControlConfig_pb2.ToolConfiguration()
        tool_config.tool_transform = tool_transform
        tool_config.tool_mass = mass_kg

        self.connection.control_client.SetToolConfiguration(tool_config)

    def wait(self, timeout: Optional[float] = None):
        self.connection.wait_for_action_end(timeout)

    def move_to_location(self, location: Location,
                         velocity: Optional[float] = None, acceleration: Optional[float] = None, frame: Optional[Frame] = None,
                         relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        if velocity is not None and velocity > self.max_velocity:
            raise robot_arms.RobotArmInvalidVelocityError(f'Invalid velocity: {velocity} m/s, must be less than {self.max_velocity} m/s')

        if frame is not None:
            raise robot_arms.RobotArmNotSupportedError(f'Frame parameter not supported')

        action = Base_pb2.Action()

        target_pose = action.reach_pose.target_pose
        location_m = location.convert_mm_to_m() if self.position_units == Units.MILLIMETERS else location.copy()
        current_location = self.location.convert_mm_to_m() if self.position_units == Units.MILLIMETERS else self.location.copy()

        if relative:
            location_m.position += current_location.position
            location_m.orientation += current_location.orientation

        target_pose.x = location_m.x
        target_pose.y = location_m.y
        target_pose.z = location_m.z
        target_pose.theta_x = location_m.rx
        target_pose.theta_y = location_m.ry
        target_pose.theta_z = location_m.rz

        velocity = self.default_velocity if velocity is None else velocity
        action.reach_pose.constraint.speed.translation = velocity / 1000.0

        self.connection.execute_action(action, wait=wait, timeout=timeout)

    def move_to_locations(self, *locations: Location,
                          velocity: Optional[float] = None, acceleration: Optional[float] = None,
                          relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        for location in locations:
            self.move_to_location(location, velocity=velocity, acceleration=acceleration,
                                  relative=relative, wait=wait, timeout=timeout)

    def move_joints(self, joint_positions: List[float],
                    velocity: Optional[float] = None, acceleration: Optional[float] = None,
                    relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        if len(joint_positions) != self.joint_count:
            raise robot_arms.RobotArmInvalidJointsError(f'Invalid number of joint angles ({len(joint_positions)}), must be {self.joint_count}')

        action = Base_pb2.Action()

        joint_offsets = self.joint_positions if relative else [0] * self.joint_count

        for joint_id in range(self.joint_count):
            joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
            joint_angle.joint_identifier = joint_id
            joint_angle.value = joint_offsets[joint_id] + joint_positions[joint_id]

        if velocity is not None:
            action.reach_joint_angles.constraint.type = Base_pb2.JOINT_CONSTRAINT_SPEED
            action.reach_joint_angles.constraint.value = velocity

        self.connection.execute_action(action, wait=wait, timeout=timeout)

    def move_joint(self, joint_id: int, position: float,
                      velocity: Optional[float] = None, acceleration: Optional[float] = None,
                      relative: bool = False, wait: bool = True, timeout: Optional[float] = None):
        action = Base_pb2.Action()

        joint_offset = self.joint_positions[joint_id] if relative else 0
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint_id
        joint_angle.value = joint_offset + position

        if velocity is not None:
            action.reach_joint_angles.constraint.type = Base_pb2.JOINT_CONSTRAINT_SPEED
            action.reach_joint_angles.constraint.value = velocity

        self.connection.execute_action(action, wait=wait, timeout=timeout)

    def move_twist(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, rx: float = 0.0, ry: float = 0.0, rz: float = 0.0,
                   duration: Optional[float] = None, wait: bool = True, timeout: Optional[float] = None):
        action = Base_pb2.Action()
        twist_command = action.send_twist_command
        twist_command.reference_frame = Base_pb2.CARTESIAN_REFERENCE_FRAME_TOOL
        twist_command.twist.linear_x = x
        twist_command.twist.linear_y = y
        twist_command.twist.linear_z = z
        twist_command.twist.angular_x = rx
        twist_command.twist.angular_y = ry
        twist_command.twist.angular_z = rz

        self.connection.execute_action(action, timeout=timeout, wait=(wait and duration is None))

        if duration is not None:
            time.sleep(duration)
            self.stop()

    def move_twist_to(self, twist: Twist, duration: Optional[float] = None, wait: bool = True, timeout: Optional[float] = None):
        self.move_twist(**twist.dict, duration=duration, wait=wait, timeout=timeout)

    def wait_for_gripper_stop(self, timeout: Optional[float] = None):
        self.gripper.wait_for_stop(timeout)

    def open_gripper(self, position: Optional[Union[float, bool]] = None, force: Optional[float] = None, velocity: Optional[float] = None,
                     wait: bool = True, timeout: Optional[float] = None):
        if position is None:
            position = 0.0
        elif isinstance(position, bool):
            position = 0.0 if position else 1.0

        self.gripper.move(position, force=force or self.gripper_default_force, velocity=velocity or self.gripper_default_velocity, timeout=timeout or 10.0)
