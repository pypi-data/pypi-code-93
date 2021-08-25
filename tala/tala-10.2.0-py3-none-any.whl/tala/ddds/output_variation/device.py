from tala.model.device import DddDevice, Validity, DeviceAction, DeviceWHQuery


class OutputVariationDevice(DddDevice):
    class ContactValidity(Validity):
        def is_valid(self, contact_to_call):
            if contact_to_call == "john":
                return True
            return False

    class ContactAndNumberTypeValidity(Validity):
        def is_valid(self, contact_to_call, number_type_to_call):
            if contact_to_call == "john" and number_type_to_call == "mobile":
                return True
            return False

    class TravelValidity(Validity):
        def is_valid(self, departure_time, destination_city):
            if departure_time == "today":
                return False
            if destination_city == "gothenburg":
                return False
            return True

    class Call(DeviceAction):
        def perform(self, contact_to_call, number_type_to_call):
            return True

    class BookTravel(DeviceAction):
        def perform(self, departure_time, destination_city):
            return True

    class TurnOnLights(DeviceAction):
        def perform(self):
            return True

    class PlayRadio(DeviceAction):
        def perform(self, channel_to_play, category_to_play):
            return True

    class queried_contact(DeviceWHQuery):
        def perform(self, queried_contact_firstname, queried_contact_lastname):
            if queried_contact_firstname == "mary" and queried_contact_lastname == "johnson":
                return [{"sort": "queried_contact",
                         "grammar_entry": "Mary Johnson"}]
            return []

    class queried_phonenumber(DeviceWHQuery):
        def perform(self, queried_contact):
            return [{"sort": "phonenumber",
                     "grammar_entry": "0123456789"}]
