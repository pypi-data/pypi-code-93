from sensiml.device_flashing import DeviceFlasher
from pathlib import Path


class NordicThingyFlasher(DeviceFlasher):
    def __init__(self):
        super(NordicThingyFlasher, self).__init__()
        self._name = "Nordic nrfjprog flasher"
        self._flash_methods = ["J-Link"]
        self._programmers = None
        self._supported_platforms = ["Nordic Thingy"]
        self._needs_scan = False
        self._description = "Flash Knowledge Pack binaries on Nordic devices using nrfutils' nrfjprog J-Link utility."
        self._flash_file_ext = ".hex"

    @property
    def programmers(self):
        return self._programmers

    @staticmethod
    def refresh_programmers_list():
        print(
            "Nordic programmer uses NRFJprog, and does not need to scan for programmers."
        )

    @staticmethod
    def _find_all_probes():
        return list()

    def flash(self, hex_file_path: Path, probe: int = 0, method: str = ""):
        """
        Flashes microcontroller.

        The method flashes mcu using ST-Link Utility's CLI interface.
        To keep things simple most of the flags are hardcoded.

        Args:
            hex_file_path: Path of the hex file that will be used to flash the mcu
            probe: unused for Nordic

        Returns:
            flash_status: Either 'successful' or 'failed'
            checksum: the hex file checksum provided by ST-Link Utility CLI.
                It will be zero if programming fails.
        """
        abs_path = hex_file_path.absolute()
        programming_command = [
            "nrfjprog --program {} -f nrf52 --sectorerase && nrfjprog --reset -f nrf52".format(
                abs_path
            )
        ]
        self._wait_for_process(programming_command)
