from typing import Optional


class Actuator:
    @property
    def position(self) -> float:
        return 0.0

    @position.setter
    def position(self, value: float):
        pass

    def move(self, position: float, velocity: Optional[float] = None, acceleration: Optional[float] = None,
             relative: bool = False, wait: bool = True):
        pass


class PneumaticActuator(Actuator):
    pass


class RotaryActuator(Actuator):
    @property
    def position_degrees(self) -> float:
        return 0.0

    @position_degrees.setter
    def position_degrees(self, degrees: float):
        pass

    def move_degrees(self, degrees: float, velocity_degrees: Optional[float] = None,
                     acceleration_degrees: Optional[float] = None,
                     relative: bool = False, wait: bool = True):
        pass


class LinearActuator(Actuator):
    @property
    def position_mm(self) -> float:
        return 0.0

    @position_mm.setter
    def position_mm(self, mm: float):
        pass

    def move_mm(self, mm: float, velocity_mm: Optional[float] = None, acceleration_mm: Optional[float] = None,
                relative: bool = False, wait: bool = True):
        pass