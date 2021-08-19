from ..serial_device import SerialDevice
from naneos_backend.logger import logger
import datetime
import numpy
import pandas
from pytz import UTC


class Defender510(SerialDevice):
    def __init__(self, com_port: str = None, baud: int = 9600, scanning=False) -> None:
        super().__init__(com_port, baud)
        self._timeout = 5

        if self._check_for_defender():
            logger.debug(f"Initialized {self._name} on {self._port}")
        else:
            if scanning is False:
                logger.error(f"Defender on ({com_port}) could not be initialized.")

    ####################################################################################
    def _check_for_defender(self):
        if self._open_port():
            self._serial.flushInput()

            line_list = self._read_device_raw()
            if len(line_list) == 32:
                if line_list[2] == "mL/min":
                    self._initialized = True
                    self._name = "Defender 510"
                    self._serial_number = 0

                else:
                    self._initialized = False
                    self._close_port()
            else:
                self._initialized = False
                self._close_port()

        return self._initialized


    ####################################################################################
    def _separate_line_to_list(self, raw_line: str) -> list:
        line = raw_line.replace("\n", "").replace("\r", "").replace("\x00", "")
        return line.split(",")

    def _close_port(self) -> None:
        if self._serial.isOpen():
            logger.debug(f"Closed connection to {self._name} on {self._port}")
            super()._close_port()

    # override
    def read_device(self) -> pandas.Series:
        raw_list = self._read_device_raw()
        timestamp = datetime.datetime.now(UTC)

        if len(raw_list) == 32:
            raw_list = [raw_list[0]]
        else:
            return None

        if self._check_raw_reading(raw_list):
            float_values = numpy.asarray(raw_list, dtype=numpy.float32, order="C")
            return pandas.Series(float_values, name=timestamp, index=self.IDX)

        return None

    ####################################################################################
    IDX = ["flow_ml"]
