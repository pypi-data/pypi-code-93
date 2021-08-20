import serial.tools.list_ports


def show_port_info():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        print("******************************************************************************************")
        print(f"Description: {p.description}")
        print(f"     >>> serial.Serial(serial_info.info.grab_with_description(""arduino"")")
        print(f"Device: {p.device}")
        print(f"HWID: {p.hwid}")
        print(f"     >>> serial.Serial(serial_info.info.grab_with_hwid(1234)")
        print(f"Interface: {p.interface}")
        print(f"Manufacturer: {p.manufacturer}")
        print(f"Name: {p.name}")
        print(f"VID: {p.vid}")
        print(f"PID: {p.pid}")
        print(f"     >>> serial.Serial(serial_info.info.grab_with_vid_pid(1111, 1111)")
        print(f"Product: {p.product}")
        print(f"Serial Number: {p.serial_number}")

    if len(ports) == 0:
        print("There are no devices connected to com ports.")
    else:
        print("******************************************************************************************")


def grab_with_vid_pid(vid, pid):
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if p.vid == vid and p.pid == pid:
            return p.device
        else:
            raise RuntimeError(f"Could not find serial port with the vid:pid {vid}{pid}")


def grab_with_description(description):
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if p.description == description:
            return p.device
        else:
            raise RuntimeError(f"Could not find serial port with the description {description}")


def grab_with_serial_number(serial_number):
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if p.serial_number == serial_number:
            return p.device
        else:
            raise RuntimeError(f"Could not find serial port with the serial_number {serial_number}")