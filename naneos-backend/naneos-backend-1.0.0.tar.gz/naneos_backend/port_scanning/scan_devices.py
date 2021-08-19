from naneos_backend.devices.naneos.partector2 import Partector2
from naneos_backend.devices.naneos.silentPump import SilentPump
from naneos_backend.devices.third_party.defender import Defender510
from .device_mapping import DeviceMapping


def scan_p2(com_port: str):
    p2 = Partector2(com_port=com_port, scanning=True)
    p2._close_port()

    if p2._initialized:
        return DeviceMapping(name="P2", serial_number=p2._serial_number, port=com_port)
    else:
        return False


def scan_silent_pump(com_port: str):
    sp = SilentPump(com_port=com_port, scanning=True)
    sp._close_port()

    if sp._initialized:
        return DeviceMapping(
            name="silent_pump", serial_number=sp._serial_number, port=com_port
        )
    else:
        return False


def scan_defender(com_port: str):
    defender = Defender510(com_port=com_port, scanning=True)
    defender._close_port()

    if defender._initialized:
        return DeviceMapping(
            name="defender", serial_number=defender._serial_number, port=com_port
        )
    else:
        return False
