from ..commands import cmd_dataclass

get_device_number = cmd_dataclass("N?", "Asks for the serial number of the device.")
get_hv_state = cmd_dataclass("O?", "Returns the state of the HV module.")
set_hv_on = cmd_dataclass("O0001!", "Activates hv. Device must have air flow!")
set_hv_off = cmd_dataclass("O0000!", "Deactivates hv.")
set_read_freq_0_Hz = cmd_dataclass("X0000!", "Cyclic readout off.")
set_read_freq_1_Hz = cmd_dataclass("X0001!", "Cyclic readout 1 Hz.")
set_read_freq_10_Hz = cmd_dataclass("X0002!", "Cyclic readout 10 Hz.")
set_read_freq_100_Hz = cmd_dataclass("X0003!", "Cyclic readout 100 Hz.")
