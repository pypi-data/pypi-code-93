from pick import pick

from evdev import InputDevice, list_devices
from asterisk_doorphone.usb_keyboard import UsbKeyboard


def select_device():
    devices = [InputDevice(device) for device in list_devices()]
    option, index = pick(devices, 'Please select the device to use as keyboard: ')
    return option.path


def main():
    try:
        doorphone = UsbKeyboard()
        device_path = select_device()
        doorphone.get_exclusive_access_to_keyboard(device_path)
    except (FileNotFoundError, IOError) as error:
        print(error)
    else:
        numbers = {}
        while True:
            print("Press a button on the asterisk_doorphone keypad.")
            code = doorphone.get_keycode()
            num = input("Enter the number for the key code {code}: ".format(code=code))
            numbers[str(code)] = num
            if input("will you configure another key? (y)/n: ") == "n":
                break

        with open("./apartments.py", "w") as file:
            file.write('numbers = {\n')
            for key, value in numbers.items():
                file.write('"{code}": "{number}",\r\n'.format(code=key, number=value))
            file.write('}\n')


if __name__ == "__main__":
    import sys
    sys.exit(main())
