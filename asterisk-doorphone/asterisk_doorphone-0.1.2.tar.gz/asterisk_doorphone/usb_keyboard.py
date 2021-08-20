import time

from evdev import InputDevice, ecodes

from asterisk_doorphone.asterisk_ami import AsteriskAMI


class UsbKeyboard:
    def __init__(self, apartments=None, config=None):
        self.apartments = apartments
        self.ami = None
        self.config = config
        self.device = None

    def get_exclusive_access_to_keyboard(self, path: str):
        """assign the device in <path> to use as keyboard"""
        self.device = InputDevice(path)
        self.device.grab()

    def get_keycode(self):
        """returns the keycode from a push down event in the keyboard"""
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                print("-- Event code: ", event.code)
                return str(event.code)

    def get_apartment_number(self):
        """Returns a string with the apartment extension number"""
        code = self.get_keycode()
        if code in self.apartments.numbers:
            return str(self.apartments.numbers[code])
        else:
            print("The apartment for the code {code} does not exist".format(code=code))
            return None

    def is_available(self, extension: str):
        """Check if the asterisk_doorphone extension it's available"""
        response = self.ami.sip_peer_status(extension)
        return True if "PeerStatus: Reachable" in response else False

    def call_apartment(self, extension: str):
        """
        If the asterisk_doorphone is available places a call to the extension provided
        and connect it to the asterisk_doorphone
        """
        if self.is_available(self.config.DOORPHONE_EXTENSION):
            channel = "{tech}/{exten}@{context}}".format(
                tech=self.config.DOORPHONE_TECH,
                exten=self.config.DOORPHONE_EXTENSION,
                context=self.config.ORIGINATE_CONTEXT
            )
            self.ami.originate(
                channel=channel,
                exten=extension,
                context=self.config.ORIGINATE_CONTEXT,
                caller_id=self.config.DOORPHONE_CALLER_ID
            )
        else:
            print("Doorphone unavailable")

    def connect_to_asterisk(self):
        self.ami = AsteriskAMI()
        self.ami.connect(self.config.SERVER_IP, self.config.SERVER_PORT)
        self.ami.login(self.config.AMI_USERNAME, self.config.AMI_PASSWORD)

    def run_loop(self):
        if not self.apartments:
            raise Exception(
                """
                You must provide a dictionary with a keyboard keycode as key and 
                a string with the apartment number as value
                """)
        if not self.config:
            raise Exception("You must provide a config File")

        while True:
            try:
                print("New asterisk_doorphone")
                print("Gaining exclusive access to keyboard")
                self.get_exclusive_access_to_keyboard(self.config.DEVICE_PATH)
                print("Connecting to AsteriskPBX...")
                self.connect_to_asterisk()
            except Exception as error:
                self.device.ungrab()
                print("Error: ", error)
                time.sleep(3)
            else:
                while True:
                    try:
                        print("Press a key please.")
                        number = self.get_apartment_number()
                        if number:
                            self.call_apartment(number)
                    except Exception as error:
                        print(error)
                        break

    def start(self):
        return self.run_loop()


def doorphone_keyboard(*args, **kwargs):
    """Construct and start a :class:`DoorphoneKeyboard <DoorphoneKeyboard>`.
    Usage::
    from asterisk_doorphone import DoorphoneKeyboard

    import config
    import apartments


    def main():
        asterisk_doorphone = DoorphoneKeyboard(apartments, config)
        asterisk_doorphone.start()
    """
    usb_keyboard = UsbKeyboard(*args, **kwargs)
    return usb_keyboard.start()


if __name__ == "__main__":
    import sys
    sys.exit(doorphone_keyboard())
