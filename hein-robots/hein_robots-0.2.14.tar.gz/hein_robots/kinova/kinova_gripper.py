import time
from hein_robots.base import robot_arms
from hein_robots.kinova.kortex import KortexConnection
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2


class KinovaGripper:
    def __init__(self, connection: KortexConnection):
        self.connection = connection

    @property
    def feedback(self):
        return self.connection.cyclic_client.RefreshFeedback()

    @property
    def gripper_feedback(self):
        return self.feedback.interconnect.gripper_feedback

    @property
    def position(self):
        return self.gripper_feedback.motor[0].position

    @property
    def velocity(self):
        return self.gripper_feedback.motor[0].velocity

    def move(self, position: float, velocity: float, force: float, timeout: float = 10.0):
        # grab the current servoing mode so we can reset it after the move
        old_servoing_mode = self.connection.client.GetServoingMode()
        servoing_mode_info = Base_pb2.ServoingModeInformation()
        servoing_mode_info.servoing_mode = Base_pb2.LOW_LEVEL_SERVOING
        self.connection.client.SetServoingMode(servoing_mode_info)

        command = BaseCyclic_pb2.Command()

        # command gripper to move to position with given velocity and force
        motor_command = command.interconnect.gripper_command.motor_cmd.add()
        motor_command.position = position * 100.0
        motor_command.velocity = velocity * 100.0
        motor_command.force = force * 100.0

        # command all the actuators to hold the current position
        for actuator in self.feedback.actuators:
            actuator_command = command.actuators.add()
            actuator_command.position = actuator.position
            actuator_command.velocity = 0.0
            actuator_command.torque_joint = 0.0

        # send command
        self.connection.cyclic_client.Refresh(command)

        # we always wait for a stop so we can reset the servoing mode
        self.wait_for_stop(timeout)
        self.connection.client.SetServoingMode(old_servoing_mode)

    def wait_for_stop(self, timeout: float = 10.0):
        last_pos = self.position
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(0.1)
            current_pos = self.position

            if current_pos == last_pos:
                return

            last_pos = current_pos

        raise robot_arms.RobotArmGripperTimeoutError(f'Timeout while waiting for gripper to stop')
