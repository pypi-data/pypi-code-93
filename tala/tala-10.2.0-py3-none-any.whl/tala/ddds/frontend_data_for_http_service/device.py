# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, DeviceAction


class FrontendDataDevice(DddDevice):

    class GetMockEvent(DeviceAction):
        pass
