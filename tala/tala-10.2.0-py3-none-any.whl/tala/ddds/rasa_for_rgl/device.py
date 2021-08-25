# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, EntityRecognizer, DeviceAction, Validity, DeviceWHQuery
import unicodedata


class RasaForRglDevice(DddDevice):
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

    def exists(self, selected_contact):
        for identifier, name, number in self.CONTACTS:
            if selected_contact:
                if name.lower() == selected_contact.lower():
                    return True
        return False

    def set_call_result(self, result):
        self.call_result = result

    class Call(DeviceAction):
        def perform(self, selected_contact_to_call):
            return True

    class ContactRecognizer(EntityRecognizer):
        def recognize_entity(self, string):
            result = []
            tokens = string.split(" ")
            for contact_id, contact_name, number in self.device.CONTACTS:
                if self._contact_name_matches_tokens(contact_name, tokens):
                    contact_name = contact_name.capitalize()
                    recognized_entity = {"sort": "contact", "grammar_entry": contact_name, "name": contact_id}
                    result.append(recognized_entity)
            return result

        def _contact_name_matches_tokens(self, contact_name, tokens):
            if self._is_chinese_string(contact_name):
                return self._chinese_contact_name_matches_tokens(contact_name, tokens)
            else:
                return self._non_chinese_contact_name_matches_tokens(contact_name, tokens)

        def _is_chinese_string(self, string):
            return unicodedata.category(string[0]) == 'Lo'

        def _chinese_contact_name_matches_tokens(self, contact_name, tokens):
            for token in tokens:
                if contact_name in token:
                    return True

        def _non_chinese_contact_name_matches_tokens(self, contact_name, tokens):
            contact_name_lower = contact_name.lower()
            for token in tokens:
                if token.lower() == contact_name_lower:
                    return True

    class PhoneNumberAvailableForSelectedContactToCall(Validity):
        def is_valid(self, selected_contact):
            return self.device.has_phone_number(selected_contact)

    class ContactExistsForSelectedContactToCall(Validity):
        def is_valid(self, selected_contact):
            return self.device.exists(selected_contact)

    class PhoneNumberAvailableForSelectedContactOfPhoneNumber(Validity):
        def is_valid(self, selected_contact):
            return self.device.has_phone_number(selected_contact)

    class ContactExistsForSelectedContactOfPhoneNumber(Validity):
        def is_valid(self, selected_contact):
            return self.device.exists(selected_contact)

    class phone_number_of_contact(DeviceWHQuery):
        def perform(self, selected_contact):
            for identifier, name, number in self.device.CONTACTS:
                if name.lower() == selected_contact.lower():
                    number_entity = {"grammar_entry": number}
                    return [number_entity]
            return []
