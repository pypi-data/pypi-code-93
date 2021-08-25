# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, DeviceAction, Validity, DeviceWHQuery


class RasaForStaticEntitiesDevice(DddDevice):
    CONTACTS = [
        ("contact_john", "john", "0701234567"),
        ("contact_john_chi", "约翰", "0701234567"),
        ("contact_lisa", "lisa", "0709876543"),
        ("contact_mary", "mary", "0706574839"),
        ("contact_andy", "andy", None),
        ("contact_andy_chi", "安迪", None),
    ]

    def __init__(self):
        self.call_result = True

    def has_phone_number(self, selected_contact):
        for identifier, name, number in self.CONTACTS:
            if selected_contact:
                if name.lower() == selected_contact.lower():
                    return number is not None
        return False

    def set_call_result(self, result):
        self.call_result = result

    class Call(DeviceAction):
        def perform(self, selected_contact_to_call):
            return True

    class PhoneNumberAvailableForSelectedContactToCall(Validity):
        def is_valid(self, selected_contact):
            return self.device.has_phone_number(selected_contact)

    class PhoneNumberAvailableForSelectedContactOfPhoneNumber(Validity):
        def is_valid(self, selected_contact):
            return self.device.has_phone_number(selected_contact)

    class phone_number_of_contact(DeviceWHQuery):
        def perform(self, selected_contact):
            for identifier, name, number in self.device.CONTACTS:
                if name.lower() == selected_contact.lower():
                    number_entity = {"grammar_entry": number}
                    return [number_entity]
            return []
