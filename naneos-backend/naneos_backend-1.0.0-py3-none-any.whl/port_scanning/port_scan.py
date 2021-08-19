from naneos_backend.port_scanning.device_mapping import DeviceMapping
from serial.tools import list_ports
from naneos_backend.logger import logger
from .scan_devices import scan_p2, scan_silent_pump, scan_defender


class PortScan:
    def __init__(self, devices_to_scan: list = []) -> None:
        self._devices = []

        # fetching all free ports from system (tested on linux and windows)
        self._free_ports = []
        for p in list(list_ports.comports()):
            if p.device != "/dev/ttyAMA0":  # raspi bluetooth port
                self._free_ports.append(p.device)

        if len(self._free_ports) != 0:
            logger.debug(f"Possible COM-Ports: {self._free_ports}")
        else:
            logger.error("There are no active COM-Ports.")
            exit()

        if devices_to_scan == []:
            devices_to_scan = ["P2", "silent_pump", "defender"]

        for d in devices_to_scan:
            self._scan_for_device(device_name=d)

        self.log_possible_devices()

    def _scan_for_device(self, device_name: str):
        if device_name == "P2":
            for p in self._free_ports:
                device = scan_p2(com_port=p)
                if type(device) == DeviceMapping:
                    self._devices.append(device)
                    self.remove_port_from_list(p)

        elif device_name == "silent_pump":
            for p in self._free_ports:
                device = scan_silent_pump(com_port=p)
                if type(device) == DeviceMapping:
                    self._devices.append(device)
                    self.remove_port_from_list(p)

        elif device_name == "defender":
            for p in self._free_ports:
                device = scan_defender(com_port=p)
                if type(device) == DeviceMapping:
                    self._devices.append(device)
                    self.remove_port_from_list(p)

        # scan routine for choosen device
        # if device was found create object and remove from free_ports list

    def log_possible_devices(self):
        log_line = "\n"
        log_line += DeviceMapping.get_header_str()
        for p in self._devices:
            log_line += p.get_specs_str()

        logger.info(log_line)

    def remove_port_from_list(self, port: str):
        try:
            self._free_ports.remove(port)
        except ValueError:
            logger.error("Given port not in port list.")

    def get_p2_com_port(self):
        for p in self._devices:
            if p.name == "P2":
                return p.port

        return None

    def get_silent_pump_port(self):
        for p in self._devices:
            if p.name == "silent_pump":
                return p.port

        return None

    def get_defender_port(self):
        for p in self._devices:
            if p.name == "defender":
                return p.port

        return None
