from typing import Optional, Any, Dict
import logging
import socket
import threading
import time

logger = logging.getLogger(__name__)


class RobotiqGripper:
    STATUS_RESET = 0
    STATUS_ACTIVATING = 1
    STATUS_ACTIVE = 3

    def __init__(self, host: str, base_port: int = 63352, id: int = 1, timeout: float = 2.0, connect: bool = True):
        self.logger = logger.getChild(self.__class__.__name__)
        self.host = host
        self.port = base_port + id - 1  # convert gripper id to port number, id 1 starts at 63352
        self.timeout = timeout
        self.connection: Optional[socket.socket] = None

        if connect:
            self.connect()

    @property
    def connected(self) -> bool:
        return self.connection is not None

    @property
    def status(self) -> int:
        return int(self.get_register('STA'))

    @property
    def active(self) -> bool:
        return self.status == self.STATUS_ACTIVE

    @property
    def position_int(self) -> int:
        return int(self.get_register('POS'))

    @property
    def position(self) -> float:
        return self.position_int / 255.0

    def connect(self):
        if self.connection:
            return

        self.logger.debug(f'Connecting to Robotiq gripper at {self.host}:{self.port}')
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((self.host, self.port))
        self.connection.settimeout(self.timeout)
        self.logger.info(f'Connected to Robotiq gripper at {self.host}:{self.port}')

    def disconnect(self):
        self.logger.info(f'Disconnecting from Robotiq gripper at {self.host}:{self.port}')
        self.connection.close()
        self.connection = None

    def request(self, request: bytes) -> bytes:
        self.logger.debug(f'Sending gripper request: {request}')
        self.connection.send(request + b'\n')
        response = self.connection.recv(1024)
        self.logger.debug(f'Gripper response: {response}')
        return response

    def set_registers(self, registers: Dict[str, Any]):
        self.logger.debug(f'Setting grippper registers {registers}')
        command = 'SET ' + ' '.join([f'{name} {val}' for name, val in registers.items()])
        response = self.request(command.encode())

        if response != b'ack':
            raise RobotiqGripperSetError(f'Error setting registers, no ack received (response: {response})')

    def get_register(self, name: str) -> bytes:
        response = self.request(f'GET {name}'.encode())

        if not response.startswith(f'{name} '.encode()):
            raise RobotiqGripperInvalidResponseError(f'Invalid response: {response}')

        return response[len(name) + 1:].strip()

    def activate(self, wait: bool = True, timeout: float = 2.0, force: bool = False):
        if self.active and not force:
            return

        # clear and set activation register (resets faults)
        self.set_registers({'ACT': 0})
        self.set_registers({'ACT': 1})

        if not wait:
            return

        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.active:
                return

            time.sleep(0.01)

        raise RobotiqGripperTimeoutError(f'Timeout while waiting for gripper to activate')

    def move(self, position: float, force: float = 0.5, velocity: float = 0.5, wait: bool = True, timeout: float = 10.0):
        if position < 0 or position > 1:
            raise RobotiqGripperInvalidPositionError(f'Invalid position, must be float between 0 and 1: {position}')

        if force < 0 or force > 1:
            raise RobotiqGripperInvalidForceError(f'Invalid force, must be float between 0 and 1: {force}')

        if velocity < 0 or velocity > 1:
            raise RobotiqGripperInvalidSpeedError(f'Invalid speed, must be float between 0 and 1: {force}')

        position_int = round(position * 255)
        force_int = round(force * 255)
        velocity_int = round(velocity * 255)

        self.set_registers({'POS': position_int, 'SPE': velocity_int, 'FOR': force_int, 'GTO': 1})

        if wait:
            time.sleep(0.1)
            self.wait_for_stop(timeout)

    def wait_for_stop(self, timeout: float = 10.0):
        last_pos = self.position_int
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(0.1)
            current_pos = self.position_int

            if current_pos == last_pos:
                return

            last_pos = current_pos

        raise RobotiqGripperTimeoutError(f'Timeout while waiting for gripper to stop')

    def open(self, force: Optional[float] = None, velocity: Optional[float] = None, wait: bool = True, timeout: float = 10.0):
        self.move(0, force=force, velocity=velocity, wait=wait, timeout=timeout)

    def close(self, force: Optional[float] = None, velocity: Optional[float] = None, wait: bool = True, timeout: float = 10.0):
        self.move(1, force=force, velocity=velocity, wait=wait, timeout=timeout)


class RobotiqGripperError(Exception):
    pass


class RobotiqGripperSetError(RobotiqGripperError):
    pass


class RobotiqGripperConnectionError(RobotiqGripperError):
    pass


class RobotiqGripperInvalidResponseError(RobotiqGripperError):
    pass


class RobotiqGripperInvalidForceError(RobotiqGripperError):
    pass


class RobotiqGripperInvalidSpeedError(RobotiqGripperError):
    pass


class RobotiqGripperInvalidPositionError(RobotiqGripperError):
    pass


class RobotiqGripperTimeoutError(RobotiqGripperError):
    pass