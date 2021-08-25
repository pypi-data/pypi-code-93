from tala.model.device import DddDevice, EntityRecognizer


class SmallGrammarDevice(DddDevice):
    class CityRecognizer(EntityRecognizer):
        def recognize_entity(self, string):
            return [{"name": "city_dublin", "sort": "city", "grammar_entry": "Dublin"}]
