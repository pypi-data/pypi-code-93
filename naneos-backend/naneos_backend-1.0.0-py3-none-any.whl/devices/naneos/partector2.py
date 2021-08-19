from ..serial_device import SerialDevice
from naneos_backend.logger import logger
from naneos_backend.commands.src import p2_cmd


class Partector2(SerialDevice):
    def __init__(self, com_port: str, baud: int = 9600, scanning=False) -> None:
        super().__init__(com_port, baud)

        if self._check_for_p2(scanning):  # enter this when device is detected
            self.send_cmd(p2_cmd.set_read_freq_0_Hz.cmd)
            self._serial.flushInput()
            logger.debug(f"Initialized {self._name} on {self._port}.")
        else:
            if scanning is False:
                logger.error(f"P2 on ({com_port}) could not be initialized.")

    ####################################################################################
    def _check_for_p2(self, scanning=False):
        if self._open_port():
            serial_number = self.send_cmd_with_answer(p2_cmd.get_device_number.cmd)

            try:
                if serial_number == "":
                    raise ValueError()
                serial_number = int(serial_number)
            except ValueError:
                if scanning is False:
                    logger.warning(f"P2-serial number wrong format. ({serial_number})")
                self._close_port()
                return self._initialized

            self._serial_number = serial_number
            self._name = f"P2-serial"
            self._initialized = True

        return self._initialized

    ####################################################################################
    def _separate_line_to_list(self, raw_line: str) -> list:
        line = raw_line.replace("\n", "").replace("\r", "").replace("\x00", "")
        return line.split("\t")

    def _close_port(self) -> None:
        if self._serial.isOpen():
            self.send_cmd(p2_cmd.set_read_freq_0_Hz.cmd)

            logger.debug(f"Closed connection to {self._name} on {self._port}")
            super()._close_port()

    ####################################################################################
    IDX = [
        "RunningTime_sec",
        "Diff_nA",
        "HvModule_V",
        "ElectroMeter1_mV",
        "ElectroMeter2_mV",
        "ElectroMeter1_mA",
        "ElectroMeter2_mA",
        "Temperature_Celsius",
        "RelativeHumidity_percent",
        "Status",
        "Precipitator_V",
        "Battery_V",
        "Flow_lpm",
        "LDSA",
        "Diameter_nm",
        "Number_perCm3",
        "DifferentialPressure_Pa",
        "AmbientPressure_mbar",
        "Lag",
    ]
