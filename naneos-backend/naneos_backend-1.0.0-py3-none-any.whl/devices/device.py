import datetime
import threading

import pandas
import numpy
from pytz import UTC


class Device:
    # empty methods -> have to be implemented on connection base
    def _read_device_raw(self) -> list:
        pass

    def send_cmd(self, cmd: str):
        pass

    def send_cmd_with_answer(self, cmd: str) -> None:
        pass

    ####################################################################################
    IDX = ["template_idx"]  # this is changed on specific device level

    def __init__(self) -> None:
        self._name = "template_device"
        self._initialized = False

        self.__thread_active = False
        self.__thread_lock = False
        self.__thread_data = pandas.DataFrame(columns=self.IDX)

    ####################################################################################
    # read data from device
    def read_device(self) -> pandas.Series:
        raw_list = self._read_device_raw()
        timestamp = datetime.datetime.now(UTC)

        if self._check_raw_reading(raw_list):
            float_values = numpy.asarray(raw_list, dtype=numpy.float32, order="C")
            return pandas.Series(float_values, name=timestamp, index=self.IDX)

        return None

    def _check_raw_reading(self, raw_list: list) -> bool:
        return len(self.IDX) == len(raw_list)

    ####################################################################################
    # threading part
    def start_thread(self):
        if not self.__thread_active:
            self.__thread_active = True
            thread = threading.Thread(target=self.__thread, daemon=True)

            thread.start()

    def stop_thread(self):
        self.__thread_active = False

    def _wait_for_thread_lock(self) -> None:
        while self.__thread_lock:
            pass

    def __thread(self):
        while self.__thread_active:
            df = self.read_device()

            if df is not None:
                self._wait_for_thread_lock()

                self.__thread_lock = True
                self.__thread_data = self.__thread_data.append(df)
                self.__thread_lock = False

    def get_and_clean_thread_data(self) -> pandas.DataFrame:
        self._wait_for_thread_lock()

        self.__thread_lock = True
        df = self.__thread_data.copy()
        self.__thread_data = pandas.DataFrame(columns=self.IDX)
        self.__thread_lock = False

        return df
