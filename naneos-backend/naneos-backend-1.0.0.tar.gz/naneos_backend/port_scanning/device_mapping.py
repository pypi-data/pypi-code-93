from dataclasses import dataclass


@dataclass
class DeviceMapping:
    name: str = None
    serial_number: int = None
    port: str = None

    @staticmethod
    def get_header_str():
        line1 = f'{"detected devices":^45s}\n'
        line2 = f'{"-"*45}\n'
        line3 = f'{"device":<15s}{"serial number":<15s}{"port":<15s}\n'
        line4 = f'{"="*45}\n'

        return line1 + line2 + line3 + line4

    def get_specs_str(self):
        return f"{self.name:<15s}{self.serial_number:<15d}{self.port:<15s}\n"
