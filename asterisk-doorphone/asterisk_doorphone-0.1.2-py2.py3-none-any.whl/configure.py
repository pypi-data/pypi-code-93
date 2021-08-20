from pick import pick

from evdev import InputDevice, list_devices


def select_device():
    devices = [InputDevice(device) for device in list_devices()]
    option, index = pick(devices, 'Please select the device to use as keyboard: ')
    return option.path


def main():
    config = {
        "DEVICE_PATH": select_device(),
        "SERVER_IP": input("Please enter the AsteriskPBX server address [127.0.0.1]: ") or "127.0.0.1",
        "SERVER_PORT": int(input("Enter the AsteriskPBX AMI port number [5038]: ") or 5038),
        "AMI_USERNAME": input("Enter the AMI Username: "),
        "AMI_PASSWORD": input("Enter the AMI Password: "),
        "DOORPHONE_EXTENSION": input("Enter the asterisk_doorphone extension [asterisk_doorphone]: "
                                     or "asterisk_doorphone"),
        "DOORPHONE_CALLER_ID": input("Enter the asterisk_doorphone caller ID [Doorphone]: ") or "Doorphone",
        "DOORPHONE_CONTEXT": input("Enter the asterisk_doorphone context [from-internal]: ") or "from-internal",
        "DOORPHONE_TECH": input("Enter the asterisk_doorphone tech (SIP/IAX2/LOCAL) [SIP]: ") or "SIP",
        "ORIGINATE_CONTEXT": input("Enter the context from which the call will be made [from-internal]: ")
                                   or "from-internal",
    }

    with open("./config.py", "w") as file:
        for key, value in config.items():
            if (isinstance(value, int)):
                file.write('{} = {}\r\n'.format(key, value))
            else:
                file.write('{} = "{}"\r\n'.format(key, value))


if __name__ == "__main__":
    import sys
    sys.exit(main())
