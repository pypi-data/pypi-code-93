# -*- coding: utf-8 -*-

from tala.model.device import DddDevice, DeviceAction, DeviceWHQuery, \
    Validity, EntityRecognizer


class FrontendDataDevice(DddDevice):

    JOHN = "contact_john"
    LISA = "contact_lisa"
    MARY = "contact_mary"
    ANDY = "contact_andy"

    PHONE_NUMBERS = {
        JOHN: "0701234567",
        LISA: "0709876543",
        MARY: "0706574839",
        ANDY: None
    }

    CONTACTS = {
        "46070202122": {
            "John": JOHN,
            "Lisa": LISA,
        },
        "46070404142": {
            "Mary": MARY,
            "Andy": ANDY
        }
    }

    class ReportStartSession(DeviceAction):
        def perform(self, start_session_mock_data):
            return True

    class start_session_mock_data(DeviceWHQuery):
        def perform(self):
            session_data = "There is no session data"
            if "session_data" in dir(self.device):
                session = self.device.session_data
                if "key" in session:
                    session_data = session["key"]
            return [session_data]

    class caller_phone_number(DeviceWHQuery):
        def perform(self):
            answer = "46079808182"
            if "session_data" in dir(self.device):
                session = self.device.session_data
                if "mock_caller" in session:
                    answer = session["mock_caller"]
            return [answer]

    class MockPerformReport(DeviceAction):
        def perform(self):
            if "session_data" in dir(self.device):
                return True
            self.failure_reason = "no_mock_data"
            return False

    class GetMockEvent(DeviceAction):
        pass

    class ContactRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            called_number = "46070404142"
            if "session_data" in dir(self.device):
                session = self.device.session_data
                if "mock_called" in session:
                    called_number = session["mock_called"]
            words = string.lower().split()
            results = []
            for contact_name, identifier in self.device.CONTACTS[called_number].items():
                if contact_name.lower() in words:
                    results.append({"value": identifier, "sort": "contact",
                                    "grammar_entry": contact_name})
            return results

    class FrontendSessionDataAvailable(Validity):
        def is_valid(self, selected_contact):
            if "session_data" in dir(self.device):
                session = self.device.session_data
                if "mock_called" in session:
                    called_number = session["mock_called"]
                    is_valid = called_number is not None
                    return is_valid
            return False

    class phone_number_of_contact(DeviceWHQuery):
        def perform(self, selected_contact):
            selected_contact = "contact_{}".format(selected_contact.lower())
            number = self.device.PHONE_NUMBERS.get(selected_contact)
            return [number]
