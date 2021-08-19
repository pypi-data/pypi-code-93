from ..commands import cmd_dataclass

get_device_description = cmd_dataclass("?D\r\n", "Returns silent_pump.")
get_serial_number = cmd_dataclass("?N\r\n", "Returns the devices serial number.")
set_read_freq_0_Hz = cmd_dataclass("-v 0\r\n", "Sets readout freq. to 0 Hz.")
set_read_freq_1_Hz = cmd_dataclass("-v 1\r\n", "Sets readout freq. to 1 Hz.")
set_read_freq_10_Hz = cmd_dataclass("-v 10\r\n", "Sets readout freq. to 10 Hz.")
set_read_freq_100_Hz = cmd_dataclass("-v 100\r\n", "Sets readout freq. to 100 Hz.")
