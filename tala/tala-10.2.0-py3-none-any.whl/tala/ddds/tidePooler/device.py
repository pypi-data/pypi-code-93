import arrow

from tala.model import device


class TidepoolerDevice(device.DddDevice):
    class TidepoolerRecognizer(device.EntityRecognizer):
        """Entity recognizer for Tidepooler"""

        def recognize(self, utterance, language):
            """Recognize entities in a user utterance, given the specified language.

            This method is responsible for finding all dynamic entities in the utterance. Its accuracy affects the
            behaviour of the dialogue system.

            Since the search is conducted during runtime, particular care should be taken to ensure that the method is
            accurate, robust and has sufficient performance.

            Args:
                utterance (str): The utterance to be searched. For example 'call John'.
                language  (str): The language code of the utterance according to the ISO 639-2/B standard.
                                 Exceptions are Swedish ('sv' instead of 'swe') and Italian ('it' instead of 'ita').

            Returns:
                list of dicts: Given the example utterance "call John", the following entity could be returned
                [
                    {
                        "sort": "contact",       # The sort must be declared in the ontology.
                        "grammar_entry": "John", # The grammar entry as it occurred in 'utterance'.
                        "name": "contact_john",  # [optional] Should be a globally unique identifier. Must never be
                                                 # found as is in a user utterance. Use for example the form Sort_ID
                                                 # (e.g. contact_john).
                    },
                ]
            """
            return []

    class OneshotTideIntent(device.DeviceAction):
        def perform(self, city, date, readable_date, time, height):
            return True

    class readable_selected_date(device.DeviceWHQuery):
        def perform(self, date):
            arrow_date = arrow.get(date, "YYYY-MM-DD")
            readable_date = arrow_date.format("On dddd, MMMM D")
            return [readable_date]

    class time_of_first_high_tide(device.DeviceWHQuery):
        def perform(self):
            return ["7:18 am"]

    class height_of_first_high_tide(device.DeviceWHQuery):
        def perform(self):
            return ["1.5 feet"]

    class SupportedCitiesIntent(device.DeviceAction):
        def perform(self, cities):
            return True

    class supported_cities(device.DeviceWHQuery):
        def perform(self):
            return [
                "Seattle, Los Angeles, Monterey, San Diego, San Francisco, Boston, New York, Miami, Wilmington, Tampa, Galveston, Morehead, New Orleans, Beaufort, Myrtle Beach, Virginia Beach and Charleston"
            ]
