"""
ST-Link CLI Interface

The MIT License (MIT)

Copyright (c) 2016 mtchavez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Changes Made by SensiML corporation to create STLinkFlasher Class
Changes Copyright (c) 2019 SensiML Corporation
"""

import re
import subprocess
from typing import List
from pathlib import Path
from sensiml.device_flashing import DeviceFlasher


class STDeviceFlasher(DeviceFlasher):
    def __init__(self):
        super(STDeviceFlasher, self).__init__()
        self._name = "StLink Flasher"
        self._flash_methods = ["ST-Link SWD", "ST-Link JTAG"]
        self._supported_platforms = ["STMicro SensorTile"]
        self._needs_scan = True
        self._description = (
            "Flash Knowledge Pack binaries on STMicro Devices using ST-LINK_CLI"
        )

    @property
    def programmers(self):
        return self._programmers

    def flash(self, bin_file_path: Path, probe: int = 0, method: str = "SWD"):
        """
        Flashes microcontroller.

        The method flashes mcu using ST-Link Utility's CLI interface.
        To keep things simple most of the flags are hardcoded.

        Args:
            bin_file_path: Path of the hex file that will be used to flash the mcu
            probe: the probe number of the ST-Link programmer. Default is zero.
            method: Choose JTAG or SWD

        Returns:
            flash_status: Either 'successful' or 'failed'
            checksum: the hex file checksum provided by ST-Link Utility CLI.
                It will be zero if programming fails.
        """
        abs_path = bin_file_path.absolute()
        if "SWD" in method.upper():
            st_link_method = "SWD"
        elif "JTAG" in method.upper():
            st_link_method = "JTAG"
        print(method.lower())
        if "st-link" in method.lower():
            command = [
                "ST-LINK_CLI -c ID={0} {1} UR Hrst -Q -P {2} 0x08000000 -HardRST HIGH -Rst".format(
                    probe, st_link_method, abs_path
                )
            ]
            self._wait_for_process(command)
