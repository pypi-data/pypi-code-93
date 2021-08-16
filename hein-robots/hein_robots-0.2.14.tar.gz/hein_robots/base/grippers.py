from typing import Union
from hein_robots.base.actuators import Actuator


class Gripper(Actuator):
    @property
    def is_open(self) -> bool:
        return self.position < 0.5

    @property
    def is_closed(self) -> bool:
        return not self.is_open

    def open(self, position: Union[float, bool] = True):
        if isinstance(position, bool):
            return self.move(1.0 if position else 0.0)

        self.move(position)

    def close(self, position: Union[float, bool] = False):
        if isinstance(position, bool):
            return self.open(not position)

        self.open(position)
