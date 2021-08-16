from venturi import MachineMotionController


class VentionGantry:
    def __init__(self, host: str = '192.168.7.2', port: int = 9999, axis: int = 1):
        self.controller = MachineMotionController(host, port)
        self.axis = axis
        self.controller.wait_for_ready()

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def emergency_stop(self):
        pass

    def clear_faults(self):
        pass

    def wait(self):
        self.controller.wait_for_motion_completed()

    @property
    def position(self) -> int:
        return self.controller.get_position(self.axis)

    def home(self):
        self.controller.home_all()

    def move_relative(self, position_mm: float, wait: bool = True):
        self.controller.move_relative(self.axis, round(position_mm), wait=wait)

    def move_absolute(self, position_mm: float, wait: bool = True):
        self.controller.move_absolute(self.axis, round(position_mm), wait=wait)
