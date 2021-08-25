from tala.model.device import DddDevice, DeviceAction


class RasaStringsDevice(DddDevice):
    class ShareMedia(DeviceAction):
        def perform(self, comment):
            return True
