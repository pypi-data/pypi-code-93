import serial.tools.list_ports


def show_port_info():
    ports = serial.tools.list_ports.comports()

    for p in ports:
        print("******************************************************************************************")
        print(f"Description: {p.description}")

        print(f"Device: {p.device}")
        print(f"HWID: {p.hwid}")
        print(f"Interface: {p.interface}")
        print(f"Manufacturer: {p.manufacturer}")
        print(f"Name: {p.name}")
        print(f"VID: {p.vid}")
        print(f"PID: {p.pid}")
        print(f"Product: {p.product}")
        print(f"Serial Number: {p.serial_number}")
        print("")
        print("To connect to your device, use one of the following code examples:")
        print(f'     >>> import serial')
        print(f'     >>> ser = serial.Serial(serial_info.info.grab_with_description("{p.description}"))')
        print("")
        print(f'     >>> import serial')
        print(f"     >>> ser = serial.Serial(serial_info.info.grab_with_vid_pid({p.vid}, {p.pid}))")
        print("")
        print(f'     >>> import serial')
        print(f'     >>> ser = serial.Serial(serial_info.info.grab_with_serial_number("{p.serial_number}"))')

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
            raise RuntimeError(f"Could not find serial port with the vid:pid {vid}{pid}.")


def grab_with_description(description, exact_match=False):
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if exact_match is False:
            if description in p.description:
                return p.device
            else:
                raise RuntimeError(f"Could not find serial port with {description} in the description.")
        else:
            if description == p.description:
                return p.device
            else:
                raise RuntimeError(f"Could not find serial port with the exact description {description}")


def grab_with_serial_number(serial_number):
    ports = serial.tools.list_ports.comports()

    for p in ports:
        if p.serial_number == serial_number:
            return p.device
        else:
            raise RuntimeError(f"Could not find serial port with the serial_number {serial_number}.")