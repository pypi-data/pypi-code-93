from ..serial_device import SerialDevice
from naneos_backend.logger import logger
from naneos_backend.commands.src import silent_pump_cmd as sp_cmd



class SilentPump(SerialDevice):
    def __init__(
        self, com_port: str = None, baud: int = 115200, scanning=False
    ) -> None:
        super().__init__(com_port, baud)

        if self._check_for_silent_pump(scanning):
            logger.debug(f"Initialized {self._name} on {self._port}")
        else:
            if scanning is False:
                logger.error(f"Pump on {com_port} could not be initialized.")

    ####################################################################################
    def _check_for_silent_pump(self, scanning=False):
        if self._open_port():
            self.send_cmd(sp_cmd.set_read_freq_0_Hz.cmd)
            self._serial.flushInput()

            name = self._get_info_from_pump(sp_cmd.get_device_description.cmd)
            if name == "silent_pump":
                serial_number = self._get_info_from_pump(sp_cmd.get_serial_number.cmd)
                try:
                    if serial_number == "":
                        raise ValueError()
                    serial_number = int(serial_number)
                except ValueError:
                    if scanning is False:
                        logger.warning(f"pump-ser sn wrong format. ({serial_number})")
                    self._close_port()
                    return self._initialized

                self._serial_number = serial_number
                self._name = "silent-pump-serial"
                self._initialized = True
            else:
                self._close_port()
                if scanning is False:
                    logger.warning(f"Bad communication on port {self._port}")

        return self._initialized

    ####################################################################################
    def _get_info_from_pump(self, cmd):
        info = self.send_cmd_with_answer(cmd)
        info = info.replace(" ", "").replace("\r", "").replace("\n", "")
        info = info.replace("INFO:\t", "")
        info = info.split(":")[-1]
        return info

    def _separate_line_to_list(self, raw_line: str) -> list:
        line = raw_line.replace("\n", "").replace("\r", "").replace("\x00", "")
        return line.split("\t")

    def _close_port(self) -> None:
        if self._serial.isOpen():
            self.send_cmd(sp_cmd.set_read_freq_0_Hz.cmd)

            logger.debug(f"Closed connection to {self._name} on {self._port}")
            return super()._close_port()

    ####################################################################################
    IDX = [
        "total_min",
        "voltage_V",
        "current_mA",
        "power_mW",
        "temperature_C",
        "setpoint",
        "flow_ml",
        "frequency_Hz",
    ]
