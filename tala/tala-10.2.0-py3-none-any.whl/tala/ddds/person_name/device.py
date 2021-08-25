# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, DeviceAction, DeviceWHQuery


class PersonNameDevice(DddDevice):
    class Call(DeviceAction):
        def perform(self, name_of_contact_to_call):
            return True

    class CreateReport(DeviceAction):
        def perform(self, name_of_person_in_report):
            return name_of_person_in_report == u"Amélie Bernard"

    class name_of_person_in_report(DeviceWHQuery):
        def perform(self):
            return [{"name": u"Amélie Bernard",
                     "sort": "person_name"}]
