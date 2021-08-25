from tdm.lib.device import DeviceWHQuery, DeviceAction, EntityRecognizer, DddDevice

JOHN = "first_name_john"
ANNA = "first_name_anna"

JOHNSON = "last_name_johnson"
THOMPSON = "last_name_thompson"

JOHN_JOHNSON = "contact_john_johnson"
JOHN_THOMPSON = "contact_john_thompson"
ANNA_JOHNSON = "contact_anna_johnson"
ANNA_THOMPSON = "contact_anna_thompson"

CONTACTS = {
    JOHN_JOHNSON: {
        "first_name": JOHN,
        "last_name": JOHNSON,
    },
    JOHN_THOMPSON: {
        "first_name": JOHN,
        "last_name": THOMPSON,
    },
    ANNA_JOHNSON: {
        "first_name": ANNA,
        "last_name": JOHNSON
    },
}

FIRST_NAMES = {"John": JOHN, "Anna": ANNA}

LAST_NAMES = {
    "Johnson": JOHNSON,
    "Thompson": THOMPSON,
}


class IncrementalSearchDevice(DddDevice):
    class Call(DeviceAction):
        def perform(self, selected_contact):
            return True

    class DeleteNumber(DeviceAction):
        def perform(self, selected_contact):
            return True

    class selected_contact(DeviceWHQuery):
        def perform(self, first_name, last_name):
            available_contacts = self.device.available_contacts(first_name, last_name)
            result = []
            for contact_id in available_contacts:
                full_name = self.device.full_name_of(contact_id)
                result.append({"name": contact_id, "sort": "contact", "grammar_entry": full_name})
            return result

    class ContactRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            result = []
            words = string.lower().split()
            first_names = self._entities_of_first_names(words)
            result.extend(first_names)
            last_names = self._entities_of_last_names(words)
            result.extend(last_names)
            return result

        def _entities_of_first_names(self, words):
            return self._entities_of_names(words, FIRST_NAMES, "first_name")

        def _entities_of_last_names(self, words):
            return self._entities_of_names(words, LAST_NAMES, "last_name")

        def _entities_of_names(self, words, names, sort):
            results = []
            for name, identifier in names.items():
                if name.lower() in words:
                    results.append({"name": identifier, "sort": sort, "grammar_entry": name.lower()})
            return results

    @classmethod
    def full_name_of(cls, contact_id):
        first_name = cls.first_name_of_contact(contact_id)
        last_name = cls.last_name_of_contact(contact_id)
        full_name = "%s %s" % (first_name, last_name)
        return full_name

    @classmethod
    def first_name_of_contact(cls, contact):
        identifier = CONTACTS[contact]["first_name"]
        return cls.name_of_identifier(FIRST_NAMES, identifier)

    @classmethod
    def last_name_of_contact(cls, contact):
        identifier = CONTACTS[contact]["last_name"]
        return cls.name_of_identifier(LAST_NAMES, identifier)

    @classmethod
    def name_of_identifier(cls, names, identifier):
        matching_names = [name for name, actual_id in names.items() if actual_id == identifier]
        assert len(
            matching_names
        ) == 1, "Expected to find one matching name but found %s for %s among %s" % (matching_names, identifier, names)
        return matching_names.pop()

    @classmethod
    def available_contacts(cls, first_name, last_name):
        matching_first_name_contacts = cls.contacts_with_matching_first_name(first_name)
        matching_last_name_contacts = cls.contacts_with_matching_last_name(last_name)
        available_contacts = matching_first_name_contacts.intersection(matching_last_name_contacts)
        return available_contacts

    @classmethod
    def contacts_with_matching_first_name(cls, first_name):
        return cls.contacts_with_matching("first_name", first_name)

    @classmethod
    def contacts_with_matching_last_name(cls, last_name):
        return cls.contacts_with_matching("last_name", last_name)

    @classmethod
    def contacts_with_matching(cls, key, value):
        if not value:
            return set(list(CONTACTS.keys()))
        return {contact_id for contact_id, contact in CONTACTS.items() if contact[key].lower() == value.lower()}

    class NumberTypeRecognizer(EntityRecognizer):
        def recognize(self, string, language):
            if "mobile" in string:
                return [{"name": "number_type_mobile", "sort": "number_type", "grammar_entry": "mobile"}]
            return []
